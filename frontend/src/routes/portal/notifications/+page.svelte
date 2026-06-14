<script lang="ts">
	import { onMount } from 'svelte';
	import { getAllNotifications, markNotificationRead } from '$lib/services/api';
	import { toast } from 'svelte-sonner';
	import { Bell, CreditCard, Wrench, Info, Megaphone, CheckCheck } from '@lucide/svelte';
	import type { NotificationItem } from '$lib/services/api';

	let notifications = $state<NotificationItem[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			const res = await getAllNotifications();
			notifications = res.data;
		} catch {
			toast.error('Failed to load notifications.');
			notifications = [];
		} finally {
			loading = false;
		}
	});

	async function handleMarkRead(n: NotificationItem) {
		if (n.is_read) return;
		try {
			await markNotificationRead(n.id);
			n.is_read = true;
		} catch {
			// ignore
		}
	}

	async function markAllRead() {
		const unread = notifications.filter(n => !n.is_read);
		await Promise.all(unread.map(n => markNotificationRead(n.id).then(() => n.is_read = true).catch(() => {})));
	}

	function formatDate(iso: string) {
		return new Date(iso).toLocaleDateString('en-US', {
			year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
		});
	}

	function notifIcon(title: string) {
		const t = title?.toLowerCase() ?? '';
		if (t.includes('payment') || t.includes('pay')) return CreditCard;
		if (t.includes('service') || t.includes('repair')) return Wrench;
		if (t.includes('inquiry') || t.includes('message')) return Megaphone;
		return Info;
	}
</script>

<div class="page-header">
	<div>
		<h1>Notifications</h1>
		<p class="subtitle">Stay updated with your latest activities.</p>
	</div>
	{#if notifications.some(n => !n.is_read)}
		<button class="btn-mark-all" onclick={markAllRead}>
			<CheckCheck size={16} /> Mark All Read
		</button>
	{/if}
</div>

{#if loading}
	<p class="loading">Loading…</p>
{:else if notifications.length === 0}
	<div class="empty">
		<Bell size={48} />
		<p>No notifications yet.</p>
	</div>
{:else}
	<div class="list">
		{#each notifications as n}
			<button class="item" class:unread={!n.is_read} onclick={() => handleMarkRead(n)}>
				<div class="icon-wrap">
					<svelte:component this={notifIcon(n.title)} size={20} />
				</div>
				<div class="body">
					<div class="title">{n.title}</div>
					<div class="msg">{n.message}</div>
					<div class="time">{formatDate(n.created_at)}</div>
				</div>
				{#if !n.is_read}
					<span class="tag">New</span>
				{/if}
			</button>
		{/each}
	</div>
{/if}

<style>
	.page-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:24px; }
	h1 { font-size:24px; font-weight:700; margin:0; color:var(--text-dark); }
	.subtitle { font-size:14px; color:var(--text-muted); margin-top:4px; }
	.btn-mark-all { display:inline-flex; align-items:center; gap:6px; padding:8px 14px; border:1px solid var(--border); border-radius:var(--radius-md); background:var(--bg-card); color:var(--text-dark); font-family:inherit; font-size:12px; font-weight:600; cursor:pointer; }
	.btn-mark-all:hover { border-color:var(--primary); color:var(--primary); }
	.loading { text-align:center; padding:40px; color:var(--text-muted); }
	.empty { display:flex; flex-direction:column; align-items:center; gap:12px; padding:60px 20px; color:var(--text-muted); }
	.empty p { font-size:14px; margin:0; }
	.list { display:flex; flex-direction:column; gap:8px; }
	.item { display:flex; align-items:flex-start; gap:14px; padding:14px 16px; background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); text-align:left; width:100%; font-family:inherit; font-size:inherit; cursor:pointer; transition:box-shadow 0.15s; }
	.item:hover { box-shadow:0 2px 8px rgba(0,0,0,0.06); }
	.item.unread { background:var(--blue-bg, #eff6ff); border-color:#bfdbfe; }
	.icon-wrap { width:38px; height:38px; border-radius:50%; background:var(--bg-muted); display:flex; align-items:center; justify-content:center; color:var(--primary); flex-shrink:0; }
	.item.unread .icon-wrap { background:var(--primary-bg); }
	.body { flex:1; min-width:0; }
	.title { font-size:14px; font-weight:600; color:var(--text-dark); }
	.msg { font-size:13px; color:var(--text-light); margin-top:2px; line-height:1.4; }
	.time { font-size:11px; color:var(--text-muted); margin-top:4px; }
	.tag { font-size:10px; font-weight:700; color:var(--text-white); background:var(--blue, #3b82f6); padding:2px 8px; border-radius:var(--radius-sm); flex-shrink:0; margin-top:2px; }
</style>
