<script lang="ts">
	import { onMount } from 'svelte';
	import { getCustomerDashboard, type CustomerDashboardResponse } from '$lib/services/api';
	import { Car, MessageSquareText, Bell, Wallet, Calendar, TrendingUp, FileText, CreditCard } from '@lucide/svelte';
	import Loader from '$lib/components/Loader.svelte';

	let data = $state<CustomerDashboardResponse['data'] | null>(null);
	let loading = $state(true);

	onMount(async () => {
		try {
			const res = await getCustomerDashboard();
			data = res.data;
		} catch {
			// offline / error
		} finally {
			loading = false;
		}
	});
</script>

<div class="page-header">
	<h1>Dashboard</h1>
	<p class="subtitle">Welcome back! Here's your overview.</p>
</div>

{#if loading}
	<div class="loader"><Loader /></div>
{:else if data}
	<div class="metrics">
		<div class="metric-card">
			<div class="metric-icon vehicles"><Car size={22} /></div>
			<div class="metric-value">{data.dashboard.my_vehicles?.length ?? 0}</div>
			<div class="metric-label">My Vehicles</div>
		</div>
		<div class="metric-card">
			<div class="metric-icon sales"><TrendingUp size={22} /></div>
			<div class="metric-value">{data.dashboard.active_sales}</div>
			<div class="metric-label">Active Sales</div>
		</div>
		<div class="metric-card">
			<div class="metric-icon inquiries"><MessageSquareText size={22} /></div>
			<div class="metric-value">{data.dashboard.open_inquiries}</div>
			<div class="metric-label">Open Inquiries</div>
		</div>
		<div class="metric-card">
			<div class="metric-icon notifications"><Bell size={22} /></div>
			<div class="metric-value">{data.dashboard.unread_notification}</div>
			<div class="metric-label">Notifications</div>
		</div>
	</div>

	<div class="dashboard-grid">
		<div class="card">
			<div class="card-header">
				<h2><Wallet size={16} /> Payment Overview</h2>
			</div>
			<div class="card-body">
				{#if data.dashboard.next_payment_due}
					<div class="payment-overview">
						<div class="payment-row">
							<span class="label">Next Payment Due</span>
							<span class="value">₱{Number(data.dashboard.next_payment_amount).toLocaleString()}</span>
						</div>
						<div class="payment-row">
							<span class="label">Due Date</span>
							<span class="value"><Calendar size={14} /> {data.dashboard.next_payment_due}</span>
						</div>
					</div>
				{:else}
					<p class="empty-msg">No upcoming payments.</p>
				{/if}
			</div>
		</div>

		<div class="card">
			<div class="card-header">
				<h2><Car size={16} /> My Vehicles</h2>
			</div>
			<div class="card-body">
				{#if data.dashboard.my_vehicles?.length > 0}
					<div class="vehicle-list">
						{#each data.dashboard.my_vehicles as v}
							<div class="vehicle-row">
								<div class="vehicle-icon-sm"><Car size={16} /></div>
								<div class="vehicle-info">
									<strong>{v.brand ?? '—'} {v.model ?? '—'}</strong>
									<span class="vehicle-sub">{v.year ?? ''} • {v.color ?? ''}</span>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<p class="empty-msg">No vehicles yet.</p>
				{/if}
			</div>
		</div>

		<div class="card full-width">
			<div class="card-header">
				<h2><FileText size={16} /> Recent Documents</h2>
			</div>
			<div class="card-body">
				{#if data.dashboard.recent_documents?.length > 0}
					<table class="mini-table">
						<thead>
							<tr><th>Document</th><th>Date</th></tr>
						</thead>
						<tbody>
							{#each data.dashboard.recent_documents as d}
								<tr>
									<td><FileText size={14} class="doc-icon" /> {d.document_name ?? d.name ?? `#${d.document_id ?? d.id}`}</td>
									<td>{d.created_at ? String(d.created_at).slice(0, 10) : '—'}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				{:else}
					<p class="empty-msg">No documents yet.</p>
				{/if}
			</div>
		</div>

		<div class="card full-width">
			<div class="card-header">
				<h2><Bell size={16} /> Recent Notifications</h2>
			</div>
			<div class="card-body">
				{#if data.notifications?.length > 0}
					<div class="notif-list">
						{#each data.notifications.slice(0, 5) as n}
							<div class="notif-item">
								<span class="notif-dot" class:unread={!n.is_read}></span>
								<div class="notif-content">
									<div class="notif-title">{n.title}</div>
									<div class="notif-msg">{n.message}</div>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<p class="empty-msg">No notifications.</p>
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
	.page-header { margin-bottom:24px; }
	h1 { font-size:24px; font-weight:700; color:var(--text-dark); margin:0; }
	.subtitle { font-size:14px; color:var(--text-muted); margin-top:4px; }
	.loader { display:grid; place-items:center; height:50vh; }
	.metrics { display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:14px; margin-bottom:24px; }
	.metric-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:18px 20px; display:flex; flex-direction:column; align-items:center; text-align:center; box-shadow:var(--shadow-sm); }
	.metric-icon { width:42px; height:42px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin-bottom:10px; }
	.metric-icon.vehicles { background:#dbeafe; color:#1d4ed8; }
	.metric-icon.sales { background:#d1fae5; color:#059669; }
	.metric-icon.inquiries { background:#fef3c7; color:#d97706; }
	.metric-icon.notifications { background:#fce7f3; color:#db2777; }
	.metric-value { font-size:28px; font-weight:700; color:var(--text-dark); }
	.metric-label { font-size:12px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-top:4px; }
	.dashboard-grid { display:grid; grid-template-columns:repeat(2, 1fr); gap:16px; }
	.card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); overflow:hidden; box-shadow:var(--shadow-sm); }
	.card.full-width { grid-column:1/-1; }
	.card-header { display:flex; align-items:center; gap:8px; padding:14px 20px; background:var(--bg-muted); border-bottom:1px solid var(--border); }
	.card-header h2 { font-size:14px; font-weight:700; margin:0; display:flex; align-items:center; gap:6px; color:var(--text-dark); }
	.card-body { padding:16px 20px; }
	.payment-overview { display:flex; flex-direction:column; gap:12px; }
	.payment-row { display:flex; justify-content:space-between; align-items:center; font-size:14px; }
	.payment-row .label { color:var(--text-muted); }
	.payment-row .value { font-weight:700; color:var(--text-dark); display:flex; align-items:center; gap:4px; }
	.empty-msg { color:var(--text-muted); font-size:13px; }
	.vehicle-list { display:flex; flex-direction:column; gap:10px; }
	.vehicle-row { display:flex; align-items:center; gap:12px; padding:10px; background:var(--bg-hover); border-radius:var(--radius-sm); }
	.vehicle-icon-sm { width:36px; height:36px; background:var(--primary-bg); border-radius:50%; display:flex; align-items:center; justify-content:center; color:var(--primary); flex-shrink:0; }
	.vehicle-info { display:flex; flex-direction:column; }
	.vehicle-info strong { font-size:13px; color:var(--text-dark); }
	.vehicle-sub { font-size:11px; color:var(--text-muted); }
	.mini-table { width:100%; border-collapse:collapse; font-size:13px; }
	.mini-table th { text-align:left; padding:8px; color:var(--text-muted); font-weight:600; font-size:11px; text-transform:uppercase; border-bottom:1px solid var(--border); }
	.mini-table td { padding:8px; border-bottom:1px solid var(--border-lighter); color:var(--text-primary); }
	.mini-table tr:last-child td { border-bottom:none; }
	.doc-icon { color:var(--primary); display:inline; margin-right:4px; vertical-align:middle; }
	.notif-list { display:flex; flex-direction:column; gap:8px; }
	.notif-item { display:flex; align-items:flex-start; gap:10px; padding:10px; background:var(--bg-hover); border-radius:var(--radius-sm); }
	.notif-dot { width:8px; height:8px; border-radius:50%; background:#d1d5db; flex-shrink:0; margin-top:4px; }
	.notif-dot.unread { background:var(--blue, #3b82f6); }
	.notif-content { flex:1; }
	.notif-title { font-size:13px; font-weight:600; color:var(--text-dark); }
	.notif-msg { font-size:12px; color:var(--text-muted); margin-top:2px; }
</style>
