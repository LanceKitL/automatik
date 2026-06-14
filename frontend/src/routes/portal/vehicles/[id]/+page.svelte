<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { getVehicleDetail, getTestDriveSlots, createBooking, reserveVehicle, payReservationFee, resolvePhotoUrl, submitInquiry } from '$lib/services/api';
	import type { VehicleItem, ServiceSlot } from '$lib/services/api';
	import { ChevronLeft, ChevronRight, Car, MessageSquare, CheckCircle, Calculator } from '@lucide/svelte';
	import CheckAnimation from '$lib/components/CheckAnimation.svelte';

	let { params } = $props();

	type AppointmentType = 'test_drive' | 'inquire' | 'reserve';

	const typeMeta: Record<AppointmentType, { label: string; desc: string; icon: any }> = {
		test_drive: {
			label: 'Test Drive',
			desc: 'Drive the unit around our showroom loop',
			icon: Car,
		},
		inquire: {
			label: 'Inquire',
			desc: 'Ask a question or leave a note about this vehicle',
			icon: MessageSquare,
		},
		reserve: {
			label: 'Reserve',
			desc: 'Reserve this vehicle for purchase',
			icon: CheckCircle,
		},
	};

	let vehicle = $state<VehicleItem | null>(null);
	let loading = $state(true);
	let error = $state('');

	let photoIndex = $state(0);
	let selectedType = $state<AppointmentType | null>(null);

	// Test Drive state
	let tdAllSlots = $state<ServiceSlot[]>([]);
	let tdLoading = $state(false);
	let tdSelectedDate = $state<string | null>(null);
	let tdSelectedSlot = $state<number | null>(null);
	let tdBooking = $state(false);
	let tdDone = $state(false);
	let showBookingModal = $state(false);
	let tdBookingConfirming = $state(false);
	let tdSelectedSlotObj = $derived(tdSlots.find(s => s.slot_id === tdSelectedSlot) ?? null);

	let tdDateGroups = $derived.by(() => {
		const map = new Map<string, ServiceSlot[]>();
		for (const s of tdAllSlots) {
			const dt = parseDT(s.slot_datetime);
			if (isNaN(dt.getTime())) continue;
			const key = dt.toISOString().slice(0, 10);
			if (!map.has(key)) map.set(key, []);
			map.get(key)!.push(s);
		}
		return [...map.entries()].sort(([a], [b]) => a.localeCompare(b));
	});

	let tdSlots = $derived(tdSelectedDate ? (tdDateGroups.find(([d]) => d === tdSelectedDate)?.[1] ?? []) : []);

	// Inquire state
	let inquireMsg = $state('');
	let inquireSending = $state(false);
	let inquireDone = $state(false);

	// Reserve state
	type ReserveState = 'idle' | 'reserving' | 'fee_modal' | 'paying' | 'success_modal' | 'done';
	let reserveState = $state<ReserveState>('idle');
	let inquiryId = $state<number | null>(null);

	// Loan Calculator state
	const INTEREST_RATE = 6.5;
	let downPayment = $state(0);
	let termMonths = $state(36);
	let loanAmount = $derived(vehicle ? Number(vehicle.price) - downPayment : 0);
	let calcMonthly = $derived.by(() => {
		const P = loanAmount;
		const n = termMonths;
		if (P <= 0 || n < 1) return 0;
		const r = INTEREST_RATE / 100 / 12;
		if (r === 0) return P / n;
		return (P * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
	});
	let calcTotalPayment = $derived(calcMonthly * termMonths);
	let calcTotalInterest = $derived(calcTotalPayment - loanAmount);

	onMount(async () => {
		try {
			const res = await getVehicleDetail(Number(params.id));
			vehicle = res.data;
		} catch {
			error = 'Vehicle not found.';
		} finally {
			loading = false;
		}
	});

	function selectType(t: AppointmentType) {
		if (vehicle?.status === 'reserved' && t !== 'reserve' && t !== 'inquire') return;
		selectedType = t;
		reserveState = 'idle';
		inquiryId = null;
		tdDone = false;
		inquireDone = false;
		tdSelectedSlot = null;
		tdSelectedDate = null;
		tdAllSlots = [];

		if (t === 'test_drive') {
			fetchAllTdSlots();
		}
	}

	async function fetchAllTdSlots() {
		tdLoading = true;
		try {
			const res = await getTestDriveSlots(undefined, 'test_drive');
			tdAllSlots = res.data;
		} catch {
			tdAllSlots = [];
		} finally {
			tdLoading = false;
		}
	}

	function handleBook() {
		if (!tdSelectedSlot || !vehicle) return;
		showBookingModal = true;
	}

	async function handleConfirmBooking() {
		if (!tdSelectedSlot || !vehicle) return;
		tdBookingConfirming = true;
		try {
			await createBooking(tdSelectedSlot, vehicle.vehicle_id, 'test_drive');
			showBookingModal = false;
			tdDone = true;
			toast.success('Test drive booked!');
		} catch {
			toast.error('Failed to book test drive.');
		} finally {
			tdBookingConfirming = false;
		}
	}

	async function handleInquire() {
		if (!inquireMsg.trim() || !vehicle) return;
		inquireSending = true;
		try {
			await submitInquiry(vehicle.vehicle_id, inquireMsg.trim());
			inquireDone = true;
			toast.success('An agent will follow up shortly.');
		} catch {
			toast.error('Failed to send inquiry.');
		} finally {
			inquireSending = false;
		}
	}

	async function handleReserve() {
		if (!vehicle) return;
		reserveState = 'reserving';
		try {
			const res = await reserveVehicle(vehicle.vehicle_id);
			inquiryId = res.inquiry_id;
			vehicle = { ...vehicle, status: 'reserved' };
			reserveState = 'fee_modal';
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to reserve vehicle.');
			reserveState = 'idle';
		}
	}

	async function handlePayFee() {
		if (!inquiryId) return;
		try {
			await payReservationFee(inquiryId);
			reserveState = 'paying';
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Payment failed.');
		}
	}

	function handlePaymentDone() {
		reserveState = 'success_modal';
	}

	function formatPrice(p: string) {
		return `₱${Number(p).toLocaleString()}`;
	}

	function parseDT(iso: string) {
		const s = String(iso);
		if (s.includes('Z') || s.includes('+') || s.endsWith('GMT') || s.endsWith('UTC')) {
			return new Date(s);
		}
		if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return new Date(s);
		return new Date(s.replace(' ', 'T') + '+08:00');
	}

	function formatDate(iso: string) {
		const d = parseDT(iso);
		if (isNaN(d.getTime())) return '—';
		return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
	}

	function formatDateShort(iso: string) {
		const d = parseDT(iso);
		if (isNaN(d.getTime())) return '—';
		return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
	}

	function formatTime(iso: string) {
		const d = parseDT(iso);
		if (isNaN(d.getTime())) return '—';
		return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
	}
</script>

{#if loading}
	<p class="loading">Loading vehicle…</p>
{:else if error || !vehicle}
	<p class="error">{error || 'Vehicle not found.'}</p>
{:else}
	<div class="page">
		<!-- LEFT: Vehicle Detail -->
		<div class="left">
			<div class="gallery">
				{#if resolvePhotoUrl(vehicle.photos?.[photoIndex]?.photo_url ?? null)}
					<img
						src={resolvePhotoUrl(vehicle.photos[photoIndex].photo_url)}
						alt="{vehicle.brand} {vehicle.model}"
						class="main-photo"
					/>
				{:else}
					<div class="no-photo">No Image</div>
				{/if}
				{#if (vehicle.photos?.length ?? 0) > 1}
					<div class="gallery-nav">
						<button onclick={() => photoIndex = Math.max(0, photoIndex - 1)} disabled={photoIndex === 0}>
							<ChevronLeft size={18} />
						</button>
						<span>{photoIndex + 1} / {vehicle.photos.length}</span>
						<button onclick={() => photoIndex = Math.min(vehicle.photos.length - 1, photoIndex + 1)} disabled={photoIndex >= vehicle.photos.length - 1}>
							<ChevronRight size={18} />
						</button>
					</div>
				{/if}
			</div>

			<h1>{vehicle.brand} {vehicle.model}</h1>
			<div class="price">{formatPrice(vehicle.price)}</div>
			<div class="meta">{vehicle.year} &middot; {vehicle.color ?? 'N/A'}</div>

			<div class="status-badge" class:reserved={vehicle.status === 'reserved'}>
				{vehicle.status}
			</div>

			<div class="specs">
				<div><span>Body Type</span>{vehicle.body_type ?? 'N/A'}</div>
				<div><span>Transmission</span>{vehicle.transmission ?? 'N/A'}</div>
				<div><span>Fuel Type</span>{vehicle.fuel_type ?? 'N/A'}</div>
				<div><span>Seating</span>{vehicle.seating_capacity ?? 'N/A'}</div>
				<div><span>VIN</span><span class="vin">{vehicle.vin}</span></div>
			</div>
		</div>

		<!-- RIGHT: Appointment Booking + Loan Calculator -->
		<div class="right">
			<div class="booking-col">
				<h2>Book an Appointment</h2>

				{#if vehicle.status === 'reserved'}
					<p class="reserved-note">This vehicle is reserved.</p>
				{/if}

				<div class="type-list">
					{#each Object.entries(typeMeta) as [key, meta]}
						{@const type = key as AppointmentType}
						<button
							class="type-card"
							class:selected={selectedType === type}
							class:muted={vehicle.status === 'reserved' && type === 'test_drive'}
							onclick={() => selectType(type)}
							disabled={vehicle.status === 'reserved' && type === 'test_drive'}
						>
							<svelte:component this={meta.icon} size={22} />
							<div class="type-text">
								<div class="type-label">{meta.label}</div>
								<div class="type-desc">{meta.desc}</div>
							</div>
						</button>
					{/each}
				</div>

				<!-- Test Drive -->
				{#if selectedType === 'test_drive'}
					<div class="booking-form">
						{#if tdDone}
							<p class="done">Test drive booked! You'll receive a confirmation.</p>
						{:else}
							{#if tdLoading}
								<p class="hint">Loading available dates…</p>
							{:else if tdDateGroups.length === 0}
								<p class="hint">No test drive slots are currently available. Please check back later or contact the dealership.</p>
							{:else}
								<p class="section-label">Select a date</p>
								<div class="date-group-list">
									{#each tdDateGroups as [date, slots]}
										<button
											class="date-chip"
											class:selected={tdSelectedDate === date}
											onclick={() => {
												tdSelectedDate = date;
												tdSelectedSlot = null;
											}}
										>
											<span class="date-label">{formatDateShort(date)}</span>
											<span class="slot-count">{slots.length} slot{slots.length !== 1 ? 's' : ''}</span>
										</button>
									{/each}
								</div>

								{#if tdSelectedDate && tdSlots.length > 0}
									<p class="section-label">Select a time for {formatDateShort(tdSelectedDate)}</p>
									<div class="slot-list">
										{#each tdSlots as s}
											<button
												class="slot-item"
												class:selected={tdSelectedSlot === s.slot_id}
												onclick={() => tdSelectedSlot = s.slot_id}
											>
												{formatTime(s.slot_datetime)}
												<span class="remaining">{s.remaining} slot{s.remaining !== 1 ? 's' : ''} left</span>
											</button>
										{/each}
									</div>
								{/if}
							{/if}

							<button class="book-btn" onclick={handleBook} disabled={!tdSelectedSlot || tdBooking}>
								{tdBooking ? 'Booking…' : 'Book Test Drive'}
							</button>
						{/if}
					</div>
				{/if}

				<!-- Inquire -->
				{#if selectedType === 'inquire'}
					<div class="booking-form">
						{#if inquireDone}
							<p class="done">Inquiry sent! An agent will follow up.</p>
						{:else}
							<label>
								Your Message
								<textarea
									bind:value={inquireMsg}
									rows="4"
									placeholder="Ask a question or leave a note about this vehicle…"
								/>
							</label>
							<button class="book-btn inquire-btn" onclick={handleInquire} disabled={inquireSending || !inquireMsg.trim()}>
								{inquireSending ? 'Sending…' : 'Send Inquiry'}
							</button>
						{/if}
					</div>
				{/if}

				<!-- Reserve -->
				{#if selectedType === 'reserve'}
					<div class="booking-form">
						{#if reserveState === 'done'}
							<p class="done">Vehicle reserved! An agent will follow up.</p>
						{:else if vehicle.status === 'reserved'}
							<p class="hint">This vehicle is already reserved.</p>
						{:else if reserveState === 'idle'}
							<p class="confirm-text">Are you sure you want to reserve the {vehicle.brand} {vehicle.model}?</p>
							<button class="book-btn reserve-btn" onclick={handleReserve}>
								Confirm Reserve
							</button>
						{:else if reserveState === 'reserving'}
							<p class="hint">Reserving…</p>
						{/if}
					</div>
				{/if}
			</div>

			<!-- Loan Calculator -->
			<div class="calc-card">
				<div class="calc-header">
					<Calculator size={18} />
					<span>Loan Calculator</span>
				</div>
				<div class="rate-badge">Fixed {INTEREST_RATE}% p.a. interest</div>

				<div class="calc-fields">
					<label>
						Down Payment (₱)
						<input type="number" bind:value={downPayment} min="0" step={50000} placeholder="0" />
					</label>
					<label>
						Term
						<select bind:value={termMonths}>
							<option value={12}>12 months</option>
							<option value={24}>24 months</option>
							<option value={36}>36 months</option>
							<option value={48}>48 months</option>
							<option value={60}>60 months</option>
						</select>
					</label>
				</div>

				<div class="calc-breakdown">
					<div class="calc-row">
						<span>Vehicle Price</span>
						<span>{formatPrice(String(vehicle.price))}</span>
					</div>
					<div class="calc-row">
						<span>Down Payment</span>
						<span class="down-pay">− {formatPrice(String(downPayment))}</span>
					</div>
					<div class="calc-divider" />
					<div class="calc-row total-row">
						<span>Loan Amount</span>
						<span class="mono">{formatPrice(String(Math.round(loanAmount)))}</span>
					</div>
					<div class="calc-divider" />
					<div class="calc-row amort-row">
						<span>Monthly Amortization</span>
						<span class="mono primary">{formatPrice(String(Math.round(calcMonthly)))}</span>
					</div>
					<div class="calc-row">
						<span>Total Payment</span>
						<span class="mono">{formatPrice(String(Math.round(calcTotalPayment)))}</span>
					</div>
					<div class="calc-row">
						<span>Total Interest</span>
						<span class="mono interest">{formatPrice(String(Math.round(calcTotalInterest)))}</span>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Test Drive Confirmation Modal -->
	{#if showBookingModal && tdSelectedSlotObj}
		<div class="modal-overlay" onclick={() => showBookingModal = false} />
		<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog">
			<div class="modal-header">
				<h3>Confirm Test Drive</h3>
				<button class="modal-close" onclick={() => showBookingModal = false}>×</button>
			</div>
			<div class="modal-body">
				<p class="td-datetime">{formatDate(tdSelectedSlotObj.slot_datetime)}</p>
				<div class="reminder-box">
					<strong>Please remember to bring:</strong>
					<ul>
						<li>Valid Driver's Licence</li>
					</ul>
				</div>
				<div class="policy-box">
					<strong>Test Drive Policy:</strong>
					<ul>
						<li>A valid Driver's Licence is required.</li>
						<li>You must be at least 18 years old.</li>
						<li>Test drive is limited to the designated route around the dealership.</li>
						<li>A dealership representative will accompany you during the test drive.</li>
						<li>The customer is responsible for any traffic violations incurred during the test drive.</li>
					</ul>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={() => showBookingModal = false}>Cancel</button>
				<button class="btn-primary" onclick={handleConfirmBooking} disabled={tdBookingConfirming}>
					{tdBookingConfirming ? 'Booking…' : 'Confirm Booking'}
				</button>
			</div>
		</div>
	{/if}

	<!-- Reservation Fee Modal -->
	{#if reserveState === 'fee_modal' && vehicle}
		<div class="modal-overlay" onclick={() => reserveState = 'done'} />
		<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog">
			<div class="modal-header">
				<h3>Reservation Fee Required</h3>
				<button class="modal-close" onclick={() => reserveState = 'done'}>×</button>
			</div>
			<div class="modal-body">
				<p>To confirm your reservation for the <strong>{vehicle.brand} {vehicle.model}</strong>, a reservation fee of <strong>₱5,000.00</strong> is required.</p>
				<p class="fee-note">You can pay this fee online now or at the dealership.</p>
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={() => reserveState = 'done'}>Pay Later</button>
				<button class="btn-primary" onclick={handlePayFee}>Pay ₱5,000</button>
			</div>
		</div>
	{/if}

	<!-- Payment Animation -->
	{#if reserveState === 'paying'}
		<CheckAnimation onAnimationEnd={handlePaymentDone} />
	{/if}

	<!-- Success Modal -->
	{#if reserveState === 'success_modal' && vehicle}
		<div class="modal-overlay" onclick={() => reserveState = 'done'} />
		<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog">
			<div class="modal-header success-header">
				<h3>Reservation Complete!</h3>
			</div>
			<div class="modal-body">
				<div class="success-icon">✓</div>
				<p>Your reservation for the <strong>{vehicle.brand} {vehicle.model}</strong> is confirmed.</p>
				<p>You may visit the dealership at any time. An agent will be ready to assist you.</p>
				<div class="reminder-box">
					<strong>Please remember to bring:</strong>
					<ul>
						<li>Valid Driver's Licence</li>
						<li>Proof of Billing &amp; Address</li>
						<li>Government Issued ID</li>
					</ul>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-primary" onclick={() => reserveState = 'done'}>Done</button>
			</div>
		</div>
	{/if}
{/if}

<style>
	.loading, .error {
		padding: 48px 0;
		text-align: center;
		color: var(--text-muted);
		font-size: 14px;
	}
	.error {
		color: var(--red);
	}

	.page {
		display: flex;
		gap: 32px;
	}

	/* LEFT PANEL */
	.left {
		width: 440px;
		flex-shrink: 0;
	}
	.gallery {
		margin-bottom: 16px;
	}
	.main-photo {
		width: 100%;
		height: 300px;
		object-fit: cover;
		border-radius: var(--radius-md);
		display: block;
		background: var(--bg-hover);
	}
	.no-photo {
		height: 300px;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--text-muted);
		font-size: 14px;
		background: var(--bg-hover);
		border-radius: var(--radius-md);
	}
	.gallery-nav {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 12px;
		margin-top: 8px;
	}
	.gallery-nav button {
		background: var(--bg-hover);
		border: none;
		border-radius: var(--radius-sm);
		padding: 4px 8px;
		cursor: pointer;
		color: var(--text-dark);
	}
	.gallery-nav button:disabled {
		opacity: 0.4;
		cursor: default;
	}
	.gallery-nav span {
		font-size: 12px;
		color: var(--text-muted);
	}

	.left h1 {
		font-size: 22px;
		font-weight: 700;
		color: var(--text-dark);
		margin: 0 0 4px;
	}
	.price {
		font-size: 20px;
		font-weight: 700;
		color: var(--blue-dark);
		margin-bottom: 2px;
	}
	.meta {
		font-size: 13px;
		color: var(--text-muted);
		margin-bottom: 10px;
	}
	.status-badge {
		display: inline-block;
		font-size: 11px;
		font-weight: 600;
		color: #059669;
		background: #d1fae5;
		padding: 2px 10px;
		border-radius: var(--radius-sm);
		text-transform: capitalize;
		margin-bottom: 16px;
	}
	.status-badge.reserved {
		color: #d97706;
		background: #fef3c7;
	}

	.specs {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 8px;
	}
	.specs div {
		font-size: 13px;
		color: var(--text-dark);
	}
	.specs div span {
		display: block;
		font-size: 11px;
		color: var(--text-muted);
		margin-bottom: 1px;
	}
	.specs .vin {
		font-size: 11px;
		word-break: break-all;
		font-family: monospace;
	}

	/* RIGHT PANEL */
	.right {
		display: flex;
		gap: 20px;
		align-items: flex-start;
		flex: 1;
		min-width: 0;
	}
	.booking-col {
		flex: 1;
		min-width: 0;
	}
	.booking-col h2 {
		font-size: 20px;
		font-weight: 700;
		color: var(--text-dark);
		margin: 0 0 16px;
	}
	.reserved-note {
		font-size: 13px;
		color: #d97706;
		background: #fef3c7;
		padding: 8px 12px;
		border-radius: var(--radius-md);
		margin-bottom: 12px;
	}

	.type-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
		margin-bottom: 16px;
	}
	.type-card {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 14px 16px;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		background: var(--bg-card);
		cursor: pointer;
		font-family: inherit;
		font-size: inherit;
		text-align: left;
		transition: all 0.15s;
		color: var(--text-dark);
	}
	.type-card:hover:not(:disabled) {
		border-color: var(--blue);
		box-shadow: 0 2px 8px rgba(59,130,246,0.08);
	}
	.type-card.selected {
		border-color: var(--blue);
		background: var(--blue-bg);
	}
	.type-card.muted, .type-card:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
	.type-card svg {
		flex-shrink: 0;
		color: var(--blue);
	}
	.type-card.selected svg {
		color: #1d4ed8;
	}
	.type-text {
		flex: 1;
		min-width: 0;
	}
	.type-label {
		font-size: 14px;
		font-weight: 600;
		color: var(--text-dark);
	}
	.type-desc {
		font-size: 12px;
		color: var(--text-light);
		margin-top: 1px;
		line-height: 1.4;
	}

	/* Booking form */
	.booking-form {
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		padding: 16px;
		background: var(--bg-muted);
	}
	.booking-form label {
		display: block;
		font-size: 12px;
		font-weight: 500;
		color: var(--text-dark);
		margin-bottom: 8px;
	}
	.booking-form label input,
	.booking-form label textarea {
		display: block;
		margin-top: 4px;
		padding: 8px 10px;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		font-size: 13px;
		font-family: inherit;
		width: 100%;
		box-sizing: border-box;
	}
	.booking-form label textarea {
		resize: vertical;
	}
	.hint {
		font-size: 12px;
		color: var(--text-muted);
		margin: 8px 0;
	}
	.done {
		font-size: 14px;
		color: #059669;
		font-weight: 500;
	}
	.confirm-text {
		font-size: 13px;
		color: var(--text-dark);
		margin: 0 0 12px;
	}
	.section-label {
		font-size: 12px;
		font-weight: 600;
		color: var(--text-dark);
		margin: 12px 0 6px;
	}
	.date-group-list {
		display: flex;
		flex-direction: column;
		gap: 4px;
		margin: 8px 0;
		max-height: 200px;
		overflow-y: auto;
	}
	.date-chip {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 10px 12px;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		background: var(--bg-card);
		font-size: 13px;
		font-family: inherit;
		cursor: pointer;
		text-align: left;
		transition: all 0.15s;
		color: var(--text-dark);
	}
	.date-chip:hover {
		border-color: var(--blue);
	}
	.date-chip.selected {
		border-color: var(--blue);
		background: var(--blue-bg);
	}
	.date-label {
		font-weight: 600;
	}
	.slot-count {
		font-size: 11px;
		color: var(--text-muted);
	}
	.slot-list {
		display: flex;
		flex-direction: column;
		gap: 4px;
		margin: 8px 0;
		max-height: 180px;
		overflow-y: auto;
	}
	.slot-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 10px;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: var(--bg-card);
		font-size: 13px;
		cursor: pointer;
		font-family: inherit;
		text-align: left;
		transition: all 0.15s;
	}
	.slot-item:hover {
		border-color: var(--blue);
	}
	.slot-item.selected {
		border-color: var(--blue);
		background: var(--blue-bg);
	}
	.remaining {
		font-size: 11px;
		color: var(--text-muted);
	}
	.book-btn {
		width: 100%;
		margin-top: 10px;
		padding: 10px;
		border: none;
		border-radius: var(--radius-md);
		background: var(--blue);
		color: var(--text-white);
		font-size: 14px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
		transition: background 0.15s;
	}
	.book-btn:hover:not(:disabled) {
		background: #2563eb;
	}
	.book-btn:disabled {
		opacity: 0.5;
		cursor: default;
	}
	.book-btn.inquire-btn {
		background: #8b5cf6;
	}
	.book-btn.inquire-btn:hover:not(:disabled) {
		background: #7c3aed;
	}
	.book-btn.reserve-btn {
		background: #059669;
	}
	.book-btn.reserve-btn:hover:not(:disabled) {
		background: #047857;
	}

	/* Loan Calculator */
	.calc-card {
		width: 280px;
		flex-shrink: 0;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		padding: 16px;
		background: var(--bg-muted);
	}
	.calc-header {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 16px;
		font-weight: 700;
		color: var(--text-dark);
		margin-bottom: 6px;
	}
	.calc-header svg {
		color: var(--blue);
	}
	.rate-badge {
		display: inline-block;
		font-size: 11px;
		font-weight: 600;
		color: #059669;
		background: #d1fae5;
		padding: 2px 10px;
		border-radius: var(--radius-sm);
		margin-bottom: 14px;
	}
	.calc-fields {
		display: flex;
		flex-direction: column;
		gap: 10px;
		margin-bottom: 16px;
	}
	.calc-fields label {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 4px;
		font-size: 12px;
		font-weight: 500;
		color: var(--text-dark);
	}
	.calc-fields input,
	.calc-fields select {
		padding: 8px 10px;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		font-size: 13px;
		font-family: inherit;
		background: var(--bg-card);
		outline: none;
	}
	.calc-fields input:focus,
	.calc-fields select:focus {
		border-color: var(--blue);
		box-shadow: 0 0 0 2px rgba(59,130,246,0.15);
	}
	.calc-breakdown {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}
	.calc-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-size: 13px;
		color: var(--text-dark);
	}
	.calc-row span:first-child {
		color: var(--text-light);
	}
	.calc-row .mono {
		font-family: monospace;
		font-weight: 600;
		color: var(--text-dark);
	}
	.calc-row .down-pay {
		color: var(--red);
	}
	.calc-row .primary {
		color: var(--blue-dark);
		font-size: 15px;
	}
	.calc-row .interest {
		color: var(--warning);
	}
	.calc-row.total-row span:last-child {
		color: var(--text-dark);
		font-weight: 700;
	}
	.calc-row.amort-row {
		padding: 4px 0;
	}
	.calc-divider {
		height: 1px;
		background: var(--border);
		margin: 2px 0;
	}

	/* Modal styles */
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
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		background: var(--bg-card);
		border-radius: var(--radius-lg);
		width: 440px;
		max-width: 90vw;
		box-shadow: 0 20px 60px rgba(0,0,0,0.25);
		z-index: 101;
	}
	.modal-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 20px 24px 0;
	}
	.modal-header h3 {
		font-size: 18px;
		font-weight: 700;
		color: var(--text-dark);
		margin: 0;
	}
	.modal-header.success-header {
		justify-content: center;
		padding-top: 32px;
	}
	.modal-close {
		background: none;
		border: none;
		font-size: 24px;
		color: var(--text-muted);
		cursor: pointer;
		padding: 0;
		line-height: 1;
	}
	.modal-body {
		padding: 16px 24px 8px;
		font-size: 14px;
		color: var(--text-dark);
		line-height: 1.5;
	}
	.modal-body p {
		margin: 0 0 10px;
	}
	.fee-note {
		font-size: 13px;
		color: var(--text-muted);
	}
	.success-icon {
		width: 56px;
		height: 56px;
		border-radius: 50%;
		background: #d1fae5;
		color: #059669;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 28px;
		font-weight: 700;
		margin: 0 auto 16px;
	}
	.td-datetime {
		font-size: 16px;
		font-weight: 700;
		text-align: center;
		margin-bottom: 16px;
		color: var(--text-dark);
	}
	.reminder-box {
		background: #fef3c7;
		border-radius: var(--radius-md);
		padding: 12px 16px;
		margin-top: 12px;
		font-size: 13px;
		color: #92400e;
		line-height: 1.5;
	}
	.reminder-box ul {
		margin: 6px 0 0;
		padding-left: 18px;
	}
	.reminder-box li {
		margin-bottom: 2px;
	}
	.policy-box {
		background: #e0f2fe;
		border-radius: var(--radius-md);
		padding: 12px 16px;
		margin-top: 12px;
		font-size: 13px;
		color: #075985;
		line-height: 1.5;
	}
	.policy-box ul {
		margin: 6px 0 0;
		padding-left: 18px;
	}
	.policy-box li {
		margin-bottom: 3px;
	}
	.modal-footer {
		display: flex;
		gap: 10px;
		justify-content: flex-end;
		padding: 16px 24px 24px;
	}
	.btn-primary {
		padding: 10px 24px;
		border: none;
		border-radius: var(--radius-md);
		background: #059669;
		color: #fff;
		font-size: 14px;
		font-weight: 600;
		font-family: inherit;
		cursor: pointer;
		transition: background 0.15s;
	}
	.btn-primary:hover {
		background: #047857;
	}
	.btn-secondary {
		padding: 10px 24px;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		background: var(--bg-card);
		color: var(--text-dark);
		font-size: 14px;
		font-weight: 500;
		font-family: inherit;
		cursor: pointer;
		transition: background 0.15s;
	}
	.btn-secondary:hover {
		background: var(--bg-hover);
	}
</style>
