<script lang="ts">
	import { onMount } from 'svelte';
	import { getMyAmortization, payAmortization } from '$lib/services/api';
	import { Calculator, CheckCircle2, Clock, AlertCircle, Car, Upload, X } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';
	import Loader from '$lib/components/Loader.svelte';

	let schedule = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);

	let showModal = $state(false);
	let payEntry = $state<Record<string, unknown> | null>(null);
	let payFile = $state<File | null>(null);
	let payMethod = $state('online');
	let paying = $state(false);

	interface VehicleGroup {
		vehicle_id: number;
		brand: string;
		model: string;
		year: number | null;
		rows: Record<string, unknown>[];
	}

	let groups = $derived.by(() => {
		const map = new Map<number, VehicleGroup>();
		for (const row of schedule) {
			const vid = Number(row.vehicle_id ?? 0);
			if (!vid) continue;
			if (!map.has(vid)) {
				map.set(vid, {
					vehicle_id: vid,
					brand: row.brand as string,
					model: row.model as string,
					year: row.year as number | null,
					rows: [],
				});
			}
			map.get(vid)!.rows.push(row);
		}
		return Array.from(map.values());
	});

	let totalEntries = $derived(schedule.length);
	let totalPaid = $derived(schedule.filter(s => (s.status as string) === 'paid').length);
	let totalOverdue = $derived(schedule.filter(s => (s.status as string) === 'overdue').length);

	function canPay(row: Record<string, unknown>, allRows: Record<string, unknown>[]): boolean {
		const s = row.status as string;
		if (s === 'paid') return false;
		const rv = row.review_status as string | undefined;
		if (rv === 'pending_verification') return false;
		if (s === 'overdue') return true;
		if (s === 'unpaid') {
			const firstUnpaid = allRows
				.filter(r => (r.status as string) === 'unpaid')
				.sort((a, b) => (a.month_number as number) - (b.month_number as number))[0];
			return firstUnpaid?.schedule_id === row.schedule_id;
		}
		return false;
	}

	function showPayModal(row: Record<string, unknown>) {
		payEntry = row;
		payFile = null;
		payMethod = 'online';
		showModal = true;
	}

	async function handlePay() {
		if (!payEntry || !payFile) return;
		paying = true;
		try {
			await payAmortization(payEntry.schedule_id as number, payFile, payMethod);
			toast.success('Payment submitted for review!');
			showModal = false;
			const res = await getMyAmortization();
			schedule = res.data ?? [];
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Payment failed');
		} finally {
			paying = false;
		}
	}

	function reviewStatusBadge(rv: string | undefined) {
		if (rv === 'pending_verification') return 'Pending Review';
		if (rv === 'rejected') return 'Rejected';
		return '';
	}

	function reviewStatusClass(rv: string | undefined) {
		if (rv === 'pending_verification') return 'status-pending';
		if (rv === 'rejected') return 'status-overdue';
		return '';
	}

	onMount(async () => {
		try {
			const res = await getMyAmortization();
			schedule = res.data ?? [];
		} catch {
			// ignore
		} finally {
			loading = false;
		}
	});

	function statusClass(s: string) {
		if (s === 'paid') return 'status-paid';
		if (s === 'pending') return 'status-pending';
		if (s === 'overdue') return 'status-overdue';
		return 'status-pending';
	}

	function statusLabel(s: string) {
		if (s === 'paid') return 'Paid';
		if (s === 'pending') return 'Pending';
		if (s === 'overdue') return 'Overdue';
		return s.charAt(0).toUpperCase() + s.slice(1);
	}
</script>

<div class="page-header">
	<h1>Amortization Schedule</h1>
	<p class="subtitle">View your loan payment schedule and track payments.</p>
</div>

{#if loading}
	<div class="loader"><Loader /></div>
{:else if schedule.length === 0}
	<div class="empty">
		<Calculator size={48} />
		<p>No amortization schedule available.</p>
		<p class="empty-sub">Schedule appears once your loan is approved.</p>
	</div>
{:else}
	<div class="metrics">
		<div class="metric-card">
			<div class="metric-value">{totalEntries}</div>
			<div class="metric-label">Total Payments</div>
		</div>
		<div class="metric-card">
			<div class="metric-value">{totalPaid}</div>
			<div class="metric-label">Paid</div>
		</div>
		<div class="metric-card">
			<div class="metric-value">{totalOverdue}</div>
			<div class="metric-label">Overdue</div>
		</div>
		<div class="metric-card">
			<div class="metric-value">{groups.length}</div>
			<div class="metric-label">Vehicles</div>
		</div>
	</div>

	{#each groups as g}
		<div class="vehicle-section">
			<div class="section-header">
				<Car size={18} />
				<span class="vehicle-name">{g.brand} {g.model}{g.year ? ` (${g.year})` : ''}</span>
				<span class="section-count">{g.rows.length} payments</span>
				<span class="section-paid">{g.rows.filter(r => (r.status as string) === 'paid').length} paid</span>
			</div>
			<div class="table-wrapper">
				<table>
					<thead>
						<tr>
							<th>Month</th>
							<th>Due Date</th>
							<th>Principal</th>
							<th>Interest</th>
							<th>Total Due</th>
							<th>Running Balance</th>
							<th>Status</th>
							<th class="action-col">Action</th>
						</tr>
					</thead>
					<tbody>
						{#each g.rows as row, i}
							<tr>
								<td>{row.month_number ?? i + 1}</td>
								<td>{row.due_date ? String(row.due_date).slice(0, 10) : '—'}</td>
								<td>₱{Number(row.principal ?? 0).toLocaleString()}</td>
								<td>₱{Number(row.interest ?? 0).toLocaleString()}</td>
								<td class="amount-cell">₱{Number(row.total_due ?? 0).toLocaleString()}</td>
								<td class="amount-cell">₱{Number(row.running_balance ?? 0).toLocaleString()}</td>
								<td>
									<span class="status-badge {statusClass(row.status as string)}">
										{statusLabel(row.status as string)}
									</span>
								</td>
								<td class="action-col">
									{#if canPay(row, g.rows)}
										<button class="btn-pay" onclick={() => showPayModal(row)}>
											Pay
										</button>
									{:else if (row.review_status as string) === 'pending_verification'}
										<span class="status-badge status-pending">Pending Review</span>
									{:else if (row.review_status as string) === 'rejected'}
										<button class="btn-pay" onclick={() => showPayModal(row)}>
											Pay Again
										</button>
									{:else if (row.status as string) === 'paid'}
										<CheckCircle2 size={16} class="paid-icon" />
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/each}
{/if}

<!-- Pay Modal -->
{#if showModal && payEntry}
	<div class="modal-overlay" onclick={() => (showModal = false)}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Pay Amortization</h2>
				<button class="btn-icon" onclick={() => (showModal = false)}><X size={18} /></button>
			</div>
			<div class="modal-body">
				<div class="pay-detail">
					<span class="pay-label">Schedule #</span>
					<span>{payEntry.schedule_id}</span>
				</div>
				<div class="pay-detail">
					<span class="pay-label">Month</span>
					<span>{payEntry.month_number}</span>
				</div>
				<div class="pay-detail">
					<span class="pay-label">Total Due</span>
					<span class="pay-amount">₱{Number(payEntry.total_due ?? 0).toLocaleString()}</span>
				</div>

				<div class="form-group">
					<label for="pay-method">Payment Method</label>
					<select id="pay-method" bind:value={payMethod}>
						<option value="online">Online</option>
						<option value="bank_transfer">Bank Transfer</option>
						<option value="cash">Cash</option>
						<option value="check">Check</option>
					</select>
				</div>

				<div class="form-group">
					<label>Upload Payment Screenshot</label>
					<div
						class="file-drop"
						class:has-file={payFile !== null}
						onclick={() => document.getElementById('pay-file-input')?.click()}
						onkeydown={(e) => e.key === 'Enter' && document.getElementById('pay-file-input')?.click()}
						tabindex="0"
						role="button"
					>
						{#if payFile}
							<Upload size={20} />
							<span>{payFile.name}</span>
						{:else}
							<Upload size={20} />
							<span>Click to select screenshot</span>
						{/if}
					</div>
					<input
						id="pay-file-input"
						type="file"
						accept="image/*"
						onchange={(e) => {
							const files = (e.target as HTMLInputElement).files;
							if (files && files.length > 0) payFile = files[0];
						}}
						style="display:none"
					/>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" onclick={() => (showModal = false)} disabled={paying}>Cancel</button>
				<button class="btn-primary" onclick={handlePay} disabled={!payFile || paying}>
					{paying ? 'Submitting...' : 'Submit for Review'}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.page-header { margin-bottom:24px; }
	h1 { font-size:24px; font-weight:700; color:var(--text-dark); margin:0; }
	.subtitle { font-size:14px; color:var(--text-muted); margin-top:4px; }
	.loader { display:grid; place-items:center; height:50vh; }
	.empty { display:flex; flex-direction:column; align-items:center; gap:8px; padding:60px 20px; color:var(--text-muted); }
	.empty p { font-size:14px; margin:0; }
	.empty-sub { font-size:12px; }
	.metrics { display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:14px; margin-bottom:24px; }
	.metric-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:18px 20px; text-align:center; box-shadow:var(--shadow-sm); }
	.metric-value { font-size:28px; font-weight:700; color:var(--primary); }
	.metric-label { font-size:11px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-top:4px; }
	.vehicle-section { margin-bottom:24px; }
	.section-header { display:flex; align-items:center; gap:10px; padding:12px 16px; background:var(--bg-muted); border:1px solid var(--border); border-bottom:none; border-radius:var(--radius-md) var(--radius-md) 0 0; }
	.vehicle-name { font-size:15px; font-weight:700; color:var(--text-dark); flex:1; }
	.section-count { font-size:11px; color:var(--text-muted); background:var(--bg-card); padding:2px 10px; border-radius:12px; }
	.section-paid { font-size:11px; color:var(--success-text); background:#d1fae5; padding:2px 10px; border-radius:12px; }
	.table-wrapper { overflow-x:auto; background:var(--bg-card); border:1px solid var(--border); border-radius:0 0 var(--radius-md) var(--radius-md); }
	table { width:100%; border-collapse:collapse; font-size:0.85rem; }
	th { text-align:left; padding:0.75rem 1rem; color:var(--text-muted); font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid var(--border); background:var(--bg-muted); }
	td { padding:0.65rem 1rem; border-bottom:1px solid var(--border-lighter); color:var(--text-primary); }
	tr:last-child td { border-bottom:none; }
	.action-col { width:120px; text-align:center; }
	.status-badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
	.status-badge.status-paid { background:#d1fae5; color:#065f46; }
	.status-badge.status-pending { background:#fef3c7; color:#92400e; }
	.status-badge.status-overdue { background:#fef2f2; color:#dc2626; }
	.btn-pay { padding:4px 16px; font-size:12px; font-weight:600; border:none; border-radius:6px; background:#2563eb; color:#fff; cursor:pointer; }
	.btn-pay:hover { background:#1d4ed8; }
	.paid-icon { color:#16a34a; margin:0 auto; display:block; }

	.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.5); display:grid; place-items:center; z-index:1000; }
	.modal { background:var(--bg-card); border-radius:var(--radius-lg); width:480px; max-width:95vw; box-shadow:var(--shadow-lg); }
	.modal-header { display:flex; align-items:center; justify-content:space-between; padding:18px 24px; border-bottom:1px solid var(--border); }
	.modal-header h2 { font-size:18px; font-weight:700; margin:0; }
	.btn-icon { background:none; border:none; cursor:pointer; color:var(--text-muted); padding:4px; border-radius:6px; }
	.btn-icon:hover { background:var(--bg-muted); }
	.modal-body { padding:24px; display:flex; flex-direction:column; gap:16px; }
	.pay-detail { display:flex; justify-content:space-between; font-size:14px; }
	.pay-label { color:var(--text-muted); }
	.pay-amount { font-size:18px; font-weight:700; color:var(--primary); }
	.form-group { display:flex; flex-direction:column; gap:6px; }
	.form-group label { font-size:13px; font-weight:600; color:var(--text-dark); }
	.form-group select { padding:8px 12px; border:1px solid var(--border); border-radius:6px; font-size:14px; background:var(--bg-card); }
	.file-drop { display:flex; align-items:center; gap:10px; padding:16px; border:2px dashed var(--border); border-radius:8px; cursor:pointer; color:var(--text-muted); font-size:13px; }
	.file-drop:hover { border-color:var(--primary); }
	.file-drop.has-file { border-color:#16a34a; color:#16a34a; }
	.modal-footer { display:flex; justify-content:flex-end; gap:10px; padding:16px 24px; border-top:1px solid var(--border); }
	.btn-cancel { padding:8px 20px; border:1px solid var(--border); border-radius:6px; background:var(--bg-card); cursor:pointer; font-size:14px; }
	.btn-cancel:disabled { opacity:0.5; cursor:default; }
	.btn-primary { padding:8px 20px; border:none; border-radius:6px; background:#2563eb; color:#fff; cursor:pointer; font-size:14px; font-weight:600; }
	.btn-primary:hover { background:#1d4ed8; }
	.btn-primary:disabled { opacity:0.5; cursor:default; }
</style>
