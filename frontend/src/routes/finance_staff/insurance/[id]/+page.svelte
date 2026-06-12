<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { getFinanceInsuranceDetail, updateFinanceInsurance } from '$lib/services/api';
	import { Shield, ArrowLeft, Save } from '@lucide/svelte';
	import Loader from '$lib/components/Loader.svelte';

	let insuranceId = $derived(Number($page.params.id));
	let record = $state<Record<string, unknown> | null>(null);
	let loading = $state(true);
	let editing = $state(false);
	let saving = $state(false);
	let message = $state('');
	let form = $state({ provider_name: '', policy_number: '', coverage_type: '', start_date: '', end_date: '', status: '' });

	onMount(async () => {
		try {
			const res = await getFinanceInsuranceDetail(insuranceId);
			record = res.data;
			form.provider_name = (record?.provider_name as string) ?? '';
			form.policy_number = (record?.policy_number as string) ?? '';
			form.coverage_type = (record?.coverage_type as string) ?? '';
			form.start_date = record?.start_date ? String(record.start_date).slice(0, 10) : '';
			form.end_date = record?.end_date ? String(record.end_date).slice(0, 10) : '';
			form.status = (record?.status as string) ?? 'active';
		} catch {
			// ignore
		} finally {
			loading = false;
		}
	});

	async function save() {
		saving = true;
		message = '';
		try {
			await updateFinanceInsurance(insuranceId, {
				provider_name: form.provider_name,
				coverage_type: form.coverage_type,
				start_date: form.start_date,
				end_date: form.end_date,
				status: form.status,
			});
			message = 'Insurance record updated.';
			editing = false;
			const res = await getFinanceInsuranceDetail(insuranceId);
			record = res.data;
		} catch (e: unknown) {
			message = e instanceof Error ? e.message : 'Error updating.';
		} finally {
			saving = false;
		}
	}

	function statusClass(s: string) {
		if (s === 'active') return 'badge-active';
		if (s === 'expired') return 'badge-expired';
		if (s === 'cancelled') return 'badge-cancelled';
		return '';
	}
</script>

<div class="page">
	<a href="/finance_staff/insurance" class="back-link" onclick={(e) => { e.preventDefault(); goto('/finance_staff/insurance'); }}>
		<ArrowLeft size={14} /> Back to Insurance
	</a>

	{#if message}<div class="msg">{message}</div>{/if}

	{#if loading}
		<div class="loader"><Loader /></div>
	{:else if record}
		<div class="page-header">
			<h1><Shield size={22} /> Policy #{record.policy_number}</h1>
			<button class="btn-edit" onclick={() => editing = !editing}>
				{editing ? 'Cancel' : 'Edit'}
			</button>
		</div>

		<div class="cards-grid">
			<div class="card">
				<h3>Policy Details</h3>
				{#if editing}
					<div class="form-body">
						<div class="form-group">
							<label>Provider</label>
							<input type="text" value="automatik" disabled class="disabled-input" />
						</div>
						<div class="form-group">
							<label>Policy Number</label>
							<input type="text" value={form.policy_number} disabled class="disabled-input" />
						</div>
						<div class="form-group">
							<label>Coverage Type</label>
							<select bind:value={form.coverage_type}>
								<option value="Comprehensive">Comprehensive</option>
								<option value="CTPL">CTPL</option>
								<option value="CTPL + Comprehensive">CTPL + Comprehensive</option>
								<option value="Third Party Liability">Third Party Liability</option>
							</select>
						</div>
						<div class="form-row">
							<div class="form-group">
								<label>Start Date</label>
								<input type="date" bind:value={form.start_date} />
							</div>
							<div class="form-group">
								<label>End Date</label>
								<input type="date" bind:value={form.end_date} />
							</div>
						</div>
						<div class="form-group">
							<label>Status</label>
							<select bind:value={form.status}>
								<option value="active">Active</option>
								<option value="expired">Expired</option>
								<option value="cancelled">Cancelled</option>
							</select>
						</div>
						<button class="btn-primary" onclick={save} disabled={saving}>
							<Save size={16} /> {saving ? 'Saving…' : 'Save Changes'}
						</button>
					</div>
				{:else}
					<div class="info-grid">
						<div class="info-row"><span class="label">Provider</span><span class="value">{record.provider_name as string}</span></div>
						<div class="info-row"><span class="label">Policy Number</span><span class="value mono">{record.policy_number as string}</span></div>
						<div class="info-row"><span class="label">Coverage Type</span><span class="value">{(record.coverage_type as string) ?? '—'}</span></div>
						<div class="info-row"><span class="label">Start Date</span><span class="value">{record.start_date ? String(record.start_date).slice(0, 10) : '—'}</span></div>
						<div class="info-row"><span class="label">End Date</span><span class="value">{record.end_date ? String(record.end_date).slice(0, 10) : '—'}</span></div>
						<div class="info-row">
							<span class="label">Status</span>
							<span class="value"><span class="status-badge {statusClass(record.status as string)}">{record.status as string}</span></span>
						</div>
					</div>
				{/if}
			</div>

			<div class="card">
				<h3>Customer & Vehicle</h3>
				<div class="info-grid">
					<div class="info-row"><span class="label">Customer</span><span class="value">{record.customer_name as string}</span></div>
					<div class="info-row"><span class="label">Vehicle</span><span class="value">{(record.brand as string) ?? ''} {(record.model as string) ?? ''} {(record.year as string) ?? ''}</span></div>
					<div class="info-row"><span class="label">Sale ID</span><span class="value mono">#{record.sale_id}</span></div>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.page { font-family:var(--font-sans); padding:2rem 1.5rem; max-width:1000px; margin:0 auto; }
	.back-link { display:inline-flex; align-items:center; gap:4px; font-size:12px; color:var(--primary-light); text-decoration:none; margin-bottom:0.75rem; }
	.back-link:hover { text-decoration:underline; }
	.msg { padding:0.5rem 0.75rem; background:#ecfdf5; color:#059669; border-radius:var(--radius-sm); font-size:13px; margin-bottom:1rem; }
	.loader { display:grid; place-items:center; height:30vh; }
	.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; }
	h1 { font-size:22px; font-weight:700; color:var(--text-dark); margin:0; display:flex; align-items:center; gap:10px; }
	.btn-edit { padding:8px 16px; border:1px solid var(--primary); border-radius:var(--radius-sm); background:var(--bg-card); color:var(--primary); font-size:13px; font-weight:600; cursor:pointer; }
	.btn-edit:hover { background:var(--primary-bg); }
	.cards-grid { display:grid; grid-template-columns:1fr 1fr; gap:1rem; }
	.card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:1.25rem; }
	.card h3 { margin:0 0 0.75rem; font-size:0.85rem; font-weight:600; color:var(--text-light); text-transform:uppercase; letter-spacing:0.03em; }
	.info-grid { display:flex; flex-direction:column; gap:0.35rem; }
	.info-row { display:flex; justify-content:space-between; align-items:center; padding:0.35rem 0; border-bottom:1px solid var(--border-lighter); }
	.info-row:last-child { border-bottom:none; }
	.label { color:var(--text-light); font-size:0.8rem; }
	.value { font-weight:600; font-size:0.85rem; color:var(--text-primary); text-align:right; }
	.mono { font-family:var(--font-mono); }
	.status-badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
	.badge-active { background:#d1fae5; color:#065f46; }
	.badge-expired { background:#fef3c7; color:#92400e; }
	.badge-cancelled { background:#fef2f2; color:#dc2626; }
	.form-body { display:flex; flex-direction:column; gap:12px; }
	.form-group { display:flex; flex-direction:column; gap:4px; }
	.form-group label { font-size:12px; font-weight:600; color:var(--text-dark); }
	.form-group input, .form-group select { padding:8px 12px; border:1px solid var(--border); border-radius:var(--radius-sm); font-size:13px; background:var(--bg-card); color:var(--text-dark); }
	.form-group select { cursor:pointer; }
	.form-row { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
	.disabled-input { opacity:0.6; }
	.btn-primary { display:inline-flex; align-items:center; gap:6px; padding:9px 18px; background:var(--primary); color:var(--text-white); border:none; border-radius:var(--radius-sm); font-size:13px; font-weight:600; cursor:pointer; width:fit-content; }
	.btn-primary:disabled { opacity:0.6; cursor:not-allowed; }
</style>
