<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import {
		getAgentTestDrives,
		assignAgentTestDrive,
		confirmAgentTestDrive,
		completeAgentTestDrive,
		cancelAgentTestDrive
	} from '$lib/services/api';
	import type { ServiceBooking } from '$lib/services/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { CarFront, LoaderCircle, Check, XCircle, UserPlus, CheckCircle } from '@lucide/svelte';
	import { formatSlotDateTime } from '$lib/utils/format';

	let bookings = $state<ServiceBooking[]>([]);
	let loading = $state(true);
	let activeTab = $state('upcoming');
	let actionLoading = $state<Record<number, string | null>>({});

	const now = new Date();
	const timestamp = now.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
		+ ' · ' + now.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });

	const tabs = [
		{ key: 'upcoming', label: 'Upcoming' },
		{ key: 'completed', label: 'Completed' },
		{ key: 'cancelled', label: 'Cancelled' },
	];

	let totalUpcoming = $derived(bookings.filter(b => b.status === 'pending' || b.status === 'confirmed').length);
	let assignedToMe = $derived(bookings.filter(b => b.assigned_to === auth.user?.user_id).length);

	onMount(() => fetchTestDrives());

	async function fetchTestDrives() {
		loading = true;
		try {
			const res = await getAgentTestDrives(activeTab);
			bookings = res.data as ServiceBooking[];
		} catch {
			bookings = [];
			toast.error('Failed to load test drives.');
		} finally {
			loading = false;
		}
	}

	function switchTab(tab: string) {
		activeTab = tab;
		fetchTestDrives();
	}

	function setAction(id: number, action: string | null) {
		actionLoading = { ...actionLoading, [id]: action };
	}

	async function handleAssign(id: number) {
		setAction(id, 'assign');
		try {
			await assignAgentTestDrive(id);
			toast.success(`Test drive #${id} assigned to you`);
			await fetchTestDrives();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to assign.');
		} finally {
			setAction(id, null);
		}
	}

	async function handleConfirm(id: number) {
		setAction(id, 'confirm');
		try {
			await confirmAgentTestDrive(id);
			toast.success(`Test drive #${id} confirmed`);
			await fetchTestDrives();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to confirm.');
		} finally {
			setAction(id, null);
		}
	}

	async function handleComplete(id: number) {
		setAction(id, 'complete');
		try {
			await completeAgentTestDrive(id);
			toast.success(`Test drive #${id} completed`);
			await fetchTestDrives();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to complete.');
		} finally {
			setAction(id, null);
		}
	}

	async function handleCancel(id: number) {
		setAction(id, 'cancel');
		try {
			await cancelAgentTestDrive(id);
			toast.success(`Test drive #${id} cancelled`);
			await fetchTestDrives();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to cancel.');
		} finally {
			setAction(id, null);
		}
	}

	function statusClass(status: string): string {
		const m: Record<string, string> = {
			pending: 's-pending',
			confirmed: 's-progress',
			completed: 's-done',
			cancelled: 's-cancelled'
		};
		return m[status] ?? 's-default';
	}

	function isAssignedToMe(booking: ServiceBooking): boolean {
		return booking.assigned_to === auth.user?.user_id;
	}

	function isActionLoading(id: number, action: string): boolean {
		return actionLoading[id] === action;
	}
</script>

<div class="page">

	<div class="top-bar">
		<div class="title-row">
			<h1>Test Drives</h1>
			<p class="subtitle">Manage and attend to customer test drive bookings.</p>
		</div>
		<span class="timestamp">{timestamp}</span>
	</div>

	{#if loading}
		<div class="loading-state"><span class="spinner"></span><p>Loading test drives…</p></div>
	{:else}

		<div class="stats-row">
			<div class="sc s1">
				<CarFront size={20} />
				<div><span class="sc-val">{totalUpcoming}</span><span class="sc-lbl">Upcoming</span></div>
			</div>
			<div class="sc s2">
				<UserPlus size={20} />
				<div><span class="sc-val">{assignedToMe}</span><span class="sc-lbl">Assigned to Me</span></div>
			</div>
		</div>

		<div class="toolbar">
			<div class="pills">
				{#each tabs as tab}
					<button class="pill" class:active={activeTab === tab.key} onclick={() => switchTab(tab.key)}>
						{tab.label}
					</button>
				{/each}
			</div>
		</div>

		<div class="card">
			<table>
				<thead>
					<tr>
						<th>#</th>
						<th>Date & Time</th>
						<th>Customer</th>
						<th>Vehicle</th>
						<th>Status</th>
						<th>Assigned To</th>
						<th class="cell-actions">Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each bookings as booking (booking.booking_id)}
						<tr>
							<td class="cell-id">{booking.booking_id}</td>
							<td>{formatSlotDateTime(booking.slot_datetime)}</td>
							<td class="cell-customer">{booking.customer_name}</td>
							<td>{booking.brand} {booking.model} {booking.year}</td>
							<td>
								<span class="status-badge {statusClass(booking.status)}">
									<span class="sdot"></span>
									{booking.status.replace(/_/g, ' ')}
								</span>
							</td>
							<td>
								{#if booking.assigned_to}
									<span class="assigned-badge" class:is-me={isAssignedToMe(booking)}>
										{isAssignedToMe(booking) ? 'You' : booking.assigned_to_name}
									</span>
								{:else}
									<span class="unassigned">Unassigned</span>
								{/if}
							</td>
							<td class="cell-actions">
								{#if activeTab === 'upcoming'}
									{#if !booking.assigned_to}
										<button
											class="action-btn assign"
											onclick={() => handleAssign(booking.booking_id)}
											disabled={isActionLoading(booking.booking_id, 'assign')}
											title="Assign to me"
										>
											{isActionLoading(booking.booking_id, 'assign') ? '…' : 'Assign to Me'}
										</button>
									{:else if isAssignedToMe(booking)}
										{#if booking.status === 'pending'}
											<button
												class="action-btn confirm"
												onclick={() => handleConfirm(booking.booking_id)}
												disabled={isActionLoading(booking.booking_id, 'confirm')}
												title="Confirm"
											>
												<CheckCircle size={13} />
												{isActionLoading(booking.booking_id, 'confirm') ? '…' : 'Confirm'}
											</button>
										{/if}
										{#if booking.status === 'confirmed'}
											<button
												class="action-btn complete"
												onclick={() => handleComplete(booking.booking_id)}
												disabled={isActionLoading(booking.booking_id, 'complete')}
												title="Complete"
											>
												<Check size={13} />
												{isActionLoading(booking.booking_id, 'complete') ? '…' : 'Complete'}
											</button>
										{/if}
										{#if booking.status === 'pending' || booking.status === 'confirmed'}
											<button
												class="action-btn danger"
												onclick={() => handleCancel(booking.booking_id)}
												disabled={isActionLoading(booking.booking_id, 'cancel')}
												title="Cancel"
											>
												<XCircle size={13} />
												{isActionLoading(booking.booking_id, 'cancel') ? '…' : 'Cancel'}
											</button>
										{/if}
									{:else}
										<span class="assigned-other">Assigned to {booking.assigned_to_name}</span>
									{/if}
								{:else}
									<span class="no-actions">—</span>
								{/if}
							</td>
						</tr>
					{:else}
						<tr>
							<td colspan="7" class="empty-state">
								{activeTab === 'upcoming' ? 'No upcoming test drives.' : activeTab === 'completed' ? 'No completed test drives.' : 'No cancelled test drives.'}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<style>
	.page { font-family: var(--font-sans); padding: 2rem; max-width: 1500px; margin: 0 auto; }

	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; flex-direction: column; align-items: start; gap: 10px; }
	.subtitle { font-size: 14px; color: var(--text-muted); margin-top: 4px; }
	h1 { font-size: 20px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; margin: 0; }
	.timestamp { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); background: var(--bg-muted); border: 0.5px solid var(--border); padding: 4px 12px; border-radius: 20px; }

	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }

	.stats-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 1.25rem; }
	.sc { background: var(--bg-stat); border-radius: 12px; padding: .9rem 1.1rem; display: flex; align-items: center; gap: 12px; position: relative; overflow: hidden; transition: transform .18s; }
	.sc:hover { transform: translateY(-2px); }
	.sc::before { content: ''; position: absolute; top: -10px; right: -10px; width: 56px; height: 56px; border-radius: 50%; opacity: .12; }
	.sc.s1::before { background: var(--accent); } .sc.s2::before { background: var(--primary-light); }
	.sc.s1 svg { color: var(--accent-dark); } .sc.s2 svg { color: var(--primary-dark); }
	.sc div { display: flex; flex-direction: column; }
	.sc-val { font-size: 26px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; line-height: 1; }
	.sc-lbl { font-size: 10px; font-weight: 500; color: var(--text-muted); letter-spacing: .6px; text-transform: uppercase; margin-top: 3px; }

	.toolbar { display: flex; align-items: center; gap: 16px; margin-bottom: 1rem; flex-wrap: wrap; }
	.pills { display: flex; gap: 4px; flex-wrap: wrap; }
	.pill { font-size: 11px; padding: 4px 12px; border-radius: 20px; border: 0.5px solid var(--border); background: var(--bg-card); color: var(--text-light); cursor: pointer; transition: all .15s; font-weight: 500; }
	.pill:hover { background: var(--bg-hover); }
	.pill.active { background: var(--primary); color: var(--accent); border-color: var(--primary); }

	.card { background: var(--bg-card); border: 0.5px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; }
	table { width: 100%; border-collapse: collapse; }
	th { padding: 9px 1rem; text-align: left; font-size: 10px; font-weight: 600; color: var(--text-muted); letter-spacing: .6px; text-transform: uppercase; background: var(--bg-canvas); border-bottom: .5px solid var(--chart-grid); }
	td { padding: 10px 1rem; font-size: 12px; color: var(--text-light); border-top: .5px solid var(--border-lighter); vertical-align: middle; }
	tr:hover td { background: var(--bg-canvas); }
	.cell-id { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); width: 50px; }
	.cell-customer { font-weight: 600; color: var(--text-primary); }
	.cell-actions { text-align: right; width: 200px; }
	.cell-actions th { text-align: right; }
	.empty-state { padding: 2rem; text-align: center; color: var(--text-muted); font-size: 13px; }

	.status-badge { display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 20px; font-size: 10px; font-weight: 600; }
	.sdot { width: 5px; height: 5px; border-radius: 50%; }
	.s-pending { background: var(--warning-bg); color: var(--warning-text); }
	.s-pending .sdot { background: var(--warning-dark); }
	.s-progress { background: var(--info-bg); color: var(--info-text); }
	.s-progress .sdot { background: var(--info); }
	.s-done { background: var(--success-bg); color: var(--success-text); }
	.s-done .sdot { background: var(--success-dark); }
	.s-cancelled { background: var(--danger-bg); color: var(--danger-text); }
	.s-cancelled .sdot { background: var(--danger); }
	.s-default { background: var(--bg-hover); color: var(--text-light); }
	.s-default .sdot { background: #888; }

	.assigned-badge { font-size: 11px; padding: 2px 8px; border-radius: 6px; background: var(--bg-hover); color: var(--text-light); }
	.assigned-badge.is-me { background: var(--info-bg); color: var(--info-text); font-weight: 600; }
	.unassigned { font-size: 11px; color: var(--text-muted); font-style: italic; }
	.assigned-other { font-size: 10px; color: var(--text-muted); }
	.no-actions { color: var(--text-muted); font-size: 11px; }

	.action-btn { display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 6px; border: 0.5px solid var(--border); background: var(--bg-card); color: var(--text-light); font-size: 11px; font-weight: 500; cursor: pointer; transition: all .15s; white-space: nowrap; }
	.action-btn:hover { background: var(--bg-hover); }
	.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
	.action-btn.assign { background: var(--primary); color: var(--accent); border-color: var(--primary); font-weight: 600; }
	.action-btn.assign:hover { opacity: 0.85; }
	.action-btn.confirm { background: var(--info-bg); color: var(--info-text); border-color: var(--info); }
	.action-btn.confirm:hover { opacity: 0.85; }
	.action-btn.complete { background: var(--success-bg); color: var(--success-text); border-color: var(--success); }
	.action-btn.complete:hover { opacity: 0.85; }
	.action-btn.danger { background: var(--danger-bg); color: var(--danger-text); border-color: var(--danger); }
	.action-btn.danger:hover { opacity: 0.85; }

	@media (max-width: 680px) {
		.stats-row { grid-template-columns: 1fr; }
	}
</style>
