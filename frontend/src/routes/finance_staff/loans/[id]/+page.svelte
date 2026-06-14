<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import {
		getFinanceLoan,
		updateFinanceLoanStatus,
		updateAmortizationStatus,
		reviewPayment,
		getFinanceInsurance,
		type LoanItem,
		type ScheduleItem,
		resolvePhotoUrl
	} from '$lib/services/api';
	import DataTable from '$lib/components/DataTable.svelte';
	import { toast } from 'svelte-sonner';
	import { ArrowLeft, Shield, Plus, Check, Ban, X } from '@lucide/svelte';

	let loanId = $derived(Number($page.params.id));
	let loan = $state<(LoanItem & { amortization_schedule: ScheduleItem[] }) | null>(null);
	let schedule = $state<ScheduleItem[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let actionLoading = $state(false);
	let insuranceRecords = $state<Record<string, unknown>[]>([]);

	let showReviewModal = $state(false);
	let reviewPaymentId = $state<number | null>(null);
	let reviewScheduleId = $state<number | null>(null);
	let reviewAction = $state<'verified' | 'rejected'>('verified');
	let reviewNote = $state('');
	let reviewing = $state(false);

	let previewUrl = $state<string | null>(null);

	onMount(async () => {
		try {
			const res = await getFinanceLoan(loanId);
			loan = res.data as LoanItem & { amortization_schedule: ScheduleItem[] };
			schedule = loan?.amortization_schedule ?? [];
			const insRes = await getFinanceInsurance();
			insuranceRecords = (insRes.data ?? []).filter((r: Record<string, unknown>) => r.sale_id === loan?.sale_id);
		} catch (e: unknown) {
			error = e instanceof Error ? e.message : 'Failed to load loan.';
		} finally {
			loading = false;
		}
	});

	async function handleStatus(status: 'approved' | 'rejected') {
		if (!confirm(`Mark this loan as ${status}?`)) return;
		actionLoading = true;
		try {
			await updateFinanceLoanStatus(loanId, status);
			toast.success(`Loan #${loanId} ${status}.`);
			const res = await getFinanceLoan(loanId);
			loan = res.data as LoanItem & { amortization_schedule: ScheduleItem[] };
			schedule = loan?.amortization_schedule ?? [];
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Error updating loan status.');
		} finally {
			actionLoading = false;
		}
	}

	async function handleMarkPaid(scheduleId: number) {
		if (!confirm('Mark this amortization entry as paid?')) return;
		try {
			await updateAmortizationStatus(scheduleId, 'paid');
			toast.success(`Entry #${scheduleId} marked as paid.`);
			const res = await getFinanceLoan(loanId);
			loan = res.data as LoanItem & { amortization_schedule: ScheduleItem[] };
			schedule = loan?.amortization_schedule ?? [];
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Error marking as paid.');
		}
	}

	function openReview(entry: ScheduleItem, action: 'verified' | 'rejected') {
		reviewPaymentId = entry.payment_id ?? null;
		reviewScheduleId = entry.schedule_id;
		reviewAction = action;
		reviewNote = '';
		showReviewModal = true;
	}

	async function handleReviewSubmit() {
		if (!reviewPaymentId) return;
		if (reviewAction === 'rejected' && !reviewNote.trim()) {
			toast.error('A rejection reason is required.');
			return;
		}
		reviewing = true;
		try {
			await reviewPayment(reviewPaymentId, reviewAction, reviewNote || undefined);
			showReviewModal = false;
			toast.success(`Payment for schedule #${reviewScheduleId} ${reviewAction}.`);
			const res = await getFinanceLoan(loanId);
			loan = res.data as LoanItem & { amortization_schedule: ScheduleItem[] };
			schedule = loan?.amortization_schedule ?? [];
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Review failed.');
		} finally {
			reviewing = false;
		}
	}

	function fmt(n: string | number | null | undefined): string {
		if (n == null) return '—';
		return `₱${Number(n).toLocaleString()}`;
	}
</script>

<div class="page">
	<!-- Back link -->
	<a href="/finance_staff/loans" class="back-link" onclick={(e) => { e.preventDefault(); goto('/finance_staff/loans'); }}>
		<ArrowLeft size={14} /> Back to Loans
	</a>

	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading loan details…</span>
		</div>
	{:else if error}
		<div class="error-msg">{error}</div>
	{:else if loan}
		<h1>Loan #{loanId}</h1>

		<div class="cards-grid">
			<!-- Customer & Vehicle Card -->
			<div class="card">
				<h3>Customer & Vehicle</h3>
				<div class="info-grid">
					<div class="info-row"><span class="label">Customer</span><span class="value">{loan.customer_name}</span></div>
					<div class="info-row"><span class="label">Sale ID</span><span class="value mono">#{loan.sale_id}</span></div>
					<div class="info-row"><span class="label">Vehicle</span><span class="value">{loan.brand} {loan.model}</span></div>
				</div>
			</div>

			<!-- Loan Details Card -->
			<div class="card">
				<h3>Loan Details</h3>
				<div class="info-grid">
					<div class="info-row"><span class="label">Loan Amount</span><span class="value highlight">{fmt(loan.loan_amount)}</span></div>
					<div class="info-row"><span class="label">Down Payment</span><span class="value">{fmt(loan.down_payment)}</span></div>
					<div class="info-row"><span class="label">Interest Rate</span><span class="value mono">{loan.interest_rate}%</span></div>
					<div class="info-row"><span class="label">Term</span><span class="value">{loan.term_months} months</span></div>
					<div class="info-row"><span class="label">Monthly Amort.</span><span class="value highlight">{fmt(loan.monthly_amortization)}</span></div>
					<div class="info-row"><span class="label">Bank / Lender</span><span class="value">{loan.bank_name ?? '—'}</span></div>
					<div class="info-row">
						<span class="label">Status</span>
						<span class="badge badge-{loan.bank_approval_status}">{loan.bank_approval_status}</span>
					</div>
				</div>

				{#if loan.bank_approval_status === 'pending'}
					<div class="action-row">
						<button class="btn-approve" onclick={() => handleStatus('approved')} disabled={actionLoading}>Approve</button>
						<button class="btn-reject" onclick={() => handleStatus('rejected')} disabled={actionLoading}>Reject</button>
					</div>
				{/if}
			</div>
		</div>

		<!-- Insurance Section -->
		<section class="schedule-section">
			<div class="section-header">
				<h2><Shield size={16} /> Insurance</h2>
				<button class="btn-add" onclick={() => goto(`/finance_staff/insurance?create&sale_id=${loan.sale_id}`)}>
					<Plus size={14} /> Add Insurance
				</button>
			</div>
			{#if insuranceRecords.length > 0}
				<div class="insurance-list">
					{#each insuranceRecords as ins}
						<div class="insurance-item">
							<div class="ins-header">
								<Shield size={16} class="ins-icon" />
								<span class="ins-provider">{ins.provider_name as string}</span>
								<span class="status-badge badge-{ins.status as string}">{ins.status as string}</span>
							</div>
							<div class="ins-details">
								<span class="ins-detail"><strong>Policy:</strong> {ins.policy_number as string}</span>
								<span class="ins-detail"><strong>Coverage:</strong> {(ins.coverage_type as string) ?? '—'}</span>
								<span class="ins-detail"><strong>Valid:</strong> {String(ins.start_date ?? '').slice(0, 4)} — {String(ins.end_date ?? '').slice(0, 4)}</span>
							</div>
							<div class="ins-actions">
								<button class="btn-view" onclick={() => goto(`/finance_staff/insurance/${ins.insurance_id}`)}>View</button>
							</div>
						</div>
					{/each}
				</div>
			{:else}
				<p class="empty">No insurance linked to this sale.</p>
			{/if}
		</section>

		<!-- Amortization Schedule -->
		<section class="schedule-section">
			<h2>Amortization Schedule</h2>
			{#if schedule.length > 0}
				<DataTable columns={['#', 'Due Date', 'Principal', 'Interest', 'Total Due', 'Running Balance', 'Status', 'Review', 'Proof', 'Actions']}>
					{#each schedule as entry (entry.schedule_id)}
						<tr>
							<td class="cell-mono">{entry.month_number}</td>
							<td>{entry.due_date ? String(entry.due_date).slice(0, 10) : '—'}</td>
							<td class="cell-mono">{fmt(entry.principal)}</td>
							<td class="cell-mono">{fmt(entry.interest)}</td>
							<td class="cell-mono">{fmt(entry.total_due)}</td>
							<td class="cell-mono">{fmt(entry.running_balance)}</td>
							<td>
								<span class="badge badge-{entry.status}">{entry.status}</span>
							</td>
							<td>
								{#if entry.review_status === 'pending_verification'}
									<span class="review-badge rb-pending">Pending Review</span>
								{:else if entry.review_status === 'verified'}
									<span class="review-badge rb-verified">Verified</span>
								{:else if entry.review_status === 'rejected'}
									<span class="review-badge rb-rejected">Rejected</span>
								{:else}
									<span class="muted">—</span>
								{/if}
							</td>
							<td>
								{#if entry.proof_of_payment}
									<button onclick={() => previewUrl = entry.proof_of_payment!} class="proof-btn">View</button>
								{:else}
									<span class="muted">—</span>
								{/if}
							</td>
							<td>
								{#if entry.review_status === 'pending_verification'}
									<div class="review-actions">
										<button class="btn-approve-sm" onclick={() => openReview(entry, 'verified')} title="Approve"><Check size={12} /></button>
										<button class="btn-reject-sm" onclick={() => openReview(entry, 'rejected')} title="Reject"><Ban size={12} /></button>
									</div>
								{:else if entry.status === 'unpaid' && !entry.review_status}
									<button class="btn-paid" onclick={() => handleMarkPaid(entry.schedule_id)}>Mark Paid</button>
								{/if}
							</td>
						</tr>
					{/each}
				</DataTable>
			{:else}
				<p class="empty">No schedule entries yet.</p>
			{/if}
		</section>

		<!-- Review Modal -->
		{#if showReviewModal && reviewPaymentId}
			<div class="modal-overlay" onclick={() => showReviewModal = false}>
				<div class="modal" onclick={(e) => e.stopPropagation()}>
					<div class="modal-header">
						<h3>{reviewAction === 'verified' ? 'Approve' : 'Reject'} Payment</h3>
						<button class="close-btn" onclick={() => showReviewModal = false}><X size={16} /></button>
					</div>
					<div class="modal-body">
						<p style="margin:0 0 8px; font-size:13px;">Payment for schedule #{reviewScheduleId}</p>
						<div class="form-group">
							<label>Note {reviewAction === 'rejected' ? '(required)' : '(optional)'}</label>
							<textarea class="review-note" bind:value={reviewNote} placeholder={reviewAction === 'rejected' ? 'Reason for rejection…' : 'Optional note…'}></textarea>
						</div>
					</div>
					<div class="modal-footer">
						<button class="btn-cancel" onclick={() => showReviewModal = false} disabled={reviewing}>Cancel</button>
						<button
							class={reviewAction === 'verified' ? 'btn-approve-sm' : 'btn-reject-sm'}
							onclick={handleReviewSubmit}
							disabled={reviewing}
							style="padding:6px 14px; font-size:12px; font-weight:600; border:none; border-radius:6px; cursor:pointer; {reviewAction === 'verified' ? 'background:#16a34a; color:#fff;' : 'background:#dc2626; color:#fff;'}"
						>
							{reviewing ? 'Processing…' : reviewAction === 'verified' ? 'Approve' : 'Reject'}
						</button>
					</div>
				</div>
			</div>
		{/if}
	{/if}
</div>

<!-- Image Preview Modal -->
{#if previewUrl}
	<div class="modal-overlay" onclick={() => previewUrl = null}>
		<div class="preview-modal" onclick={(e) => e.stopPropagation()}>
			<button class="preview-close" onclick={() => previewUrl = null}><X size={20} /></button>
			<img src={resolvePhotoUrl(previewUrl)} alt="Payment screenshot" class="preview-img" />
		</div>
	</div>
{/if}

<style>
	.page { font-family: var(--font-sans); padding: 2rem 1.5rem; max-width: 1200px; margin: 0 auto; }

	.back-link { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: var(--primary-light); text-decoration: none; margin-bottom: 0.75rem; }
	.back-link:hover { text-decoration: underline; }

	h1 { font-size: 20px; font-weight: 700; color: var(--text-primary); margin: 0 0 1.25rem; }

	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.error-msg { color: var(--danger); font-size: 13px; padding: 1rem; background: var(--danger-bg); border-radius: var(--radius-md); margin-bottom: 1rem; }

	.cards-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; }

	.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.25rem; }
	.card h3 { margin: 0 0 0.75rem; font-size: 0.85rem; font-weight: 600; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.03em; }

	.info-grid { display: flex; flex-direction: column; gap: 0.35rem; }
	.info-row { display: flex; justify-content: space-between; align-items: center; padding: 0.35rem 0; border-bottom: 1px solid var(--border-lighter); }
	.info-row:last-child { border-bottom: none; }
	.label { color: var(--text-light); font-size: 0.8rem; }
	.value { font-weight: 600; font-size: 0.85rem; color: var(--text-primary); text-align: right; }
	.mono { font-family: var(--font-mono); }
	.highlight { color: #059669; font-size: 0.95rem; }

	.badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
	.badge-pending { background: var(--warning-bg-light); color: var(--warning); }
	.badge-approved { background: #ecfdf5; color: #059669; }
	.badge-rejected { background: var(--red-bg); color: var(--red); }
	.badge-unpaid { background: var(--warning-bg-light); color: var(--warning); }
	.badge-paid { background: #ecfdf5; color: #059669; }
	.badge-overdue { background: var(--red-bg); color: var(--red); }

	.action-row { display: flex; gap: 0.5rem; margin-top: 1rem; }
	.btn-approve, .btn-reject { flex: 1; padding: 0.5rem; border: none; border-radius: var(--radius-sm); font-family: var(--font-sans); font-size: 12px; font-weight: 600; cursor: pointer; transition: opacity .15s; }
	.btn-approve { background: var(--success); color: var(--text-white); }
	.btn-approve:hover:not(:disabled) { opacity: 0.85; }
	.btn-reject { background: var(--danger-hover); color: var(--text-white); }
	.btn-reject:hover:not(:disabled) { opacity: 0.85; }
	.btn-approve:disabled, .btn-reject:disabled { opacity: 0.5; cursor: not-allowed; }

	.schedule-section { margin-top: 0.5rem; }
	.schedule-section h2 { font-size: 16px; font-weight: 700; color: var(--text-primary); margin: 0 0 0.75rem; display:flex; align-items:center; gap:6px; }

	.section-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
	.section-header h2 { margin:0; }

	.btn-add { display:inline-flex; align-items:center; gap:4px; padding:4px 10px; border:1px solid var(--primary); border-radius:var(--radius-sm); background:var(--bg-card); color:var(--primary); font-family:var(--font-sans); font-size:11px; font-weight:600; cursor:pointer; }
	.btn-add:hover { background:var(--primary-bg); }

	.insurance-list { display:flex; flex-direction:column; gap:8px; }
	.insurance-item { display:flex; align-items:center; gap:16px; padding:12px 16px; background:var(--bg-hover); border:1px solid var(--border); border-radius:var(--radius-md); }
	.ins-header { display:flex; align-items:center; gap:8px; min-width:200px; }
	.ins-icon { color:var(--primary); flex-shrink:0; }
	.ins-provider { font-weight:600; font-size:13px; color:var(--text-dark); }
	.ins-details { flex:1; display:flex; gap:16px; font-size:12px; color:var(--text-light); }
	.ins-detail { white-space:nowrap; }
	.ins-actions { flex-shrink:0; }

	.status-badge { display:inline-block; padding:2px 8px; border-radius:20px; font-size:10px; font-weight:600; }
	.status-badge.badge-active { background:#d1fae5; color:#065f46; }
	.status-badge.badge-expired { background:#fef3c7; color:#92400e; }
	.status-badge.badge-cancelled { background:#fef2f2; color:#dc2626; }

	.btn-view { background:var(--primary-bg); color:var(--primary); border:1px solid var(--primary); border-radius:var(--radius-sm); padding:4px 10px; font-size:11px; font-weight:600; cursor:pointer; }
	.btn-view:hover { background:var(--primary); color:var(--text-white); }

	.cell-mono { font-family: var(--font-mono); font-size: 11px; color: var(--text-primary); }
	.proof-link { color: var(--primary); font-weight: 600; text-decoration: none; font-size: 11px; }
	.proof-link:hover { text-decoration: underline; }
	.proof-btn { background:var(--primary-bg); color:var(--primary); border:1px solid var(--primary); border-radius:var(--radius-sm); padding:2px 8px; font-size:11px; font-weight:600; cursor:pointer; }
	.proof-btn:hover { background:var(--primary); color:var(--text-white); }
	.muted { color: var(--text-muted); font-size: 11px; }

	.preview-modal { position:relative; max-width:90vw; max-height:90vh; display:flex; align-items:center; justify-content:center; }
	.preview-img { max-width:100%; max-height:90vh; border-radius:8px; box-shadow:0 20px 60px rgba(0,0,0,0.3); }
	.preview-close { position:absolute; top:-40px; right:0; background:rgba(0,0,0,0.5); color:#fff; border:none; border-radius:50%; width:32px; height:32px; display:flex; align-items:center; justify-content:center; cursor:pointer; }
	.preview-close:hover { background:rgba(0,0,0,0.7); }
	.btn-paid { padding: 3px 10px; border: none; border-radius: var(--radius-sm); background: var(--success); color: var(--text-white); font-family: var(--font-sans); font-size: 10px; font-weight: 600; cursor: pointer; transition: opacity .15s; }
	.btn-paid:hover { opacity: 0.85; }

	.empty { color: var(--text-muted); font-style: italic; font-size: 13px; }

	.review-badge { display:inline-block; padding:2px 8px; border-radius:20px; font-size:10px; font-weight:600; }
	.rb-pending { background:#fef3c7; color:#92400e; }
	.rb-verified { background:#d1fae5; color:#065f46; }
	.rb-rejected { background:#fef2f2; color:#dc2626; }

	.review-actions { display:flex; gap:4px; }
	.btn-approve-sm, .btn-reject-sm { display:inline-flex; align-items:center; justify-content:center; width:24px; height:24px; border:none; border-radius:4px; cursor:pointer; }
	.btn-approve-sm { background:#d1fae5; color:#065f46; }
	.btn-approve-sm:hover { background:#a7f3d0; }
	.btn-reject-sm { background:#fef2f2; color:#dc2626; }
	.btn-reject-sm:hover { background:#fecaca; }

	.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:1000; padding:1rem; }
	.modal { background:var(--bg-card); border-radius:12px; width:100%; max-width:420px; box-shadow:0 20px 60px rgba(0,0,0,0.15); overflow:hidden; }
	.modal-header { display:flex; align-items:center; justify-content:space-between; padding:1rem 1.25rem; border-bottom:1px solid var(--border); }
	.modal-header h3 { font-size:15px; font-weight:700; margin:0; }
	.close-btn { display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border:none; border-radius:6px; background:transparent; color:var(--text-muted); cursor:pointer; }
	.close-btn:hover { background:var(--bg-hover); }
	.modal-body { padding:1.25rem; }
	.modal-footer { display:flex; justify-content:flex-end; gap:8px; padding:1rem 1.25rem; border-top:1px solid var(--border); }
	.form-group { display:flex; flex-direction:column; gap:4px; }
	.form-group label { font-size:11px; font-weight:600; color:var(--text-light); }
	.review-note { width:100%; min-height:60px; padding:8px 10px; border:1px solid var(--border); border-radius:8px; font-family:var(--font-sans); font-size:12px; resize:vertical; }
	.review-note:focus { border-color:var(--primary); outline:none; }
	.btn-cancel { height:34px; padding:0 16px; border:1px solid var(--border); border-radius:8px; background:var(--bg-card); font-family:inherit; font-size:12px; color:var(--text-light); cursor:pointer; }
	.btn-cancel:disabled { opacity:0.5; cursor:default; }

	@media (max-width: 768px) {
		.cards-grid { grid-template-columns: 1fr; }
	}
</style>
