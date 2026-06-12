<script lang="ts">
	import { LifeBuoy, ShieldAlert, Plus, X, FileText } from '@lucide/svelte';

	let claims = $state([
		{ id: 'WC-2024-00471', vehicle: 'Honda Civic 2024', date: '2026-05-20', type: 'Engine Misfire', status: 'open', priority: 'High' },
		{ id: 'WC-2024-00472', vehicle: 'BYD SEALION 2025', date: '2026-05-18', type: 'Battery Draining', status: 'in-review', priority: 'Medium' },
	]);
	let showForm = $state(false);
	let newClaim = $state({ vehicle: '', type: '', description: '' });

	function submitClaim() {
		if (!newClaim.vehicle || !newClaim.type) return;
		claims = [{
			id: `WC-2026-${String(Date.now()).slice(-5)}`,
			vehicle: newClaim.vehicle,
			date: new Date().toISOString().slice(0, 10),
			type: newClaim.type,
			status: 'open',
			priority: 'Medium',
		}, ...claims];
		newClaim = { vehicle: '', type: '', description: '' };
		showForm = false;
	}

	function getStatusClass(s: string) {
		if (s === 'open') return 'status-open';
		if (s === 'in-review') return 'status-review';
		if (s === 'approved') return 'status-approved';
		return 'status-closed';
	}
</script>

<div class="page-header">
	<div>
		<h1>Warranty Claims</h1>
		<p class="subtitle">Submit and track warranty claims for your vehicles.</p>
	</div>
	<button class="btn-primary" onclick={showForm = true}>
		<Plus size={18} /> New Claim
	</button>
</div>

<div class="metrics">
	<div class="metric-card">
		<div class="metric-value">{claims.length}</div>
		<div class="metric-label">Total Claims</div>
	</div>
	<div class="metric-card">
		<div class="metric-value">{claims.filter(c => c.status === 'open').length}</div>
		<div class="metric-label">Open</div>
	</div>
	<div class="metric-card">
		<div class="metric-value">{claims.filter(c => c.priority === 'High').length}</div>
		<div class="metric-label">High Priority</div>
	</div>
</div>

<div class="table-wrapper">
	<table>
		<thead>
			<tr>
				<th>Claim ID</th>
				<th>Vehicle</th>
				<th>Date</th>
				<th>Issue</th>
				<th>Priority</th>
				<th>Status</th>
				<th>Actions</th>
			</tr>
		</thead>
		<tbody>
			{#each claims as c}
				<tr>
					<td class="claim-id"><ShieldAlert size={14} /> {c.id}</td>
					<td>{c.vehicle}</td>
					<td>{c.date}</td>
					<td>{c.type}</td>
					<td><span class="priority-badge" class:high={c.priority === 'High'} class:medium={c.priority === 'Medium'} class:low={c.priority === 'Low'}>{c.priority}</span></td>
					<td><span class="status-badge {getStatusClass(c.status)}">{c.status === 'in-review' ? 'In Review' : c.status.charAt(0).toUpperCase() + c.status.slice(1)}</span></td>
					<td><button class="btn-view" title="View Details"><FileText size={14} /> View</button></td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

{#if showForm}
	<div class="modal-overlay" onclick={() => showForm = false}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Submit Warranty Claim</h2>
				<button class="modal-close" onclick={() => showForm = false}><X size={20} /></button>
			</div>
			<div class="modal-body">
				<div class="form-group">
					<label>Vehicle</label>
					<select bind:value={newClaim.vehicle}>
						<option value="">Select vehicle</option>
						<option value="Honda Civic 2024">Honda Civic 2024</option>
						<option value="BYD SEALION 2025">BYD SEALION 2025</option>
					</select>
				</div>
				<div class="form-group">
					<label>Issue Type</label>
					<select bind:value={newClaim.type}>
						<option value="">Select type</option>
						<option value="Engine Misfire">Engine Misfire</option>
						<option value="Battery Draining">Battery Draining</option>
						<option value="Electrical Issue">Electrical Issue</option>
						<option value="Transmission Problem">Transmission Problem</option>
						<option value="Other">Other</option>
					</select>
				</div>
				<div class="form-group">
					<label>Description</label>
					<textarea rows="4" bind:value={newClaim.description} placeholder="Describe the issue in detail..."></textarea>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={() => showForm = false}>Cancel</button>
				<button class="btn-primary" onclick={submitClaim}>Submit Claim</button>
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
	.claim-id { display:flex; align-items:center; gap:6px; font-weight:600; font-family:monospace; }
	.priority-badge { display:inline-block; padding:2px 8px; border-radius:var(--radius-sm); font-size:11px; font-weight:600; }
	.priority-badge.high { background:#fef2f2; color:#dc2626; }
	.priority-badge.medium { background:#fef3c7; color:#92400e; }
	.priority-badge.low { background:#d1fae5; color:#065f46; }
	.status-badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
	.status-badge.status-open { background:#fef3c7; color:#92400e; }
	.status-badge.status-review { background:#dbeafe; color:#1e40af; }
	.status-badge.status-approved { background:#d1fae5; color:#065f46; }
	.status-badge.status-closed { background:#f3f4f6; color:#6b7280; }
	.btn-view { background:var(--primary-bg); color:var(--primary); border:1px solid var(--primary); border-radius:var(--radius-sm); padding:4px 10px; font-size:11px; font-weight:600; cursor:pointer; display:inline-flex; align-items:center; gap:4px; }
	.btn-view:hover { background:var(--primary); color:var(--text-white); }
	.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:100; }
	.modal { background:var(--bg-card); border-radius:var(--radius-lg); width:500px; max-width:90vw; box-shadow:var(--shadow-lg); }
	.modal-header { display:flex; justify-content:space-between; align-items:center; padding:20px 24px; border-bottom:1px solid var(--border); }
	.modal-header h2 { font-size:18px; font-weight:700; margin:0; }
	.modal-close { background:none; border:none; cursor:pointer; color:var(--text-muted); padding:4px; border-radius:var(--radius-sm); }
	.modal-close:hover { background:var(--bg-hover); }
	.modal-body { padding:20px 24px; }
	.modal-footer { padding:16px 24px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; gap:8px; }
	.btn-secondary { padding:8px 16px; border:1px solid var(--border); border-radius:var(--radius-md); background:var(--bg-card); color:var(--text-dark); font-size:14px; font-weight:500; cursor:pointer; }
	.form-group { margin-bottom:16px; }
	.form-group label { display:block; font-size:13px; font-weight:600; color:var(--text-dark); margin-bottom:6px; }
	.form-group input, .form-group select, .form-group textarea { width:100%; padding:8px 12px; border:1px solid var(--border); border-radius:var(--radius-md); font-size:14px; background:var(--bg-card); color:var(--text-dark); }
	.form-group select { cursor:pointer; }
	.form-group textarea { resize:vertical; }
</style>
