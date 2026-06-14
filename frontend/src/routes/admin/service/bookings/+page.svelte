<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getServiceBookings, updateAdminBookingStatus, deleteServiceBooking } from '$lib/services/api';
	import type { ListResponse } from '$lib/services/api';
	import { Search, Wrench, CarFront, Warehouse, CheckCircle, XCircle, Trash2, X } from '@lucide/svelte';
	import { formatSlotDateTime } from '$lib/utils/format';

	type Booking = {
		booking_id: number;
		customer_id: number;
		slot_id: number;
		vehicle_id: number;
		booking_type: string;
		status: string;
		assigned_to: number | null;
		created_at: string;
		slot_datetime: string;
		slot_type: string;
		brand: string;
		model: string;
		year: number;
		customer_name: string;
		assigned_to_name: string | null;
	};

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<Booking[]>([]);

	let search = $state('');
	let activeFilter = $state<string>('all');

	let actionLoading = $state<Record<string, boolean>>({});

	let confirmModal = $state<{ action: string; id: number; label: string } | null>(null);

	const columns = [
		{ key: 'booking_id', label: 'ID' },
		{ key: 'customer_name', label: 'Customer' },
		{ key: 'vehicle', label: 'Vehicle' },
		{ key: 'slot_datetime', label: 'Slot' },
		{ key: 'booking_type', label: 'Type' },
		{ key: 'status', label: 'Status' },
		{ key: 'assigned_to_name', label: 'Assigned To' },
		{ key: 'actions', label: 'Actions' },
	];

	let stats = $derived({
		total: rows.length,
		test_drive: rows.filter((r) => r.booking_type === 'test_drive').length,
		maintenance: rows.filter((r) => r.booking_type === 'maintenance').length,
		repair: rows.filter((r) => r.booking_type === 'repair').length,
	});

	let filteredRows = $derived(
		rows.filter((r) => {
			const matchType = activeFilter === 'all' || r.booking_type === activeFilter;
			const s = search.toLowerCase();
			const matchSearch =
				!s ||
				String(r.customer_name ?? '').toLowerCase().includes(s) ||
				String(r.brand ?? '').toLowerCase().includes(s) ||
				String(r.model ?? '').toLowerCase().includes(s) ||
				String(r.booking_id).includes(s);
			return matchType && matchSearch;
		})
	);

	const FILTERS = ['all', 'test_drive', 'maintenance', 'repair'] as const;

	const TYPE_LABELS: Record<string, string> = {
		test_drive: 'Test Drive',
		maintenance: 'Maintenance',
		repair: 'Repair',
	};

	function filterLabel(f: string): string {
		if (f === 'all') return 'All';
		return TYPE_LABELS[f] ?? f.charAt(0).toUpperCase() + f.slice(1);
	}

	function typeBadgeClass(type: string): string {
		switch (type) {
			case 'test_drive': return 'badge-test-drive';
			case 'maintenance': return 'badge-maintenance';
			case 'repair': return 'badge-repair';
			default: return 'badge-default';
		}
	}

	function statusBadgeClass(status: string): string {
		switch (status) {
			case 'pending': return 'badge-pending';
			case 'confirmed': return 'badge-confirmed';
			case 'completed': return 'badge-completed';
			case 'cancelled': return 'badge-cancelled';
			default: return 'badge-default';
		}
	}

	async function loadBookings() {
		loading = true;
		error = null;
		try {
			const res = await getServiceBookings();
			rows = (res.data ?? []) as Booking[];
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function handleStatusAction(id: number, status: string) {
		const key = `status-${id}`;
		actionLoading[key] = true;
		try {
			await updateAdminBookingStatus(id, status);
			toast.success(`Booking #${id} ${status}.`);
			await loadBookings();
		} catch (e) {
			toast.error((e as Error).message || `Failed to ${status} booking.`);
		} finally {
			actionLoading[key] = false;
		}
	}

	async function handleDelete(id: number) {
		const key = `delete-${id}`;
		actionLoading[key] = true;
		try {
			await deleteServiceBooking(id);
			toast.success(`Booking #${id} deleted.`);
			confirmModal = null;
			await loadBookings();
		} catch (e) {
			toast.error((e as Error).message || 'Failed to delete booking.');
		} finally {
			actionLoading[key] = false;
		}
	}

	function openConfirm(action: string, id: number, label: string) {
		confirmModal = { action, id, label };
	}

	onMount(loadBookings);
</script>

<div class="page">
	<!-- Top bar -->
	<div class="top-bar">
		<div class="title-row">
			<div>
				<h1>Service Bookings</h1>
				<p class="title-subtitle">Manage test drive, maintenance, and repair bookings</p>
			</div>
		</div>
		<div class="toolbar">
			<div class="search-wrap">
				<Search class="search-icon" size={14} />
				<input
					type="text"
					class="search-input"
					placeholder="Search by customer, vehicle, ID…"
					bind:value={search}
				/>
			</div>
		</div>
	</div>

	<!-- Stats row -->
	<div class="stats-row">
		<div class="mini-stat s-total">
			<Wrench size={18} />
			<div>
				<span class="mini-val">{stats.total}</span>
				<span class="mini-lbl">Total</span>
			</div>
		</div>
		<div class="mini-stat s-test-drive">
			<CarFront size={18} />
			<div>
				<span class="mini-val">{stats.test_drive}</span>
				<span class="mini-lbl">Test Drive</span>
			</div>
		</div>
		<div class="mini-stat s-maintenance">
			<Warehouse size={18} />
			<div>
				<span class="mini-val">{stats.maintenance}</span>
				<span class="mini-lbl">Maintenance</span>
			</div>
		</div>
		<div class="mini-stat s-repair">
			<Wrench size={18} />
			<div>
				<span class="mini-val">{stats.repair}</span>
				<span class="mini-lbl">Repair</span>
			</div>
		</div>
	</div>

	<!-- Filter pills -->
	<div class="filter-row">
		{#each FILTERS as f}
			<button
				class="filter-btn"
				class:active={activeFilter === f}
				onclick={() => (activeFilter = f)}
			>
				{filterLabel(f)}
			</button>
		{/each}
	</div>

	<!-- Loading / Error / Empty / Table -->
	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading bookings…</span>
		</div>
	{:else if error}
		<div class="error-msg">{error}</div>
	{:else if filteredRows.length === 0}
		<div class="empty-state">No bookings found.</div>
	{:else}
		<DataTable columns={columns}>
			{#each filteredRows as row (row.booking_id)}
				<tr>
					<td><span class="cell-id">#{row.booking_id}</span></td>
					<td class="cell-name">{row.customer_name}</td>
					<td class="cell-vehicle">{row.brand} {row.model} ({row.year})</td>
					<td class="cell-slot">{formatSlotDateTime(row.slot_datetime)}</td>
					<td>
						<span class="badge {typeBadgeClass(row.booking_type)}">{TYPE_LABELS[row.booking_type] ?? row.booking_type}</span>
					</td>
					<td>
						<span class="badge {statusBadgeClass(row.status)}">{row.status}</span>
					</td>
					<td class="cell-assigned">
						{#if row.assigned_to_name}
							{row.assigned_to_name}
						{:else}
							<span class="unassigned">Unassigned</span>
						{/if}
					</td>
					<td class="cell-actions">
						{#if row.status === 'pending'}
							<button
								class="act-btn act-confirm"
								disabled={actionLoading[`status-${row.booking_id}`]}
								onclick={() => handleStatusAction(row.booking_id, 'confirmed')}
							>
								{#if actionLoading[`status-${row.booking_id}`]}
									<div class="spinner-sm"></div>
								{/if}
								Confirm
							</button>
							<button
								class="act-btn act-cancel"
								disabled={actionLoading[`status-${row.booking_id}`]}
								onclick={() => openConfirm('cancel', row.booking_id, `Cancel booking #${row.booking_id}?`)}
							>
								Cancel
							</button>
						{:else if row.status === 'confirmed'}
							<button
								class="act-btn act-complete"
								disabled={actionLoading[`status-${row.booking_id}`]}
								onclick={() => handleStatusAction(row.booking_id, 'completed')}
							>
								{#if actionLoading[`status-${row.booking_id}`]}
									<div class="spinner-sm"></div>
								{/if}
								Complete
							</button>
							<button
								class="act-btn act-cancel"
								disabled={actionLoading[`status-${row.booking_id}`]}
								onclick={() => openConfirm('cancel', row.booking_id, `Cancel booking #${row.booking_id}?`)}
							>
								Cancel
							</button>
						{/if}
						<button
							class="act-btn act-delete"
							disabled={actionLoading[`delete-${row.booking_id}`]}
							onclick={() => openConfirm('delete', row.booking_id, `Delete booking #${row.booking_id}?`)}
						>
							{#if actionLoading[`delete-${row.booking_id}`]}
								<div class="spinner-sm"></div>
							{:else}
								<Trash2 size={12} />
							{/if}
						</button>
					</td>
				</tr>
			{/each}
		</DataTable>
	{/if}
</div>

<!-- Confirmation modal -->
{#if confirmModal}
	<div class="modal-overlay" onclick={() => (confirmModal = null)}>
		<div class="modal-box" onclick={(e) => e.stopPropagation()}>
			<button class="modal-close" onclick={() => (confirmModal = null)}>
				<X size={16} />
			</button>
			<p class="modal-text">{confirmModal.label}</p>
			<div class="modal-actions">
				<button class="modal-btn modal-btn-secondary" onclick={() => (confirmModal = null)}>
					Keep
				</button>
				<button
					class="modal-btn modal-btn-danger"
					onclick={() => {
						if (confirmModal.action === 'delete') {
							handleDelete(confirmModal.id);
						} else if (confirmModal.action === 'cancel') {
							handleStatusAction(confirmModal.id, 'cancelled');
						}
					}}
				>
					{confirmModal.action === 'delete' ? 'Delete' : 'Cancel Booking'}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

	.page { font-family: 'Syne', sans-serif; padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

	/* Top bar */
	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; align-items: center; gap: 10px; }
	.title-subtitle { font-size: 13px; color: #9ca3af; margin: 2px 0 0; font-weight: 400; }
	h1 { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; margin: 0; }
	.toolbar { display: flex; align-items: center; gap: 10px; }
	.search-wrap { position: relative; }
	.search-wrap :global(.search-icon) { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; pointer-events: none; }
	.search-input { height: 34px; padding: 0 12px 0 32px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; color: #1a1a2e; background: #f9fafb; outline: none; width: 220px; }
	.search-input:focus { border-color: #7c9df7; background: #fff; }

	/* Mini stats */
	.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 1.25rem; }
	.mini-stat { background: #f8f7f4; border-radius: 10px; padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
	.s-total :global(svg) { color: #1a1a2e; flex-shrink: 0; }
	.s-test-drive :global(svg) { color: #4f46e5; flex-shrink: 0; }
	.s-maintenance :global(svg) { color: #b45309; flex-shrink: 0; }
	.s-repair :global(svg) { color: #059669; flex-shrink: 0; }
	.mini-stat div { display: flex; flex-direction: column; }
	.mini-val { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; line-height: 1; }
	.mini-lbl { font-size: 10px; font-weight: 500; color: #9ca3af; letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

	/* Filter pills */
	.filter-row { display: flex; gap: 6px; margin-bottom: 1rem; flex-wrap: wrap; }
	.filter-btn { height: 28px; padding: 0 12px; border: 0.5px solid #e5e7eb; border-radius: 20px; background: #f9fafb; font-family: 'Syne', sans-serif; font-size: 11px; color: #6b7280; cursor: pointer; transition: .15s; }
	.filter-btn.active { background: #1a1a2e; color: #e8c97e; border-color: #1a1a2e; }

	/* Loading & Error */
	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: #9ca3af; font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid #e5e7eb; border-top-color: #1a1a2e; border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.spinner-sm { width: 12px; height: 12px; border: 1.5px solid currentColor; border-top-color: transparent; border-radius: 50%; animation: spin .7s linear infinite; display: inline-block; vertical-align: middle; }
	.error-msg { color: #A32D2D; font-size: 13px; padding: 1rem; background: #FCEBEB; border-radius: 8px; margin-bottom: 1rem; }
	.empty-state { text-align: center; padding: 2.5rem; color: #9ca3af; font-size: 13px; }

	/* Table cells */
	.cell-id { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #7c9df7; }
	.cell-name { font-size: 13px; font-weight: 600; color: #1a1a2e; white-space: nowrap; }
	.cell-vehicle { font-size: 12px; color: #374151; white-space: nowrap; }
	.cell-slot { font-size: 12px; color: #6b7280; white-space: nowrap; }
	.cell-assigned { font-size: 12px; color: #374151; }
	.cell-actions { display: flex; gap: 4px; align-items: center; flex-wrap: nowrap; }

	.unassigned { font-style: italic; color: #9ca3af; }

	/* Badges */
	.badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
	.badge-test-drive { background: #eef2ff; color: #4f46e5; }
	.badge-maintenance { background: #fef3c7; color: #b45309; }
	.badge-repair { background: #ecfdf5; color: #059669; }
	.badge-default { background: #f3f4f6; color: #6b7280; }
	.badge-pending { background: #fef3c7; color: #b45309; }
	.badge-confirmed { background: #dbeafe; color: #2563eb; }
	.badge-completed { background: #ecfdf5; color: #059669; }
	.badge-cancelled { background: #fcebeb; color: #dc2626; }

	/* Action buttons */
	.act-btn { display: inline-flex; align-items: center; gap: 4px; height: 26px; padding: 0 10px; border: 0.5px solid #e5e7eb; border-radius: 6px; font-family: 'Syne', sans-serif; font-size: 10px; font-weight: 600; cursor: pointer; transition: .15s; background: #fff; color: #374151; letter-spacing: 0.2px; }
	.act-btn:disabled { opacity: 0.5; cursor: not-allowed; }
	.act-confirm { background: #1a1a2e; color: #e8c97e; border-color: #1a1a2e; }
	.act-confirm:hover:not(:disabled) { opacity: 0.85; }
	.act-complete { background: #059669; color: #fff; border-color: #059669; }
	.act-complete:hover:not(:disabled) { opacity: 0.85; }
	.act-cancel { color: #dc2626; border-color: #fca5a5; }
	.act-cancel:hover:not(:disabled) { background: #fef2f2; }
	.act-delete { color: #6b7280; border-color: #e5e7eb; padding: 0 6px; }
	.act-delete:hover:not(:disabled) { color: #dc2626; border-color: #fca5a5; background: #fef2f2; }

	/* Confirmation modal */
	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; z-index: 1000; }
	.modal-box { background: #fff; border-radius: 12px; padding: 1.5rem; max-width: 380px; width: 90%; position: relative; box-shadow: 0 8px 30px rgba(0,0,0,0.15); }
	.modal-close { position: absolute; top: 12px; right: 12px; background: none; border: none; cursor: pointer; color: #9ca3af; padding: 4px; }
	.modal-close:hover { color: #374151; }
	.modal-text { font-size: 14px; color: #1a1a2e; font-weight: 600; margin: 0 0 1.25rem; }
	.modal-actions { display: flex; gap: 8px; justify-content: flex-end; }
	.modal-btn { height: 34px; padding: 0 16px; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; cursor: pointer; transition: .15s; border: 0.5px solid #e5e7eb; }
	.modal-btn-secondary { background: #f9fafb; color: #374151; }
	.modal-btn-secondary:hover { background: #f3f4f6; }
	.modal-btn-danger { background: #dc2626; color: #fff; border-color: #dc2626; }
	.modal-btn-danger:hover { opacity: 0.85; }

	@media (max-width: 640px) {
		.stats-row { grid-template-columns: 1fr 1fr; }
		.top-bar { flex-direction: column; align-items: flex-start; }
	}
</style>
