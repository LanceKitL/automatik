<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getPayments, recordPayment, deletePayment, adminUploadPaymentProof, getSales, type ListResponse } from '$lib/services/api';
	import { Search, Plus, CreditCard, Banknote, Landmark, Globe, Trash2, ExternalLink, X } from '@lucide/svelte';

	interface PaymentItem {
		payment_id: number;
		sale_id: number;
		amount_paid: number;
		payment_method: string;
		payment_allocation: string | null;
		payment_date: string;
		proof_of_payment: string | null;
		customer_name: string;
		brand: string;
		model: string;
		recorded_by_name: string;
	}

	interface SaleOption {
		sale_id: number;
		label: string;
	}

	let loading = $state(true);
	let payments = $state<PaymentItem[]>([]);

	let searchQuery = $state('');
	let activeFilter = $state('all');
	const filters = ['all', 'cash', 'bank_transfer', 'check', 'online'] as const;

	let showModal = $state(false);
	let saleOptions = $state<SaleOption[]>([]);
	let selectedSaleId = $state<number | null>(null);
	let amount = $state<number>(0);
	let method = $state('cash');
	let reference = $state('');
	let recording = $state(false);

	let deleting = $state<number | null>(null);
	let showDeleteConfirm = $state(false);
	let deleteTargetId = $state<number | null>(null);

	let showProofModal = $state(false);
	let proofImageUrl = $state('');

	// Record payment modal — file upload
	let payFile = $state<File | null>(null);

	const tableColumns = [
		{ key: 'payment_id', label: 'ID' },
		{ key: 'customer', label: 'Customer' },
		{ key: 'vehicle', label: 'Vehicle' },
		{ key: 'amount', label: 'Amount' },
		{ key: 'method', label: 'Method' },
		{ key: 'allocation', label: 'Allocation' },
		{ key: 'date', label: 'Date' },
		{ key: 'proof', label: 'Proof' },
		{ key: 'actions', label: 'Actions' }
	];

	let filteredPayments = $derived.by(() => {
		let list = payments;
		if (activeFilter !== 'all') {
			list = list.filter((p) => p.payment_method === activeFilter);
		}
		if (searchQuery.trim()) {
			const q = searchQuery.toLowerCase();
			list = list.filter(
				(p) =>
					(p.customer_name ?? '').toLowerCase().includes(q) ||
					String(p.amount_paid).includes(q) ||
					(p.payment_method ?? '').toLowerCase().includes(q)
			);
		}
		return list;
	});

	let stats = $derived({
		total: payments.reduce((s, p) => s + Number(p.amount_paid), 0),
		cash: payments.filter((p) => p.payment_method === 'cash').length,
		bank_transfer: payments.filter((p) => p.payment_method === 'bank_transfer').length,
		online: payments.filter((p) => p.payment_method === 'online').length
	});

	function formatDate(dateStr: string): string {
		if (!dateStr) return '—';
		return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	function methodLabel(m: string): string {
		const map: Record<string, string> = { cash: 'Cash', bank_transfer: 'Bank Transfer', check: 'Check', online: 'Online' };
		return map[m] ?? m;
	}

	function formatCurrency(val: number): string {
		return '$' + Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	}

	async function loadPayments() {
		loading = true;
		try {
			const res = await getPayments();
			payments = (res.data ?? []) as PaymentItem[];
		} catch (e) {
			toast.error((e as Error).message || 'Failed to load payments.');
		} finally {
			loading = false;
		}
	}

	async function openRecordModal() {
		showModal = true;
		selectedSaleId = null;
		amount = 0;
		method = 'cash';
		reference = '';
		payFile = null;
		try {
			const res = await getSales();
			const data = (res as { data: unknown[] }).data ?? [];
			saleOptions = data.map((s: Record<string, unknown>) => {
				const sale = (s as { sales: { sale_id: number }; customer: { username: string }; vehicle: { brand: string; model: string } });
				return {
					sale_id: sale.sales.sale_id,
					label: `#${sale.sales.sale_id} — ${sale.customer.username} (${sale.vehicle.brand} ${sale.vehicle.model})`
				};
			});
		} catch {
			saleOptions = [];
		}
	}

	async function handleRecordPayment() {
		if (!selectedSaleId || amount <= 0) return;
		recording = true;
		try {
			const payload: Record<string, unknown> = {
				amount_paid: amount,
				payment_method: method,
				payment_allocation: 'full_cash'
			};
			if (reference) payload.reference = reference;
			const res = await recordPayment(selectedSaleId, payload);
			// Upload proof if file selected
			if (payFile) {
				try {
					await adminUploadPaymentProof(res.payment_id, payFile);
				} catch {
					toast.error('Payment recorded but proof upload failed.');
				}
			}
			toast.success('Payment recorded.');
			showModal = false;
			await loadPayments();
		} catch (e) {
			toast.error((e as Error).message || 'Failed to record payment.');
		} finally {
			recording = false;
		}
	}

	function promptDelete(id: number) {
		deleteTargetId = id;
		showDeleteConfirm = true;
	}

	async function confirmDelete() {
		if (deleteTargetId === null) return;
		deleting = deleteTargetId;
		try {
			await deletePayment(deleteTargetId);
			toast.success('Payment deleted.');
			showDeleteConfirm = false;
			deleteTargetId = null;
			await loadPayments();
		} catch (e) {
			toast.error((e as Error).message || 'Failed to delete payment.');
		} finally {
			deleting = null;
		}
	}

	function filterLabel(f: string): string {
		return f === 'all' ? 'All' : methodLabel(f);
	}

	onMount(loadPayments);
</script>

<div class="page">
	<!-- Top bar -->
	<div class="top-bar">
		<div class="title-row">
			<div>
				<h1>Payments</h1>
				<p class="title-subtitle">Record and manage customer payments</p>
			</div>
		</div>
		<div class="toolbar">
			<div class="search-wrap">
				<Search class="search-icon" size={14} />
				<input
					type="text"
					class="search-input"
					placeholder="Search by customer, vehicle, amount…"
					bind:value={searchQuery}
				/>
			</div>
			<button class="create-btn" onclick={openRecordModal}>
				<Plus size={14} />Record Payment
			</button>
		</div>
	</div>

	<!-- Mini stats -->
	<div class="stats-row">
		<div class="mini-stat s-total">
			<CreditCard size={18} />
			<div>
				<span class="mini-val">{formatCurrency(stats.total)}</span>
				<span class="mini-lbl">Total</span>
			</div>
		</div>
		<div class="mini-stat s-cash">
			<Banknote size={18} />
			<div>
				<span class="mini-val">{stats.cash}</span>
				<span class="mini-lbl">Cash</span>
			</div>
		</div>
		<div class="mini-stat s-transfer">
			<Landmark size={18} />
			<div>
				<span class="mini-val">{stats.bank_transfer}</span>
				<span class="mini-lbl">Bank Transfer</span>
			</div>
		</div>
		<div class="mini-stat s-online">
			<Globe size={18} />
			<div>
				<span class="mini-val">{stats.online}</span>
				<span class="mini-lbl">Online</span>
			</div>
		</div>
	</div>

	<!-- Filter pills -->
	<div class="filter-row">
		{#each filters as f}
			<button
				class="filter-btn"
				class:active={activeFilter === f}
				onclick={() => (activeFilter = f)}
			>
				{filterLabel(f)}
			</button>
		{/each}
	</div>

	<!-- Loading / Empty / Table -->
	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading payments…</span>
		</div>
	{:else if filteredPayments.length === 0}
		<div class="empty-state">No payments found.</div>
	{:else}
		<DataTable columns={tableColumns}>
			{#each filteredPayments as p (p.payment_id)}
				<tr>
					<td><span class="cell-id">#{p.payment_id}</span></td>
					<td class="cell-name">{p.customer_name ?? '—'}</td>
					<td class="cell-vehicle">{p.brand} {p.model}</td>
					<td><span class="cell-amount">{formatCurrency(p.amount_paid)}</span></td>
					<td><span class="badge badge-{p.payment_method}">{methodLabel(p.payment_method)}</span></td>
					<td class="cell-allocation">{p.payment_allocation ?? '—'}</td>
					<td class="cell-date">{formatDate(p.payment_date)}</td>
					<td>
						{#if p.proof_of_payment}
							<button class="proof-link" onclick={() => { proofImageUrl = p.proof_of_payment; showProofModal = true; }}>
								<ExternalLink size={12} /> View
							</button>
						{:else}
							<span class="no-proof">—</span>
						{/if}
					</td>
					<td>
						<button
							class="delete-btn"
							disabled={deleting === p.payment_id}
							onclick={() => promptDelete(p.payment_id)}
						>
							<Trash2 size={13} />
						</button>
					</td>
				</tr>
			{/each}
		</DataTable>
	{/if}
</div>

<!-- Proof of Payment Image Modal -->
{#if showProofModal}
	<div class="modal-overlay" onclick={() => showProofModal = false}>
		<div class="proof-modal" onclick={(e) => e.stopPropagation()}>
			<div class="proof-modal-header">
				<h2>Proof of Payment</h2>
				<button class="modal-close" onclick={() => showProofModal = false}>
					<X size={16} />
				</button>
			</div>
			<div class="proof-modal-body">
				{#if proofImageUrl?.match(/\.(png|jpe?g|gif|webp|bmp)$/i)}
					<img src={proofImageUrl} alt="Proof of payment" class="proof-img" />
				{:else}
					<a href={proofImageUrl} target="_blank" rel="noopener noreferrer" class="proof-fallback">
						Open file in new tab
					</a>
				{/if}
			</div>
		</div>
	</div>
{/if}

<!-- Record Payment Modal -->
{#if showModal}
	<div class="modal-overlay" onclick={() => (showModal = false)}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Record Payment</h2>
				<button class="modal-close" onclick={() => (showModal = false)}>
					<X size={16} />
				</button>
			</div>
			<div class="modal-body">
				<label class="field">
					<span class="field-label">Sale</span>
					<select class="field-input" bind:value={selectedSaleId}>
						<option value={null} disabled>Select a sale…</option>
						{#each saleOptions as opt}
							<option value={opt.sale_id}>{opt.label}</option>
						{/each}
					</select>
				</label>
				<label class="field">
					<span class="field-label">Amount</span>
					<input type="number" class="field-input" bind:value={amount} min="0" step="0.01" placeholder="0.00" />
				</label>
				<label class="field">
					<span class="field-label">Method</span>
					<select class="field-input" bind:value={method}>
						<option value="cash">Cash</option>
						<option value="bank_transfer">Bank Transfer</option>
						<option value="check">Check</option>
						<option value="online">Online</option>
					</select>
				</label>
			<label class="field">
				<span class="field-label">Reference <span class="optional">(optional)</span></span>
					<input type="text" class="field-input" bind:value={reference} placeholder="Reference / notes…" />
				</label>
				<label class="field">
					<span class="field-label">Proof <span class="optional">(optional)</span></span>
					<input type="file" class="field-input" accept="image/*,.pdf" onchange={(e) => { const t = e.target as HTMLInputElement; payFile = t.files?.[0] ?? null; }} />
				</label>
			</div>
			<div class="modal-footer">
				<button class="modal-cancel" onclick={() => (showModal = false)}>Cancel</button>
				<button
					class="modal-submit"
					disabled={!selectedSaleId || amount <= 0 || recording}
					onclick={handleRecordPayment}
				>
					{recording ? 'Recording…' : 'Record Payment'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Delete confirmation modal -->
{#if showDeleteConfirm}
	<div class="modal-overlay" onclick={() => { showDeleteConfirm = false; deleteTargetId = null; }} role="presentation">
		<div class="modal modal-sm" onclick={(e) => e.stopPropagation()} role="alertdialog">
			<div class="modal-header">
				<h2>Delete Payment</h2>
				<button class="modal-close" onclick={() => { showDeleteConfirm = false; deleteTargetId = null; }}>
					<X size={16} />
				</button>
			</div>
			<div class="modal-body">
				<p>Are you sure you want to delete payment <strong>#{deleteTargetId}</strong>? This action cannot be undone.</p>
			</div>
			<div class="modal-footer">
				<button class="modal-cancel" onclick={() => { showDeleteConfirm = false; deleteTargetId = null; }}>Cancel</button>
				<button class="modal-submit modal-submit-danger" onclick={confirmDelete} disabled={deleting === deleteTargetId}>
					{deleting === deleteTargetId ? 'Deleting…' : 'Delete'}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

	.page { font-family: 'Syne', sans-serif; padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

	/* Top bar */
	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; align-items: center; gap: 10px; }
	.title-subtitle { font-size: 13px; color: #9ca3af; margin: 2px 0 0; font-weight: 400; }
	h1 { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; margin: 0; }
	.toolbar { display: flex; align-items: center; gap: 10px; }
	.search-wrap { position: relative; }
	.search-wrap :global(.search-icon) { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; pointer-events: none; }
	.search-input { height: 34px; padding: 0 12px 0 32px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; color: #1a1a2e; background: #f9fafb; outline: none; width: 220px; }
	.search-input:focus { border-color: #7c9df7; background: #fff; }
	.create-btn { display: flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px; background: #1a1a2e; color: #e8c97e; border: none; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; cursor: pointer; letter-spacing: 0.2px; transition: opacity .15s; white-space: nowrap; }
	.create-btn:hover { opacity: 0.85; }

	/* Mini stats */
	.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 1.25rem; }
	.mini-stat { background: #f8f7f4; border-radius: 10px; padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
	.s-total :global(svg) { color: #1a1a2e; flex-shrink: 0; }
	.s-cash :global(svg) { color: #059669; flex-shrink: 0; }
	.s-transfer :global(svg) { color: #4f46e5; flex-shrink: 0; }
	.s-online :global(svg) { color: #2563eb; flex-shrink: 0; }
	.mini-stat div { display: flex; flex-direction: column; }
	.mini-val { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; line-height: 1; }
	.mini-lbl { font-size: 10px; font-weight: 500; color: #9ca3af; letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

	/* Filter pills */
	.filter-row { display: flex; gap: 6px; margin-bottom: 1rem; flex-wrap: wrap; }
	.filter-btn { height: 28px; padding: 0 12px; border: 0.5px solid #e5e7eb; border-radius: 20px; background: #f9fafb; font-family: 'Syne', sans-serif; font-size: 11px; color: #6b7280; cursor: pointer; transition: .15s; }
	.filter-btn.active { background: #1a1a2e; color: #e8c97e; border-color: #1a1a2e; }

	/* Loading & Error */
	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: #9ca3af; font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid #e5e7eb; border-top-color: #1a1a2e; border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.empty-state { text-align: center; padding: 2.5rem; color: #9ca3af; font-size: 13px; }

	/* Table cells */
	.cell-id { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #7c9df7; }
	.cell-name { font-size: 13px; font-weight: 600; color: #1a1a2e; }
	.cell-vehicle { font-size: 12px; color: #374151; }
	.cell-amount { font-family: 'DM Mono', monospace; font-size: 12px; color: #059669; font-weight: 500; }
	.cell-allocation { font-size: 12px; color: #6b7280; }
	.cell-date { font-size: 12px; color: #6b7280; }

	/* Method badges */
	.badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
	.badge-cash { background: #ecfdf5; color: #059669; }
	.badge-bank_transfer { background: #eef2ff; color: #4f46e5; }
	.badge-check { background: #fef3c7; color: #b45309; }
	.badge-online { background: #dbeafe; color: #2563eb; }

	/* Proof link */
	.proof-link { display: inline-flex; align-items: center; gap: 4px; font-size: 11px; font-weight: 600; color: #7c9df7; background: none; border: none; padding: 2px 8px; border-radius: 4px; cursor: pointer; transition: background .15s; font-family: inherit; }
	.proof-link:hover { background: #eef2ff; }
	.no-proof { color: #d1d5db; font-size: 12px; }

	/* Delete button */
	.delete-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border: none; border-radius: 6px; background: transparent; color: #9ca3af; cursor: pointer; transition: .15s; }
	.delete-btn:hover { background: #fcebeb; color: #dc2626; }
	.delete-btn:disabled { opacity: 0.4; cursor: not-allowed; }

	/* Modal */
	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
	.modal { background: #fff; border-radius: 12px; width: 480px; max-width: 94vw; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
	.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 1px solid #e5e7eb; }
	.modal-header h2 { font-size: 16px; font-weight: 700; color: #1a1a2e; margin: 0; }
	.modal-close { display: flex; align-items: center; justify-content: center; width: 28px; height: 28px; border: none; border-radius: 6px; background: transparent; color: #9ca3af; cursor: pointer; transition: .15s; }
	.modal-close:hover { background: #f3f4f6; color: #1a1a2e; }
	.modal-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 14px; }
	.field { display: flex; flex-direction: column; gap: 4px; }
	.field-label { font-size: 11px; font-weight: 600; color: #374151; letter-spacing: 0.3px; text-transform: uppercase; }
	.optional { font-weight: 400; text-transform: none; color: #9ca3af; font-size: 10px; }
	.field-input { height: 36px; padding: 0 10px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 13px; color: #1a1a2e; background: #f9fafb; outline: none; }
	.field-input:focus { border-color: #7c9df7; background: #fff; }
	select.field-input { cursor: pointer; appearance: auto; }
	.modal-footer { display: flex; align-items: center; justify-content: flex-end; gap: 8px; padding: 1rem 1.25rem; border-top: 1px solid #e5e7eb; }
	.modal-cancel { height: 34px; padding: 0 14px; border: 0.5px solid #e5e7eb; border-radius: 8px; background: #fff; font-family: 'Syne', sans-serif; font-size: 12px; color: #6b7280; cursor: pointer; transition: .15s; }
	.modal-cancel:hover { background: #f9fafb; }
	.modal-submit { height: 34px; padding: 0 14px; background: #1a1a2e; color: #e8c97e; border: none; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; cursor: pointer; transition: opacity .15s; }
	.modal-submit:hover { opacity: 0.85; }
	.modal-submit:disabled { opacity: 0.4; cursor: not-allowed; }
	.modal-submit-danger { background: #dc2626; color: #fff; }
	.modal-submit-danger:hover { opacity: 0.85; }
	.modal-sm { width: 400px; }
	.modal-body p { margin: 0; font-size: 14px; color: #1a1a2e; line-height: 1.5; }

	/* Proof image modal */
	.proof-modal { background: #fff; border-radius: 12px; width: 600px; max-width: 94vw; max-height: 90vh; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.15); display: flex; flex-direction: column; }
	.proof-modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 1px solid #e5e7eb; }
	.proof-modal-header h2 { font-size: 16px; font-weight: 700; color: #1a1a2e; margin: 0; }
	.proof-modal-body { padding: 1.25rem; display: flex; align-items: center; justify-content: center; overflow: auto; }
	.proof-img { max-width: 100%; max-height: 65vh; object-fit: contain; border-radius: 8px; }
	.proof-fallback { font-size: 14px; color: #7c9df7; text-decoration: underline; padding: 2rem; }

	@media (max-width: 640px) {
		.stats-row { grid-template-columns: 1fr 1fr; }
		.top-bar { flex-direction: column; align-items: flex-start; }
	}
</style>
