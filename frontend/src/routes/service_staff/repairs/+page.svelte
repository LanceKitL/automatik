<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import {
		getServiceStaffBookings,
		assignAndOpenIntake,
		updateServiceBookingStatus,
		updateTechnicianNotes
	} from '$lib/services/api';
	import { goto } from '$app/navigation';
	import { formatSlotDateTime } from '$lib/utils/format';
	import { Wrench, X, Check, FileText, Pen, Search } from '@lucide/svelte';

	let bookings = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);
	let statusFilter = $state('all');
	let searchQuery = $state('');

	let editingNotes = $state<number | null>(null);
	let notesText = $state('');

	let cancellingId = $state<number | null>(null);

	onMount(loadData);

	async function loadData() {
		loading = true;
		try {
			const res = await getServiceStaffBookings('repair');
			bookings = res.data as Record<string, unknown>[];
		} catch {
			toast.error('Failed to load bookings.');
		} finally {
			loading = false;
		}
	}

	let displayBookings = $derived.by(() => {
		let list = bookings.filter(b => (b.slot_type as string) === 'repair' && b.status !== 'completed' && b.status !== 'cancelled');
		if (statusFilter !== 'all') list = list.filter(b => (b.status as string) === statusFilter);
		if (searchQuery) {
			const q = searchQuery.toLowerCase();
			list = list.filter(b =>
				String(b.booking_id).includes(q) ||
				String(b.customer_name ?? '').toLowerCase().includes(q) ||
				String(b.brand ?? '').toLowerCase().includes(q) ||
				String(b.model ?? '').toLowerCase().includes(q)
			);
		}
		return list;
	});

	let totalCount = $derived(bookings.length);
	let pendingCount = $derived(bookings.filter(b => b.status === 'pending').length);
	let inProgressCount = $derived(bookings.filter(b => b.status === 'in_progress' || b.status === 'awaiting_signature').length);

	const statuses = ['all', 'pending', 'confirmed', 'draft_estimate', 'awaiting_signature', 'in_progress'];

	function statusClass(status: string | null | undefined): string {
		if (!status) return 's-default';
		const s = status.toLowerCase();
		if (s === 'confirmed' || s === 'approved' || s === 'resolved') return 's-confirmed';
		if (s === 'pending' || s === 'submitted') return 's-pending';
		if (s === 'cancelled' || s === 'rejected') return 's-cancelled';
		if (s === 'under_review' || s === 'draft_estimate') return 's-review';
		if (s === 'in_progress' || s === 'awaiting_signature') return 's-progress';
		if (s === 'completed') return 's-completed';
		return 's-default';
	}

	function badgeClass(t: string | null | undefined): string {
		if (!t) return 'badge-default';
		const v = t.toLowerCase();
		if (v === 'repair') return 'badge-repair';
		if (v === 'maintenance') return 'badge-maintenance';
		if (v === 'test_drive') return 'badge-test-drive';
		return 'badge-default';
	}

	function formatId(id: number): string {
		return `BK-${String(id).padStart(4, '0')}`;
	}

	async function handleAssignAndOpenIntake(bookingId: number) {
		try {
			await assignAndOpenIntake(bookingId);
			toast.success('Intake opened!');
			await goto(`/service_staff/repairs/${bookingId}/intake`);
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to open intake.');
		}
	}

	async function handleStatus(bookingId: number, status: string) {
		try {
			await updateServiceBookingStatus(bookingId, status);
			toast.success(`Booking #${bookingId} ${status}.`);
			cancellingId = null;
			await loadData();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : `Failed to ${status} booking.`);
		}
	}

	function openNotes(id: number, current: string | null) {
		editingNotes = id;
		notesText = current ?? '';
	}

	async function saveNotes() {
		if (editingNotes === null) return;
		try {
			await updateTechnicianNotes(editingNotes, notesText);
			toast.success(`Notes saved for ${formatId(editingNotes)}.`);
			editingNotes = null;
			notesText = '';
			await loadData();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to save notes.');
		}
	}
</script>

<div class="dash">
	<div class="top-bar">
		<div class="logo-row">
			<h1>Repairs</h1>
			<p class="subtitle">Monitor and track customers repair booking.</p>
		</div>
	</div>

	<div class="toolbar">
		<div class="status-tabs">
			{#each statuses as s}
				<button class:active={statusFilter === s} onclick={() => statusFilter = s}>
					{s === 'all' ? 'All' : s.replace(/_/g, ' ')}
				</button>
			{/each}
		</div>
		<div class="search-wrap">
			<Search size={14} />
			<input bind:value={searchQuery} placeholder="Search ID, customer, vehicle…" />
		</div>
	</div>

	{#if loading}
		<div class="loading-state"><div class="spinner"></div><span>Loading repairs…</span></div>
	{:else if displayBookings.length === 0}
		<div class="empty-state">
			<Wrench size={32} />
			<p>No repair bookings found.</p>
		</div>
	{:else}
		<div class="table-wrap">
			<table class="data-table">
				<thead>
					<tr>
						<th>ID</th>
						<th>Customer & Vehicle</th>
						<th>Service</th>
						<th>Slot</th>
						<th>Status</th>
						<th>Assigned</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each displayBookings as b}
						<tr>
							<td class="id-cell">{formatId(b.booking_id as number)}</td>
							<td>
								{b.customer_name ?? '—'}<br>
								<small>{b.year ?? ''} {b.brand ?? ''} {b.model ?? ''}</small>
							</td>
							<td>
								<span class={badgeClass(b.slot_type as string ?? b.booking_type as string)}>
									{(b.slot_type as string ?? b.booking_type as string)?.replace(/_/g, ' ') ?? '—'}
								</span>
							</td>
							<td>{formatSlotDateTime(b.slot_datetime)}</td>
							<td><span class="status-badge {statusClass(b.status as string)}">{(b.status as string)?.replace(/_/g, ' ') ?? '—'}</span></td>
							<td>{b.assigned_to_name ?? '—'}</td>
							<td class="actions-cell">
								{#if b.assigned_to === null && (b.status === 'confirmed' || b.status === 'pending')}
									<button class="btn-sm btn-primary" onclick={() => handleAssignAndOpenIntake(b.booking_id as number)}>
										<FileText size={13} /> Intake
									</button>
								{/if}
								{#if b.status === 'confirmed' && b.assigned_to !== null}
									<a href="/service_staff/repairs/{b.booking_id}/intake" class="btn-sm btn-outline">
										<FileText size={13} /> Open
									</a>
								{/if}
								{#if b.status === 'draft_estimate' || b.status === 'awaiting_signature' || b.status === 'in_progress'}
									<a href="/service_staff/repairs/{b.booking_id}/intake" class="btn-sm btn-outline">
										<Pen size={13} /> Estimate
									</a>
								{/if}
								{#if b.status === 'in_progress' && b.assigned_to}
									<button class="btn-sm btn-success" onclick={() => handleStatus(b.booking_id as number, 'completed')}>
										<Check size={13} /> Complete
									</button>
								{/if}
								{#if b.status === 'pending' || b.status === 'confirmed' || b.status === 'draft_estimate' || b.status === 'awaiting_signature'}
									<button class="btn-sm btn-ghost-danger" onclick={() => cancellingId = b.booking_id as number}>
										<X size={13} />
									</button>
								{/if}
								<button class="btn-sm btn-ghost" onclick={() => openNotes(b.booking_id as number, b.technician_notes as string | null)}>
									<Pen size={13} />
								</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<!-- Cancel Confirmation Modal -->
{#if cancellingId !== null}
	<div class="modal-overlay" onclick={() => cancellingId = null}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h3><X size={18} /> Cancel Booking</h3>
				<button class="modal-close" onclick={() => cancellingId = null}>×</button>
			</div>
			<div class="modal-body">
				<p>Are you sure you want to cancel <strong>{formatId(cancellingId)}</strong>?</p>
				<p class="field-hint">This will free the service slot and notify the customer.</p>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" onclick={() => cancellingId = null}>Keep Booking</button>
				<button class="btn-danger" onclick={() => handleStatus(cancellingId, 'cancelled')}>Yes, Cancel Booking</button>
			</div>
		</div>
	</div>
{/if}

<!-- Notes Modal -->
{#if editingNotes !== null}
	<div class="modal-overlay" onclick={() => editingNotes = null}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h3><Pen size={18} /> Technician Notes — {formatId(editingNotes)}</h3>
				<button class="modal-close" onclick={() => editingNotes = null}>×</button>
			</div>
			<div class="modal-body">
				<textarea bind:value={notesText} rows="5" placeholder="Enter diagnosis notes, observations, or instructions…"></textarea>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" onclick={() => { editingNotes = null; notesText = ''; }}>Cancel</button>
				<button class="btn-primary" onclick={saveNotes}>Save Notes</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.dash { padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; font-family: var(--font-sans); }

	.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 40vh; gap: 1rem; color: var(--text-light); }
	.spinner { width: 28px; height: 28px; border: 2.5px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin 0.7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.empty-state { text-align: center; padding: 4rem 0; color: var(--text-muted); display: flex; flex-direction: column; align-items: center; gap: 8px; }

	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
	.logo-row { display: flex; flex-direction: column; align-items: start; justify-content: start; }
	.subtitle {
		font-size: 14px;
		color: var(--text-muted);
		margin-top: 4px;
	}
	h1 { font-size: 24px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; margin: 0; }
	.count-pill { font-size: 12px; background: var(--bg-muted); color: var(--text-muted); padding: 2px 10px; border-radius: 12px; font-weight: 600; }

	/* Stat Cards */
	.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 14px; margin-bottom: 1.25rem; }
	.stat-card { background: var(--bg-stat); border-radius: var(--radius-lg); padding: 1.25rem 1.4rem; position: relative; overflow: hidden; transition: transform 0.18s ease, box-shadow 0.18s ease; }
	.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.07); }
	.stat-card::before { content: ''; position: absolute; top: -12px; right: -12px; width: 70px; height: 70px; border-radius: 50%; opacity: 0.12; }
	.c-total::before { background: #6b7280; }
	.c-pending::before { background: #f59e0b; }
	.c-progress::before { background: #3b82f6; }
	.c-completed::before { background: #10b981; }
	.stat-value { font-size: 30px; font-weight: 700; color: var(--text-primary); letter-spacing: -1px; line-height: 1; margin-bottom: 6px; font-variant-numeric: tabular-nums; }
	.stat-label { font-size: 11px; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }

	/* Toolbar */
	.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 0.75rem; }
	.search-wrap { display: flex; align-items: center; gap: 6px; background: var(--bg-card); border: 0.5px solid var(--border); border-radius: var(--radius-sm); padding: 6px 10px; }
	.search-wrap input { border: none; background: none; outline: none; font-size: 12px; color: var(--text-primary); font-family: inherit; min-width: 160px; }
	.search-wrap svg { color: var(--text-muted); flex-shrink: 0; }

	/* Status filter tabs */
	.status-tabs { display: flex; gap: 4px; flex-wrap: wrap; }
	.status-tabs button { padding: 4px 10px; border: 0.5px solid var(--border); background: var(--bg-card); border-radius: 12px; font-size: 11px; font-weight: 600; cursor: pointer; color: var(--text-muted); font-family: inherit; transition: all 0.15s; text-transform: capitalize; }
	.status-tabs button.active { background: var(--primary); color: var(--text-white); border-color: var(--primary); }
	.status-tabs button:hover:not(.active) { background: var(--bg-hover); }

	/* Table */
	.table-wrap { background: var(--bg-card); border-radius: var(--radius-lg); border: 0.5px solid var(--border); overflow: auto; }
	.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
	.data-table th { text-align: left; padding: 10px 14px; font-weight: 600; color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); background: var(--bg-muted); white-space: nowrap; }
	.data-table td { padding: 10px 14px; border-bottom: 1px solid var(--border); color: var(--text-primary); }
	.data-table tbody tr:hover { background: var(--bg-hover); }
	.data-table tbody tr:last-child td { border-bottom: none; }
	.id-cell { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); white-space: nowrap; }
	small { color: var(--text-light); font-size: 11px; }

	/* Status badges */
	.status-badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; text-transform: capitalize; white-space: nowrap; }
	:global(.s-pending) { background: #fef3c7; color: #92400e; }
	:global(.s-confirmed) { background: #dbeafe; color: #1e40af; }
	:global(.s-review) { background: #e0e7ff; color: #3730a3; }
	:global(.s-progress) { background: #d1fae5; color: #065f46; }
	:global(.s-completed) { background: #d1fae5; color: #166534; }
	:global(.s-cancelled) { background: #fee2e2; color: #991b1b; }
	:global(.s-default) { background: var(--bg-muted); color: var(--text-muted); }

	/* Service type badges */
	:global(.badge-repair) { background: #dcfce7; color: #166534; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; text-transform: capitalize; }
	:global(.badge-maintenance) { background: #dbeafe; color: #1e40af; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; text-transform: capitalize; }
	:global(.badge-test-drive) { background: #fef3c7; color: #92400e; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; text-transform: capitalize; }
	:global(.badge-default) { background: var(--bg-muted); color: var(--text-muted); font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; }

	/* Action buttons */
	.actions-cell { display: flex; gap: 4px; flex-wrap: wrap; }
	.btn-sm { display: inline-flex; align-items: center; gap: 3px; padding: 4px 8px; border-radius: var(--radius-sm); font-size: 11px; font-weight: 600; cursor: pointer; border: none; font-family: inherit; text-decoration: none; white-space: nowrap; transition: all 0.12s; }
	.btn-primary { background: var(--primary); color: var(--text-white); }
	.btn-primary:hover { opacity: 0.85; }
	.btn-outline { background: none; border: 0.5px solid var(--border); color: var(--text-dark); }
	.btn-outline:hover { background: var(--bg-hover); }
	.btn-success { background: #16a34a; color: #fff; }
	.btn-success:hover { background: #15803d; }
	.btn-ghost { background: none; color: var(--text-muted); }
	.btn-ghost:hover { background: var(--bg-hover); color: var(--text-dark); }
	.btn-ghost-danger { background: none; color: var(--text-muted); }
	.btn-ghost-danger:hover { background: #fee2e2; color: #dc2626; }

	/* Modal */
	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
	.modal { background: var(--bg-card); border-radius: var(--radius-lg); width: 460px; max-width: 90vw; box-shadow: var(--shadow-lg); }
	.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--border); }
	.modal-header h3 { font-size: 16px; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; }
	.modal-close { background: none; border: none; cursor: pointer; color: var(--text-muted); padding: 4px; border-radius: var(--radius-sm); font-size: 20px; }
	.modal-close:hover { background: var(--bg-hover); }
	.modal-body { padding: 20px 24px; }
	.modal-body p { margin: 0 0 8px; font-size: 14px; color: var(--text-primary); }
	.modal-body textarea { width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 13px; font-family: inherit; resize: vertical; background: var(--bg-card); color: var(--text-primary); box-sizing: border-box; }
	.field-hint { font-size: 12px; color: var(--text-muted); margin: 0; }
	.modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 16px 24px; border-top: 1px solid var(--border); }
	.btn-cancel { background: none; border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; color: var(--text-muted); font-family: inherit; }
	.btn-cancel:hover { background: var(--bg-hover); }
	.btn-danger { background: #dc2626; color: #fff; border: none; border-radius: var(--radius-sm); padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; }
	.btn-danger:hover { background: #b91c1c; }
</style>
