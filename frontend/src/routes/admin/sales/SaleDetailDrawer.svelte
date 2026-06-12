<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getSale,
		updateSaleStatus,
		updateContract,
		addInsurance,
		updateInsurance,
		recordPayment,
		type SaleItem,
		type SingleUserResponse
	} from '$lib/services/api';

	let {
		sale,
		onclose,
		onupdated
	}: {
		sale: SaleItem;
		onclose: () => void;
		onupdated: () => void;
	} = $props();

	// ── Full sale detail from API ─────────────────────────────────────────────
	let detail = $state<SingleUserResponse['data'] | null>(null);
	let loading = $state(true);
	let detailError = $state('');

	// ── Contract update ───────────────────────────────────────────────────────
	let contractUrl = $state('');
	let contractStatus = $state('');
	let contractUpdating = $state(false);

	// ── Insurance add ────────────────────────────────────────────────────────
	let insuranceProvider = $state('');
	let insurancePolicy = $state('');
	let insuranceStart = $state('');
	let insuranceEnd = $state('');
	let insuranceAdding = $state(false);

	// ── Record Payment ───────────────────────────────────────────────────────
	let payAmount = $state<number | ''>('');
	let payMethod = $state('cash');
	let payAllocation = $state('full_cash');
	let payReference = $state('');
	let payRecording = $state(false);

	async function handleRecordPayment() {
		if (!detail || payAmount === '' || !payMethod) return;
		actionError = '';
		payRecording = true;
		try {
			await recordPayment(sale.sales.sale_id, {
				amount_paid: Number(payAmount),
				payment_method: payMethod,
				payment_allocation: payAllocation,
				reference: payReference || null
			});
			payAmount = '';
			payMethod = 'cash';
			payAllocation = 'full_cash';
			payReference = '';
			onupdated();
		} catch (e: unknown) {
			actionError = e instanceof Error ? e.message : 'Failed to record payment.';
		} finally {
			payRecording = false;
		}
	}

	// ── Status update ────────────────────────────────────────────────────────
	let statusUpdating = $state(false);

	// ── Generic action state ──────────────────────────────────────────────────
	let actionError = $state('');

	onMount(async () => {
		try {
			const res = await getSale(sale.sales.sale_id);
			detail = res.data;
			if (detail?.contract) {
				contractUrl = detail.contract.contract_url || '';
				contractStatus = detail.contract.status || 'draft';
			}
		} catch (e: unknown) {
			detailError = e instanceof Error ? e.message : 'Failed to load sale details.';
		} finally {
			loading = false;
		}
	});

	async function handleUpdateContract() {
		if (!detail) return;
		actionError = '';
		contractUpdating = true;
		try {
			const payload: Record<string, unknown> = {};
			if (contractUrl) payload.contract_url = contractUrl;
			if (contractStatus) payload.status = contractStatus;
			await updateContract(sale.sales.sale_id, payload);
			onupdated();
		} catch (e: unknown) {
			actionError = e instanceof Error ? e.message : 'Failed to update contract.';
		} finally {
			contractUpdating = false;
		}
	}

	async function handleAddInsurance() {
		actionError = '';
		if (!insuranceProvider || !insurancePolicy || !insuranceStart || !insuranceEnd) {
			actionError = 'All insurance fields are required.';
			return;
		}
		insuranceAdding = true;
		try {
			await addInsurance(sale.sales.sale_id, {
				provider_name: insuranceProvider,
				policy_number: insurancePolicy,
				start_date: insuranceStart,
				end_date: insuranceEnd
			});
			insuranceProvider = '';
			insurancePolicy = '';
			insuranceStart = '';
			insuranceEnd = '';
			onupdated();
		} catch (e: unknown) {
			actionError = e instanceof Error ? e.message : 'Failed to add insurance.';
		} finally {
			insuranceAdding = false;
		}
	}

	async function handleUpdateStatus(newStatus: string) {
		actionError = '';
		statusUpdating = true;
		try {
			await updateSaleStatus(sale.sales.sale_id, newStatus);
			onupdated();
		} catch (e: unknown) {
			actionError = e instanceof Error ? e.message : 'Failed to update status.';
		} finally {
			statusUpdating = false;
		}
	}

	function handleOverlayClick(e: MouseEvent) {
		if (e.target === e.currentTarget) onclose();
	}

	function formatDate(d: string | null | undefined): string {
		if (!d) return '—';
		return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}
</script>

<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
<div class="overlay" onclick={handleOverlayClick} role="presentation">
	<div class="drawer" onclick={(e) => e.stopPropagation()} role="dialog">
		<div class="drawer-header">
			<h2>Sale #{sale.sales.sale_id}</h2>
			<button class="close-btn" onclick={onclose}>×</button>
		</div>

		<div class="drawer-body">
			{#if loading}
			<div class="loading-state"><div class="spinner"></div><span>Loading details…</span></div>
		{:else if detailError}
				<div class="form-error">{detailError}</div>
			{:else if detail}
				{#if actionError}
					<div class="form-error">{actionError}</div>
				{/if}

				<!-- Sale Info -->
				<section class="section">
					<h3>Sale Details</h3>
					<div class="info-grid">
						<div class="info-row"><span class="label">Sale Date</span><span class="value">{formatDate(detail.sale?.sale_date)}</span></div>
						<div class="info-row"><span class="label">Status</span><span class="badge badge-{detail.sale?.status}">{detail.sale?.status}</span></div>
						<div class="info-row"><span class="label">Total Amount</span><span class="value price">${Number(detail.sale?.total_amount).toLocaleString()}</span></div>
						<div class="info-row"><span class="label">Inquiry ID</span><span class="value">{sale.sales.inquiry_id ?? '—'}</span></div>
					</div>
				</section>

				<!-- Customer -->
				<section class="section">
					<h3>Customer</h3>
					<div class="info-grid">
						<div class="info-row"><span class="label">Name</span><span class="value">{detail.customer?.name}</span></div>
						<div class="info-row"><span class="label">Email</span><span class="value">{detail.customer?.email}</span></div>
					</div>
				</section>

				<!-- Agent -->
				<section class="section">
					<h3>Agent</h3>
					<p class="value">{detail.agent?.name ?? '—'}</p>
				</section>

				<!-- Vehicle -->
				<section class="section">
					<h3>Vehicle</h3>
					<div class="info-grid">
						<div class="info-row"><span class="label">Brand</span><span class="value">{detail.vehicle?.brand}</span></div>
						<div class="info-row"><span class="label">Model</span><span class="value">{detail.vehicle?.model}</span></div>
						<div class="info-row"><span class="label">Year</span><span class="value">{detail.vehicle?.year}</span></div>
						<div class="info-row"><span class="label">Body Type</span><span class="value">{detail.vehicle?.body_type}</span></div>
						<div class="info-row"><span class="label">List Price</span><span class="value">${Number(detail.vehicle?.price).toLocaleString()}</span></div>
					</div>
				</section>

				<!-- Contract -->
				<section class="section">
					<h3>Contract</h3>
					{#if detail.contract}
						<div class="info-grid">
							<div class="info-row"><span class="label">Status</span><span class="badge badge-{detail.contract.status}">{detail.contract.status}</span></div>
							<div class="info-row"><span class="label">Contract URL</span><span class="value mono">{detail.contract.contract_url ? detail.contract.contract_url.slice(0, 40) + '…' : '—'}</span></div>
						</div>
						<div class="inline-form">
							<input type="text" placeholder="Contract URL" bind:value={contractUrl} />
							<select bind:value={contractStatus}>
								<option value="draft">Draft</option>
								<option value="pending_signature">Pending Signature</option>
								<option value="signed">Signed</option>
								<option value="cancelled">Cancelled</option>
							</select>
							<button class="btn-sm btn-primary" onclick={handleUpdateContract} disabled={contractUpdating}>
								{contractUpdating ? '…' : 'Update'}
							</button>
						</div>
					{:else}
						<p class="empty-note">No contract yet.</p>
					{/if}
				</section>

				<!-- Insurance -->
				<section class="section">
					<h3>Insurance Records</h3>
					{#if detail.insurance && detail.insurance.length > 0}
						{#each detail.insurance as ins}
							<div class="insurance-card">
								<div class="info-row"><span class="label">Provider</span><span class="value">{ins.provider_name}</span></div>
								<div class="info-row"><span class="label">Policy #</span><span class="value mono">{ins.policy_number}</span></div>
								<div class="info-row"><span class="label">Period</span><span class="value">{formatDate(ins.start_date)} – {formatDate(ins.end_date)}</span></div>
							</div>
						{/each}
					{:else}
						<p class="empty-note">No insurance records.</p>
					{/if}
					<div class="inline-form">
						<input type="text" placeholder="Provider" bind:value={insuranceProvider} />
						<input type="text" placeholder="Policy #" bind:value={insurancePolicy} />
						<input type="date" bind:value={insuranceStart} />
						<input type="date" bind:value={insuranceEnd} />
						<button class="btn-sm btn-primary" onclick={handleAddInsurance} disabled={insuranceAdding}>
							{insuranceAdding ? '…' : 'Add Insurance'}
						</button>
					</div>
				</section>

				<!-- Payments -->
				<section class="section">
					<h3>Payments</h3>
					{#if detail.payments && detail.payments.length > 0}
						{#each detail.payments as p}
							<div class="payment-row">
								<span class="mono">${Number(p.amount_paid).toLocaleString()}</span>
								<span class="date">{formatDate(p.payment_date)}</span>
								<span class="method">{p.payment_method}</span>
								<span class="allocation">{p.payment_allocation ?? '—'}</span>
								<span class="recorder">{p.recorded_by_name}</span>
							</div>
						{/each}
					{:else}
						<p class="empty-note">No payments recorded.</p>
					{/if}

					<div class="inline-form">
						<input type="number" step="0.01" min="0" placeholder="Amount" bind:value={payAmount} />
						<select bind:value={payMethod}>
							<option value="cash">Cash</option>
							<option value="bank_transfer">Bank Transfer</option>
							<option value="check">Check</option>
							<option value="online">Online</option>
						</select>
						<select bind:value={payAllocation}>
							<option value="full_cash">Full Cash</option>
							<option value="downpayment">Down Payment</option>
							<option value="amortization">Amortization</option>
							<option value="service_fee">Service Fee</option>
							<option value="maintenance">Maintenance</option>
							<option value="repair">Repair</option>
						</select>
						<input type="text" placeholder="Reference (optional)" bind:value={payReference} />
						<button class="btn-sm btn-primary" onclick={handleRecordPayment} disabled={payRecording}>
							{payRecording ? '…' : 'Record Payment'}
						</button>
					</div>
				</section>

				<!-- Status actions -->
				<div class="actions-section">
					<h3>Change Status</h3>
					<div class="status-actions">
						<button class="btn-sm btn-pending" onclick={() => handleUpdateStatus('pending')} disabled={statusUpdating}>Set Pending</button>
						<button class="btn-sm btn-completed" onclick={() => handleUpdateStatus('completed')} disabled={statusUpdating}>Complete</button>
						<button class="btn-sm btn-cancelled" onclick={() => handleUpdateStatus('cancelled')} disabled={statusUpdating}>Cancel</button>
					</div>
				</div>

			{/if}
		</div>
	</div>
</div>

<style>
	.overlay {
		position: fixed; inset: 0; background: rgba(0,0,0,0.35);
		z-index: 1000; display: flex; justify-content: flex-end;
	}

	.drawer {
		width: 32rem; max-width: 95vw; height: 100vh;
		background: var(--bg-card); box-shadow: -4px 0 24px rgba(0,0,0,0.12);
		display: flex; flex-direction: column; overflow: hidden;
		animation: slideIn 0.2s ease-out;
		font-family: var(--font-sans);
	}
	@keyframes slideIn {
		from { transform: translateX(100%); }
		to { transform: translateX(0); }
	}

	.drawer-header {
		display: flex; align-items: center; justify-content: space-between;
		padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border); flex-shrink: 0;
	}
	.drawer-header h2 { margin: 0; font-size: 1.15rem; color: var(--text-primary); }
	.close-btn {
		background: none; border: none; font-size: 1.5rem; cursor: pointer;
		color: var(--text-muted); padding: 0.25rem; line-height: 1;
	}
	.close-btn:hover { color: var(--text-dark); }

	.drawer-body {
		padding: 1.25rem 1.5rem; overflow-y: auto; flex: 1;
	}

	.form-error {
		background: var(--danger-bg); color: var(--danger); padding: 0.5rem 0.75rem;
		border-radius: var(--radius-sm); font-size: 0.8rem; margin-bottom: 0.75rem;
	}

	/* ── Sections ───────────────────────────── */
	.section { margin-bottom: 1.25rem; }
	.section h3 {
		font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;
		color: var(--text-muted); margin: 0 0 0.5rem;
	}

	.info-grid { display: flex; flex-direction: column; gap: 0.3rem; }
	.info-row { display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid var(--border-lighter); }
	.label { color: var(--text-light); font-size: 0.8rem; }
	.value { font-weight: 600; font-size: 0.85rem; color: var(--text-primary); text-align: right; }
	.mono { font-family: var(--font-mono); font-size: 0.8rem; }
	.price { color: #059669; font-size: 0.95rem; }

	.empty-note { color: var(--text-muted); font-style: italic; font-size: 0.85rem; margin: 0; }

	/* Badges */
	.badge {
		display: inline-block; padding: 3px 12px; border-radius: 12px;
		font-size: 0.7rem; font-weight: 600; text-transform: capitalize;
	}
	.badge-pending { background: var(--warning-bg-light); color: var(--warning); }
	.badge-completed { background: #ecfdf5; color: #059669; }
	.badge-cancelled { background: var(--red-bg); color: var(--red); }
	.badge-draft { background: var(--bg-hover); color: var(--text-light); }
	.badge-pending_signature { background: var(--warning-bg-light); color: var(--warning); }
	.badge-signed { background: #ecfdf5; color: #059669; }

	/* Inline form */
	.inline-form {
		margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.4rem;
	}
	.inline-form input, .inline-form select {
		padding: 0.4rem 0.6rem; border: 1px solid #d1d5db; border-radius: var(--radius-sm);
		font-family: var(--font-sans); font-size: 0.8rem;
		color: var(--text-primary); background: var(--bg-muted);
	}
	.inline-form input:focus, .inline-form select:focus {
		outline: none; border-color: var(--primary-light); background: var(--bg-card);
	}

	.btn-sm {
		padding: 0.35rem 0.75rem; border: none; border-radius: var(--radius-sm);
		font-family: var(--font-sans); font-size: 0.75rem;
		font-weight: 600; cursor: pointer; transition: opacity .15s;
	}
	.btn-sm:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn-primary { background: var(--primary); color: var(--accent); }
	.btn-primary:hover:not(:disabled) { opacity: 0.85; }

	/* Insurance card */
	.insurance-card {
		background: var(--bg-muted); border: 1px solid var(--border);
		border-radius: var(--radius-md); padding: 0.5rem 0.75rem; margin-bottom: 0.5rem;
	}
	.insurance-card .info-row:last-child { border-bottom: none; }

	/* Payment row */
	.payment-row {
		display: flex; gap: 0.75rem; align-items: center;
		padding: 0.35rem 0; border-bottom: 1px solid var(--border-lighter);
		font-size: 0.8rem;
	}
	.payment-row .mono { font-family: var(--font-mono); font-weight: 600; color: #059669; min-width: 80px; }
	.payment-row .date { color: var(--text-light); min-width: 100px; }
	.payment-row .method { color: var(--text-dark); background: var(--bg-hover); padding: 1px 6px; border-radius: var(--radius-sm); }
	.payment-row .recorder { color: var(--text-muted); font-size: 0.75rem; margin-left: auto; }

	/* Status actions */
	.actions-section { margin-top: 1.5rem; border-top: 1px solid var(--border); padding-top: 1rem; }
	.actions-section h3 {
		font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;
		color: var(--text-muted); margin: 0 0 0.5rem;
	}
	.status-actions { display: flex; gap: 0.4rem; }
	.btn-pending { background: var(--warning-bg-light); color: var(--warning); }
	.btn-pending:hover:not(:disabled) { background: #fef3c7; }
	.btn-completed { background: #ecfdf5; color: #059669; }
	.btn-completed:hover:not(:disabled) { background: #d1fae5; }
	.btn-cancelled { background: var(--red-bg); color: var(--red); }
	.btn-cancelled:hover:not(:disabled) { background: #fee2e2; }

	.loading-state {
		display: flex; flex-direction: column; align-items: center;
		gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px;
	}
	.spinner {
		width: 24px; height: 24px; border: 2px solid var(--border);
		border-top-color: var(--primary); border-radius: 50%;
		animation: spin .7s linear infinite;
	}
	@keyframes spin { to { transform: rotate(360deg); } }
</style>
