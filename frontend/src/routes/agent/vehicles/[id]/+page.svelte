<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { getAgentVehicleDetail, createAgentInquiry, bookAgentTestDrive, getTestDriveSlots, resolvePhotoUrl } from '$lib/services/api';
	import type { VehicleItem, ServiceSlot } from '$lib/services/api';
	import { ChevronLeft, ChevronRight, Car, MessageSquare, Calendar, X, Users, Cog, Fuel, Calculator } from '@lucide/svelte';
	import { goto } from '$app/navigation';

	let { params } = $props();

	let vehicle = $state<VehicleItem | null>(null);
	let loading = $state(true);

	let photoIndex = $state(0);

	// Inquiry modal state
	let showInquiryModal = $state(false);
	let inquiryForm = $state({ guest_name: '', guest_email: '', guest_number: '', message: '' });
	let submittingInquiry = $state(false);

	// Test drive modal state
	let showTdModal = $state(false);
	let tdAllSlots = $state<ServiceSlot[]>([]);
	let tdLoading = $state(false);
	let tdSelectedDate = $state<string | null>(null);
	let tdSelectedSlot = $state<number | null>(null);
	let tdBooking = $state(false);
	let tdForm = $state({ guest_name: '', guest_email: '' });
	let showTdConfirmModal = $state(false);
	let tdConfirming = $state(false);

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

	let tdDateGroups = $derived.by(() => {
		const map = new Map<string, ServiceSlot[]>();
		for (const s of tdAllSlots) {
			const d = s.slot_datetime.slice(0, 10);
			if (!map.has(d)) map.set(d, []);
			map.get(d)!.push(s);
		}
		return map;
	});

	let tdSlots = $derived(tdDateGroups.get(tdSelectedDate ?? '') ?? []);
	let tdSelectedSlotObj = $derived(tdSlots.find(s => s.slot_id === tdSelectedSlot) ?? null);

	function parseDT(s: string): Date {
		if (s.endsWith('GMT') || s.endsWith('UTC')) return new Date(s);
		if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return new Date(s + 'T00:00:00');
		if (s.includes('Z') || s.includes('+')) return new Date(s);
		return new Date(s.replace(' ', 'T') + '+08:00');
	}

	function formatDateShort(dateStr: string) {
		const d = parseDT(dateStr);
		return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
	}

	function formatTime(dt: string) {
		const d = parseDT(dt);
		return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
	}

	onMount(async () => {
		try {
			const res = await getAgentVehicleDetail(Number(params.id));
			vehicle = res.data;
		} catch {
			toast.error('Failed to load vehicle.');
		} finally {
			loading = false;
		}
	});

	function openInquiry() {
		inquiryForm = { guest_name: '', guest_email: '', guest_number: '', message: '' };
		showInquiryModal = true;
	}

	async function handleSubmitInquiry() {
		if (!inquiryForm.guest_name || !inquiryForm.guest_email || !inquiryForm.message) return;
		submittingInquiry = true;
		try {
			await createAgentInquiry({
				vehicle_id: vehicle!.vehicle_id,
				message: inquiryForm.message,
				guest_name: inquiryForm.guest_name,
				guest_email: inquiryForm.guest_email,
				guest_number: inquiryForm.guest_number || undefined,
			});
			toast.success('Inquiry created and assigned to you!');
			showInquiryModal = false;
			goto('/agent/inquiries');
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to create inquiry');
		} finally {
			submittingInquiry = false;
		}
	}

	async function openTdModal() {
		tdForm = { guest_name: '', guest_email: '' };
		tdSelectedDate = null;
		tdSelectedSlot = null;
		tdAllSlots = [];
		showTdModal = true;
		tdLoading = true;
		try {
			const res = await getTestDriveSlots();
			tdAllSlots = res.data;
		} catch {
			toast.error('Failed to load test drive slots.');
			tdAllSlots = [];
		} finally {
			tdLoading = false;
		}
	}

	function selectTdSlot(slot: ServiceSlot) {
		tdSelectedSlot = slot.slot_id;
	}

	function proceedToConfirm() {
		if (!tdForm.guest_name || !tdForm.guest_email || !tdSelectedSlot) return;
		showTdConfirmModal = true;
	}

	async function confirmTdBooking() {
		tdConfirming = true;
		try {
			await bookAgentTestDrive({
				slot_id: tdSelectedSlot!,
				vehicle_id: vehicle!.vehicle_id,
				guest_name: tdForm.guest_name,
				guest_email: tdForm.guest_email,
			});
			toast.success('Test drive booked! Confirmation email sent to guest.');
			showTdConfirmModal = false;
			showTdModal = false;
			goto('/agent/vehicles');
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to book test drive');
		} finally {
			tdConfirming = false;
		}
	}

	function formatPrice(p: string) {
		return `₱${Number(p).toLocaleString()}`;
	}
</script>

{#if loading}
	<div class="loader-wrap"><div class="spinner"></div></div>
{:else if !vehicle}
	<div class="error-msg">Vehicle not found.</div>
{:else if vehicle}
	<div class="page">
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

		<div class="info">
			<h1>{vehicle.brand} {vehicle.model}</h1>
			<div class="year-badge">{vehicle.year}</div>
			<div class="price">{formatPrice(vehicle.price)}</div>

			<div class="specs-grid">
				<div class="spec-item"><Cog size={16} /><span>{vehicle.transmission ?? '—'}</span></div>
				<div class="spec-item"><Fuel size={16} /><span>{vehicle.fuel_type ?? '—'}</span></div>
				<div class="spec-item"><Users size={16} /><span>{vehicle.seating_capacity ?? '—'} seater</span></div>
				<div class="spec-item"><Car size={16} /><span>{vehicle.body_type ?? '—'}</span></div>
			</div>

			<div class="details">
				<div class="detail-row"><span class="label">Color</span><span class="value">{vehicle.color ?? '—'}</span></div>
				<div class="detail-row"><span class="label">VIN</span><span class="value mono">{vehicle.vin}</span></div>
				<div class="detail-row"><span class="label">Status</span><span class="value">{vehicle.status}</span></div>
			</div>

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

			<div class="actions">
				<button class="btn-action inquiry" onclick={openInquiry}>
					<MessageSquare size={18} /> Create Inquiry
				</button>
				<button class="btn-action test-drive" onclick={openTdModal}>
					<Calendar size={18} /> Schedule Test Drive
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Inquiry Modal -->
{#if showInquiryModal}
	<div class="modal-overlay" onclick={() => showInquiryModal = false}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Create Inquiry</h2>
				<button class="modal-close" onclick={() => showInquiryModal = false}><X size={20} /></button>
			</div>
			<div class="modal-body">
				<div class="form-group">
					<label>Guest Name <span class="req">*</span></label>
					<input type="text" bind:value={inquiryForm.guest_name} placeholder="Full name" />
				</div>
				<div class="form-group">
					<label>Guest Email <span class="req">*</span></label>
					<input type="email" bind:value={inquiryForm.guest_email} placeholder="email@example.com" />
				</div>
				<div class="form-group">
					<label>Contact Number</label>
					<input type="tel" bind:value={inquiryForm.guest_number} placeholder="+63 9XX XXX XXXX" />
				</div>
				<div class="form-group">
					<label>Message <span class="req">*</span></label>
					<textarea rows="3" bind:value={inquiryForm.message} placeholder="Customer's inquiry or message…"></textarea>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" onclick={() => showInquiryModal = false} disabled={submittingInquiry}>Cancel</button>
				<button class="btn-primary" onclick={handleSubmitInquiry} disabled={!inquiryForm.guest_name || !inquiryForm.guest_email || !inquiryForm.message || submittingInquiry}>
					{submittingInquiry ? 'Creating…' : 'Create & Assign to Me'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Test Drive Modal -->
{#if showTdModal}
	<div class="modal-overlay" onclick={() => showTdModal = false}>
		<div class="modal modal-wide" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Schedule Test Drive</h2>
				<button class="modal-close" onclick={() => showTdModal = false}><X size={20} /></button>
			</div>
			<div class="modal-body">
				<div class="form-group">
					<label>Guest Name <span class="req">*</span></label>
					<input type="text" bind:value={tdForm.guest_name} placeholder="Full name" />
				</div>
				<div class="form-group">
					<label>Guest Email <span class="req">*</span></label>
					<input type="email" bind:value={tdForm.guest_email} placeholder="email@example.com" />
				</div>

				<div class="form-group">
					<label>Select Date</label>
					{#if tdLoading}
						<p class="hint">Loading slots…</p>
					{:else if tdDateGroups.size === 0}
						<p class="hint">No test drive slots available.</p>
					{:else}
						<div class="date-chips">
							{#each [...tdDateGroups.keys()].sort() as d}
								<button class="date-chip" class:active={tdSelectedDate === d} onclick={() => { tdSelectedDate = d; tdSelectedSlot = null; }}>
									{formatDateShort(d)}
								</button>
							{/each}
						</div>
					{/if}
				</div>

				{#if tdSelectedDate && tdSlots.length > 0}
					<div class="form-group">
						<label>Select Time</label>
						<div class="time-chips">
							{#each tdSlots as slot}
								<button class="time-chip" class:active={tdSelectedSlot === slot.slot_id} onclick={() => selectTdSlot(slot)} disabled={slot.remaining < 1}>
									{formatTime(slot.slot_datetime)}
									<span class="remaining">{slot.remaining} left</span>
								</button>
							{/each}
						</div>
					</div>
				{/if}
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" onclick={() => showTdModal = false} disabled={tdBooking}>Cancel</button>
				<button class="btn-primary" onclick={proceedToConfirm} disabled={!tdForm.guest_name || !tdForm.guest_email || !tdSelectedSlot}>
					Continue
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Test Drive Confirmation Modal -->
{#if showTdConfirmModal && tdSelectedSlotObj}
	<div class="modal-overlay" onclick={() => showTdConfirmModal = false}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Confirm Test Drive</h2>
				<button class="modal-close" onclick={() => showTdConfirmModal = false}><X size={20} /></button>
			</div>
			<div class="modal-body">
				<div class="confirm-info">
					<div class="confirm-row"><span>Vehicle</span><strong>{vehicle?.brand} {vehicle?.model}</strong></div>
					<div class="confirm-row"><span>Guest</span><strong>{tdForm.guest_name} ({tdForm.guest_email})</strong></div>
					<div class="confirm-row"><span>Date</span><strong>{formatDateShort(tdSelectedDate!)}</strong></div>
					<div class="confirm-row"><span>Time</span><strong>{formatTime(tdSelectedSlotObj.slot_datetime)}</strong></div>
				</div>
				<div class="policy-note">
					<strong>Reminders:</strong>
					<ul>
						<li>Valid driver's licence is required</li>
						<li>Guest must be at least 18 years old</li>
						<li>Test drive follows dealer's designated route</li>
						<li>Dealer representative will accompany</li>
					</ul>
					<p>A confirmation email will be sent to the guest's email address.</p>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" onclick={() => showTdConfirmModal = false} disabled={tdConfirming}>Cancel</button>
				<button class="btn-primary" onclick={confirmTdBooking} disabled={tdConfirming}>
					{tdConfirming ? 'Booking…' : 'Confirm Booking'}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.loader-wrap { display:grid; place-items:center; height:50vh; }
	.spinner { width:28px; height:28px; border:2.5px solid var(--border); border-top-color:var(--primary); border-radius:50%; animation:spin .7s linear infinite; }
	@keyframes spin { to { transform:rotate(360deg); } }
	.error-msg { padding:40px; text-align:center; color:#dc2626; }

	.page { display:grid; grid-template-columns:1fr 1fr; gap:32px; max-width:1200px; margin:0 auto; padding:24px 0; }

	.gallery { }
	.main-photo { position:relative; border-radius:var(--radius-md); overflow:hidden; background:var(--bg-hover); aspect-ratio:16/10; display:flex; align-items:center; justify-content:center; }
	.main-photo img { width:100%; height:100%; object-fit:cover; }
	.no-photo-lg { color:var(--text-muted); }
	.nav-btn { position:absolute; top:50%; transform:translateY(-50%); background:rgba(0,0,0,0.4); color:#fff; border:none; border-radius:50%; width:36px; height:36px; display:flex; align-items:center; justify-content:center; cursor:pointer; }
	.nav-btn:hover { background:rgba(0,0,0,0.6); }
	.nav-btn.left { left:8px; }
	.nav-btn.right { right:8px; }
	.thumbnails { display:flex; gap:8px; margin-top:8px; }
	.thumb { width:64px; height:48px; border-radius:6px; overflow:hidden; border:2px solid transparent; cursor:pointer; padding:0; background:none; }
	.thumb.active { border-color:var(--blue); }
	.thumb img { width:100%; height:100%; object-fit:cover; }

	.info { display:flex; flex-direction:column; gap:12px; }
	h1 { font-size:28px; font-weight:700; color:var(--text-dark); margin:0; }
	.year-badge { display:inline-block; padding:2px 10px; border-radius:20px; background:var(--bg-hover); color:var(--text-light); font-size:12px; font-weight:600; width:fit-content; }
	.price { font-size:24px; font-weight:700; color:var(--primary); }

	.specs-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:8px; }
	.spec-item { display:flex; align-items:center; gap:8px; padding:10px 12px; background:var(--bg-hover); border-radius:var(--radius-sm); color:var(--text-dark); font-size:13px; font-weight:500; }
	.spec-item span { text-transform:capitalize; }

	.details { display:flex; flex-direction:column; gap:6px; padding:12px 0; border-top:1px solid var(--border); border-bottom:1px solid var(--border); }
	.detail-row { display:flex; justify-content:space-between; font-size:13px; }
	.detail-row .label { color:var(--text-muted); }
	.detail-row .value { font-weight:600; color:var(--text-dark); }
	.mono { font-family:monospace; }

	.actions { display:flex; gap:10px; margin-top:8px; }
	.btn-action { flex:1; display:flex; align-items:center; justify-content:center; gap:8px; padding:12px; border:none; border-radius:var(--radius-md); font-size:14px; font-weight:600; cursor:pointer; font-family:inherit; }
	.btn-action.inquiry { background:var(--blue); color:#fff; }
	.btn-action.inquiry:hover { opacity:0.9; }
	.btn-action.test-drive { background:#059669; color:#fff; }
	.btn-action.test-drive:hover { opacity:0.9; }

	.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:100; }
	.modal { background:var(--bg-card); border-radius:var(--radius-lg); width:480px; max-width:90vw; box-shadow:var(--shadow-lg); max-height:90vh; overflow-y:auto; }
	.modal-wide { width:560px; }
	.modal-header { display:flex; justify-content:space-between; align-items:center; padding:20px 24px; border-bottom:1px solid var(--border); }
	.modal-header h2 { font-size:18px; font-weight:700; margin:0; }
	.modal-close { background:none; border:none; cursor:pointer; color:var(--text-muted); padding:4px; border-radius:var(--radius-sm); }
	.modal-close:hover { background:var(--bg-hover); }
	.modal-body { padding:20px 24px; }
	.modal-footer { display:flex; justify-content:flex-end; gap:8px; padding:16px 24px; border-top:1px solid var(--border); }

	.form-group { margin-bottom:16px; }
	.form-group label { display:block; font-size:13px; font-weight:600; color:var(--text-dark); margin-bottom:6px; }
	.form-group .req { color:#dc2626; }
	.form-group input, .form-group textarea, .form-group select { width:100%; padding:10px 12px; border:1px solid var(--border); border-radius:var(--radius-md); font-size:14px; background:var(--bg-card); color:var(--text-dark); box-sizing:border-box; font-family:inherit; }
	.form-group textarea { resize:vertical; }
	.form-group input:focus, .form-group textarea:focus { outline:none; border-color:var(--blue); box-shadow:0 0 0 2px rgba(59,130,246,0.15); }

	.btn-primary { padding:10px 20px; border:none; border-radius:var(--radius-md); background:var(--blue); color:#fff; font-size:14px; font-weight:600; cursor:pointer; font-family:inherit; }
	.btn-primary:hover { opacity:0.9; }
	.btn-primary:disabled { opacity:0.5; cursor:not-allowed; }
	.btn-cancel { padding:10px 20px; border:1px solid var(--border); border-radius:var(--radius-md); background:var(--bg-card); color:var(--text-dark); font-size:14px; cursor:pointer; font-family:inherit; }
	.btn-cancel:disabled { opacity:0.5; cursor:not-allowed; }

	.date-chips, .time-chips { display:flex; flex-wrap:wrap; gap:8px; }
	.date-chip, .time-chip { padding:8px 14px; border:1px solid var(--border); border-radius:var(--radius-md); background:var(--bg-card); font-size:13px; color:var(--text-dark); cursor:pointer; font-family:inherit; }
	.date-chip.active, .time-chip.active { background:var(--blue); color:#fff; border-color:var(--blue); }
	.time-chip:disabled { opacity:0.4; cursor:not-allowed; }
	.remaining { display:block; font-size:10px; opacity:0.7; text-align:center; }
	.hint { font-size:13px; color:var(--text-muted); }

	.confirm-info { display:flex; flex-direction:column; gap:8px; margin-bottom:16px; }
	.confirm-row { display:flex; justify-content:space-between; font-size:14px; padding:4px 0; }
	.confirm-row strong { color:var(--text-dark); }
	.policy-note { background:var(--bg-hover); border-radius:var(--radius-md); padding:12px 16px; font-size:12px; color:var(--text-light); }
	.policy-note ul { margin:6px 0; padding-left:16px; }
	.policy-note li { margin-bottom:2px; }
	.policy-note p { margin:8px 0 0; }

	/* Loan Calculator */
	.calc-card { border:1px solid var(--border); border-radius:var(--radius-md); padding:16px; background:var(--bg-muted); }
	.calc-header { display:flex; align-items:center; gap:8px; font-size:16px; font-weight:700; color:var(--text-dark); margin-bottom:6px; }
	.calc-header svg { color:var(--blue); }
	.rate-badge { display:inline-block; font-size:11px; font-weight:600; color:#059669; background:#d1fae5; padding:2px 10px; border-radius:var(--radius-sm); margin-bottom:14px; }
	.calc-fields { display:flex; flex-direction:column; gap:10px; margin-bottom:16px; }
	.calc-fields label { flex:1; display:flex; flex-direction:column; gap:4px; font-size:12px; font-weight:500; color:var(--text-dark); }
	.calc-fields input, .calc-fields select { padding:8px 10px; border:1px solid var(--border); border-radius:var(--radius-sm); font-size:13px; font-family:inherit; background:var(--bg-card); outline:none; }
	.calc-fields input:focus, .calc-fields select:focus { border-color:var(--blue); box-shadow:0 0 0 2px rgba(59,130,246,0.15); }
	.calc-breakdown { display:flex; flex-direction:column; gap:6px; }
	.calc-row { display:flex; justify-content:space-between; align-items:center; font-size:13px; color:var(--text-dark); }
	.calc-row span:first-child { color:var(--text-light); }
	.calc-row .mono { font-family:monospace; font-weight:600; color:var(--text-dark); }
	.calc-row .down-pay { color:var(--red); }
	.calc-row .primary { color:var(--blue-dark); font-size:15px; }
	.calc-row .interest { color:var(--warning); }
	.calc-row.total-row span:last-child { color:var(--text-dark); font-weight:700; }
	.calc-row.amort-row { padding:4px 0; }
	.calc-divider { height:1px; background:var(--border); margin:4px 0; }

	@media (max-width:768px) { .page { grid-template-columns:1fr; } }
</style>
