<script lang="ts">
	import { onMount } from 'svelte';
	import { getMyPayments, uploadPaymentProof } from '$lib/services/api';
	import { CreditCard, Wallet, Calendar, AlertTriangle, Upload, Eye } from '@lucide/svelte';

	let payments = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);
	let uploadingId = $state<number | null>(null);
	let uploadError = $state('');

	onMount(async () => {
		try {
			const res = await getMyPayments();
			payments = res.data as Record<string, unknown>[];
		} catch {
			// ignore
		} finally {
			loading = false;
		}
	});

	function formatCurrency(v: unknown) {
		return `₱${Number(v).toLocaleString()}`;
	}

	let totalPaid = $derived(payments.reduce((s, p) => s + Number(p.amount_paid ?? 0), 0));

	async function handleUpload(paymentId: number) {
		const input = document.createElement('input');
		input.type = 'file';
		input.accept = 'image/*';
		input.onchange = async () => {
			const file = input.files?.[0];
			if (!file) return;
			uploadingId = paymentId;
			uploadError = '';
			try {
				const res = await uploadPaymentProof(paymentId, file);
				const p = payments.find((p: any) => p.payment_id === paymentId);
				if (p) p.proof_of_payment = res.proof_of_payment;
			} catch (e: unknown) {
				uploadError = e instanceof Error ? e.message : 'Upload failed.';
			} finally {
				uploadingId = null;
			}
		};
		input.click();
	}
</script>

<div class="page-header">
	<h1>Payment History</h1>
	<p class="subtitle">View and manage your payment records.</p>
</div>

{#if uploadError}
	<div class="alert-error"><AlertTriangle size={16} /> {uploadError}</div>
{/if}

<div class="metrics">
	<div class="metric-card">
		<div class="metric-icon paid"><Wallet size={22} /></div>
		<div class="metric-value">{formatCurrency(totalPaid)}</div>
		<div class="metric-label">Total Paid</div>
	</div>
	<div class="metric-card">
		<div class="metric-icon count"><CreditCard size={22} /></div>
		<div class="metric-value">{payments.length}</div>
		<div class="metric-label">Transactions</div>
	</div>
	<div class="metric-card">
		<div class="metric-icon due"><Calendar size={22} /></div>
		<div class="metric-value">{payments.filter((p: any) => p.payment_date).length}</div>
		<div class="metric-label">With Proof</div>
	</div>
</div>

{#if loading}
	<p class="loading">Loading…</p>
{:else if payments.length === 0}
	<div class="empty">No payments found.</div>
{:else}
	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					<th>ID</th>
					<th>Vehicle</th>
					<th>Amount</th>
					<th>Method</th>
					<th>Allocation</th>
					<th>Date</th>
					<th>Proof</th>
				</tr>
			</thead>
			<tbody>
				{#each payments as p (p.payment_id)}
					<tr>
						<td class="id-cell">#{p.payment_id}</td>
						<td>{(p.brand ?? '') + ' ' + (p.model ?? '')}</td>
						<td class="amount-cell">{formatCurrency(p.amount_paid)}</td>
						<td><span class="method-tag">{p.payment_method ?? '—'}</span></td>
						<td>{p.payment_allocation ?? '—'}</td>
						<td>{p.payment_date ? String(p.payment_date).slice(0, 10) : '—'}</td>
						<td>
							{#if p.proof_of_payment}
								<a href={String(p.proof_of_payment)} target="_blank" rel="noopener" class="proof-link"><Eye size={14} /> View</a>
							{:else}
								<button
									class="upload-btn"
									onclick={() => handleUpload(p.payment_id as number)}
									disabled={uploadingId === p.payment_id}
								>
									<Upload size={14} />
									{uploadingId === p.payment_id ? 'Uploading…' : 'Upload'}
								</button>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

<style>
	.page-header { margin-bottom:24px; }
	h1 { font-size:24px; font-weight:700; color:var(--text-dark); margin:0; }
	.subtitle { font-size:14px; color:var(--text-muted); margin-top:4px; }
	.alert-error { display:flex; align-items:center; gap:8px; background:#fef2f2; color:#dc2626; padding:10px 14px; border-radius:var(--radius-sm); font-size:13px; margin-bottom:16px; border:1px solid #fecaca; }
	.metrics { display:grid; grid-template-columns:repeat(auto-fit, minmax(160px, 1fr)); gap:14px; margin-bottom:24px; }
	.metric-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:18px 20px; display:flex; flex-direction:column; align-items:center; text-align:center; box-shadow:var(--shadow-sm); }
	.metric-icon { width:42px; height:42px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin-bottom:10px; }
	.metric-icon.paid { background:#d1fae5; color:#059669; }
	.metric-icon.count { background:#dbeafe; color:#1d4ed8; }
	.metric-icon.due { background:#fef3c7; color:#d97706; }
	.metric-value { font-size:22px; font-weight:700; color:var(--text-dark); }
	.metric-label { font-size:11px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-top:4px; }
	.loading, .empty { text-align:center; padding:40px; color:var(--text-muted); }
	.table-wrapper { overflow-x:auto; background:var(--bg-card); border-radius:var(--radius-md); border:1px solid var(--border); box-shadow:var(--shadow-sm); }
	table { width:100%; border-collapse:collapse; font-size:0.85rem; }
	th { text-align:left; padding:0.75rem 1rem; color:var(--text-muted); font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid var(--border); background:var(--bg-muted); }
	td { padding:0.65rem 1rem; border-bottom:1px solid var(--border-lighter); color:var(--text-primary); vertical-align:middle; }
	tr:last-child td { border-bottom:none; }
	.id-cell { font-family:monospace; font-weight:600; color:var(--primary); }
	.amount-cell { font-weight:700; color:var(--text-dark); }
	.method-tag { display:inline-block; padding:2px 8px; border-radius:var(--radius-sm); background:#f3f4f6; color:#374151; font-size:11px; font-weight:600; }
	.proof-link { color:var(--primary); font-weight:600; text-decoration:none; display:inline-flex; align-items:center; gap:4px; }
	.proof-link:hover { text-decoration:underline; }
	.upload-btn { display:inline-flex; align-items:center; gap:4px; padding:4px 10px; border:1px solid var(--primary); border-radius:var(--radius-sm); background:var(--bg-card); color:var(--primary); font-family:inherit; font-size:11px; font-weight:600; cursor:pointer; }
	.upload-btn:hover:not(:disabled) { background:var(--primary-bg); }
	.upload-btn:disabled { opacity:0.5; cursor:not-allowed; }
</style>
