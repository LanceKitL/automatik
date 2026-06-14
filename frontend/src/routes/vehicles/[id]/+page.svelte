<script lang="ts">
	import { onMount } from 'svelte';
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { toast } from 'svelte-sonner';
	import { getPublicVehicleDetail, getServiceSlots, guestReserveVehicle, guestPayReservationFee, guestCreateBooking, submitGuestInquiry, resolvePhotoUrl } from '$lib/services/api';
	import type { VehicleItem } from '$lib/services/api';
	import { ChevronLeft, ChevronRight, Car, MessageSquare, CheckCircle, X, CreditCard, Users, Cog, Fuel, Calculator } from '@lucide/svelte';
	import { goto } from '$app/navigation';

	let { params } = $props();

	let vehicle = $state<VehicleItem | null>(null);
	let loading = $state(true);
	let error = $state('');

	let photoIndex = $state(0);

	// Modal state
	type ModalType = 'none' | 'inquire' | 'reserve' | 'test_drive';
	let activeModal = $state<{ type: ModalType; vehicle: VehicleItem } | null>(null);

	let inquireForm = $state({ name: '', email: '', phone: '', message: '' });
	let inquireSending = $state(false);
	let inquireDone = $state(false);

	let reserveStep = $state<'form' | 'pay' | 'done'>('form');
	let reserveForm = $state({ name: '', email: '', phone: '' });
	let reserveSending = $state(false);
	let reserveInquiryId = $state<number | null>(null);
	let reservePaying = $state(false);

	let tdStep = $state<'form' | 'slot' | 'done'>('form');
	let tdForm = $state({ name: '', email: '', phone: '' });
	let tdSlots = $state<Record<string, unknown>[]>([]);
	let tdDateGroups = $state<[string, Record<string, unknown>[]][]>([]);
	let tdSelectedDate = $state<string | null>(null);
	let tdSelectedSlot = $state<number | null>(null);
	let tdLoading = $state(false);
	let tdSending = $state(false);

	// Loan Calculator
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
			const res = await getPublicVehicleDetail(Number(params.id));
			vehicle = res.data;
		} catch {
			error = 'Vehicle not found.';
		} finally {
			loading = false;
		}
	});

	function openInquire(v: VehicleItem) {
		inquireForm = { name: '', email: '', phone: '', message: '' };
		inquireDone = false;
		activeModal = { type: 'inquire', vehicle: v };
	}

	function openReserve(v: VehicleItem) {
		reserveForm = { name: '', email: '', phone: '' };
		reserveStep = 'form';
		reserveInquiryId = null;
		activeModal = { type: 'reserve', vehicle: v };
	}

	function openTestDrive(v: VehicleItem) {
		tdForm = { name: '', email: '', phone: '' };
		tdStep = 'form';
		tdSlots = [];
		tdDateGroups = [];
		tdSelectedDate = null;
		tdSelectedSlot = null;
		activeModal = { type: 'test_drive', vehicle: v };
	}

	function closeModal() { activeModal = null; }

	async function handleSendInquiry() {
		if (!activeModal || !inquireForm.name || !inquireForm.email || !inquireForm.message) return;
		inquireSending = true;
		try {
			await submitGuestInquiry({ vehicle_id: activeModal.vehicle.vehicle_id, name: inquireForm.name, email: inquireForm.email, number: inquireForm.phone || undefined, message: inquireForm.message });
			inquireDone = true;
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to send inquiry.');
		} finally { inquireSending = false; }
	}

	async function handleReserve() {
		if (!activeModal || !reserveForm.name || !reserveForm.email) return;
		reserveSending = true;
		try {
			const res = await guestReserveVehicle(activeModal.vehicle.vehicle_id, { guest_name: reserveForm.name, guest_email: reserveForm.email, guest_number: reserveForm.phone || undefined });
			reserveInquiryId = res.inquiry_id;
			reserveStep = 'pay';
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to reserve.');
		} finally { reserveSending = false; }
	}

	async function handleReservePay() {
		if (!reserveInquiryId) return;
		reservePaying = true;
		try {
			await guestPayReservationFee(reserveInquiryId);
			reserveStep = 'done';
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Payment failed.');
		} finally { reservePaying = false; }
	}

	async function handleLoadSlots() {
		if (!activeModal) return;
		tdLoading = true;
		try {
			const res = await getServiceSlots(undefined, 'test_drive');
			const all = res.data as Record<string, unknown>[];
			tdSlots = all;
			const groups = new Map<string, Record<string, unknown>[]>();
			for (const s of all) {
				const d = new Date(String(s.slot_datetime)).toISOString().slice(0, 10);
				if (!groups.has(d)) groups.set(d, []);
				groups.get(d)!.push(s);
			}
			tdDateGroups = [...groups.entries()].sort(([a], [b]) => a.localeCompare(b));
		} catch { tdSlots = []; tdDateGroups = []; }
		finally { tdLoading = false; }
	}

	async function handleBookTestDrive() {
		if (!activeModal || !tdSelectedSlot) return;
		tdSending = true;
		try {
			await guestCreateBooking({ guest_name: tdForm.name, guest_email: tdForm.email, guest_number: tdForm.phone || undefined, slot_id: tdSelectedSlot, vehicle_id: activeModal.vehicle.vehicle_id, booking_type: 'test_drive' });
			tdStep = 'done';
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Booking failed.');
		} finally { tdSending = false; }
	}

	function formatPrice(p: string) {
		return `₱${Number(p).toLocaleString()}`;
	}

	function formatDateShort(iso: string) {
		return new Date(iso).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
	}
	function formatTime(iso: string) {
		return new Date(iso).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
	}
	function tdSlotsForDate(date: string) {
		return tdSlots.filter((s) => new Date(String(s.slot_datetime)).toISOString().slice(0, 10) === date);
	}
</script>

<Navbar />

<div class="page">
	{#if loading}
		<div class="loader-wrap"><div class="spinner"></div></div>
	{:else if error || !vehicle}
		<div class="error-msg">{error || 'Vehicle not found.'}</div>
	{:else}
		<div class="detail-layout">
			<!-- LEFT: Photo Gallery -->
			<div class="gallery">
				<div class="main-photo">
					{#if vehicle.photos?.length > 0}
						<img src={resolvePhotoUrl(vehicle.photos[photoIndex]?.photo_url)} alt="{vehicle.brand} {vehicle.model}" />
					{:else}
						<div class="no-photo-lg"><Car size={48} /></div>
					{/if}
					{#if vehicle.photos?.length > 1}
						<button class="nav-btn left" onclick={() => photoIndex = (photoIndex - 1 + vehicle.photos.length) % vehicle.photos.length}><ChevronLeft size={20} /></button>
						<button class="nav-btn right" onclick={() => photoIndex = (photoIndex + 1) % vehicle.photos.length}><ChevronRight size={20} /></button>
					{/if}
				</div>
				{#if vehicle.photos?.length > 1}
					<div class="thumbnails">
						{#each vehicle.photos as photo, i}
							<button class="thumb" class:active={i === photoIndex} onclick={() => photoIndex = i}>
								<img src={resolvePhotoUrl(photo.photo_url)} alt="" />
							</button>
						{/each}
					</div>
				{/if}
			</div>

			<!-- RIGHT: Info + Actions -->
			<div class="info">
				<button class="back-link" onclick={() => goto('/vehicles')}>← Back to Browse</button>

				<h1>{vehicle.brand} {vehicle.model}</h1>
				<div class="year-badge">{vehicle.year}</div>
				<div class="price">{formatPrice(vehicle.price)}</div>
				<div class="status-badge" class:reserved={vehicle.status === 'reserved'}>
					{vehicle.status}
				</div>

				<div class="specs-grid">
					<div class="spec-item"><Cog size={16} /><span>{vehicle.transmission ?? '—'}</span></div>
					<div class="spec-item"><Fuel size={16} /><span>{vehicle.fuel_type ?? '—'}</span></div>
					<div class="spec-item"><Users size={16} /><span>{vehicle.seating_capacity ?? '—'} seater</span></div>
					<div class="spec-item"><Car size={16} /><span>{vehicle.body_type ?? '—'}</span></div>
				</div>

				<div class="details">
					<div class="detail-row"><span class="label">Color</span><span class="value">{vehicle.color ?? '—'}</span></div>
					<div class="detail-row"><span class="label">VIN</span><span class="value mono">{vehicle.vin}</span></div>
				</div>

				<!-- Action Buttons -->
				<div class="actions">
					<button class="btn-action inquiry" onclick={() => openInquire(vehicle!)}>
						<MessageSquare size={18} /> Inquire
					</button>
					<button class="btn-action reserve" onclick={() => openReserve(vehicle!)}>
						<CheckCircle size={18} /> Reserve
					</button>
					<button class="btn-action test-drive" onclick={() => openTestDrive(vehicle!)}>
						<Car size={18} /> Test Drive
					</button>
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
						<div class="calc-row"><span>Vehicle Price</span><span>{formatPrice(String(vehicle.price))}</span></div>
						<div class="calc-row"><span>Down Payment</span><span class="down-pay">− {formatPrice(String(downPayment))}</span></div>
						<div class="calc-divider" />
						<div class="calc-row total-row"><span>Loan Amount</span><span class="mono">{formatPrice(String(Math.round(loanAmount)))}</span></div>
						<div class="calc-divider" />
						<div class="calc-row amort-row"><span>Monthly Amortization</span><span class="mono primary">{formatPrice(String(Math.round(calcMonthly)))}</span></div>
						<div class="calc-row"><span>Total Payment</span><span class="mono">{formatPrice(String(Math.round(calcTotalPayment)))}</span></div>
						<div class="calc-row"><span>Total Interest</span><span class="mono interest">{formatPrice(String(Math.round(calcTotalInterest)))}</span></div>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<!-- Inquire Modal -->
{#if activeModal && activeModal.type === 'inquire'}
	<div class="modal-overlay" onclick={closeModal} role="presentation" />
	<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
		<div class="modal-head">
			<h3>Inquire About {activeModal.vehicle.brand} {activeModal.vehicle.model}</h3>
			<button class="modal-close" onclick={closeModal}><X size={18} /></button>
		</div>
		<div class="modal-body">
			{#if inquireDone}
				<div class="done-msg">Inquiry sent! An agent will follow up shortly.</div>
			{:else}
				<label class="modal-label">Name <span class="req">*</span></label>
				<input class="modal-input" type="text" bind:value={inquireForm.name} placeholder="Your full name" />
				<label class="modal-label">Email <span class="req">*</span></label>
				<input class="modal-input" type="email" bind:value={inquireForm.email} placeholder="your@email.com" />
				<label class="modal-label">Phone</label>
				<input class="modal-input" type="tel" bind:value={inquireForm.phone} placeholder="+63 912 345 6789" />
				<label class="modal-label">Message <span class="req">*</span></label>
				<textarea class="modal-textarea" bind:value={inquireForm.message} rows="3" placeholder="Ask a question or leave a note…"></textarea>
				<button class="modal-btn" onclick={handleSendInquiry} disabled={inquireSending || !inquireForm.name || !inquireForm.email || !inquireForm.message}>
					{inquireSending ? 'Sending…' : 'Send Inquiry'}
				</button>
			{/if}
		</div>
	</div>
{/if}

<!-- Reserve Modal -->
{#if activeModal && activeModal.type === 'reserve'}
	<div class="modal-overlay" onclick={closeModal} role="presentation" />
	<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
		<div class="modal-head">
			<h3>Reserve {activeModal.vehicle.brand} {activeModal.vehicle.model}</h3>
			<button class="modal-close" onclick={closeModal}><X size={18} /></button>
		</div>
		<div class="modal-body">
			{#if reserveStep === 'done'}
				<div class="done-msg">
					<div class="done-icon"><CheckCircle size={40} /></div>
					<strong>Reservation Complete!</strong>
					<p>The vehicle has been reserved. An agent will follow up.</p>
				</div>
			{:else if reserveStep === 'pay'}
				<div class="pay-prompt">
					<CreditCard size={32} />
					<p><strong>Reservation Fee Required</strong></p>
					<p>To confirm your reservation, a fee of <strong>₱5,000.00</strong> is required.</p>
					<div class="pay-actions">
						<button class="modal-btn-secondary" onclick={() => (reserveStep = 'done')}>Pay Later</button>
						<button class="modal-btn" onclick={handleReservePay} disabled={reservePaying}>
							{reservePaying ? 'Processing…' : 'Pay ₱5,000'}
						</button>
					</div>
				</div>
			{:else}
				<label class="modal-label">Name <span class="req">*</span></label>
				<input class="modal-input" type="text" bind:value={reserveForm.name} placeholder="Your full name" />
				<label class="modal-label">Email <span class="req">*</span></label>
				<input class="modal-input" type="email" bind:value={reserveForm.email} placeholder="your@email.com" />
				<label class="modal-label">Phone</label>
				<input class="modal-input" type="tel" bind:value={reserveForm.phone} placeholder="+63 912 345 6789" />
				<button class="modal-btn" onclick={handleReserve} disabled={reserveSending || !reserveForm.name || !reserveForm.email}>
					{reserveSending ? 'Reserving…' : 'Confirm Reserve'}
				</button>
			{/if}
		</div>
	</div>
{/if}

<!-- Test Drive Modal -->
{#if activeModal && activeModal.type === 'test_drive'}
	<div class="modal-overlay" onclick={closeModal} role="presentation" />
	<div class="modal modal-wide" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
		<div class="modal-head">
			<h3>Test Drive {activeModal.vehicle.brand} {activeModal.vehicle.model}</h3>
			<button class="modal-close" onclick={closeModal}><X size={18} /></button>
		</div>
		<div class="modal-body">
			{#if tdStep === 'done'}
				<div class="done-msg">
					<div class="done-icon"><CheckCircle size={40} /></div>
					<strong>Test Drive Booked!</strong>
					<p>You'll receive a confirmation. Please bring a valid driver's licence.</p>
				</div>
			{:else if tdStep === 'slot'}
				{#if tdLoading}
					<p class="hint">Loading available dates…</p>
				{:else if tdDateGroups.length === 0}
					<p class="hint">No test drive slots currently available. Please check back later.</p>
				{:else}
					<p class="modal-label">Select a date</p>
					<div class="date-group-list">
						{#each tdDateGroups as [date, slots]}
							<button class="date-chip" class:selected={tdSelectedDate === date} onclick={() => { tdSelectedDate = date; tdSelectedSlot = null; }}>
								<span class="date-label">{formatDateShort(date)}</span>
								<span class="slot-count">{slots.length} slot{slots.length !== 1 ? 's' : ''}</span>
							</button>
						{/each}
					</div>
					{#if tdSelectedDate}
						{@const dateSlots = tdSlotsForDate(tdSelectedDate)}
						<p class="modal-label">Select a time for {formatDateShort(tdSelectedDate)}</p>
						<div class="slot-list">
							{#each dateSlots as s}
								<button class="slot-item" class:selected={tdSelectedSlot === s.slot_id} onclick={() => (tdSelectedSlot = s.slot_id as number)}>
									{formatTime(s.slot_datetime as string)}
									<span class="remaining">{(s as any).remaining ?? 1} slot{(s as any).remaining !== 1 ? 's' : ''} left</span>
								</button>
							{/each}
						</div>
					{/if}
					<button class="modal-btn" onclick={handleBookTestDrive} disabled={!tdSelectedSlot || tdSending}>
						{tdSending ? 'Booking…' : 'Book Test Drive'}
					</button>
				{/if}
			{:else}
				<label class="modal-label">Name <span class="req">*</span></label>
				<input class="modal-input" type="text" bind:value={tdForm.name} placeholder="Your full name" />
				<label class="modal-label">Email <span class="req">*</span></label>
				<input class="modal-input" type="email" bind:value={tdForm.email} placeholder="your@email.com" />
				<label class="modal-label">Phone</label>
				<input class="modal-input" type="tel" bind:value={tdForm.phone} placeholder="+63 912 345 6789" />
				<button class="modal-btn" onclick={() => { tdStep = 'slot'; handleLoadSlots(); }} disabled={!tdForm.name || !tdForm.email}>
					Choose Date
				</button>
			{/if}
		</div>
	</div>
{/if}

<Footer />

<style>
	.page {

		font-family: var(--font-sans);
		padding: 9rem 1.5rem 2rem;
		max-width: 1200px;
		margin: 0 auto;
		min-height: 100vh;
	}

	.loader-wrap { display: grid; place-items: center; height: 50vh; }
	.spinner { width: 28px; height: 28px; border: 2.5px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.error-msg { padding: 40px; text-align: center; color: #dc2626; }

	.detail-layout {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 32px;
		align-items: start;
	}

	/* ─── Gallery ─── */
	.gallery { }
	.main-photo {
		position: relative;
		border-radius: var(--radius-md);
		overflow: hidden;
		background: var(--bg-hover);
		aspect-ratio: 16/10;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.main-photo img { width: 100%; height: 100%; object-fit: cover; }
	.no-photo-lg { color: var(--text-muted); }
	.nav-btn {
		position: absolute; top: 50%; transform: translateY(-50%);
		background: rgba(0,0,0,0.4); color: #fff; border: none;
		border-radius: 50%; width: 36px; height: 36px;
		display: flex; align-items: center; justify-content: center;
		cursor: pointer;
	}
	.nav-btn:hover { background: rgba(0,0,0,0.6); }
	.nav-btn.left { left: 8px; }
	.nav-btn.right { right: 8px; }
	.thumbnails { display: flex; gap: 8px; margin-top: 8px; }
	.thumb {
		width: 64px; height: 48px; border-radius: 6px; overflow: hidden;
		border: 2px solid transparent; cursor: pointer; padding: 0; background: none;
	}
	.thumb.active { border-color: var(--blue); }
	.thumb img { width: 100%; height: 100%; object-fit: cover; }

	/* ─── Info ─── */
	.info { display: flex; flex-direction: column; gap: 12px; }
	.back-link {
		background: none; border: none; color: var(--text-muted);
		font-size: 13px; cursor: pointer; padding: 0; font-family: inherit;
		text-align: left; width: fit-content;
	}
	.back-link:hover { color: var(--blue); }
	h1 { font-size: 28px; font-weight: 700; color: var(--text-dark); margin: 0; }
	.year-badge {
		display: inline-block; padding: 2px 10px; border-radius: 20px;
		background: var(--bg-hover); color: var(--text-light); font-size: 12px;
		font-weight: 600; width: fit-content;
	}
	.price { font-size: 24px; font-weight: 700; color: var(--primary); }
	.status-badge {
		display: inline-block; font-size: 11px; font-weight: 600;
		color: #059669; background: #d1fae5; padding: 2px 10px;
		border-radius: var(--radius-sm); text-transform: capitalize;
	}
	.status-badge.reserved { color: #d97706; background: #fef3c7; }

	.specs-grid {
		display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;
	}
	.spec-item {
		display: flex; align-items: center; gap: 8px;
		padding: 10px 12px; background: var(--bg-hover);
		border-radius: var(--radius-sm); color: var(--text-dark);
		font-size: 13px; font-weight: 500;
	}
	.spec-item span { text-transform: capitalize; }

	.details {
		display: flex; flex-direction: column; gap: 6px;
		padding: 12px 0; border-top: 1px solid var(--border);
		border-bottom: 1px solid var(--border);
	}
	.detail-row { display: flex; justify-content: space-between; font-size: 13px; }
	.detail-row .label { color: var(--text-muted); }
	.detail-row .value { font-weight: 600; color: var(--text-dark); }
	.mono { font-family: monospace; }

	/* ─── Action Buttons ─── */
	.actions { display: flex; gap: 10px; }
	.btn-action {
		flex: 1; display: flex; align-items: center; justify-content: center;
		gap: 8px; padding: 12px; border: none; border-radius: var(--radius-md);
		font-size: 14px; font-weight: 600; cursor: pointer; font-family: inherit;
		transition: opacity 0.15s;
	}
	.btn-action:hover { opacity: 0.9; }
	.btn-action.inquiry { background: var(--blue); color: #fff; }
	.btn-action.reserve { background: #059669; color: #fff; }
	.btn-action.test-drive { background: #d97706; color: #fff; }

	/* ─── Loan Calculator ─── */
	.calc-card {
		border: 1px solid var(--border); border-radius: var(--radius-md);
		padding: 16px; background: var(--bg-muted);
	}
	.calc-header {
		display: flex; align-items: center; gap: 8px;
		font-size: 16px; font-weight: 700; color: var(--text-dark); margin-bottom: 6px;
	}
	.calc-header svg { color: var(--blue); }
	.rate-badge {
		display: inline-block; font-size: 11px; font-weight: 600;
		color: #059669; background: #d1fae5; padding: 2px 10px;
		border-radius: var(--radius-sm); margin-bottom: 14px;
	}
	.calc-fields { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }
	.calc-fields label {
		flex: 1; display: flex; flex-direction: column; gap: 4px;
		font-size: 12px; font-weight: 500; color: var(--text-dark);
	}
	.calc-fields input, .calc-fields select {
		padding: 8px 10px; border: 1px solid var(--border);
		border-radius: var(--radius-sm); font-size: 13px;
		font-family: inherit; background: var(--bg-card); outline: none;
	}
	.calc-fields input:focus, .calc-fields select:focus {
		border-color: var(--blue); box-shadow: 0 0 0 2px rgba(59,130,246,0.15);
	}
	.calc-breakdown { display: flex; flex-direction: column; gap: 6px; }
	.calc-row {
		display: flex; justify-content: space-between; align-items: center;
		font-size: 13px; color: var(--text-dark);
	}
	.calc-row span:first-child { color: var(--text-light); }
	.calc-row .mono { font-family: monospace; font-weight: 600; color: var(--text-dark); }
	.calc-row .down-pay { color: var(--red); }
	.calc-row .primary { color: var(--blue-dark); font-size: 15px; }
	.calc-row .interest { color: var(--warning); }
	.calc-row.total-row span:last-child { color: var(--text-dark); font-weight: 700; }
	.calc-row.amort-row { padding: 4px 0; }
	.calc-divider { height: 1px; background: var(--border); margin: 4px 0; }

	/* ─── Modals (lighter portal style) ─── */
	.modal-overlay {
		position: fixed; inset: 0; background: rgba(0,0,0,0.45);
		z-index: 1000; display: flex; align-items: center;
		justify-content: center; padding: 1rem;
	}
	.modal {
		position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
		width: 460px; max-width: calc(100vw - 2rem); max-height: 85vh;
		background: #fff; border-radius: 14px;
		box-shadow: 0 20px 60px rgba(0,0,0,0.15); z-index: 1010;
		display: flex; flex-direction: column; overflow-y: auto;
	}
	.modal-wide { width: 520px; }
	.modal-head {
		display: flex; align-items: center; justify-content: space-between;
		padding: 1.25rem 1.5rem; border-bottom: 1px solid #e5e7eb; flex-shrink: 0;
	}
	.modal-head h3 { margin: 0; font-size: 16px; font-weight: 700; color: #1a1a2e; }
	.modal-close {
		background: none; border: none; cursor: pointer; color: #9ca3af;
		padding: 4px; border-radius: 4px;
	}
	.modal-close:hover { color: #1a1a2e; background: #f3f4f6; }
	.modal-body { padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 10px; }
	.modal-label { font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.3px; }
	.req { color: #dc2626; }
	.modal-input, .modal-textarea {
		padding: 10px 12px; border: 1px solid #d1d5db;
		border-radius: 8px; font-family: var(--font-sans);
		font-size: 13px; outline: none;
	}
	.modal-input:focus, .modal-textarea:focus { border-color: var(--primary); }
	.modal-textarea { resize: vertical; min-height: 80px; }
	.modal-btn {
		padding: 10px 20px; background: var(--primary); color: #fff;
		border: none; border-radius: 8px; font-family: var(--font-sans);
		font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s;
	}
	.modal-btn:hover:not(:disabled) { background: var(--primary-dark); }
	.modal-btn:disabled { opacity: 0.5; cursor: not-allowed; }
	.modal-btn-secondary {
		padding: 10px 20px; background: #fff; color: #374151;
		border: 1px solid #d1d5db; border-radius: 8px; font-family: var(--font-sans);
		font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s;
	}
	.modal-btn-secondary:hover { background: #f9fafb; }
	.done-msg { text-align: center; padding: 1.5rem 0; color: #065f46; font-size: 14px; display: flex; flex-direction: column; align-items: center; gap: 8px; }
	.done-icon { color: #059669; }
	.pay-prompt { text-align: center; padding: 1rem 0; display: flex; flex-direction: column; align-items: center; gap: 10px; }
	.pay-prompt p { margin: 0; color: #374151; font-size: 14px; }
	.pay-actions { display: flex; gap: 10px; margin-top: 8px; }
	.date-group-list, .slot-list { display: flex; flex-direction: column; gap: 6px; }
	.hint { color: #9ca3af; font-size: 13px; text-align: center; padding: 1rem 0; margin: 0; }
	.date-chip {
		display: flex; align-items: center; justify-content: space-between;
		padding: 10px 14px; border: 1px solid #e5e7eb; border-radius: 10px;
		background: #fff; cursor: pointer; font-family: var(--font-sans);
		font-size: 13px; text-align: left; transition: border-color 0.2s;
	}
	.date-chip:hover { border-color: var(--primary); }
	.date-chip.selected { border-color: var(--primary); background: #eef2ff; }
	.date-label { font-weight: 600; color: #1a1a2e; }
	.slot-count { font-size: 11px; color: #6b7280; }
	.slot-item {
		display: flex; align-items: center; justify-content: space-between;
		padding: 8px 14px; border: 1px solid #e5e7eb; border-radius: 8px;
		background: #fff; cursor: pointer; font-family: var(--font-sans);
		font-size: 13px; text-align: left; transition: border-color 0.2s;
	}
	.slot-item:hover { border-color: var(--primary); }
	.slot-item.selected { border-color: var(--primary); background: #eef2ff; }
	.remaining { font-size: 11px; color: #6b7280; }

	@media (max-width: 768px) {
		.detail-layout { grid-template-columns: 1fr; }
		.actions { flex-direction: column; }
	}
</style>
