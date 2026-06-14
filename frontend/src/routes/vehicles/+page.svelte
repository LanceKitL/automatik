<script lang="ts">
	import { onMount } from 'svelte';
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { getAvailableVehicles, getServiceSlots, guestReserveVehicle, guestPayReservationFee, guestCreateBooking, submitGuestInquiry, resolvePhotoUrl } from '$lib/services/api';
	import { Search, X, MessageSquare, CheckCircle, Car, CreditCard, ChevronDown, ArrowUpDown } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	let vehicles = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);
	let search = $state('');
	let selectedBody = $state('');
	let selectedTrans = $state('');
	let selectedFuel = $state('');
	let selectedBrand = $state('');
	let selectedColor = $state('');
	let selectedSeats = $state(0);
	let selectedYear = $state(0);
	let sortBy = $state('default');

	const bodyOptions = ['Sedan', 'SUV'];
	const transOptions = ['Manual', 'Automatic'];
	const fuelOptions = ['Gasoline', 'Diesel'];
	const brandOptions = ['BYD', 'Honda', 'Hyundai', 'Mitsubishi', 'Toyota'];
	const colorOptions = ['Black', 'White', 'Red', 'Gray', 'Silver'];
	const seatOptions = [4, 5, 6, 7];
	const yearOptions = [2022, 2023, 2024, 2025, 2026];

	let filtered = $derived(
		vehicles
			.filter((v) => {
				const q = search.toLowerCase();
				if (q && !`${v.brand ?? ''} ${v.model ?? ''} ${v.year ?? ''} ${v.color ?? ''} ${v.body_type ?? ''}`
					.toLowerCase().includes(q)) return false;
				if (selectedBody && (v.body_type ?? '').toLowerCase() !== selectedBody.toLowerCase()) return false;
				if (selectedTrans && (v.transmission ?? '').toLowerCase() !== selectedTrans.toLowerCase()) return false;
				if (selectedFuel && (v.fuel_type ?? '').toLowerCase() !== selectedFuel.toLowerCase()) return false;
				if (selectedBrand && v.brand !== selectedBrand) return false;
				if (selectedColor && (v.color ?? '').toLowerCase() !== selectedColor.toLowerCase()) return false;
				if (selectedSeats && Number(v.seating_capacity) !== selectedSeats) return false;
				if (selectedYear && Number(v.year) !== selectedYear) return false;
				return true;
			})
			.sort((a, b) => {
				if (sortBy === 'price-asc') return Number(a.price ?? 0) - Number(b.price ?? 0);
				if (sortBy === 'price-desc') return Number(b.price ?? 0) - Number(a.price ?? 0);
				return 0;
			})
	);

	// Modal state
	type ModalType = 'none' | 'inquire' | 'reserve' | 'test_drive';
	let activeModal = $state<{ type: ModalType; vehicle: Record<string, unknown> } | null>(null);

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

	onMount(async () => {
		const params = new URLSearchParams(window.location.search);
		if (params.get('search')) search = params.get('search')!;
		if (params.get('body')) selectedBody = params.get('body')!;
		if (params.get('trans')) selectedTrans = params.get('trans')!;
		if (params.get('fuel')) selectedFuel = params.get('fuel')!;
		if (params.get('brand')) selectedBrand = params.get('brand')!;
		if (params.get('color')) selectedColor = params.get('color')!;
		if (params.get('seats')) selectedSeats = Number(params.get('seats'));
		if (params.get('year')) selectedYear = Number(params.get('year'));
		if (params.get('sort')) sortBy = params.get('sort')!;

		try {
			const res = await getAvailableVehicles();
			vehicles = res.data as Record<string, unknown>[];
		} catch {
			vehicles = [];
		} finally {
			loading = false;
		}
	});

	function handleSearch() {
		const params = new URLSearchParams();
		if (search.trim()) params.set('search', search.trim());
		if (selectedBody) params.set('body', selectedBody);
		if (selectedTrans) params.set('trans', selectedTrans);
		if (selectedFuel) params.set('fuel', selectedFuel);
		if (selectedBrand) params.set('brand', selectedBrand);
		if (selectedColor) params.set('color', selectedColor);
		if (selectedSeats) params.set('seats', String(selectedSeats));
		if (selectedYear) params.set('year', String(selectedYear));
		if (sortBy !== 'default') params.set('sort', sortBy);
		const qs = params.toString();
		goto(qs ? `/vehicles?${qs}` : '/vehicles', { replaceState: true });
	}

	// Modal actions

	function getPhotoUrl(v: Record<string, unknown>, idx: number) {
		return resolvePhotoUrl((v as any).photos?.[idx]?.photo_url ?? null);
	}

	function openInquire(v: Record<string, unknown>) {
		inquireForm = { name: '', email: '', phone: '', message: '' };
		inquireDone = false;
		activeModal = { type: 'inquire', vehicle: v };
	}

	function openReserve(v: Record<string, unknown>) {
		reserveForm = { name: '', email: '', phone: '' };
		reserveStep = 'form';
		reserveInquiryId = null;
		activeModal = { type: 'reserve', vehicle: v };
	}

	function openTestDrive(v: Record<string, unknown>) {
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
			await submitGuestInquiry({ vehicle_id: activeModal.vehicle.vehicle_id as number, name: inquireForm.name, email: inquireForm.email, number: inquireForm.phone || undefined, message: inquireForm.message });
			inquireDone = true;
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to send inquiry.');
		} finally { inquireSending = false; }
	}

	async function handleReserve() {
		if (!activeModal || !reserveForm.name || !reserveForm.email) return;
		reserveSending = true;
		try {
			const res = await guestReserveVehicle(activeModal.vehicle.vehicle_id as number, { guest_name: reserveForm.name, guest_email: reserveForm.email, guest_number: reserveForm.phone || undefined });
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
			await guestCreateBooking({ guest_name: tdForm.name, guest_email: tdForm.email, guest_number: tdForm.phone || undefined, slot_id: tdSelectedSlot, vehicle_id: activeModal.vehicle.vehicle_id as number, booking_type: 'test_drive' });
			tdStep = 'done';
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Booking failed.');
		} finally { tdSending = false; }
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
	<div class="page-inner">
		<h1>Browse Vehicles</h1>

		<div class="search-section">
			<div class="search-row">
				<div class="search-input-wrap">
					<Search size={16} class="search-ico" />
					<input type="text" bind:value={search} placeholder="Search by brand, model, or type…" class="search-input" onkeydown={(e) => e.key === 'Enter' && handleSearch()} />
				</div>
				<button class="search-btn" onclick={handleSearch}>Search</button>
			</div>
			<div class="filter-clusters">
				<div class="filter-group">
					<span class="filter-lbl"><ArrowUpDown size={11} /> Sort</span>
					<select class="sort-select" bind:value={sortBy}>
						<option value="default">Default</option>
						<option value="price-asc">Price: Low → High</option>
						<option value="price-desc">Price: High → Low</option>
					</select>
				</div>
				<div class="filter-group">
					<span class="filter-lbl">Body</span>
					<div class="pills">
						<button class="pill" class:active={!selectedBody} onclick={() => selectedBody = ''}>All</button>
						{#each bodyOptions as b}
							<button class="pill" class:active={selectedBody === b} onclick={() => selectedBody = b}>{b}</button>
						{/each}
					</div>
				</div>
				<div class="filter-group">
					<span class="filter-lbl">Trans.</span>
					<div class="pills">
						<button class="pill" class:active={!selectedTrans} onclick={() => selectedTrans = ''}>All</button>
						{#each transOptions as t}
							<button class="pill" class:active={selectedTrans === t} onclick={() => selectedTrans = t}>{t}</button>
						{/each}
					</div>
				</div>
				<div class="filter-group">
					<span class="filter-lbl">Fuel</span>
					<div class="pills">
						<button class="pill" class:active={!selectedFuel} onclick={() => selectedFuel = ''}>All</button>
						{#each fuelOptions as f}
							<button class="pill" class:active={selectedFuel === f} onclick={() => selectedFuel = f}>{f}</button>
						{/each}
					</div>
				</div>
				<div class="filter-group">
					<span class="filter-lbl">Brand</span>
					<div class="pills">
						<button class="pill" class:active={!selectedBrand} onclick={() => selectedBrand = ''}>All</button>
						{#each brandOptions as b}
							<button class="pill" class:active={selectedBrand === b} onclick={() => selectedBrand = b}>{b}</button>
						{/each}
					</div>
				</div>
				<div class="filter-group">
					<span class="filter-lbl">Color</span>
					<div class="pills">
						<button class="pill" class:active={!selectedColor} onclick={() => selectedColor = ''}>All</button>
						{#each colorOptions as c}
							<button class="pill" class:active={selectedColor === c} onclick={() => selectedColor = c}>{c}</button>
						{/each}
					</div>
				</div>
				<div class="filter-group">
					<span class="filter-lbl">Year</span>
					<div class="pills">
						<button class="pill" class:active={!selectedYear} onclick={() => selectedYear = 0}>All</button>
						{#each yearOptions as y}
							<button class="pill" class:active={selectedYear === y} onclick={() => selectedYear = y}>{y}</button>
						{/each}
					</div>
				</div>
				<div class="filter-group">
					<span class="filter-lbl">Seats</span>
					<div class="pills">
						<button class="pill" class:active={!selectedSeats} onclick={() => selectedSeats = 0}>All</button>
						{#each seatOptions as s}
							<button class="pill" class:active={selectedSeats === s} onclick={() => selectedSeats = s}>{s}</button>
						{/each}
					</div>
				</div>
			</div>
		</div>

		{#if loading}
			<div class="loading-state"><span class="spinner"></span><p>Loading vehicles…</p></div>
		{:else if filtered.length === 0}
			<p class="empty-state">No vehicles match your filters.</p>
		{:else}
			<div class="vehicles-grid">
				{#each filtered as v (v.vehicle_id)}
					<div class="vehicle-card" onclick={() => goto(`/vehicles/${v.vehicle_id}`)}>
						<div class="vehicle-thumb">
							<span class="badge-new">New</span>
							{#if getPhotoUrl(v, 0)}
								<img src={getPhotoUrl(v, 0)} alt="{v.brand ?? ''} {v.model ?? ''}" class="vehicle-photo" />
							{:else}
								<div class="no-photo">{(v.brand ?? 'Brand') as string} {(v.model ?? 'Model') as string}</div>
							{/if}
						</div>
						<div class="vehicle-body">
							<h3 class="vehicle-name">{v.brand ?? ''} {v.model ?? ''}</h3>
							<div class="vehicle-specs">
								<span>{(v.year ?? '') as string}</span>
								<span class="sep">·</span>
								<span>{(v.body_type ?? '') as string}</span>
								<span class="sep">·</span>
								<span>{(v.transmission ?? '') as string}</span>
							</div>
							<div class="vehicle-price">
								{v.price ? `₱${Number(v.price).toLocaleString()}` : 'Call for Pricing'}
							</div>
							<div class="vehicle-actions">
								<button class="act-btn act-inquire" onclick={(e) => { e.stopPropagation(); openInquire(v); }}>
									<MessageSquare size={13} /> Inquire
								</button>
								<button class="act-btn act-reserve" onclick={(e) => { e.stopPropagation(); openReserve(v); }}>
									<CheckCircle size={13} /> Reserve
								</button>
								<button class="act-btn act-testdrive" onclick={(e) => { e.stopPropagation(); openTestDrive(v); }}>
									<Car size={13} /> Test Drive
								</button>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<!-- Inquire Modal -->
{#if activeModal && activeModal.type === 'inquire'}
	<div class="modal-overlay" onclick={closeModal} role="presentation" />
	<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
		<div class="modal-head">
			<h3>Inquire About {String(activeModal.vehicle.brand ?? '')} {String(activeModal.vehicle.model ?? '')}</h3>
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
			<h3>Reserve {String(activeModal.vehicle.brand ?? '')} {String(activeModal.vehicle.model ?? '')}</h3>
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
			<h3>Test Drive {String(activeModal.vehicle.brand ?? '')} {String(activeModal.vehicle.model ?? '')}</h3>
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
	.page { font-family: var(--font-sans); padding: 6rem 1.5rem 2rem; max-width: 1200px; margin: 0 auto; min-height: 100vh; }
	.page-inner { max-width: 1200px; margin: 0 auto; }
	h1 { font-size: 1.75rem; font-weight: 700; color: #1a1a2e; margin: 0 0 1.5rem; }

	.search-section { margin-top: 3rem; margin-bottom: 2rem; }
	.search-row { display: flex; gap: 8px; margin-bottom: 1rem; }
	.search-input-wrap { position: relative; flex: 1; max-width: 480px; }
	.search-btn { padding: 12px 20px; background: var(--primary); color: #fff; border: none; border-radius: 10px; font-family: var(--font-sans); font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap; transition: background 0.2s; }
	.search-btn:hover { background: var(--primary-dark); }
	:global(.search-ico) { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: #9ca3af; pointer-events: none; }
	.search-input { width: 100%; padding: 12px 16px 12px 40px; border: 2px solid #e5e7eb; border-radius: 10px; font-family: var(--font-sans); font-size: 14px; outline: none; box-sizing: border-box; }
	.search-input:focus { border-color: var(--primary); }
	.filter-clusters { display: flex; flex-wrap: wrap; gap: 1.25rem; }
	.filter-group { display: flex; flex-direction: column; gap: 6px; }
	.filter-lbl { font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }
	.pills { display: flex; gap: 4px; flex-wrap: wrap; }
	.pill { padding: 5px 12px; border-radius: 20px; border: 1px solid #e5e7eb; background: #fff; font-family: var(--font-sans); font-size: 12px; color: #6b7280; cursor: pointer; transition: all 0.15s; }
	.pill.active { background: var(--primary); color: #fff; border-color: var(--primary); }
	.pill:hover:not(.active) { border-color: var(--primary); color: var(--primary); }
	.sort-select { padding: 5px 10px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff; font-family: var(--font-sans); font-size: 12px; color: #374151; outline: none; cursor: pointer; }
	.sort-select:focus { border-color: var(--primary); }
	.filter-group .filter-lbl svg { display: inline; vertical-align: middle; margin-right: 2px; }

	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: #9ca3af; font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid #e5e7eb; border-top-color: var(--primary); border-radius: 50%; animation: spin 0.7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.empty-state { text-align: center; padding: 3rem; color: #9ca3af; font-size: 14px; }

	.vehicles-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.25rem; }
	.vehicle-card { border-radius: 14px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #f0f0f0; transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; }
	.vehicle-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
	.vehicle-thumb { position: relative; height: 180px; background: linear-gradient(135deg, #1a1a2e, #2d2d5e); display: flex; align-items: flex-end; padding: 1rem; overflow: hidden; }
	.vehicle-photo { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
	.badge-new { position: absolute; top: 12px; left: 12px; background: #e8c97e; color: #1a1a2e; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; z-index: 1; }
	.no-photo { color: rgba(255,255,255,0.5); font-size: 14px; font-weight: 500; }
	.vehicle-body { padding: 1rem 1.15rem 1.15rem; }
	.vehicle-name { font-size: 1rem; font-weight: 600; color: #1a1a2e; margin: 0 0 6px; }
	.vehicle-specs { font-size: 12px; color: #9ca3af; margin-bottom: 8px; display: flex; gap: 4px; }
	.sep { color: #e5e7eb; }
	.vehicle-price { font-size: 1.05rem; font-weight: 700; color: var(--primary); }

	/* Action buttons */
	.vehicle-actions { display: flex; gap: 6px; margin-top: 10px; }
	.act-btn { flex: 1; display: inline-flex; align-items: center; justify-content: center; gap: 4px; padding: 7px 6px; border: none; border-radius: 8px; font-family: var(--font-sans); font-size: 11px; font-weight: 600; cursor: pointer; transition: background 0.2s; min-width: 0; white-space: nowrap; }
	.act-inquire { background: #eef2ff; color: #4338ca; }
	.act-inquire:hover { background: #e0e7ff; }
	.act-reserve { background: #f0fdf4; color: #166534; }
	.act-reserve:hover { background: #dcfce7; }
	.act-testdrive { background: #fef3c7; color: #92400e; }
	.act-testdrive:hover { background: #fde68a; }

	/* Modals */
	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 1rem; }
	.modal { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 460px; max-width: calc(100vw - 2rem); max-height: 85vh; background: #fff; border-radius: 14px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); z-index: 1010; display: flex; flex-direction: column; overflow-y: auto; }
	.modal-wide { width: 520px; }
	.modal-head { display: flex; align-items: center; justify-content: space-between; padding: 1.25rem 1.5rem; border-bottom: 1px solid #e5e7eb; flex-shrink: 0; }
	.modal-head h3 { margin: 0; font-size: 16px; font-weight: 700; color: #1a1a2e; }
	.modal-close { background: none; border: none; cursor: pointer; color: #9ca3af; padding: 4px; border-radius: 4px; }
	.modal-close:hover { color: #1a1a2e; background: #f3f4f6; }
	.modal-body { padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 10px; }
	.modal-label { font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.3px; }
	.req { color: #dc2626; }
	.modal-input, .modal-textarea { padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-family: var(--font-sans); font-size: 13px; outline: none; }
	.modal-input:focus, .modal-textarea:focus { border-color: var(--primary); }
	.modal-textarea { resize: vertical; min-height: 80px; }
	.modal-btn { padding: 10px 20px; background: var(--primary); color: #fff; border: none; border-radius: 8px; font-family: var(--font-sans); font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
	.modal-btn:hover:not(:disabled) { background: var(--primary-dark); }
	.modal-btn:disabled { opacity: 0.5; cursor: not-allowed; }
	.modal-btn-secondary { padding: 10px 20px; background: #fff; color: #374151; border: 1px solid #d1d5db; border-radius: 8px; font-family: var(--font-sans); font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
	.modal-btn-secondary:hover { background: #f9fafb; }
	.done-msg { text-align: center; padding: 1.5rem 0; color: #065f46; font-size: 14px; display: flex; flex-direction: column; align-items: center; gap: 8px; }
	.done-icon { color: #059669; }
	.pay-prompt { text-align: center; padding: 1rem 0; display: flex; flex-direction: column; align-items: center; gap: 10px; }
	.pay-prompt p { margin: 0; color: #374151; font-size: 14px; }
	.pay-actions { display: flex; gap: 10px; margin-top: 8px; }
	.date-group-list, .slot-list { display: flex; flex-direction: column; gap: 6px; }
	.hint { color: #9ca3af; font-size: 13px; text-align: center; padding: 1rem 0; margin: 0; }
	.date-chip { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border: 1px solid #e5e7eb; border-radius: 10px; background: #fff; cursor: pointer; font-family: var(--font-sans); font-size: 13px; text-align: left; transition: border-color 0.2s; }
	.date-chip:hover { border-color: var(--primary); }
	.date-chip.selected { border-color: var(--primary); background: #eef2ff; }
	.date-label { font-weight: 600; color: #1a1a2e; }
	.slot-count { font-size: 11px; color: #6b7280; }
	.slot-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 14px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff; cursor: pointer; font-family: var(--font-sans); font-size: 13px; text-align: left; transition: border-color 0.2s; }
	.slot-item:hover { border-color: var(--primary); }
	.slot-item.selected { border-color: var(--primary); background: #eef2ff; }
	.remaining { font-size: 11px; color: #6b7280; }

	@media (max-width: 1024px) { .vehicles-grid { grid-template-columns: repeat(2, 1fr); } }
	@media (max-width: 640px) { .vehicles-grid { grid-template-columns: 1fr; } .filter-clusters { flex-direction: column; gap: 0.75rem; } }
</style>
