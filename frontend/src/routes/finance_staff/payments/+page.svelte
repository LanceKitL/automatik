<script lang="ts">
	import { onMount } from 'svelte';
	import { getFinancePayments, createFinancePayment, getFinanceLoans, reviewPayment, resolvePhotoUrl } from '$lib/services/api';
	import DataTable from '$lib/components/DataTable.svelte';
	import { toast } from 'svelte-sonner';
	import { Eye, Plus, X, AlertTriangle, RefreshCw, Check, Ban } from '@lucide/svelte';

	let payments = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);
	let search = $state('');
	let filterMethod = $state<'all' | string>('all');
	let filterReview = $state<'all' | 'pending_verification'>('all');
	let dateFrom = $state('');
	let dateTo = $state('');

	// Record Payment modal
	let showModal = $state(false);

	// Review modal
	let showReviewModal = $state(false);
	let reviewTarget = $state<Record<string, unknown> | null>(null);
	let reviewAction = $state<'verified' | 'rejected'>('verified');
	let reviewNote = $state('');
	let reviewing = $state(false);

	let previewUrl = $state<string | null>(null);
	let saving = $state(false);
	let modalError = $state('');
	let sales = $state<Record<string, unknown>[]>([]);
	let payForm = $state({
		sale_id: '',
		amount_paid: '',
		payment_method: 'cash',
		payment_allocation: 'amortization',
		reference: '',
	});

	const now = new Date();
	const timestamp = now.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
		+ ' · ' + now.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });

	function filtered() {
		return payments.filter(p => {
			const pm = String(p.payment_method ?? '').toLowerCase();
			const matchMethod = filterMethod === 'all' || pm === filterMethod;
			const matchReview = filterReview === 'all' || (p.review_status as string) === filterReview;
			const matchDateFrom = !dateFrom || String(p.payment_date ?? '').slice(0, 10) >= dateFrom;
			const matchDateTo = !dateTo || String(p.payment_date ?? '').slice(0, 10) <= dateTo;
			const s = search.toLowerCase();
			const matchSearch = !s
				|| String(p.customer_name ?? '').toLowerCase().includes(s)
				|| (String(p.brand ?? '') + ' ' + String(p.model ?? '')).toLowerCase().includes(s)
				|| String(p.payment_id ?? '').toLowerCase().includes(s);
			return matchMethod && matchReview && matchDateFrom && matchDateTo && matchSearch;
		});
	}

	let totalCollected = $derived(payments.reduce((s, p) => s + Number(p.amount_paid), 0));
	let withProof = $derived(payments.filter(p => p.proof_of_payment).length);
	let todayCount = $derived.by(() => {
		const today = new Date().toISOString().slice(0, 10);
		return payments.filter(p => String(p.payment_date ?? '').slice(0, 10) === today).length;
	});

	function methodBadgeClass(m: string | undefined): string {
		const s = (m ?? '').toLowerCase();
		if (s === 'cash') return 'mb m-cash';
		if (s.includes('bank')) return 'mb m-bank';
		if (s === 'online') return 'mb m-online';
		return 'mb m-def';
	}

	function allocBadgeClass(a: string | undefined): string {
		const s = (a ?? '').toLowerCase();
		if (s.includes('down')) return 'ab a-dp';
		if (s.includes('amort') || s.includes('monthly')) return 'ab a-int';
		if (s.includes('insur')) return 'ab a-ins';
		if (s.includes('service') || s.includes('fee')) return 'ab a-svc';
		if (s.includes('full') || s.includes('cash')) return 'ab a-fc';
		return 'ab a-def';
	}

	function reviewLabel(rv: string | undefined): string {
		if (rv === 'pending_verification') return 'Pending';
		if (rv === 'verified') return 'Verified';
		if (rv === 'rejected') return 'Rejected';
		return '—';
	}

	function reviewClass(rv: string | undefined): string {
		if (rv === 'pending_verification') return 'rb-pending';
		if (rv === 'verified') return 'rb-verified';
		if (rv === 'rejected') return 'rb-rejected';
		return 'rb-def';
	}

	function openReview(p: Record<string, unknown>, action: 'verified' | 'rejected') {
		reviewTarget = p;
		reviewAction = action;
		reviewNote = '';
		showReviewModal = true;
	}

	async function handleReview() {
		if (!reviewTarget) return;
		if (reviewAction === 'rejected' && !reviewNote.trim()) {
			toast.error('A rejection reason is required.');
			return;
		}
		reviewing = true;
		try {
			await reviewPayment(reviewTarget.payment_id as number, reviewAction, reviewNote || undefined);
			toast.success(reviewAction === 'verified' ? 'Payment approved' : 'Payment rejected');
			showReviewModal = false;
			await loadPayments();
		} catch (e: unknown) {
			const msg = e instanceof Error ? e.message : 'Review failed';
			toast.error(msg);
		} finally {
			reviewing = false;
		}
	}

	async function loadPayments() {
		loading = true;
		try {
			const res = await getFinancePayments();
			payments = res.data as Record<string, unknown>[];
		} catch { toast.error('Failed to load payments.'); }
		finally { loading = false; }
	}

	async function loadSales() {
		try {
			const res = await getFinanceLoans();
			sales = res.data ?? [];
		} catch { toast.error('Failed to load sales data.'); }
	}

	onMount(async () => {
		await Promise.all([loadPayments(), loadSales()]);
	});

	async function openModal() {
		showModal = true;
		modalError = '';
		payForm = { sale_id: '', amount_paid: '', payment_method: 'cash', payment_allocation: 'amortization', reference: '' };
	}

	async function handleRecordPayment() {
		if (!payForm.sale_id || !payForm.amount_paid || !payForm.payment_method) {
			modalError = 'Sale, amount, and method are required.';
			return;
		}
		saving = true;
		modalError = '';
		try {
			await createFinancePayment(Number(payForm.sale_id), {
				amount_paid: Number(payForm.amount_paid),
				payment_method: payForm.payment_method,
				payment_allocation: payForm.payment_allocation,
				reference: payForm.reference || null,
			});
			toast.success('Payment recorded successfully.');
			showModal = false;
			await loadPayments();
		} catch (e: unknown) {
			modalError = e instanceof Error ? e.message : 'Failed to record payment.';
		} finally {
			saving = false;
		}
	}
</script>

<div class="page">

	<div class="top-bar">
		<div class="title-row">
			<h1>Payments</h1>
			<span style="color:var(--text-muted); margin-top:4px; font-size:14px">Monitor your clients payments</span>
		</div>
		<div class="top-actions">
			<button class="btn-refresh" onclick={loadPayments}><RefreshCw size={14} /></button>
			<button class="btn-record" onclick={openModal}><Plus size={14} /> Record Payment</button>
			<span class="timestamp">{timestamp}</span>
		</div>
	</div>

	<div class="stats-row">
		<div class="sc s1">
			<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="sc-icon" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
			<div class="sc-val">{payments.length}</div>
			<div class="sc-lbl">Total Payments</div>
		</div>
		<div class="sc s2">
			<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="sc-icon" aria-hidden="true"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>
			<div class="sc-val">₱{totalCollected.toLocaleString()}</div>
			<div class="sc-lbl">Total Collected</div>
		</div>
		<div class="sc s3">
			<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="sc-icon" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><polyline points="9 15 11 17 15 13"/></svg>
			<div class="sc-val">{withProof}</div>
			<div class="sc-lbl">With Proof</div>
		</div>
		<div class="sc s4">
			<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="sc-icon" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
			<div class="sc-val">{todayCount}</div>
			<div class="sc-lbl">Today</div>
		</div>
	</div>

		<div class="toolbar">
			<div class="search-wrap">
				<svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
				<input class="search-input" type="text" placeholder="Search customer or vehicle…" bind:value={search} />
			</div>
			<div class="filter-row">
				<button class="fp" class:active={filterMethod === 'all'} onclick={() => filterMethod = 'all'}>All</button>
				<button class="fp" class:active={filterMethod === 'cash'} onclick={() => filterMethod = 'cash'}>Cash</button>
				<button class="fp" class:active={filterMethod === 'bank_transfer'} onclick={() => filterMethod = 'bank_transfer'}>Bank</button>
				<button class="fp" class:active={filterMethod === 'online'} onclick={() => filterMethod = 'online'}>Online</button>
			</div>
			<div class="filter-row">
				<button class="fp" class:active={filterReview === 'all'} onclick={() => filterReview = 'all'}>All Status</button>
				<button class="fp" class:active={filterReview === 'pending_verification'} onclick={() => filterReview = 'pending_verification'}>Pending Verification</button>
			</div>
			<div class="date-filters">
				<input type="date" class="date-input" bind:value={dateFrom} title="From" />
				<span class="date-sep">–</span>
				<input type="date" class="date-input" bind:value={dateTo} title="To" />
				{#if dateFrom || dateTo}
					<button class="clear-dates" onclick={() => { dateFrom = ''; dateTo = ''; }}><X size={12} /></button>
				{/if}
			</div>
		</div>

	{#if loading}
		<div class="loading-state"><span class="spinner"></span><p>Loading payments…</p></div>
	{:else}
		<DataTable columns={['ID','Customer','Vehicle','Amount','Method','Allocation','Review','Date','Recorded By','Proof','Action']}>
			{#each filtered() as p (p.payment_id)}
				<tr>
					<td class="td-id">{p.payment_id}</td>
					<td class="td-name">{p.customer_name ?? '—'}</td>
					<td class="td-vehicle">{(p.brand ?? '') + ' ' + (p.model ?? '') || '—'}</td>
					<td class="td-amount">₱{Number(p.amount_paid).toLocaleString()}</td>
					<td><span class="{methodBadgeClass(p.payment_method as string)}">{p.payment_method ?? '—'}</span></td>
					<td><span class="{allocBadgeClass(p.payment_allocation as string)}">{p.payment_allocation ?? '—'}</span></td>
					<td>
						<span class="review-badge {reviewClass(p.review_status as string)}">{reviewLabel(p.review_status as string)}</span>
					</td>
					<td class="td-date">{p.payment_date ? String(p.payment_date).slice(0, 10) : '—'}</td>
					<td class="td-rec">{p.recorded_by_name ?? '—'}</td>
					<td class="td-proof">
						{#if p.proof_of_payment}
							<button onclick={() => previewUrl = String(p.proof_of_payment)} class="proof-btn" aria-label="View proof of payment"><Eye size={14} /></button>
						{:else}
							<span class="muted">—</span>
						{/if}
					</td>
					<td class="td-action">
						{#if (p.review_status as string) === 'pending_verification'}
							<div class="review-actions">
								<button class="btn-approve" onclick={() => openReview(p, 'verified')} title="Approve"><Check size={14} /></button>
								<button class="btn-reject" onclick={() => openReview(p, 'rejected')} title="Reject"><Ban size={14} /></button>
							</div>
						{:else}
							<span class="muted">—</span>
						{/if}
					</td>
				</tr>
			{:else}
				<tr><td colspan="11" class="empty-state">No payments found.</td></tr>
			{/each}
		</DataTable>
	{/if}
</div>

<!-- Review Modal -->
{#if showReviewModal && reviewTarget}
	<div class="modal-overlay" onclick={() => showReviewModal = false}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>{reviewAction === 'verified' ? 'Approve' : 'Reject'} Payment</h2>
				<button class="close-btn" onclick={() => showReviewModal = false}><X size={18} /></button>
			</div>
			<div class="modal-body">
				<div style="font-size:13px; display:flex; flex-direction:column; gap:6px;">
					<p style="margin:0;"><strong>Payment ID:</strong> #{reviewTarget.payment_id}</p>
					<p style="margin:0;"><strong>Customer:</strong> {reviewTarget.customer_name}</p>
					<p style="margin:0;"><strong>Amount:</strong> ₱{Number(reviewTarget.amount_paid).toLocaleString()}</p>
					<p style="margin:0;"><strong>Schedule ID:</strong> {reviewTarget.schedule_id ?? '—'}</p>
						{#if reviewTarget.proof_of_payment}
							<p style="margin:0;">
								<strong>Proof:</strong>
								<button onclick={() => previewUrl = String(reviewTarget.proof_of_payment)} style="background:none; border:none; color:var(--primary); text-decoration:underline; cursor:pointer; font-size:13px; padding:0;">View Screenshot</button>
							</p>
						{/if}
				</div>
				<div class="form-group">
					<label>Note {reviewAction === 'rejected' ? '(required)' : '(optional)'}</label>
					<textarea class="review-note" bind:value={reviewNote} placeholder={reviewAction === 'rejected' ? 'Reason for rejection…' : 'Optional note…'}></textarea>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" onclick={() => showReviewModal = false} disabled={reviewing}>Cancel</button>
				<button
					class={reviewAction === 'verified' ? 'btn-review-approve' : 'btn-review-reject'}
					onclick={handleReview}
					disabled={reviewing}
				>
					{reviewing ? 'Processing…' : reviewAction === 'verified' ? 'Approve Payment' : 'Reject Payment'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Image Preview Modal -->
{#if previewUrl}
	<div class="modal-overlay" onclick={() => previewUrl = null}>
		<div class="preview-modal" onclick={(e) => e.stopPropagation()}>
			<button class="preview-close" onclick={() => previewUrl = null}><X size={20} /></button>
			<img src={resolvePhotoUrl(previewUrl)} alt="Payment screenshot" class="preview-img" />
		</div>
	</div>
{/if}

<!-- Record Payment Modal -->
{#if showModal}
	<div class="modal-overlay" onclick={() => showModal = false}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Record Payment</h2>
				<button class="close-btn" onclick={() => showModal = false}><X size={18} /></button>
			</div>
			<form onsubmit={(e) => { e.preventDefault(); handleRecordPayment(); }}>
				<div class="modal-body">
					{#if modalError}
						<div class="alert-error"><AlertTriangle size={14} /> {modalError}</div>
					{/if}
					<div class="form-group">
						<label>Sale (Loan) <span class="req">*</span></label>
						<select bind:value={payForm.sale_id}>
							<option value="">— Select a sale —</option>
							{#each sales as s}
								<option value={s.sale_id ?? s.loan_id}>
									#{s.sale_id ?? s.loan_id} — {s.customer_name ?? '—'} / {s.brand ?? ''} {s.model ?? ''}
								</option>
							{/each}
						</select>
					</div>
					<div class="form-row">
						<div class="form-group">
							<label>Amount <span class="req">*</span></label>
							<input type="number" step="0.01" min="0" bind:value={payForm.amount_paid} placeholder="0.00" />
						</div>
						<div class="form-group">
							<label>Method <span class="req">*</span></label>
							<select bind:value={payForm.payment_method}>
								<option value="cash">Cash</option>
								<option value="bank_transfer">Bank Transfer</option>
								<option value="check">Check</option>
								<option value="online">Online</option>
							</select>
						</div>
					</div>
					<div class="form-row">
						<div class="form-group">
							<label>Allocation</label>
							<select bind:value={payForm.payment_allocation}>
								<option value="amortization">Amortization</option>
								<option value="insurance">Insurance</option>
								<option value="service_fee">Service Fee</option>
							</select>
						</div>
						<div class="form-group">
							<label>Reference</label>
							<input type="text" bind:value={payForm.reference} placeholder="Optional ref #" />
						</div>
					</div>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn-cancel" onclick={() => showModal = false}>Cancel</button>
					<button type="submit" class="btn-submit" disabled={saving}>{saving ? 'Saving…' : 'Record Payment'}</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<style>
	@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

	.page { font-family: var(--font-sans, 'Syne', sans-serif); padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

	/* Top bar */
	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; flex-direction: column; margin: 0;padding: 0; align-items: center; gap: 10px; align-items: start; }
	h1 { font-size: 24px; font-weight: 700; color: var(--text-primary); margin: 0; }
	.top-actions { display: flex; align-items: center; gap: 8px; }
	.timestamp { font-family: var(--font-mono, 'DM Mono', monospace); font-size: 11px; color: var(--text-muted, #8892b0); background: var(--bg-muted, #f7f9fe); border: 0.5px solid var(--border, #dce3f5); padding: 4px 12px; border-radius: 20px; }
	.btn-refresh { width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center; border: 0.5px solid var(--border, #dce3f5); border-radius: 8px; background: var(--bg-card, #fff); color: var(--text-light, #5b6684); cursor: pointer; }
	.btn-refresh:hover { background: var(--bg-muted, #f7f9fe); }
	.btn-record { display: inline-flex; align-items: center; gap: 6px; height: 32px; padding: 0 14px; border: none; border-radius: 8px; background: var(--primary-deeper, #1a2e80); color: var(--accent, #e8c97e); font-family: inherit; font-size: 12px; font-weight: 600; cursor: pointer; }
	.btn-record:hover { opacity: .9; }

	/* Loading */
	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted, #8892b0); font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid var(--border, #dce3f5); border-top-color: var(--primary, #3a5bd9); border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }

	/* Stat cards */
	.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 1rem; }
	.sc { background: var(--bg-stat, #f0f3fb); border-radius: 10px; padding: .65rem .9rem; position: relative; overflow: hidden; }
	.sc::before { content: ''; position: absolute; top: -8px; right: -8px; width: 44px; height: 44px; border-radius: 50%; opacity: .12; }
	.sc.s1::before { background: var(--accent, #e8c97e); }
	.sc.s2::before { background: var(--primary, #3a5bd9); }
	.sc.s3::before { background: var(--success, #2e9a6b); }
	.sc.s4::before { background: var(--warning, #b45309); }
	.sc-icon { display: block; margin-bottom: 6px; }
	.sc.s1 .sc-icon { color: var(--accent-dark, #c9a84c); }
	.sc.s2 .sc-icon { color: var(--primary, #3a5bd9); }
	.sc.s3 .sc-icon { color: var(--success, #2e9a6b); }
	.sc.s4 .sc-icon { color: var(--warning, #b45309); }
	.sc-val { font-size: 18px; font-weight: 700; color: var(--text-primary, #12173a); letter-spacing: -.5px; line-height: 1; }
	.sc-lbl { font-size: 10px; font-weight: 500; color: var(--text-muted, #8892b0); letter-spacing: .5px; text-transform: uppercase; margin-top: 2px; }

	/* Toolbar */
	.toolbar { display: flex; align-items: center; gap: 3rem; margin-bottom: 1rem; flex-wrap: wrap; }
	.search-wrap { position: relative; flex: 1; min-width: 160px; }
	.search-icon { position: absolute; left: 9px; top: 50%; transform: translateY(-50%); color: var(--text-muted, #8892b0); pointer-events: none; }
	.search-input { width: 100%; height: 32px; padding: 0 10px 0 30px; border: 0.5px solid var(--border, #dce3f5); border-radius: 8px; font-family: var(--font-sans, 'Syne', sans-serif); font-size: 12px; color: var(--text-primary, #12173a); background: var(--bg-card, #ffffff); outline: none; }
	.search-input:focus { border-color: var(--primary, #3a5bd9); }
	.filter-row { display: flex; gap: 5px; flex-shrink: 0; }
	.fp { height: 28px; padding: 0 11px; border: 0.5px solid var(--border, #dce3f5); border-radius: 20px; background: var(--bg-muted, #f7f9fe); font-family: var(--font-sans, 'Syne', sans-serif); font-size: 11px; color: var(--text-light, #5b6684); cursor: pointer; transition: .15s; white-space: nowrap; }
	.fp.active { background: var(--primary-deeper, #1a2e80); color: var(--accent, #e8c97e); border-color: var(--primary-deeper, #1a2e80); }
	.date-filters { display: flex; align-items: center; gap: 4px; flex-shrink: 0; }
	.date-input { height: 28px; padding: 0 8px; border: 0.5px solid var(--border, #dce3f5); border-radius: 8px; font-family: var(--font-sans, 'Syne', sans-serif); font-size: 11px; color: var(--text-primary, #12173a); background: var(--bg-card, #fff); outline: none; width: 115px; }
	.date-sep { color: var(--text-muted, #8892b0); font-size: 11px; }
	.clear-dates { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border: none; border-radius: 50%; background: var(--bg-hover, #eaeef8); color: var(--text-muted, #8892b0); cursor: pointer; flex-shrink: 0; }

	/* Table cells */
	:global(.td-id)     { font-family: var(--font-mono, 'DM Mono', monospace); font-size: 10px; color: var(--text-muted, #8892b0); }
	:global(.td-name)   { font-size: 12px; font-weight: 600; color: var(--text-primary, #12173a); }
	:global(.td-vehicle){ font-size: 11px; color: var(--text-light, #5b6684); }
	:global(.td-amount) { font-family: var(--font-mono, 'DM Mono', monospace); font-size: 11px; color: var(--success-dark, #1e7a4e); font-weight: 600; }
	:global(.td-date)   { font-family: var(--font-mono, 'DM Mono', monospace); font-size: 10px; color: var(--text-muted, #8892b0); }
	:global(.td-rec)    { font-size: 11px; color: var(--text-light, #5b6684); }
	:global(.td-proof)  { text-align: center; }
	.empty-state { padding: 2.5rem; text-align: center; color: var(--text-muted, #8892b0); font-size: 12px; }

	/* Method badges */
	.mb { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 20px; font-size: 10px; font-weight: 600; white-space: nowrap; }
	.m-cash   { background: var(--success-bg, #e6f4ed); color: var(--success-text, #1a5c3e); }
	.m-bank   { background: var(--primary-bg, #eef2fd); color: var(--primary-deeper, #1a2e80); }
	.m-online { background: var(--warning-bg, #fdf0d9); color: var(--warning-text, #7a3a04); }
	.m-def    { background: var(--bg-hover, #eaeef8); color: var(--text-light, #5b6684); }

	/* Allocation badges */
	.ab { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 20px; font-size: 10px; font-weight: 600; }
	.a-dp  { background: var(--primary-bg, #eef2fd); color: var(--primary-deeper, #1a2e80); }
	.a-int { background: var(--warning-bg, #fdf0d9); color: var(--warning-text, #7a3a04); }
	.a-ins { background: var(--success-bg, #e6f4ed); color: var(--success-text, #1a5c3e); }
	.a-svc { background: var(--bg-hover, #eaeef8); color: var(--text-light, #5b6684); }
	.a-fc  { background: #f0fdf4; color: #166534; }
	.a-def { background: var(--bg-hover, #eaeef8); color: var(--text-light, #5b6684); }

	/* Proof link */
	.proof-link { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 8px; background: var(--primary-bg, #eef2fd); color: var(--primary-deeper, #1a2e80); text-decoration: none; transition: background .15s; }
	.proof-link:hover { background: var(--primary-bg-mid, #dce4fb); }
	.proof-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 8px; background: var(--primary-bg, #eef2fd); color: var(--primary-deeper, #1a2e80); border: none; cursor: pointer; transition: background .15s; }
	.proof-btn:hover { background: var(--primary-bg-mid, #dce4fb); }
	.muted { color: var(--text-muted, #8892b0); }

	.preview-modal { position:relative; max-width:90vw; max-height:90vh; display:flex; align-items:center; justify-content:center; }
	.preview-img { max-width:100%; max-height:90vh; border-radius:8px; box-shadow:0 20px 60px rgba(0,0,0,0.3); }
	.preview-close { position:absolute; top:-40px; right:0; background:rgba(0,0,0,0.5); color:#fff; border:none; border-radius:50%; width:32px; height:32px; display:flex; align-items:center; justify-content:center; cursor:pointer; }
	.preview-close:hover { background:rgba(0,0,0,0.7); }

	/* Modal */
	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; }
	.modal { background: var(--bg-card, #fff); border-radius: 12px; width: 100%; max-width: 500px; box-shadow: 0 20px 60px rgba(0,0,0,.15); overflow: hidden; }
	.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 1px solid var(--border, #dce3f5); }
	.modal-header h2 { font-size: 16px; font-weight: 700; color: var(--text-primary, #12173a); margin: 0; }
	.close-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border: none; border-radius: 6px; background: transparent; color: var(--text-muted, #8892b0); cursor: pointer; }
	.close-btn:hover { background: var(--bg-hover, #eaeef8); }
	.modal-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
	.alert-error { display: flex; align-items: center; gap: 6px; background: #fef2f2; color: #dc2626; padding: 8px 12px; border-radius: var(--radius-sm, 6px); font-size: 12px; border: 1px solid #fecaca; }
	.form-group { display: flex; flex-direction: column; gap: 4px; flex: 1; }
	.form-group label { font-size: 11px; font-weight: 600; color: var(--text-light, #5b6684); letter-spacing: .3px; }
	.form-group .req { color: #dc2626; }
	.form-group input,
	.form-group select { height: 36px; padding: 0 10px; border: 0.5px solid var(--border, #dce3f5); border-radius: 8px; font-family: var(--font-sans, 'Syne', sans-serif); font-size: 12px; color: var(--text-primary, #12173a); background: var(--bg-card, #fff); outline: none; }
	.form-group input:focus,
	.form-group select:focus { border-color: var(--primary, #3a5bd9); }
	.form-row { display: flex; gap: 12px; }
	.modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 1rem 1.25rem; border-top: 1px solid var(--border, #dce3f5); }
	.btn-cancel { height: 34px; padding: 0 16px; border: 0.5px solid var(--border, #dce3f5); border-radius: 8px; background: var(--bg-card, #fff); font-family: inherit; font-size: 12px; color: var(--text-light, #5b6684); cursor: pointer; }
	.btn-submit { height: 34px; padding: 0 16px; border: none; border-radius: 8px; background: var(--primary-deeper, #1a2e80); color: var(--accent, #e8c97e); font-family: inherit; font-size: 12px; font-weight: 600; cursor: pointer; }
	.btn-submit:disabled { opacity: .5; cursor: not-allowed; }

	.review-badge { display:inline-block; padding:2px 8px; border-radius:20px; font-size:10px; font-weight:600; }
	.rb-pending { background:#fef3c7; color:#92400e; }
	.rb-verified { background:#d1fae5; color:#065f46; }
	.rb-rejected { background:#fef2f2; color:#dc2626; }
	.rb-def { background:var(--bg-muted); color:var(--text-muted); }

	.td-action { text-align:center; }
	.review-actions { display:flex; gap:4px; justify-content:center; }
	.btn-approve, .btn-reject { display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border:none; border-radius:6px; cursor:pointer; }
	.btn-approve { background:#d1fae5; color:#065f46; }
	.btn-approve:hover { background:#a7f3d0; }
	.btn-reject { background:#fef2f2; color:#dc2626; }
	.btn-reject:hover { background:#fecaca; }

	.btn-review-approve { height:34px; padding:0 16px; border:none; border-radius:8px; background:#16a34a; color:#fff; font-family:inherit; font-size:12px; font-weight:600; cursor:pointer; }
	.btn-review-approve:hover { background:#15803d; }
	.btn-review-reject { height:34px; padding:0 16px; border:none; border-radius:8px; background:#dc2626; color:#fff; font-family:inherit; font-size:12px; font-weight:600; cursor:pointer; }
	.btn-review-reject:hover { background:#b91c1c; }
	.review-note { width:100%; min-height:60px; padding:8px 10px; border:0.5px solid var(--border); border-radius:8px; font-family:var(--font-sans); font-size:12px; resize:vertical; }
	.review-note:focus { border-color:var(--primary); outline:none; }

	@media (max-width: 600px) {
		.stats-row { grid-template-columns: repeat(2, 1fr); }
		.modal { max-width: 100%; }
	}
</style>
