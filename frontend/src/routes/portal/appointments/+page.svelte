<script lang="ts">
	import { CalendarCheck, Clock, Car, User, X } from '@lucide/svelte';

	let appointments = $state([
		{ id: 1, date: '2026-06-15', time: '10:00 AM', type: 'Vehicle Inspection', vehicle: 'Honda Civic', advisor: 'John Mark', status: 'confirmed' },
		{ id: 2, date: '2026-06-18', time: '02:00 PM', type: 'Test Drive', vehicle: 'BYD SEALION', advisor: 'Jane Smith', status: 'pending' },
	]);
	let showModal = $state(false);
	let selectedDate = $state('');
	let selectedTime = $state('');

	function cancelAppt(id: number) {
		appointments = appointments.filter(a => a.id !== id);
	}

	function bookAppt() {
		if (!selectedDate || !selectedTime) return;
		appointments = [...appointments, {
			id: Date.now(),
			date: selectedDate,
			time: selectedTime + ':00',
			type: 'General',
			vehicle: 'TBD',
			advisor: 'TBD',
			status: 'pending',
		}];
		showModal = false;
		selectedDate = '';
		selectedTime = '';
	}
</script>

<div class="page-header">
	<div>
		<h1>Appointments</h1>
		<p class="subtitle">Schedule and manage your appointments with us.</p>
	</div>
	<button class="btn-primary" onclick={showModal = true}>
		<CalendarCheck size={18} /> New Appointment
	</button>
</div>

<div class="metrics">
	<div class="metric-card">
		<div class="metric-value">{appointments.length}</div>
		<div class="metric-label">Total</div>
	</div>
	<div class="metric-card">
		<div class="metric-value">{appointments.filter(a => a.status === 'confirmed').length}</div>
		<div class="metric-label">Confirmed</div>
	</div>
	<div class="metric-card">
		<div class="metric-value">{appointments.filter(a => a.status !== 'confirmed').length}</div>
		<div class="metric-label">Pending</div>
	</div>
</div>

<div class="table-wrapper">
	<table>
		<thead>
			<tr>
				<th>Date</th>
				<th>Time</th>
				<th>Type</th>
				<th>Vehicle</th>
				<th>Advisor</th>
				<th>Status</th>
				<th>Actions</th>
			</tr>
		</thead>
		<tbody>
			{#each appointments as a}
				<tr>
					<td><CalendarCheck size={14} class="icon-muted" /> {a.date}</td>
					<td><Clock size={14} class="icon-muted" /> {a.time}</td>
					<td>{a.type}</td>
					<td><Car size={14} class="icon-muted" /> {a.vehicle}</td>
					<td><User size={14} class="icon-muted" /> {a.advisor}</td>
					<td>
						<span class="status-badge" class:confirmed={a.status === 'confirmed'} class:pending={a.status === 'pending'}>
							{a.status.charAt(0).toUpperCase() + a.status.slice(1)}
						</span>
					</td>
					<td>
						<button class="btn-cancel" onclick={() => cancelAppt(a.id)}><X size={14} /> Cancel</button>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

{#if showModal}
	<div class="modal-overlay" onclick={() => showModal = false}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>New Appointment</h2>
				<button class="modal-close" onclick={() => showModal = false}><X size={20} /></button>
			</div>
			<div class="modal-body">
				<div class="form-group">
					<label>Date</label>
					<input type="date" bind:value={selectedDate} />
				</div>
				<div class="form-group">
					<label>Time</label>
					<input type="time" bind:value={selectedTime} />
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={() => showModal = false}>Cancel</button>
				<button class="btn-primary" onclick={bookAppt}>Book</button>
			</div>
		</div>
	</div>
{/if}

<style>
	h1 { font-size:24px; font-weight:700; color:var(--text-dark); margin:0; }
	.subtitle { font-size:14px; color:var(--text-muted); margin-top:4px; }
	.page-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:24px; }
	.btn-primary { display:inline-flex; align-items:center; gap:8px; background:var(--primary); color:var(--text-white); border:none; border-radius:var(--radius-md); padding:10px 20px; font-size:14px; font-weight:600; cursor:pointer; }
	.btn-primary:hover { opacity:0.9; }
	.metrics { display:grid; grid-template-columns:repeat(auto-fit, minmax(120px, 1fr)); gap:12px; margin-bottom:20px; }
	.metric-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:16px; text-align:center; }
	.metric-value { font-size:28px; font-weight:700; color:var(--primary); }
	.metric-label { font-size:12px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-top:4px; }
	.table-wrapper { overflow-x:auto; background:var(--bg-card); border-radius:var(--radius-md); border:1px solid var(--border); box-shadow:var(--shadow-sm); }
	table { width:100%; border-collapse:collapse; font-size:0.85rem; }
	th { text-align:left; padding:0.75rem 1rem; color:var(--text-muted); font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid var(--border); background:var(--bg-muted); }
	td { padding:0.65rem 1rem; border-bottom:1px solid var(--border-lighter); color:var(--text-primary); vertical-align:middle; }
	tr:last-child td { border-bottom:none; }
	.icon-muted { color:var(--text-muted); display:inline; margin-right:4px; vertical-align:middle; }
	.status-badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
	.status-badge.confirmed { background:#d1fae5; color:#065f46; }
	.status-badge.pending { background:#fef3c7; color:#92400e; }
	.btn-cancel { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; border-radius:var(--radius-sm); padding:4px 10px; font-size:11px; font-weight:600; cursor:pointer; display:inline-flex; align-items:center; gap:4px; }
	.btn-cancel:hover { background:#fee2e2; }
	.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:100; }
	.modal { background:var(--bg-card); border-radius:var(--radius-lg); width:450px; max-width:90vw; box-shadow:var(--shadow-lg); }
	.modal-header { display:flex; justify-content:space-between; align-items:center; padding:20px 24px; border-bottom:1px solid var(--border); }
	.modal-header h2 { font-size:18px; font-weight:700; margin:0; }
	.modal-close { background:none; border:none; cursor:pointer; color:var(--text-muted); padding:4px; border-radius:var(--radius-sm); }
	.modal-close:hover { background:var(--bg-hover); }
	.modal-body { padding:20px 24px; }
	.modal-footer { padding:16px 24px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; gap:8px; }
	.btn-secondary { padding:8px 16px; border:1px solid var(--border); border-radius:var(--radius-md); background:var(--bg-card); color:var(--text-dark); font-size:14px; font-weight:500; cursor:pointer; }
	.form-group { margin-bottom:16px; }
	.form-group label { display:block; font-size:13px; font-weight:600; color:var(--text-dark); margin-bottom:6px; }
	.form-group input { width:100%; padding:8px 12px; border:1px solid var(--border); border-radius:var(--radius-md); font-size:14px; background:var(--bg-card); color:var(--text-dark); }
</style>
