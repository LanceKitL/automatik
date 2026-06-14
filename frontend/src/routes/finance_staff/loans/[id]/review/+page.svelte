<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { getFinanceLoan, updateFinanceLoanStatus, getFinanceInsurance } from '$lib/services/api';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';

	let loanId = $derived(Number($page.params.id));
	let loan = $state<Record<string, unknown> | null>(null);
	let schedule = $state<Record<string, unknown>[]>([]);
  let loading = $state(true);
  let actionLoading = $state(false);
	let rejectionReason = $state('');
	let insuranceRecords = $state<Record<string, unknown>[]>([]);

	const REJECTION_REASONS = [
		'Insufficient income',
		'Poor credit history',
		'Incomplete documentation',
		'Vehicle value mismatch',
		'Existing delinquent account',
		'Other'
	];

	onMount(async () => {
		try {
			const res = await getFinanceLoan(loanId);
			loan = res.data as Record<string, unknown>;
			schedule = (loan.amortization_schedule as Record<string, unknown>[]) ?? [];
			const insRes = await getFinanceInsurance();
			insuranceRecords = (insRes.data ?? []).filter((r: Record<string, unknown>) => r.sale_id === loan?.sale_id);
		} catch {
			toast.error('Failed to load loan details.');
		} finally {
			loading = false;
		}
	});

	async function handleApprove() {
		if (!confirm('Approve this loan application?')) return;
		actionLoading = true;
		try {
			await updateFinanceLoanStatus(loanId, 'approved');
			toast.success('Loan approved.');
			const res = await getFinanceLoan(loanId);
			loan = res.data as Record<string, unknown>;
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Error approving loan.');
		} finally {
			actionLoading = false;
		}
	}

	async function handleReject() {
		if (!rejectionReason) {
			toast.error('Please select a rejection reason.');
			return;
		}
		if (!confirm(`Reject this loan? Reason: ${rejectionReason}`)) return;
		actionLoading = true;
		try {
			await updateFinanceLoanStatus(loanId, 'rejected');
			toast.success(`Loan rejected. Reason: ${rejectionReason}`);
			const res = await getFinanceLoan(loanId);
			loan = res.data as Record<string, unknown>;
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Error rejecting loan.');
		} finally {
			actionLoading = false;
		}
	}

	function formatCurrency(val: number | string | null): string {
		if (val == null) return '—';
		return `₱${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
	}

	let isPending = $derived(loan?.bank_approval_status === 'pending');
</script>

<div class="page">
<h1>Loan Review — #{loanId}</h1>

{#if loading}
	<p>Loading…</p>
{:else if loan}
	<div class="split">
		<!-- LEFT: Applicant, Vehicle, Loan Details -->
		<div class="left-panel">
			<section class="card">
				<h3>Customer Information</h3>
				<div class="info-grid">
					<div class="info-row">
						<span class="label">Name</span>
						<span class="value">{(loan.customer_name as string) ?? '—'}</span>
					</div>
					<div class="info-row">
						<span class="label">Sale ID</span>
						<span class="value">#{loan.sale_id}</span>
					</div>
				</div>
			</section>

			<section class="card">
				<h3>Vehicle Information</h3>
				<div class="info-grid">
					<div class="info-row">
						<span class="label">Brand</span>
						<span class="value">{(loan.brand as string) ?? '—'}</span>
					</div>
					<div class="info-row">
						<span class="label">Model</span>
						<span class="value">{(loan.model as string) ?? '—'}</span>
					</div>
				</div>
			</section>

			<section class="card">
				<h3>Loan Details</h3>
				<div class="info-grid">
					<div class="info-row">
						<span class="label">Loan Amount</span>
						<span class="value highlight">{formatCurrency(loan.loan_amount)}</span>
					</div>
					<div class="info-row">
						<span class="label">Down Payment</span>
						<span class="value">{formatCurrency(loan.down_payment)}</span>
					</div>
					<div class="info-row">
						<span class="label">Interest Rate</span>
						<span class="value">{loan.interest_rate}%</span>
					</div>
					<div class="info-row">
						<span class="label">Term</span>
						<span class="value">{loan.term_months} months</span>
					</div>
					<div class="info-row">
						<span class="label">Monthly Amortization</span>
						<span class="value">{formatCurrency(loan.monthly_amortization)}</span>
					</div>
					<div class="info-row">
						<span class="label">Bank / Lender</span>
						<span class="value">{(loan.bank_name as string) ?? '—'}</span>
					</div>
					<div class="info-row">
						<span class="label">Status</span>
						<span class="value">
							<span class="status-badge status-{(loan.bank_approval_status as string)?.toLowerCase() ?? 'unknown'}">
								{loan.bank_approval_status}
							</span>
						</span>
					</div>
				</div>
			</section>

			<section class="card">
				<h3>Amortization Schedule</h3>
				{#if schedule.length > 0}
					<table class="amort-table">
						<thead>
							<tr>
								<th>#</th>
								<th>Due Date</th>
								<th>Amount</th>
								<th>Status</th>
								<th>Proof</th>
							</tr>
						</thead>
						<tbody>
							{#each schedule as entry}
								<tr>
									<td>{entry.month_number}</td>
									<td>{entry.due_date ? String(entry.due_date).slice(0, 10) : '—'}</td>
									<td>{formatCurrency(entry.amount_due)}</td>
									<td>
										<span class="status-badge status-{(entry.status as string)?.toLowerCase() ?? 'unknown'}">
											{entry.status ?? '—'}
										</span>
									</td>
									<td>
										{#if (entry.status as string) === 'paid' && entry.proof_of_payment}
											<a href={String(entry.proof_of_payment)} target="_blank" rel="noopener" class="proof-link">View</a>
										{:else}
											<span class="muted">—</span>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				{:else}
					<p class="empty">No schedule entries.</p>
				{/if}
			</section>

			<section class="card">
				<h3>Insurance ({insuranceRecords.length})</h3>
				{#if insuranceRecords.length > 0}
					<div class="ins-summary">
						{#each insuranceRecords as ins}
							<div class="ins-row">
								<span class="ins-provider">{(ins.provider_name as string) ?? '—'}</span>
								<span class="ins-policy">{(ins.policy_number as string) ?? '—'}</span>
								<span class="status-badge status-{(ins.status as string)?.toLowerCase() ?? 'unknown'}">{(ins.status as string) ?? '—'}</span>
							</div>
						{/each}
					</div>
				{:else}
					<p class="empty">No insurance linked.</p>
				{/if}
			</section>
		</div>

		<!-- RIGHT: Decision Panel -->
		<div class="right-panel">
			<section class="card decision-card">
				<h3>Decision</h3>

				{#if isPending}
					<div class="decision-section">
						<h4>Approve</h4>
						<p class="desc">Approve this loan application and proceed to contracting.</p>
						<button
							class="btn-approve"
							onclick={handleApprove}
							disabled={actionLoading}
						>
							{actionLoading ? 'Processing…' : '✓ Approve Loan'}
						</button>
					</div>

					<hr>

					<div class="decision-section">
						<h4>Reject</h4>
						<p class="desc">Reject this application with a reason.</p>
						<label for="rejection-reason">Rejection Reason</label>
						<select id="rejection-reason" bind:value={rejectionReason}>
							<option value="">— Select reason —</option>
							{#each REJECTION_REASONS as reason}
								<option value={reason}>{reason}</option>
							{/each}
						</select>
						<button
							class="btn-reject"
							onclick={handleReject}
							disabled={actionLoading || !rejectionReason}
						>
							{actionLoading ? 'Processing…' : '✕ Reject Loan'}
						</button>
					</div>
				{:else}
					<div class="decision-outcome">
						<p>
							<span class="status-badge status-{(loan.bank_approval_status as string)?.toLowerCase() ?? 'unknown'}">
								{loan.bank_approval_status}
							</span>
						</p>
						<p class="desc">This loan has already been reviewed.</p>
					</div>
				{/if}
			</section>
		</div>
	</div>
{/if}
</div>

<style>
	@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

	.page { font-family: 'Syne', sans-serif; padding: 2rem 1.5rem; max-width: 1400px; margin: 0 auto; }
	h1 { padding: 0; margin: 0 0 1rem; font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 700; color: #1a1a2e; }
	.split { display: flex; gap: 1.5rem; padding: 0; }
	.left-panel { flex: 1; display: flex; flex-direction: column; gap: 1rem; }
	.right-panel { width: 22rem; position: sticky; top: 1.5rem; align-self: flex-start; }

	.card { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 1.25rem; }
	.card h3 { margin: 0 0 0.75rem; font-size: 1rem; color: #333; }
	.info-grid { display: flex; flex-direction: column; gap: 0.5rem; }
	.info-row { display: flex; justify-content: space-between; align-items: center; padding: 0.25rem 0; border-bottom: 1px solid #f0f0f0; }
	.info-row:last-child { border-bottom: none; }
	.label { color: #666; font-size: 0.85rem; }
	.value { font-weight: 600; font-size: 0.9rem; }
	.highlight { font-size: 1.1rem; color: #27ae60; }

	.status-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
	.status-pending { background: #fef9e7; color: #7d6608; }
	.status-approved { background: #eafaf1; color: #1e8449; }
	.status-rejected { background: #fdedec; color: #c0392b; }
	.status-unknown { background: #f0f0f0; color: #666; }

	.amort-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
	.amort-table th { text-align: left; padding: 0.4rem 0.5rem; border-bottom: 2px solid #ddd; }
	.amort-table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid #f0f0f0; }
	.empty { color: #999; font-style: italic; }

	.ins-summary { display:flex; flex-direction:column; gap:6px; }
	.ins-row { display:flex; align-items:center; gap:8px; padding:6px 8px; background:#f9f9f9; border-radius:4px; font-size:0.8rem; }
	.ins-provider { font-weight:600; flex:1; }
	.ins-policy { font-family:monospace; color:#555; }

	.proof-link { color: #5289e1; font-weight: 600; text-decoration: none; font-size: 0.8rem; }
	.proof-link:hover { text-decoration: underline; }
	.muted { color: #bbb; font-size: 0.8rem; }

	.decision-card { border-color: #5289e1; border-width: 2px; }
	.decision-section { margin-bottom: 1rem; }
	.decision-section h4 { margin: 0 0 0.25rem; font-size: 0.95rem; }
	.desc { color: #666; font-size: 0.85rem; margin: 0 0 0.75rem; }
	.decision-section label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.25rem; color: #555; }
	.decision-section select { width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 0.75rem; }
	.btn-approve { width: 100%; padding: 0.6rem; background: #27ae60; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 0.95rem; font-weight: 600; }
	.btn-approve:disabled { opacity: 0.5; }
	.btn-reject { width: 100%; padding: 0.6rem; background: #e74c3c; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 0.95rem; font-weight: 600; }
	.btn-reject:disabled { opacity: 0.5; }
	.decision-outcome { text-align: center; padding: 1rem 0; }
	hr { border: none; border-top: 1px solid #ddd; margin: 1rem 0; }
</style>
