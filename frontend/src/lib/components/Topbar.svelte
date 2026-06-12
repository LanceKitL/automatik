<script lang="ts">
	import { onMount } from 'svelte';
	import { Bell, LogOut, User } from '@lucide/svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { getRecentNotifications, markNotificationRead } from '$lib/services/api';
	import type { NotificationItem } from '$lib/services/api';
	import { goto } from '$app/navigation';

	let open = $state(false);
	let notifOpen = $state(false);
	let notifications = $state<NotificationItem[]>([]);
	let unreadCount = $derived(notifications.filter((n) => !n.is_read).length);

	onMount(() => {
		fetchNotifs();
	});

	function toggleDropdown() {
		open = !open;
		notifOpen = false;
	}

	function toggleNotif() {
		notifOpen = !notifOpen;
		open = false;
		if (notifOpen) fetchNotifs();
	}

	async function fetchNotifs() {
		try {
			const res = await getRecentNotifications();
			notifications = res.data;
		} catch {
			notifications = [];
		}
	}

	async function handleRead(n: NotificationItem) {
		if (!n.is_read) {
			await markNotificationRead(n.id);
			n.is_read = true;
		}
	}

	function goToNotifs() {
		notifOpen = false;
		goto('/portal/notifications');
	}

	function handleLogout() {
		auth.logout();
	}

	function formatTime(iso: string) {
		const d = new Date(iso);
		const now = new Date();
		const diff = now.getTime() - d.getTime();
		const mins = Math.floor(diff / 60000);
		if (mins < 1) return 'Just now';
		if (mins < 60) return `${mins}m ago`;
		const hrs = Math.floor(mins / 60);
		if (hrs < 24) return `${hrs}h ago`;
		const days = Math.floor(hrs / 24);
		return `${days}d ago`;
	}
</script>

<div class="topbar">
	<div class="spacer" />

	<div class="right">
		<!-- Notification bell -->
		<div class="notif-wrapper">
			<button class="icon-btn" onclick={toggleNotif}>
				<Bell size={20} />
				{#if unreadCount > 0}
					<span class="badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
				{/if}
			</button>

			{#if notifOpen}
				<div class="notif-dropdown">
					<div class="notif-header">
						<span class="notif-title">Notifications</span>
					</div>
					<div class="notif-list">
						{#if notifications.length === 0}
							<div class="empty">No notifications</div>
						{:else}
							{#each notifications as n}
								<button
									class="notif-item"
									class:unread={!n.is_read}
									onclick={() => handleRead(n)}
								>
									<div class="notif-dot" class:dot-read={n.is_read} />
									<div class="notif-body">
										<div class="notif-msg">{n.message}</div>
										<div class="notif-time">{formatTime(n.created_at)}</div>
									</div>
								</button>
							{/each}
						{/if}
					</div>
					<button class="see-all" onclick={goToNotifs}>See all notifications</button>
				</div>
			{/if}
		</div>

		<!-- User dropdown -->
		<div class="user-wrapper">
			<button class="user-btn" onclick={toggleDropdown}>
				<div class="avatar">
					{(auth.user?.username ?? auth.user?.email ?? '?').charAt(0).toUpperCase()}
				</div>
				<span class="user-name">{auth.user?.username ?? auth.user?.email?.split('@')[0] ?? 'User'}</span>
			</button>

			{#if open}
				<div class="user-dropdown">
					<div class="dropdown-info">
						<div class="dropdown-email">{auth.user?.email}</div>
						<div class="dropdown-role">{(auth.user?.role ?? '').replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</div>
					</div>
					<button class="dropdown-item" onclick={handleLogout}>
						<LogOut size={16} />
						Logout
					</button>
				</div>
			{/if}
		</div>
	</div>
</div>

{#if open || notifOpen}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="backdrop" onclick={() => { open = false; notifOpen = false; }} />
{/if}

<style>
	.topbar {
		display: flex;
		align-items: center;
		height: 56px;
		padding: 0 24px;
		background: var(--bg-card);
		border-bottom: 1px solid var(--border);
		position: sticky;
		top: 0;
		z-index: 55;
	}
	.spacer {
		flex: 1;
	}
	.right {
		display: flex;
		align-items: center;
		gap: 12px;
	}
	.icon-btn {
		position: relative;
		background: none;
		border: none;
		cursor: pointer;
		padding: 6px;
		border-radius: 8px;
		color: var(--text-light);
	}
	.icon-btn:hover {
		background: var(--bg-hover);
	}
	.badge {
		position: absolute;
		top: 0;
		right: 0;
		background: var(--red);
		color: var(--text-white);
		font-size: 10px;
		font-weight: 700;
		min-width: 16px;
		height: 16px;
		border-radius: 8px;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0 4px;
		line-height: 1;
	}
	.notif-wrapper, .user-wrapper {
		position: relative;
	}
	.notif-dropdown, .user-dropdown {
		position: absolute;
		right: 0;
		top: calc(100% + 6px);
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-lg);
		z-index: 60;
		min-width: 260px;
	}
	.notif-dropdown {
		width: 340px;
	}
	.notif-header {
		padding: 12px 14px;
		border-bottom: 1px solid var(--border-lighter);
	}
	.notif-title {
		font-weight: 600;
		font-size: 14px;
		color: var(--text-dark);
	}
	.notif-list {
		max-height: 320px;
		overflow-y: auto;
	}
	.notif-item {
		display: flex;
		gap: 10px;
		padding: 10px 14px;
		width: 100%;
		text-align: left;
		background: none;
		border: none;
		border-bottom: 1px solid var(--bg-hover-light);
		cursor: pointer;
		font-family: inherit;
		font-size: inherit;
	}
	.notif-item:hover {
		background: var(--bg-hover-light);
	}
	.notif-item.unread {
		background: var(--blue-bg);
	}
	.notif-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--primary);
		flex-shrink: 0;
		margin-top: 4px;
	}
	.notif-dot.dot-read {
		background: transparent;
	}
	.notif-body {
		flex: 1;
		min-width: 0;
	}
	.notif-msg {
		font-size: 13px;
		color: var(--text-light);
		line-height: 1.4;
		word-break: break-word;
	}
	.notif-time {
		font-size: 11px;
		color: var(--text-muted);
		margin-top: 2px;
	}
	.empty {
		padding: 24px;
		text-align: center;
		color: var(--text-muted);
		font-size: 13px;
	}
	.see-all {
		display: block;
		width: 100%;
		padding: 10px;
		text-align: center;
		font-size: 13px;
		color: var(--primary);
		font-weight: 500;
		background: none;
		border: none;
		border-top: 1px solid var(--border-lighter);
		cursor: pointer;
	}
	.see-all:hover {
		background: var(--bg-hover-light);
	}
	.user-btn {
		display: flex;
		align-items: center;
		gap: 8px;
		background: none;
		border: none;
		cursor: pointer;
		padding: 4px 8px;
		border-radius: 8px;
	}
	.user-btn:hover {
		background: var(--bg-hover);
	}
	.avatar {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background: var(--primary);
		color: var(--text-white);
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 600;
		font-size: 14px;
	}
	.user-name {
		font-size: 14px;
		font-weight: 500;
		color: var(--text-light);
	}
	.user-dropdown {
		min-width: 200px;
	}
	.dropdown-info {
		padding: 12px 14px;
		border-bottom: 1px solid var(--border-lighter);
	}
	.dropdown-email {
		font-size: 13px;
		color: var(--text-light);
		font-weight: 500;
	}
	.dropdown-role {
		font-size: 11px;
		color: var(--text-muted);
		margin-top: 2px;
		text-transform: capitalize;
	}
	.dropdown-item {
		display: flex;
		align-items: center;
		gap: 8px;
		width: 100%;
		padding: 10px 14px;
		background: none;
		border: none;
		cursor: pointer;
		font-size: 13px;
		color: var(--red);
		font-family: inherit;
	}
	.dropdown-item:hover {
		background: var(--red-bg);
	}
	.backdrop {
		position: fixed;
		inset: 0;
		z-index: 50;
	}
</style>
