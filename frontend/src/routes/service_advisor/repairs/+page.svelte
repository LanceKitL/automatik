<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getAdvisorServiceBookings,
		getMyServiceBookings,
		assignAndOpenIntake,
		updateServiceBookingStatus,
		updateTechnicianNotes
	} from '$lib/services/api';
	import DataTable from '$lib/components/DataTable.svelte';
	import { goto } from '$app/navigation';

	let bookings = $state<Record<string, unknown>[]>([]);
	let myBookings = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);
	let message = $state('');
	let editingNotes = $state<number | null>(null);
	let notesText = $state('');
	let showMyBookings = $state(false);

	onMount(async () => {
		await loadData();
	});

	async function loadData() {
		loading = true;
		try {
			const [allRes, myRes] = await Promise.all([
				getAdvisorServiceBookings(),
				getMyServiceBookings()
			]);
			bookings = allRes.data as Record<string, unknown>[];
			myBookings = myRes.data as Record<string, unknown>[];
		} catch {
			// error
		} finally {
			loading = false;
		}
	}

	async function handleAssignAndOpenIntake(bookingId: number) {
		try {
			const res = await assignAndOpenIntake(bookingId);
			message = res.message;
			await goto(`/service_advisor/bookings/${bookingId}/intake`);
		} catch (e: unknown) {
			message = e instanceof Error ? e.message : 'Error.';
		}
	}

	async function handleStatus(bookingId: number, status: string) {
		if (!confirm(`Mark booking #${bookingId} as ${status}?`)) return;
		try {
			await updateServiceBookingStatus(bookingId, status);
			message = `Booking #${bookingId} ${status}.`;
			await loadData();
		} catch (e: unknown) {
			message = e instanceof Error ? e.message : 'Error.';
		}
	}

	function startEditNotes(bookingId: number, currentNotes: string | null) {
		editingNotes = bookingId;
		notesText = currentNotes ?? '';
	}

	async function saveNotes() {
		if (editingNotes === null) return;
		try {
			await updateTechnicianNotes(editingNotes, notesText);
			message = `Notes updated for booking #${editingNotes}.`;
			editingNotes = null;
			notesText = '';
			await loadData();
		} catch (e: unknown) {
			message = e instanceof Error ? e.message : 'Error.';
		}
	}

	let displayBookings = $derived(showMyBookings ? myBookings : bookings);

	function badgeClass(bookingType: string | null): string {
		if (bookingType === 'maintenance') return 'badge-green';
		if (bookingType === 'repair') return 'badge-blue';
		return 'badge-gray';
	}

	function formatId(id: number): string {
		return `BK-${String(id).padStart(4, '0')}`;
	}
</script>

<h1>Service Bookings</h1>

{#if message}
	<p class="msg">{message}</p>
{/if}

<div class="tabs">
	<button class:active={!showMyBookings} onclick={() => showMyBookings = false}>All Bookings</button>
	<button class:active={showMyBookings} onclick={() => showMyBookings = true}>My Bookings ({myBookings.length})</button>
</div>

{#if loading}
	<p>Loading…</p>
{:else if displayBookings.length > 0}
	<DataTable columns={['Booking ID', 'Customer & Vehicle', 'Service', 'Date', 'Status', 'Assigned', 'Actions']}>
		{#each displayBookings as b}
			<tr>
				<td>{formatId(b.booking_id as number)}</td>
				<td>
					{b.customer_name ?? '—'}<br>
					<small>{b.year ?? ''} {b.brand ?? ''} {b.model ?? ''}</small>
				</td>
				<td>
					<span class={badgeClass(b.slot_type as string ?? b.booking_type as string)}>
						{b.slot_type ?? b.booking_type ?? '—'}
					</span>
				</td>
				<td>{b.slot_datetime ? String(b.slot_datetime).slice(0, 16) : '—'}</td>
				<td>{b.status ?? '—'}</td>
				<td>{b.assigned_to_name ?? 'Unassigned'}</td>
				<td>
					{#if b.assigned_to === null && !showMyBookings}
						<button onclick={() => handleAssignAndOpenIntake(b.booking_id as number)} class="btn-primary">
							Assign &amp; Open Intake
						</button>
					{/if}
					{#if b.status === 'confirmed' && b.assigned_to !== null}
						<a href="/service_advisor/bookings/{b.booking_id}/intake" class="btn-link">Open Intake</a>
					{/if}
					{#if b.status === 'draft_estimate' || b.status === 'awaiting_signature' || b.status === 'in_progress'}
						<a href="/service_advisor/bookings/{b.booking_id}/intake" class="btn-link">View Estimate</a>
					{/if}
					{#if b.status === 'pending' || b.status === 'confirmed'}
						<button onclick={() => handleStatus(b.booking_id as number, 'cancelled')}>Cancel</button>
					{/if}
					{#if b.status === 'in_progress'}
						<button onclick={() => handleStatus(b.booking_id as number, 'completed')}>Complete</button>
					{/if}
					<button onclick={() => startEditNotes(b.booking_id as number, b.technician_notes as string | null)}>Notes</button>
				</td>
			</tr>
		{/each}
	</DataTable>
{:else}
	<p>No bookings found.</p>
{/if}

{#if editingNotes !== null}
	<div class="modal-overlay" onclick={() => editingNotes = null}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<h3>Technician Notes — {formatId(editingNotes)}</h3>
			<textarea bind:value={notesText} rows="4"></textarea>
			<div class="modal-actions">
				<button onclick={() => editingNotes = null}>Cancel</button>
				<button onclick={saveNotes}>Save Notes</button>
			</div>
		</div>
	</div>
{/if}

<style>
	h1 { padding: 1.5rem 1.5rem 0; margin: 0; }
	.msg { padding: 0.5rem 1.5rem; color: var(--success); }
	.tabs { padding: 1rem 1.5rem; display: flex; gap: 0.5rem; }
	.tabs button { padding: 0.4rem 0.75rem; cursor: pointer; border: 1px solid #ccc; background: var(--bg-card); border-radius: var(--radius-sm); }
	.tabs button.active { background: var(--primary); color: var(--text-white); border-color: var(--primary); }
	td button, td a { margin-right: 0.25rem; padding: 0.25rem 0.5rem; cursor: pointer; font-size: 0.8rem; }
	.btn-primary { background: var(--primary); color: var(--text-white); border: none; border-radius: var(--radius-sm); }
	.btn-link { text-decoration: none; color: var(--primary); }
	small { color: var(--text-light); font-size: 0.8rem; }
	.badge-green { display: inline-block; padding: 2px 8px; border-radius: var(--radius-sm); background: var(--success); color: var(--text-white); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
	.badge-blue { display: inline-block; padding: 2px 8px; border-radius: var(--radius-sm); background: var(--primary); color: var(--text-white); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
	.badge-gray { display: inline-block; padding: 2px 8px; border-radius: var(--radius-sm); background: var(--text-muted); color: var(--text-white); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
	.modal-overlay {
		position: fixed; inset: 0; background: rgba(0,0,0,0.4);
		display: flex; align-items: center; justify-content: center;
	}
	.modal {
		background: var(--bg-card); padding: 1.5rem; border-radius: var(--radius-md); min-width: 24rem;
	}
	.modal textarea { width: 100%; margin: 0.5rem 0; padding: 0.5rem; }
	.modal-actions { display: flex; gap: 0.5rem; justify-content: flex-end; }
	.modal-actions button { padding: 0.4rem 0.75rem; cursor: pointer; }
</style>
