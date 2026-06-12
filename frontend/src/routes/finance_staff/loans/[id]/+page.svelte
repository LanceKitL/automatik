<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import {
		getFinanceLoan,
		updateFinanceLoanStatus,
		updateAmortizationStatus,
		getFinanceInsurance,
		type LoanItem,
		type ScheduleItem
	} from '$lib/services/api';
	import DataTable from '$lib/components/DataTable.svelte';
	import { ArrowLeft, Shield, Plus } from '@lucide/svelte';

	let loanId = $derived(Number($page.params.id));
	let loan = $state<(LoanItem & { amortization_schedule: ScheduleItem[] }) | null>(null);
	let schedule = $state<ScheduleItem[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let message = $state('');
	let actionLoading = $state(false);
	let insuranceRecords = $state<Record<string, unknown>[]>([]);

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
		message = '';
		try {
			await updateFinanceLoanStatus(loanId, status);
			message = `Loan #${loanId} ${status}.`;
			const res = await getFinanceLoan(loanId);
			loan = res.data as LoanItem & { amortization_schedule: ScheduleItem[] };
			schedule = loan?.amortization_schedule ?? [];
		} catch (e: unknown) {
			message = e instanceof Error ? e.message : 'Error.';
		} finally {
			actionLoading = false;
		}
	}

	async function handleMarkPaid(scheduleId: number) {
		if (!confirm('Mark this amortization entry as paid?')) return;
		message = '';
		try {
			await updateAmortizationStatus(scheduleId, 'paid');
			message = `Entry #${scheduleId} marked as paid.`;
			const res = await getFinanceLoan(loanId);
			loan = res.data as LoanItem & { amortization_schedule: ScheduleItem[] };
			schedule = loan?.amortization_schedule ?? [];
		} catch (e: unknown) {
			message = e instanceof Error ? e.message : 'Error.';
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

	{#if message}
		<div class="msg">{message}</div>
	{/if}

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
				<DataTable columns={['#', 'Due Date', 'Principal', 'Interest', 'Total Due', 'Running Balance', 'Status', 'Proof', 'Actions']}>
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
								{#if entry.status === 'paid' && entry.proof_of_payment}
									<a href={entry.proof_of_payment} target="_blank" rel="noopener" class="proof-link">View</a>
								{:else}
									<span class="muted">—</span>
								{/if}
							</td>
							<td>
								{#if entry.status === 'unpaid'}
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
	{/if}
</div>

<style>
	.page { font-family: var(--font-sans); padding: 2rem 1.5rem; max-width: 1200px; margin: 0 auto; }

	.back-link { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: var(--primary-light); text-decoration: none; margin-bottom: 0.75rem; }
	.back-link:hover { text-decoration: underline; }

	h1 { font-size: 20px; font-weight: 700; color: var(--text-primary); margin: 0 0 1.25rem; }

	.msg { padding: 0.5rem 0.75rem; background: #ecfdf5; color: #059669; border-radius: var(--radius-sm); font-size: 13px; margin-bottom: 1rem; }

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
	.muted { color: var(--text-muted); font-size: 11px; }
	.btn-paid { padding: 3px 10px; border: none; border-radius: var(--radius-sm); background: var(--success); color: var(--text-white); font-family: var(--font-sans); font-size: 10px; font-weight: 600; cursor: pointer; transition: opacity .15s; }
	.btn-paid:hover { opacity: 0.85; }

	.empty { color: var(--text-muted); font-style: italic; font-size: 13px; }

	@media (max-width: 768px) {
		.cards-grid { grid-template-columns: 1fr; }
	}
</style>
