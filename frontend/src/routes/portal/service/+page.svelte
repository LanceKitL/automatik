<script lang="ts">
	import { onMount } from 'svelte';
	import { Wrench, Calendar, Car, Clock, X, FileText, Check } from '@lucide/svelte';
	import { getCustomerServiceBookings, cancelServiceBooking, signEstimate, acknowledgeEstimate, getCustomerDashboard, getServiceSlots, createBooking, getMyWarrantyClaims } from '$lib/services/api';
	import type { ServiceBooking, ServiceSlot, CustomerDashboardVehicle, WarrantyClaim } from '$lib/services/api';
	import { toast } from 'svelte-sonner';

	let bookings = $state<ServiceBooking[]>([]);
	let vehicles = $state<CustomerDashboardVehicle[]>([]);
	let loading = $state(true);
	let filter = $state('all');
	let showingModal = $state(false);
	let confirming = $state(false);
	let viewingBooking = $state<ServiceBooking | null>(null);
	let signingLoading = $state(false);

	const types = ['all', 'repair', 'maintenance'];

	let filtered = $derived(
		filter === 'all' ? bookings : bookings.filter(b => b.booking_type === filter)
	);

	// Booking modal state
	let selVehicleId = $state<number | ''>('');
	let selType = $state<'maintenance' | 'repair'>('maintenance');
	let selDate = $state('');
	let selSlotId = $state<number | ''>('');
	let availableSlots = $state<ServiceSlot[]>([]);
	let slotsLoading = $state(false);
	let notes = $state('');
	let approvedClaims = $state<WarrantyClaim[]>([]);
	let selClaimId = $state<number | ''>('');

	// Group slots by date for date picker
	let dateGroups = $derived.by(() => {
		const groups = new Map<string, ServiceSlot[]>();
		for (const s of availableSlots) {
			const d = new Date(s.slot_datetime).toISOString().slice(0, 10);
			if (!groups.has(d)) groups.set(d, []);
			groups.get(d)!.push(s);
		}
		return groups;
	});

	let dateList = $derived(Array.from(dateGroups.keys()).sort());

	onMount(async () => {
		try {
			const [bRes, dRes, cRes] = await Promise.all([
				getCustomerServiceBookings(),
				getCustomerDashboard(),
				getMyWarrantyClaims()
			]);
			bookings = bRes.data.filter(b => b.booking_type === 'maintenance' || b.booking_type === 'repair');
			vehicles = dRes.data.dashboard.my_vehicles;
			approvedClaims = (cRes as WarrantyClaim[]).filter(c => c.status === 'approved');
		} catch {
			bookings = [];
		} finally {
			loading = false;
		}
	});

	async function cancelBooking(id: number) {
		try {
			await cancelServiceBooking(id);
			bookings = bookings.filter(b => b.booking_id !== id);
			toast.success('Booking cancelled');
		} catch {
			toast.error('Failed to cancel booking');
		}
	}

	async function handleDateClick(date: string) {
		selDate = date;
		selSlotId = '';
		slotsLoading = true;
		try {
			const res = await getServiceSlots(date, selType);
			availableSlots = res.data;
		} catch {
			availableSlots = [];
		} finally {
			slotsLoading = false;
		}
	}

	async function handleTypeChange() {
		selDate = '';
		selSlotId = '';
		availableSlots = [];
	}

	async function confirmBooking() {
		if (!selVehicleId || !selSlotId) return;
		confirming = true;
		try {
			await createBooking(selSlotId, selVehicleId, selType, notes, selClaimId || undefined);
			toast.success('Service booked successfully');
			showingModal = false;
			resetModal();
			const res = await getCustomerServiceBookings();
			bookings = res.data;
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to book service');
		} finally {
			confirming = false;
		}
	}

	function resetModal() {
		selVehicleId = '';
		selType = 'maintenance';
		selDate = '';
		selSlotId = '';
		availableSlots = [];
		notes = '';
		selClaimId = '';
	}

	function openModal() {
		resetModal();
		showingModal = true;
	}

	function formatDate(dt: string) {
		const d = new Date(dt);
		return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' });
	}

	function formatTime(dt: string) {
		const d = new Date(dt);
		return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZone: 'UTC' });
	}

	function formatDateShort(dateStr: string) {
		const d = new Date(dateStr + 'T00:00:00');
		return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
	}

	function parseEstimate(raw: string | null): Record<string, unknown> | null {
		if (!raw) return null;
		try { return JSON.parse(raw); } catch { return null; }
	}

	function formatPeso(n: number): string {
		return '₱' + Number(n).toLocaleString();
	}

	function openEstimate(b: ServiceBooking) {
		viewingBooking = b;
	}

	function closeEstimate() {
		viewingBooking = null;
	}

	async function handleSign() {
		if (!viewingBooking) return;
		signingLoading = true;
		try {
			await signEstimate(viewingBooking.booking_id);
			toast.success('Estimate signed! Work is now in progress.');
			viewingBooking = null;
			const res = await getCustomerServiceBookings();
			bookings = res.data;
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to sign estimate.');
		} finally {
			signingLoading = false;
		}
	}

	async function handleAcknowledge() {
		if (!viewingBooking) return;
		signingLoading = true;
		try {
			await acknowledgeEstimate(viewingBooking.booking_id);
			toast.success('Thank you! The service team has been notified.');
			viewingBooking = null;
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to acknowledge.');
		} finally {
			signingLoading = false;
		}
	}
</script>

<div class="page-header">
	<div>
		<h1>Service Appointments</h1>
		<p class="subtitle">Manage your appointments — repairs & maintenance</p>
	</div>
	<button class="btn-primary" onclick={openModal}>
		<Wrench size={18} /> Book a Service
	</button>
</div>

<div class="metrics">
	<div class="metric-card">
		<div class="metric-value">{bookings.length}</div>
		<div class="metric-label">Total Bookings</div>
	</div>
	<div class="metric-card">
		<div class="metric-value">{bookings.filter(b => b.status === 'pending').length}</div>
		<div class="metric-label">Pending</div>
	</div>
	<div class="metric-card">
		<div class="metric-value">{bookings.filter(b => b.status === 'confirmed' || b.status === 'completed').length}</div>
		<div class="metric-label">Confirmed</div>
	</div>
</div>

<div class="filters">
	{#each types as t}
		<button class="filter-tab" class:active={filter === t} onclick={() => filter = t}>
			{t === 'all' ? 'All' : t.charAt(0).toUpperCase() + t.slice(1)}
		</button>
	{/each}
</div>

{#if loading}
	<p class="loading">Loading bookings…</p>
{:else if filtered.length === 0}
	<div class="empty">No bookings found. Click "Book a Service" to get started.</div>
{:else}
	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					<th>Date & Time</th>
					<th>Type</th>
					<th>Vehicle</th>
					<th>Status</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each filtered as b}
					<tr>
						<td><Calendar size={14} class="icon-muted" /> {formatDate(b.slot_datetime)} @ {formatTime(b.slot_datetime)}</td>
						<td><span class="type-tag" class:repair={b.booking_type === 'repair'} class:maintenance={b.booking_type === 'maintenance'} class:test_drive={b.booking_type === 'test_drive'}>{b.booking_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span></td>
						<td><Car size={14} class="icon-muted" /> {b.brand} {b.model}</td>
						<td><span class="status-badge" class:confirmed={b.status === 'confirmed'} class:pending={b.status === 'pending'} class:cancelled={b.status === 'cancelled'} class:in_progress={b.status === 'in_progress'} class:completed={b.status === 'completed'}>{b.status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span></td>
						<td>
							<div class="actions-cell">
								{#if b.estimate_data}
									<button class="btn-view-estimate" onclick={() => openEstimate(b)}>
										<FileText size={13} /> {b.status === 'awaiting_signature' ? 'View & Sign' : 'View Estimate'}
									</button>
								{/if}
								{#if b.status !== 'cancelled' && b.status !== 'completed'}
									<button class="btn-cancel" onclick={() => cancelBooking(b.booking_id)}><X size={14} /> Cancel</button>
								{/if}
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

{#if showingModal}
	<div class="modal-overlay" onclick={() => showingModal = false}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Book a Service</h2>
				<button class="modal-close" onclick={() => showingModal = false}><X size={20} /></button>
			</div>
			<div class="modal-body">
				<div class="form-group">
					<label>Vehicle</label>
					<select bind:value={selVehicleId}>
						<option value="">Select your vehicle</option>
						{#each vehicles as v}
							<option value={v.vehicle_id}>{v.brand} {v.model} {v.year ? `(${v.year})` : ''}</option>
						{/each}
					</select>
				</div>

				<div class="form-group">
					<label>Booking Type</label>
					<div class="radio-group">
						<label class="radio-label">
							<input type="radio" bind:group={selType} value="maintenance" onchange={handleTypeChange} /> Maintenance
						</label>
						<label class="radio-label">
							<input type="radio" bind:group={selType} value="repair" onchange={handleTypeChange} /> Repair
						</label>
					</div>
				</div>

				<div class="form-group">
					<label>Notes (optional)</label>
					<textarea bind:value={notes} placeholder="Describe the issue or any special instructions…" rows="3"></textarea>
				</div>

				{#if approvedClaims.length > 0}
					<div class="form-group">
						<label>Warranty Claim (optional)</label>
						<select bind:value={selClaimId}>
							<option value="">Not applicable</option>
							{#each approvedClaims as c}
								<option value={c.claim_id}>Claim #{c.claim_id} — {c.vehicle.brand} {c.vehicle.model} ({c.claim_type})</option>
							{/each}
						</select>
					</div>
				{/if}

				{#if selVehicleId}
					<div class="form-group">
						<label>Select Date</label>
						{#if slotsLoading}
							<p class="hint">Loading slots…</p>
						{:else if dateList.length === 0}
							<div class="date-chips">
								<button class="date-chip inactive" onclick={() => handleDateClick('')}>
									Load available dates
								</button>
							</div>
						{:else}
							<div class="date-chips">
								{#each dateList as d}
									<button class="date-chip" class:active={selDate === d} onclick={() => handleDateClick(d)}>
										{formatDateShort(d)}
									</button>
								{/each}
							</div>
						{/if}
					</div>

					{#if selDate && dateGroups.size > 0}
						<div class="form-group">
							<label>Select Time</label>
							<div class="time-chips">
								{#each (dateGroups.get(selDate) || []) as slot}
									<button class="time-chip" class:active={selSlotId === slot.slot_id} onclick={() => selSlotId = slot.slot_id} disabled={slot.remaining < 1}>
										{formatTime(slot.slot_datetime)}
										<span class="remaining">{slot.remaining} left</span>
									</button>
								{/each}
							</div>
						</div>
					{/if}
				{/if}
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={() => showingModal = false}>Cancel</button>
				<button class="btn-primary" onclick={confirmBooking} disabled={!selVehicleId || !selSlotId || confirming}>
					{confirming ? 'Booking…' : 'Confirm Booking'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Estimate Viewer Drawer -->
{#if viewingBooking}
	{@const est = parseEstimate(viewingBooking.estimate_data)}
	<div class="modal-overlay" onclick={closeEstimate}>
		<div class="modal drawer-wide" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Estimate — #{viewingBooking.booking_id}</h2>
				<button class="modal-close" onclick={closeEstimate}><X size={20} /></button>
			</div>
			<div class="modal-body">
				<div class="est-meta">
					<span>{viewingBooking.brand} {viewingBooking.model}</span>
					<span class="status-badge" class:confirmed={viewingBooking.status === 'confirmed'} class:pending={viewingBooking.status === 'pending'} class:cancelled={viewingBooking.status === 'cancelled'} class:in_progress={viewingBooking.status === 'in_progress'} class:completed={viewingBooking.status === 'completed'}>{viewingBooking.status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
				</div>

				{#if est}
					{@const parts = (est.parts as Array<{description:string;unit_cost:number;qty:number}>) ?? []}
					{@const labor = (est.labor as Array<{description:string;hours:number;rate:number}>) ?? []}
					{@const misc = (est.misc as Array<{description:string;amount:number}>) ?? []}
					{@const subtotal = Number(est.subtotal) || 0}
					{@const tax = Number(est.tax) || 0}
					{@const total = Number(est.total) || 0}
					{@const taxRate = Number(est.tax_rate) || 0}

					<!-- Parts -->
					{#if parts.length > 0}
						<section class="est-section">
							<h3>Parts & Supplies</h3>
							<div class="est-table">
								{#each parts as p}
									<div class="est-row">
										<span class="est-desc">{p.description}</span>
										<span class="est-detail">{formatPeso(p.unit_cost)} × {p.qty}</span>
										<span class="est-total">{formatPeso(p.unit_cost * p.qty)}</span>
									</div>
								{/each}
							</div>
						</section>
					{/if}

					<!-- Labor -->
					{#if labor.length > 0}
						<section class="est-section">
							<h3>Labor</h3>
							<div class="est-table">
								{#each labor as l}
									<div class="est-row">
										<span class="est-desc">{l.description}</span>
										<span class="est-detail">{l.hours}h × {formatPeso(l.rate)}/hr</span>
										<span class="est-total">{formatPeso(l.hours * l.rate)}</span>
									</div>
								{/each}
							</div>
						</section>
					{/if}

					<!-- Misc -->
					{#if misc.length > 0}
						<section class="est-section">
							<h3>Miscellaneous</h3>
							<div class="est-table">
								{#each misc as m}
									<div class="est-row">
										<span class="est-desc">{m.description}</span>
										<span class="est-detail"></span>
										<span class="est-total">{formatPeso(m.amount)}</span>
									</div>
								{/each}
							</div>
						</section>
					{/if}

					<!-- Summary -->
					<section class="est-section est-summary">
						<div class="s-row"><span>Subtotal</span><span>{formatPeso(subtotal)}</span></div>
						<div class="s-row s-tax"><span>Tax ({taxRate}%)</span><span>{formatPeso(tax)}</span></div>
						<div class="s-divider"></div>
						<div class="s-row s-total"><span>Total</span><span class="total-val">{formatPeso(total)}</span></div>
					</section>

					<!-- Customer Notes -->
					{#if est.customer_notes}
						<section class="est-section">
							<h3>Your Notes</h3>
							<p class="est-notes">{est.customer_notes as string}</p>
						</section>
					{/if}
				{:else}
					<p class="est-empty">No estimate data available.</p>
				{/if}
			</div>
			<div class="modal-footer">
				{#if viewingBooking.status === 'draft_estimate' && est}
					<button class="btn-acknowledge" onclick={handleAcknowledge} disabled={signingLoading}>
						{signingLoading ? 'Acknowledging…' : 'Acknowledge & Continue'}
					</button>
				{:else if viewingBooking.status === 'awaiting_signature' && est}
					<button class="btn-secondary" onclick={closeEstimate}>Close</button>
					<button class="btn-primary btn-sign" onclick={handleSign} disabled={signingLoading}>
						<Check size={16} /> {signingLoading ? 'Signing…' : 'Sign & Approve'}
					</button>
				{:else}
					<button class="btn-secondary" onclick={closeEstimate}>Close</button>
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
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
	.metrics {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
		gap: 12px;
		margin-bottom: 20px;
	}
	.metric-card {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		padding: 16px 20px;
		text-align: center;
	}
	.metric-value {
		font-size: 28px;
		font-weight: 700;
		color: var(--primary);
	}
	.metric-label {
		font-size: 12px;
		color: var(--text-muted);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		margin-top: 4px;
	}
	.filters {
		display: flex;
		gap: 6px;
		margin-bottom: 16px;
	}
	.filter-tab {
		padding: 6px 14px;
		border: 1px solid var(--border);
		border-radius: 20px;
		background: var(--bg-card);
		font-size: 12px;
		color: var(--text-dark);
		cursor: pointer;
		font-family: inherit;
		font-weight: 500;
	}
	.filter-tab.active {
		background: var(--primary);
		color: var(--text-white);
		border-color: var(--primary);
	}
	.loading, .empty {
		text-align: center;
		padding: 40px 20px;
		color: var(--text-muted);
	}
	.table-wrapper {
		overflow-x: auto;
		background: var(--bg-card);
		border-radius: var(--radius-md);
		border: 1px solid var(--border);
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
	}
	td {
		padding: 0.65rem 1rem;
		border-bottom: 1px solid var(--border-lighter);
		color: var(--text-primary);
		vertical-align: middle;
	}
	tr:last-child td {
		border-bottom: none;
	}
	.icon-muted {
		color: var(--text-muted);
		display: inline;
		margin-right: 4px;
		vertical-align: middle;
	}
	.type-tag {
		display: inline-block;
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		font-size: 11px;
		font-weight: 600;
	}
	.type-tag.repair { background: #fef3c7; color: #92400e; }
	.type-tag.maintenance { background: #dbeafe; color: #1e40af; }
	.type-tag.test_drive { background: #d1fae5; color: #065f46; }
	.status-badge {
		display: inline-block;
		padding: 2px 10px;
		border-radius: 20px;
		font-size: 11px;
		font-weight: 600;
	}
	.status-badge.confirmed { background: #d1fae5; color: #065f46; }
	.status-badge.pending { background: #fef3c7; color: #92400e; }
	.status-badge.cancelled { background: #f3f4f6; color: #6b7280; }
	.status-badge.in_progress { background: #dbeafe; color: #1e40af; }
	.status-badge.completed { background: #d1fae5; color: #065f46; }
	.btn-cancel {
		background: #fef2f2;
		color: #dc2626;
		border: 1px solid #fecaca;
		border-radius: var(--radius-sm);
		padding: 4px 10px;
		font-size: 11px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
		display: inline-flex;
		align-items: center;
		gap: 4px;
	}
	.btn-cancel:hover { background: #fee2e2; }
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
		width: 500px;
		max-width: 90vw;
		box-shadow: var(--shadow-lg);
	}
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
	}
	.modal-close {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--text-muted);
		padding: 4px;
		border-radius: var(--radius-sm);
	}
	.modal-close:hover { background: var(--bg-hover); }
	.modal-body {
		padding: 20px 24px;
	}
	.modal-footer {
		padding: 16px 24px;
		border-top: 1px solid var(--border);
		display: flex;
		justify-content: flex-end;
		gap: 8px;
	}
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
	.form-group { margin-bottom: 16px; }
	.form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--text-dark); margin-bottom: 6px; }
	.form-group select, .form-group input, .form-group textarea { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: var(--radius-md); font-size: 14px; background: var(--bg-card); color: var(--text-dark); box-sizing: border-box; font-family: inherit; }
	.form-group textarea { resize: vertical; min-height: 60px; }
	.form-group select { cursor: pointer; }
	.radio-group { display: flex; gap: 16px; }
	.radio-label { display: flex; align-items: center; gap: 6px; font-size: 14px; color: var(--text-dark); cursor: pointer; }
	.radio-label input { width: auto; }
	.date-chips, .time-chips { display: flex; flex-wrap: wrap; gap: 8px; }
	.date-chip, .time-chip {
		padding: 8px 14px;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		background: var(--bg-card);
		font-size: 13px;
		color: var(--text-dark);
		cursor: pointer;
		font-family: inherit;
	}
	.date-chip.active, .time-chip.active { background: var(--primary); color: var(--text-white); border-color: var(--primary); }
	.date-chip.inactive { border-style: dashed; color: var(--text-muted); cursor: default; }
	.time-chip:disabled { opacity: 0.4; cursor: not-allowed; }
	.remaining { display: block; font-size: 10px; opacity: 0.7; text-align: center; }
	.hint { font-size: 13px; color: var(--text-muted); }

	/* ── Action buttons ──────────────────────── */
	.actions-cell { display: flex; gap: 4px; flex-wrap: wrap; }
	.btn-view-estimate {
		display: inline-flex; align-items: center; gap: 4px;
		padding: 4px 10px; border: 1px solid #dbeafe; border-radius: var(--radius-sm);
		background: #eef2ff; color: #4f46e5; font-size: 11px; font-weight: 600;
		cursor: pointer; font-family: inherit;
	}
	.btn-view-estimate:hover { background: #e0e7ff; }
	.btn-sign { gap: 6px; }
	.btn-acknowledge {
		width: 100%; padding: 10px 16px;
		border: none; border-radius: var(--radius-md);
		background: #059669; color: #fff;
		font-size: 14px; font-weight: 600; cursor: pointer;
		font-family: inherit;
	}
	.btn-acknowledge:hover { background: #047857; }
	.btn-acknowledge:disabled { opacity: 0.5; cursor: not-allowed; }

	/* ── Estimate drawer ─────────────────────── */
	.drawer-wide { width: 600px; max-height: 85vh; display: flex; flex-direction: column; }
	.drawer-wide .modal-body { overflow-y: auto; flex: 1; }
	.est-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; font-size: 0.85rem; color: var(--text-muted); }
	.est-section { margin-bottom: 1rem; }
	.est-section h3 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin: 0 0 0.4rem; }
	.est-table { border: 1px solid var(--border); border-radius: var(--radius-sm); overflow: hidden; }
	.est-row { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.75rem; font-size: 0.82rem; border-bottom: 1px solid var(--border-lighter); }
	.est-row:last-child { border-bottom: none; }
	.est-row:nth-child(even) { background: var(--bg-muted); }
	.est-desc { flex: 1; font-weight: 500; color: var(--text-dark); }
	.est-detail { width: 8rem; color: var(--text-light); font-size: 0.78rem; text-align: right; }
	.est-total { width: 6rem; text-align: right; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; }
	.est-summary { background: #f8faff; border: 1px solid #dce6f5; border-radius: var(--radius-sm); padding: 0.75rem 1rem; }
	.s-row { display: flex; justify-content: space-between; padding: 0.25rem 0; font-size: 0.85rem; }
	.s-tax { color: var(--text-muted); font-size: 0.8rem; }
	.s-divider { border-top: 1px solid #e2e8f0; margin: 0.35rem 0; }
	.s-total { padding-top: 0.15rem; }
	.total-val { font-size: 1.2rem; font-weight: 800; color: #059669; }
	.est-notes { font-style: italic; color: var(--text-light); font-size: 0.85rem; margin: 0; background: var(--bg-muted); padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); }
	.est-empty { text-align: center; color: var(--text-muted); padding: 2rem; }
</style>
