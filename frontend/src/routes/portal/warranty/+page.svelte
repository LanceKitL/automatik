<script lang="ts">
	import { onMount } from 'svelte';
	import { LifeBuoy, Plus, X, FileText } from '@lucide/svelte';
	import { getMyWarrantyClaims, createWarrantyClaim, getCustomerDashboard } from '$lib/services/api';
	import type { WarrantyClaim } from '$lib/services/api';
	import { toast } from 'svelte-sonner';

	let claims = $state<WarrantyClaim[]>([]);
	let sales = $state<{ sale_id: number; vehicle_id: number }[]>([]);
	let vehicles = $state<{ vehicle_id: number; brand: string; model: string; year?: number }[]>([]);
	let loading = $state(true);
	let showForm = $state(false);
	let submitting = $state(false);

	let newClaim = $state({ saleId: 0, claimType: '', description: '' });

	let vehicleOptions = $derived.by(() => {
		const vehicleMap = new Map<number, { brand: string; model: string; year?: number }>();
		for (const v of vehicles) {
			vehicleMap.set(v.vehicle_id, v);
		}
		return sales
			.filter(s => vehicleMap.has(s.vehicle_id))
			.map(s => {
				const v = vehicleMap.get(s.vehicle_id)!;
				return {
					sale_id: s.sale_id,
					label: `${v.brand} ${v.model}${v.year ? ` (${v.year})` : ''}`
				};
			});
	});

	const claimTypes = [
		{ value: 'repair', label: 'Repair' },
		{ value: 'replacement', label: 'Replacement' },
		{ value: 'refund', label: 'Refund' },
	];

	onMount(async () => {
		try {
			const [cRes, dRes] = await Promise.all([
				getMyWarrantyClaims(),
				getCustomerDashboard()
			]);
			claims = cRes;
			const dashData = dRes.data as {
				dashboard: { my_vehicles: typeof vehicles };
				sales: typeof sales;
			};
			vehicles = dashData.dashboard.my_vehicles;
			sales = (dashData.sales || []).map((s: Record<string, unknown>) => ({
				sale_id: s.sale_id as number,
				vehicle_id: s.vehicle_id as number
			}));
		} catch {
			claims = [];
		} finally {
			loading = false;
		}
	});

	async function submitClaim() {
		if (!newClaim.saleId || !newClaim.claimType || !newClaim.description) return;
		submitting = true;
		try {
			await createWarrantyClaim({
				sale_id: newClaim.saleId,
				claim_type: newClaim.claimType,
				description: newClaim.description
			});
			toast.success('Warranty claim submitted');
			showForm = false;
			newClaim = { saleId: 0, claimType: '', description: '' };
			const res = await getMyWarrantyClaims();
			claims = res;
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to submit claim');
		} finally {
			submitting = false;
		}
	}

	function formatDate(dt: string) {
		if (!dt) return '—';
		const d = new Date(dt);
		return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' });
	}

	function statusLabel(s: string) {
		const map: Record<string, string> = {
			submitted: 'Submitted',
			under_review: 'Under Review',
			approved: 'Approved',
			rejected: 'Rejected',
			resolved: 'Resolved',
		};
		return map[s] || s.charAt(0).toUpperCase() + s.slice(1).replace(/_/g, ' ');
	}

	function statusClass(s: string) {
		const map: Record<string, string> = {
			submitted: 'status-submitted',
			under_review: 'status-review',
			approved: 'status-approved',
			rejected: 'status-rejected',
			resolved: 'status-resolved',
		};
		return map[s] || '';
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
		<div class="metric-value">{claims.filter(c => c.status === 'submitted' || c.status === 'under_review').length}</div>
		<div class="metric-label">Open</div>
	</div>
	<div class="metric-card">
		<div class="metric-value">{claims.filter(c => c.status === 'resolved' || c.status === 'approved').length}</div>
		<div class="metric-label">Resolved</div>
	</div>
</div>

{#if loading}
	<p class="loading">Loading warranty claims…</p>
{:else if claims.length === 0}
	<div class="empty">No warranty claims yet. Click "New Claim" to submit one.</div>
{:else}
	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					<th>Claim ID</th>
					<th>Vehicle</th>
					<th>Date</th>
					<th>Issue</th>
					<th>Status</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each claims as c}
					<tr>
						<td class="claim-id"><LifeBuoy size={14} /> {c.claim_id}</td>
						<td>{c.vehicle.brand} {c.vehicle.model}</td>
						<td>{formatDate(c.submitted_at)}</td>
						<td>{c.claim_type.replace(/_/g, ' ').replace(/\b\w/g, ch => ch.toUpperCase())}</td>
						<td><span class="status-badge {statusClass(c.status)}">{statusLabel(c.status)}</span></td>
						<td><button class="btn-view" title="View Details" disabled><FileText size={14} /> View</button></td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

{#if showForm}
	<div class="modal-overlay" onclick={() => { if (!submitting) showForm = false; }}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Submit Warranty Claim</h2>
				<button class="modal-close" onclick={() => showForm = false} disabled={submitting}><X size={20} /></button>
			</div>
			<div class="modal-body">
				<div class="form-group">
					<label>Vehicle</label>
					<select bind:value={newClaim.saleId}>
						<option value={0}>Select vehicle</option>
						{#each vehicleOptions as vo}
							<option value={vo.sale_id}>{vo.label}</option>
						{/each}
					</select>
				</div>
				<div class="form-group">
					<label>Claim Type</label>
					<select bind:value={newClaim.claimType}>
						<option value="">Select type</option>
						{#each claimTypes as ct}
							<option value={ct.value}>{ct.label}</option>
						{/each}
					</select>
				</div>
				<div class="form-group">
					<label>Description</label>
					<textarea rows="4" bind:value={newClaim.description} placeholder="Describe the issue in detail..."></textarea>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={() => showForm = false} disabled={submitting}>Cancel</button>
			<button class="btn-primary" onclick={submitClaim} disabled={!newClaim.saleId || !newClaim.claimType || !newClaim.description || submitting}>
				{#if submitting}
					<span class="btn-spinner"></span> Submitting…
				{:else}
					Submit Claim
				{/if}
			</button>
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
	.btn-primary:disabled { opacity:0.5; cursor:not-allowed; }
	.btn-spinner { display:inline-block; width:14px; height:14px; border:2px solid rgba(255,255,255,0.3); border-top-color:#fff; border-radius:50%; animation:btn-spin .6s linear infinite; }
	@keyframes btn-spin { to { transform:rotate(360deg); } }
	.metrics { display:grid; grid-template-columns:repeat(auto-fit, minmax(120px, 1fr)); gap:12px; margin-bottom:20px; }
	.metric-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:16px; text-align:center; }
	.metric-value { font-size:28px; font-weight:700; color:var(--primary); }
	.metric-label { font-size:12px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-top:4px; }
	.loading, .empty { text-align:center; padding:40px 20px; color:var(--text-muted); }
	.table-wrapper { overflow-x:auto; background:var(--bg-card); border-radius:var(--radius-md); border:1px solid var(--border); box-shadow:var(--shadow-sm); }
	table { width:100%; border-collapse:collapse; font-size:0.85rem; }
	th { text-align:left; padding:0.75rem 1rem; color:var(--text-muted); font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid var(--border); background:var(--bg-muted); }
	td { padding:0.65rem 1rem; border-bottom:1px solid var(--border-lighter); color:var(--text-primary); vertical-align:middle; }
	tr:last-child td { border-bottom:none; }
	.claim-id { display:flex; align-items:center; gap:6px; font-weight:600; font-family:monospace; }
	.status-badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
	.status-badge.status-submitted { background:#fef3c7; color:#92400e; }
	.status-badge.status-review { background:#dbeafe; color:#1e40af; }
	.status-badge.status-approved { background:#d1fae5; color:#065f46; }
	.status-badge.status-rejected { background:#fef2f2; color:#dc2626; }
	.status-badge.status-resolved { background:#f3f4f6; color:#6b7280; }
	.btn-view { background:var(--primary-bg); color:var(--primary); border:1px solid var(--primary); border-radius:var(--radius-sm); padding:4px 10px; font-size:11px; font-weight:600; cursor:pointer; display:inline-flex; align-items:center; gap:4px; }
	.btn-view:hover { background:var(--primary); color:var(--text-white); }
	.btn-view:disabled { opacity:0.4; cursor:not-allowed; }
	.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:100; }
	.modal { background:var(--bg-card); border-radius:var(--radius-lg); width:500px; max-width:90vw; box-shadow:var(--shadow-lg); }
	.modal-header { display:flex; justify-content:space-between; align-items:center; padding:20px 24px; border-bottom:1px solid var(--border); }
	.modal-header h2 { font-size:18px; font-weight:700; margin:0; }
	.modal-close { background:none; border:none; cursor:pointer; color:var(--text-muted); padding:4px; border-radius:var(--radius-sm); }
	.modal-close:hover { background:var(--bg-hover); }
	.modal-close:disabled { opacity:0.4; cursor:not-allowed; }
	.modal-body { padding:20px 24px; }
	.modal-footer { padding:16px 24px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; gap:8px; }
	.btn-secondary { padding:8px 16px; border:1px solid var(--border); border-radius:var(--radius-md); background:var(--bg-card); color:var(--text-dark); font-size:14px; font-weight:500; cursor:pointer; }
	.form-group { margin-bottom:16px; }
	.form-group label { display:block; font-size:13px; font-weight:600; color:var(--text-dark); margin-bottom:6px; }
	.form-group select, .form-group textarea { width:100%; padding:8px 12px; border:1px solid var(--border); border-radius:var(--radius-md); font-size:14px; background:var(--bg-card); color:var(--text-dark); }
	.form-group select { cursor:pointer; }
	.form-group textarea { resize:vertical; }
</style>
