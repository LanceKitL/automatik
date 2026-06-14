<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import {
		getServiceStaffBookings,
		createMaintenanceBooking,
		updateServiceBookingStatus,
		updateTechnicianNotes,
		updateBookingNotes,
		getServiceStaffCustomers,
		getServiceSlots,
	} from '$lib/services/api';
	import type { CustomerWithVehicles, ServiceSlot } from '$lib/services/api';
	import { Plus, Wrench, Search } from '@lucide/svelte';
	import { formatSlotDateTime, formatSlotOption } from '$lib/utils/format';

	let bookings = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);
	let statusFilter = $state('all');
	let searchQuery = $state('');

	let customers = $state<CustomerWithVehicles[]>([]);
	let slots = $state<ServiceSlot[]>([]);

	let showAddModal = $state(false);
	let addCustomerId = $state<number | ''>('');
	let addVehicleId = $state<number | ''>('');
	let addSlotId = $state<number | ''>('');
	let addNotes = $state('');
	let adding = $state(false);

	let editingNotes = $state<{ id: number; technician: boolean } | null>(null);
	let notesText = $state('');

	let selectedStatus = $state<{ id: number; status: string } | null>(null);

	onMount(async () => {
		await Promise.all([loadData(), loadFormData()]);
	});

	async function loadData() {
		loading = true;
		try {
			const res = await getServiceStaffBookings('maintenance');
			bookings = res.data as Record<string, unknown>[];
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to load maintenance bookings.');
		} finally {
			loading = false;
		}
	}

	async function loadFormData() {
		try {
			const [custRes, slotRes] = await Promise.all([
				getServiceStaffCustomers(),
				getServiceSlots(undefined, 'maintenance')
			]);
			customers = custRes.data;
			slots = slotRes.data;
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to load form data.');
		}
	}

	let displayBookings = $derived.by(() => {
		let list = bookings.filter(b => b.status !== 'completed' && b.status !== 'cancelled');
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

	let filteredVehicles = $derived(
		addCustomerId !== '' ? customers.find(c => c.user_id === addCustomerId)?.vehicles ?? [] : []
	);

	function resetAddForm() {
		addCustomerId = '';
		addVehicleId = '';
		addSlotId = '';
		addNotes = '';
	}

	async function handleAdd() {
		if (!addCustomerId || !addVehicleId || !addSlotId) {
			toast.error('Please select customer, vehicle, and slot.');
			return;
		}
		adding = true;
		try {
			await createMaintenanceBooking({
				customer_id: addCustomerId as number,
				vehicle_id: addVehicleId as number,
				slot_id: addSlotId as number,
				notes: addNotes
			});
			toast.success('Maintenance booking created!');
			showAddModal = false;
			resetAddForm();
			await loadData();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to create booking.');
		} finally {
			adding = false;
		}
	}

	async function handleStatus(id: number, status: string) {
		try {
			await updateServiceBookingStatus(id, status);
			toast.success(`Booking #${id} marked as ${status}.`);
			selectedStatus = null;
			await loadData();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to update status.');
		}
	}

	async function handleSaveNotes() {
		if (!editingNotes) return;
		try {
			if (editingNotes.technician) {
				await updateTechnicianNotes(editingNotes.id, notesText);
			} else {
				await updateBookingNotes(editingNotes.id, notesText);
			}
			toast.success('Notes updated.');
			editingNotes = null;
			notesText = '';
			await loadData();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to save notes.');
		}
	}

	function openNotesModal(id: number, current: string | null, technician: boolean) {
		editingNotes = { id, technician };
		notesText = current ?? '';
	}

	function formatId(id: number): string {
		return `BK-${String(id).padStart(4, '0')}`;
	}

	function statusClass(s: string | null | undefined): string {
		if (!s) return 's-default';
		const st = s.toLowerCase();
		if (st === 'confirmed' || st === 'approved' || st === 'resolved') return 's-confirmed';
		if (st === 'pending' || st === 'submitted') return 's-pending';
		if (st === 'cancelled' || st === 'rejected') return 's-cancelled';
		if (st === 'under_review' || st === 'draft_estimate') return 's-review';
		if (st === 'in_progress' || st === 'awaiting_signature') return 's-progress';
		if (st === 'completed') return 's-completed';
		return 's-default';
	}
</script>

<div class="container">
	<div class="page-header">
		<div>
			<h1>Maintenance</h1>
			<p class="subtitle">Create and manage scheduled maintenance bookings.</p>
		</div>
		<button class="btn-primary" onclick={() => showAddModal = true}>
			<Plus size={18} /> Add Maintenance
		</button>
	</div>

	{#if loading}
		<div class="loading-state">
			<span class="spinner"></span>
			<p>Loading maintenance bookings…</p>
		</div>
	{:else}
		<div class="toolbar">
			<div class="status-tabs">
				<button class:active={statusFilter === 'all'} onclick={() => statusFilter = 'all'}>All ({bookings.length})</button>
				<button class:active={statusFilter === 'pending'} onclick={() => statusFilter = 'pending'}>Pending</button>
				<button class:active={statusFilter === 'confirmed'} onclick={() => statusFilter = 'confirmed'}>Confirmed</button>
				<button class:active={statusFilter === 'in_progress'} onclick={() => statusFilter = 'in_progress'}>In Progress</button>
			</div>
			<div class="search-wrap">
				<Search size={14} />
				<input bind:value={searchQuery} placeholder="Search ID, customer, vehicle…" />
			</div>
		</div>

		{#if displayBookings.length === 0}
			<div class="empty-state">
				<Wrench size={48} />
				<p>No maintenance bookings found.</p>
			</div>
		{:else}
			<div class="table-wrap">
				<table>
					<thead>
						<tr>
							<th>ID</th>
							<th>Customer</th>
							<th>Vehicle</th>
							<th>Slot</th>
							<th>Status</th>
							<th>Assigned</th>
							<th>Notes</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						{#each displayBookings as b}
						<tr>
							<td class="mono">{formatId(b.booking_id as number)}</td>
							<td>{b.customer_name ?? '—'}</td>
							<td>{b.year ?? ''} {b.brand ?? ''} {b.model ?? ''}</td>
							<td>{formatSlotDateTime(b.slot_datetime)}</td>
							<td><span class={statusClass(b.status as string)}>{(b.status as string)?.replace(/_/g, ' ') ?? '—'}</span></td>
							<td>{b.assigned_to_name ?? 'Unassigned'}</td>
							<td class="notes-cell" title={(b.notes as string) || ''}>
								{(b.notes as string)?.length > 30 ? String(b.notes).slice(0, 30) + '…' : (b.notes as string) || '—'}
							</td>
							<td class="actions-cell">
								{#if b.status === 'confirmed'}
									<button class="btn-sm btn-outline" onclick={() => handleStatus(b.booking_id as number, 'completed')}>Complete</button>
								{/if}
								{#if b.status === 'pending'}
									<button class="btn-sm btn-outline" onclick={() => selectedStatus = { id: b.booking_id as number, status: 'confirmed' }}>Confirm</button>
									<button class="btn-sm btn-outline-danger" onclick={() => handleStatus(b.booking_id as number, 'cancelled')}>Cancel</button>
								{/if}
								{#if b.status === 'in_progress'}
									<button class="btn-sm btn-outline" onclick={() => handleStatus(b.booking_id as number, 'completed')}>Complete</button>
								{/if}
								<button class="btn-sm btn-ghost" onclick={() => openNotesModal(b.booking_id as number, b.technician_notes as string | null, true)}>Tech Notes</button>
								<button class="btn-sm btn-ghost" onclick={() => openNotesModal(b.booking_id as number, b.notes as string | null, false)}>Notes</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
	{/if}

	<!-- Add Maintenance Modal -->
	{#if showAddModal}
		<div class="modal-overlay" onclick={() => showAddModal = false}>
			<div class="modal" onclick={(e) => e.stopPropagation()}>
				<div class="modal-header">
					<h2><Wrench size={20} /> New Maintenance Booking</h2>
					<button class="modal-close" onclick={() => { showAddModal = false; resetAddForm(); }}>×</button>
				</div>
				<div class="modal-body">
					<label>
						<span>Customer</span>
						<select bind:value={addCustomerId} onchange={() => { addVehicleId = ''; }}>
							<option value="">Select customer…</option>
							{#each customers as c}
								<option value={c.user_id}>{c.username} ({c.email})</option>
							{/each}
						</select>
					</label>
					<label>
						<span>Vehicle</span>
						<select bind:value={addVehicleId} disabled={addCustomerId === ''}>
							<option value="">Select vehicle…</option>
							{#each filteredVehicles as v}
								<option value={v.vehicle_id}>{v.brand} {v.model} ({v.year})</option>
							{/each}
						</select>
						{#if addCustomerId !== '' && filteredVehicles.length === 0}
							<p class="field-hint">No vehicles found for this customer.</p>
						{/if}
					</label>
					<label>
						<span>Service Slot</span>
						<select bind:value={addSlotId}>
							<option value="">Select slot…</option>
							{#each slots as s}
								<option value={s.slot_id}>
									{formatSlotOption(s)}
								</option>
							{/each}
						</select>
						{#if slots.length === 0}
							<p class="field-hint">No maintenance slots available. Create one in the admin panel.</p>
						{/if}
					</label>
					<label>
						<span>Notes</span>
						<textarea bind:value={addNotes} placeholder="Customer request or service notes…" rows="3"></textarea>
					</label>
				</div>
				<div class="modal-footer">
					<button class="btn-secondary" onclick={() => { showAddModal = false; resetAddForm(); }}>Cancel</button>
					<button class="btn-primary" onclick={handleAdd} disabled={adding}>
						{adding ? 'Creating…' : 'Create Booking'}
					</button>
				</div>
			</div>
		</div>
	{/if}

	<!-- Confirm Status Modal -->
	{#if selectedStatus}
		<div class="modal-overlay" onclick={() => selectedStatus = null}>
			<div class="modal modal-sm" onclick={(e) => e.stopPropagation()}>
				<div class="modal-header">
					<h2>Update Status</h2>
					<button class="modal-close" onclick={() => selectedStatus = null}>×</button>
				</div>
				<div class="modal-body">
					<p>Mark booking <strong>{formatId(selectedStatus.id)}</strong> as <strong>{selectedStatus.status.replace(/_/g, ' ')}</strong>?</p>
				</div>
				<div class="modal-footer">
					<button class="btn-secondary" onclick={() => selectedStatus = null}>No</button>
					<button class="btn-primary" onclick={() => handleStatus(selectedStatus.id, selectedStatus.status)}>Yes, update</button>
				</div>
			</div>
		</div>
	{/if}

	<!-- Edit Notes Modal -->
	{#if editingNotes}
		<div class="modal-overlay" onclick={() => editingNotes = null}>
			<div class="modal" onclick={(e) => e.stopPropagation()}>
				<div class="modal-header">
					<h2>{editingNotes.technician ? 'Technician Notes' : 'Booking Notes'} — {formatId(editingNotes.id)}</h2>
					<button class="modal-close" onclick={() => editingNotes = null}>×</button>
				</div>
				<div class="modal-body">
					<textarea bind:value={notesText} rows="4"></textarea>
				</div>
				<div class="modal-footer">
					<button class="btn-secondary" onclick={() => editingNotes = null}>Cancel</button>
					<button class="btn-primary" onclick={handleSaveNotes}>Save Notes</button>
				</div>
			</div>
		</div>
	{/if}

</div>

<style>
	.container{
		padding: 2rem;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 24px;
	}
	h1 {
		font-size: 24px;
		font-weight: 700;
		color: var(--text-dark);
		margin: 0;
	}
	.subtitle {
		font-size: 14px;
		color: var(--text-muted);
		margin-top: 4px;
	}
	.btn-primary {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		background: var(--primary);
		color: var(--text-white);
		border: none;
		border-radius: var(--radius-md);
		padding: 10px 20px;
		font-size: 14px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
	}
	.btn-primary:hover { opacity: 0.9; }
	.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn-secondary {
		padding: 8px 16px;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		background: var(--bg-card);
		color: var(--text-dark);
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		font-family: inherit;
	}
	.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 1rem; flex-wrap: wrap; }
	.status-tabs { display: flex; gap: 4px; flex-wrap: wrap; }
	.status-tabs button { padding: 4px 10px; border: 0.5px solid var(--border); background: var(--bg-card); border-radius: 12px; font-size: 11px; font-weight: 600; cursor: pointer; color: var(--text-muted); font-family: inherit; transition: all 0.15s; text-transform: capitalize; }
	.status-tabs button.active { background: var(--primary); color: var(--text-white); border-color: var(--primary); }
	.status-tabs button:hover:not(.active) { background: var(--bg-hover); }
	.search-wrap { display: flex; align-items: center; gap: 6px; background: var(--bg-card); border: 0.5px solid var(--border); border-radius: var(--radius-sm); padding: 6px 10px; }
	.search-wrap input { border: none; background: none; outline: none; font-size: 12px; color: var(--text-primary); font-family: inherit; min-width: 160px; }
	.search-wrap svg { color: var(--text-muted); flex-shrink: 0; }
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 12px;
		padding: 60px 20px;
		color: var(--text-muted);
	}
	.spinner {
		width: 32px;
		height: 32px;
		border: 3px solid var(--border);
		border-top-color: var(--primary);
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
	}
	@keyframes spin { to { transform: rotate(360deg); } }
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 16px;
		padding: 60px 20px;
		color: var(--text-muted);
	}
	.table-wrap {
		background: var(--bg-card);
		border-radius: var(--radius-md);
		border: 1px solid var(--border);
		overflow-x: auto;
		box-shadow: var(--shadow-sm);
	}
	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.85rem;
	}
	th {
		text-align: left;
		padding: 0.75rem 1rem;
		color: var(--text-muted);
		font-weight: 600;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		border-bottom: 1px solid var(--border);
		background: var(--bg-muted);
		white-space: nowrap;
	}
	td {
		padding: 0.65rem 1rem;
		border-bottom: 1px solid var(--border-lighter);
		color: var(--text-primary);
		vertical-align: middle;
	}
	tr:last-child td { border-bottom: none; }
	tr:hover td { background: var(--bg-hover); }
	.mono { font-family: monospace; font-size: 0.8rem; }
	.notes-cell {
		max-width: 160px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		color: var(--text-muted);
		font-size: 0.8rem;
	}
	.actions-cell {
		white-space: nowrap;
		display: flex;
		gap: 4px;
		flex-wrap: wrap;
	}
	.btn-sm {
		padding: 4px 10px;
		font-size: 11px;
		font-weight: 600;
		border-radius: var(--radius-sm);
		cursor: pointer;
		font-family: inherit;
		white-space: nowrap;
	}
	.btn-outline {
		background: transparent;
		border: 1px solid var(--primary);
		color: var(--primary);
	}
	.btn-outline:hover { background: var(--primary); color: var(--text-white); }
	.btn-outline-danger {
		background: transparent;
		border: 1px solid var(--danger);
		color: var(--danger);
	}
	.btn-outline-danger:hover { background: var(--danger); color: var(--text-white); }
	.btn-ghost {
		background: transparent;
		border: 1px solid var(--border);
		color: var(--text-muted);
	}
	.btn-ghost:hover { background: var(--bg-hover); color: var(--text-primary); }
	.s-confirmed, .s-completed {
		display: inline-block;
		padding: 2px 10px;
		border-radius: 20px;
		font-size: 11px;
		font-weight: 600;
		background: #d1fae5;
		color: #065f46;
	}
	.s-pending {
		display: inline-block;
		padding: 2px 10px;
		border-radius: 20px;
		font-size: 11px;
		font-weight: 600;
		background: #fef3c7;
		color: #92400e;
	}
	.s-cancelled {
		display: inline-block;
		padding: 2px 10px;
		border-radius: 20px;
		font-size: 11px;
		font-weight: 600;
		background: #fee2e2;
		color: #dc2626;
	}
	.s-review {
		display: inline-block;
		padding: 2px 10px;
		border-radius: 20px;
		font-size: 11px;
		font-weight: 600;
		background: #fef9e7;
		color: #7d6608;
	}
	.s-progress {
		display: inline-block;
		padding: 2px 10px;
		border-radius: 20px;
		font-size: 11px;
		font-weight: 600;
		background: #dbeafe;
		color: #1e40af;
	}
	.s-default {
		display: inline-block;
		padding: 2px 10px;
		border-radius: 20px;
		font-size: 11px;
		font-weight: 600;
		background: #f3f4f6;
		color: #6b7280;
	}
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.4);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}
	.modal {
		background: var(--bg-card);
		border-radius: var(--radius-lg);
		width: 520px;
		max-width: 90vw;
		box-shadow: var(--shadow-lg);
	}
	.modal-sm { width: 380px; }
	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20px 24px;
		border-bottom: 1px solid var(--border);
	}
	.modal-header h2 {
		font-size: 18px;
		font-weight: 700;
		margin: 0;
		display: flex;
		align-items: center;
		gap: 8px;
	}
	.modal-close {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 22px;
		color: var(--text-muted);
		padding: 4px 8px;
		border-radius: var(--radius-sm);
	}
	.modal-close:hover { background: var(--bg-hover); }
	.modal-body {
		padding: 20px 24px;
		display: flex;
		flex-direction: column;
		gap: 16px;
	}
	.modal-body label {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}
	.modal-body label > span {
		font-size: 13px;
		font-weight: 600;
		color: var(--text-dark);
	}
	.modal-body select, .modal-body textarea {
		padding: 8px 12px;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		font-size: 14px;
		font-family: inherit;
		background: var(--bg-card);
		color: var(--text-primary);
	}
	.modal-body textarea { resize: vertical; }
	.field-hint {
		font-size: 12px;
		color: var(--text-muted);
		margin: 0;
	}
	.modal-footer {
		padding: 16px 24px;
		border-top: 1px solid var(--border);
		display: flex;
		justify-content: flex-end;
		gap: 8px;
	}
</style>
