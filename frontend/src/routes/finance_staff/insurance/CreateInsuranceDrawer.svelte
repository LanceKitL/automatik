<script lang="ts">
	import { onMount } from 'svelte';
	import { getFinanceLoansWithoutInsurance, createFinanceInsurance } from '$lib/services/api';
	import { X, Plus } from '@lucide/svelte';

	let { onclose }: { onclose: () => void } = $props();

	let sales = $state<Record<string, unknown>[]>([]);
	let saving = $state(false);
	let error = $state('');
	let form = $state({
		sale_id: '',
		policy_number: '',
		coverage_type: 'Comprehensive',
		start_date: '',
		end_date: '',
	});

	onMount(async () => {
		try {
			const res = await getFinanceLoansWithoutInsurance();
			sales = res.data ?? [];
		} catch {
			// ignore
		}
	});

	async function submit(e: Event) {
		e.preventDefault();
		if (!form.sale_id || !form.policy_number || !form.start_date || !form.end_date) {
			error = 'Please fill in all required fields.';
			return;
		}
		saving = true;
		error = '';
		try {
			await createFinanceInsurance(Number(form.sale_id), {
				provider_name: 'automatik',
				policy_number: form.policy_number,
				coverage_type: form.coverage_type,
				start_date: form.start_date,
				end_date: form.end_date,
			});
			window.location.reload();
		} catch (e: unknown) {
			error = e instanceof Error ? e.message : 'Failed to create insurance.';
		} finally {
			saving = false;
		}
	}
</script>

<div class="overlay" onclick={onclose}>
	<div class="drawer" onclick={(e) => e.stopPropagation()}>
		<div class="drawer-header">
			<h2>Add Insurance Policy</h2>
			<button class="close-btn" onclick={onclose}><X size={20} /></button>
		</div>
		<form onsubmit={submit}>
			<div class="drawer-body">
				{#if error}
					<div class="alert-error">{error}</div>
				{/if}
				<div class="form-group">
					<label>Sale (Loan) <span class="required">*</span></label>
					<select bind:value={form.sale_id}>
						<option value="">— Select a sale —</option>
						{#each sales as s}
							<option value={s.sale_id ?? s.loan_id}>#{s.sale_id ?? s.loan_id} — {s.customer_name ?? '—'} / {s.brand ?? ''} {s.model ?? ''}</option>
						{/each}
					</select>
				</div>
				<div class="form-row">
					<div class="form-group">
						<label>Policy Number <span class="required">*</span></label>
						<input type="text" bind:value={form.policy_number} placeholder="e.g. POL-2026-001" />
					</div>
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
						<label>Start Date <span class="required">*</span></label>
						<input type="date" bind:value={form.start_date} />
					</div>
					<div class="form-group">
						<label>End Date <span class="required">*</span></label>
						<input type="date" bind:value={form.end_date} />
					</div>
				</div>
			</div>
			<div class="drawer-footer">
				<button type="button" class="btn-secondary" onclick={onclose}>Cancel</button>
				<button type="submit" class="btn-primary" disabled={saving}>
					<Plus size={16} /> {saving ? 'Creating…' : 'Add Insurance'}
				</button>
			</div>
		</form>
	</div>
</div>

<style>
	.overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; justify-content:flex-end; z-index:200; }
	.drawer { width:480px; max-width:100vw; background:var(--bg-card); height:100%; display:flex; flex-direction:column; box-shadow:-4px 0 20px rgba(0,0,0,0.1); }
	.drawer-header { display:flex; justify-content:space-between; align-items:center; padding:20px 24px; border-bottom:1px solid var(--border); }
	.drawer-header h2 { font-size:18px; font-weight:700; margin:0; }
	.close-btn { background:none; border:none; cursor:pointer; color:var(--text-muted); padding:4px; border-radius:var(--radius-sm); }
	.close-btn:hover { background:var(--bg-hover); }
	.drawer-body { flex:1; overflow-y:auto; padding:20px 24px; }
	.drawer-footer { padding:16px 24px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; gap:8px; }
	.alert-error { background:#fef2f2; color:#dc2626; padding:8px 12px; border-radius:var(--radius-sm); font-size:12px; margin-bottom:12px; }
	.form-group { margin-bottom:16px; }
	.form-group label { display:block; font-size:13px; font-weight:600; color:var(--text-dark); margin-bottom:6px; }
	.form-group input, .form-group select { width:100%; padding:9px 12px; border:1px solid var(--border); border-radius:var(--radius-sm); font-size:13px; background:var(--bg-card); color:var(--text-dark); }
	.form-group select { cursor:pointer; }
	.form-row { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
	.required { color:#dc2626; }
	.btn-primary { display:inline-flex; align-items:center; gap:6px; padding:9px 18px; background:var(--primary); color:var(--text-white); border:none; border-radius:var(--radius-sm); font-size:13px; font-weight:600; cursor:pointer; }
	.btn-primary:disabled { opacity:0.6; cursor:not-allowed; }
	.btn-secondary { padding:9px 18px; border:1px solid var(--border); border-radius:var(--radius-sm); background:var(--bg-card); color:var(--text-dark); font-size:13px; font-weight:500; cursor:pointer; }
</style>
