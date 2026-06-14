<script lang="ts">
	import { onMount } from 'svelte';
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { getAvailableVehicles, getServiceSlots, guestReserveVehicle, guestPayReservationFee, guestCreateBooking, submitGuestInquiry, resolvePhotoUrl } from '$lib/services/api';
	import { Search, ChevronLeft, ChevronRight, ShieldCheck, Zap, Eye, HeartHandshake, MessageSquare, CheckCircle, Car, X, CreditCard } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import hero1 from '$lib/assets/HERO/1.jpg';
	import hero2 from '$lib/assets/HERO/2.jpg';
	import hero3 from '$lib/assets/HERO/3.jpg';

	let slide = $state(0);
	let vehicles = $state<Record<string, unknown>[]>([]);
	let vehiclesLoaded = $state(false);

	// Modal state
	type ModalType = 'none' | 'inquire' | 'reserve' | 'test_drive';
	let activeModal = $state<{ type: ModalType; vehicle: Record<string, unknown> } | null>(null);

	// Inquire form
	let inquireForm = $state({ name: '', email: '', phone: '', message: '' });
	let inquireSending = $state(false);
	let inquireDone = $state(false);

	// Reserve form
	let reserveStep = $state<'form' | 'pay' | 'done'>('form');
	let reserveForm = $state({ name: '', email: '', phone: '' });
	let reserveSending = $state(false);
	let reserveInquiryId = $state<number | null>(null);
	let reservePaying = $state(false);

	// Test drive form
	let tdStep = $state<'form' | 'slot' | 'done'>('form');
	let tdForm = $state({ name: '', email: '', phone: '' });
	let tdSlots = $state<Record<string, unknown>[]>([]);
	let tdDateGroups = $state<[string, Record<string, unknown>[]][]>([]);
	let tdSelectedDate = $state<string | null>(null);
	let tdSelectedSlot = $state<number | null>(null);
	let tdLoading = $state(false);
	let tdSending = $state(false);

	const slides = [
		{
			title: 'Drive Your Dream',
			subtitle: 'Brand new cars, zero compromise. Every vehicle comes with full manufacturer warranty.',
			accent: '#C9A84C',
			tag: 'Zero Mileage Guaranteed',
			image: hero1,
		},
		{
			title: 'Simple. Fast. Approved.',
			subtitle: 'Get behind the wheel in no time. Streamlined financing with decisions in minutes.',
			accent: '#34e89e',
			tag: 'Financing in Minutes',
			image: hero2,
		},
		{
			title: 'Honest Pricing. Every Time.',
			subtitle: 'No trade-ins, no hidden fees, no negotiations. Just transparent deals on brand new cars.',
			accent: '#7eb8f7',
			tag: 'Transparent Deals',
			image: hero3,
		},
	];

	const features = [
		{ icon: ShieldCheck, title: 'Brand New Only', desc: 'Zero mileage, full manufacturer warranty on every vehicle.' },
		{ icon: Zap, title: 'Fast Approvals', desc: 'Financing decisions in minutes, not days.' },
		{ icon: Eye, title: 'Transparent Pricing', desc: 'No hidden fees. What you see is what you pay.' },
		{ icon: HeartHandshake, title: 'Hassle-Free', desc: 'No trade-ins, no pressure. Simple, fair, and fast.' },
	];

	const testimonials = [
		{
			quote: 'The easiest car buying experience I\'ve ever had. From application to approval in under an hour!',
			name: 'Maria Santos',
			role: 'Verified Buyer',
			initials: 'MS',
		},
		{
			quote: 'No hidden fees, no pressure tactics. Just honest pricing and great service. Highly recommended.',
			name: 'Juan Dela Cruz',
			role: 'Verified Buyer',
			initials: 'JD',
		},
		{
			quote: 'I was approved for financing within minutes. Drove home my brand new car the same day.',
			name: 'Ana Reyes',
			role: 'Verified Buyer',
			initials: 'AR',
		},
	];

	const bodyTypes = ['All', 'SUV', 'Sedan', 'Hatchback', 'Pickup'];
	const colors = ['All', 'Red', 'Blue', 'Black', 'White', 'Silver'];
	const transmissions = ['All', 'Automatic', 'Manual'];

	let selectedBody = $state('All');
	let selectedColor = $state('All');
	let selectedTransmission = $state('All');
	let searchQuery = $state('');

	let interval: ReturnType<typeof setInterval> | undefined;

	onMount(async () => {
		interval = setInterval(() => {
			slide = (slide + 1) % slides.length;
		}, 5500);

		try {
			const res = await getAvailableVehicles();
			vehicles = (res.data ?? []).slice(0, 4);
		} catch {
			vehicles = [];
		} finally {
			vehiclesLoaded = true;
		}

		return () => {
			if (interval) clearInterval(interval);
		};
	});

	function goSlide(i: number) {
		slide = i;
		if (interval) {
			clearInterval(interval);
			interval = setInterval(() => {
				slide = (slide + 1) % slides.length;
			}, 5500);
		}
	}

	function prevSlide() { goSlide((slide - 1 + slides.length) % slides.length); }
	function nextSlide() { goSlide((slide + 1) % slides.length); }

	function handleSearch() {
		const params = new URLSearchParams();
		if (searchQuery.trim()) params.set('search', searchQuery.trim());
		if (selectedBody !== 'All') params.set('body', selectedBody);
		if (selectedColor !== 'All') params.set('color', selectedColor);
		if (selectedTransmission !== 'All') params.set('trans', selectedTransmission);
		goto(`/vehicles?${params.toString()}`);
	}

	// ── Modal actions ──────────────────────────────────────

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

	function closeModal() {
		activeModal = null;
	}

	async function handleSendInquiry() {
		if (!activeModal || !inquireForm.name || !inquireForm.email || !inquireForm.message) return;
		inquireSending = true;
		try {
			await submitGuestInquiry({
				vehicle_id: activeModal.vehicle.vehicle_id as number,
				name: inquireForm.name,
				email: inquireForm.email,
				number: inquireForm.phone || undefined,
				message: inquireForm.message,
			});
			inquireDone = true;
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to send inquiry.');
		} finally {
			inquireSending = false;
		}
	}

	async function handleReserve() {
		if (!activeModal || !reserveForm.name || !reserveForm.email) return;
		reserveSending = true;
		try {
			const res = await guestReserveVehicle(activeModal.vehicle.vehicle_id as number, {
				guest_name: reserveForm.name,
				guest_email: reserveForm.email,
				guest_number: reserveForm.phone || undefined,
			});
			reserveInquiryId = res.inquiry_id;
			reserveStep = 'pay';
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to reserve.');
		} finally {
			reserveSending = false;
		}
	}

	async function handleReservePay() {
		if (!reserveInquiryId) return;
		reservePaying = true;
		try {
			await guestPayReservationFee(reserveInquiryId);
			reserveStep = 'done';
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Payment failed.');
		} finally {
			reservePaying = false;
		}
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
		} catch {
			tdSlots = [];
			tdDateGroups = [];
		} finally {
			tdLoading = false;
		}
	}

	async function handleBookTestDrive() {
		if (!activeModal || !tdSelectedSlot) return;
		tdSending = true;
		try {
			await guestCreateBooking({
				guest_name: tdForm.name,
				guest_email: tdForm.email,
				guest_number: tdForm.phone || undefined,
				slot_id: tdSelectedSlot,
				vehicle_id: activeModal.vehicle.vehicle_id as number,
				booking_type: 'test_drive',
			});
			tdStep = 'done';
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Booking failed.');
		} finally {
			tdSending = false;
		}
	}

	function formatDateShort(iso: string) {
		const d = new Date(iso);
		return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
	}

	function formatTime(iso: string) {
		const d = new Date(iso);
		return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
	}

	function tdSlotsForDate(date: string) {
		return tdSlots.filter((s) => new Date(String(s.slot_datetime)).toISOString().slice(0, 10) === date);
	}
</script>

<Navbar />

<!-- ─── HERO ─────────────────────────────────────────── -->
<section class="hero">
	{#each slides as s, i}
		<div class="hero-slide" class:active={i === slide}>
			<div class="hero-bg" />
			<div class="hero-grid-overlay" />

			<!-- Left: text -->
			<div class="hero-content">
				<span class="hero-tag">{s.tag}</span>
				<h1 class="hero-title">{s.title}</h1>
				<p class="hero-subtitle">{s.subtitle}</p>
				<div class="hero-cta-row">
					<a href="/vehicles" class="btn-primary">Browse Vehicles</a>
					<a href="/loan-calculator" class="btn-ghost">Get Financing</a>
				</div>
			</div>

			<!-- Right: image panel -->
			<div class="hero-image-panel">
				<img src={s.image} alt={s.title} class="hero-img" />
			</div>
		</div>
	{/each}

	<button class="carousel-btn carousel-prev" onclick={prevSlide} aria-label="Previous slide">
		<ChevronLeft size={22} />
	</button>
	<button class="carousel-btn carousel-next" onclick={nextSlide} aria-label="Next slide">
		<ChevronRight size={22} />
	</button>

	<div class="carousel-track">
		{#each slides as s, i}
			<button
				class="track-item"
				class:active={i === slide}
				onclick={() => goSlide(i)}
			>
				<span class="track-number">0{i + 1}</span>
				<span class="track-line" />
				<span class="track-title">{s.title}</span>
			</button>
		{/each}
	</div>
</section>

<!-- ─── SEARCH DOCK ──────────────────────────────────── -->
<section class="search-dock">
	<div class="dock-inner">
		<div class="search-row">
			<div class="search-input-wrap">
				<Search size={18} class="search-ico" />
				<input
					type="text"
							class="search-input"
					placeholder="Search by brand, model, or type…"
					bind:value={searchQuery}
					onkeydown={(e) => e.key === 'Enter' && handleSearch()}
				/>
			</div>
			<button class="search-btn" onclick={handleSearch}>Search</button>
		</div>

		<div class="filter-row">
			<div class="filter-cluster">
				<span class="filter-lbl">Body</span>
				{#each bodyTypes as bt}
					<button class="chip" class:on={selectedBody === bt} onclick={() => (selectedBody = bt)}>{bt}</button>
				{/each}
			</div>
			<div class="filter-cluster">
				<span class="filter-lbl">Color</span>
				{#each colors as c}
					<button class="chip" class:on={selectedColor === c} onclick={() => (selectedColor = c)}>{c}</button>
				{/each}
			</div>
			<div class="filter-cluster">
				<span class="filter-lbl">Trans.</span>
				{#each transmissions as t}
					<button class="chip" class:on={selectedTransmission === t} onclick={() => (selectedTransmission = t)}>{t}</button>
				{/each}
			</div>
		</div>
	</div>
</section>

<!-- ─── FEATURED VEHICLES ────────────────────────────── -->
<section class="section vehicles-section">
	<div class="section-inner">
		<div class="section-header-row">
			<div>
				<div class="section-eyebrow">Inventory</div>
				<h2 class="section-title left">Featured Vehicles</h2>
			</div>
			<a href="/vehicles" class="link-all">View All &nbsp;→</a>
		</div>

		{#if !vehiclesLoaded}
			<div class="loading-row">
				<span class="loading-dot" /><span class="loading-dot" /><span class="loading-dot" />
			</div>
		{:else}
			<div class="vehicles-grid">
				{#each (vehicles.length > 0 ? vehicles : [{}, {}, {}, {}]) as v, i}
					<div class="vehicle-card" onclick={() => (v as any).vehicle_id && goto(`/vehicles/${(v as any).vehicle_id}`)}>
						<div class="vehicle-thumb">
							<span class="badge-new">New</span>
							{#if (v as any).photos?.[0]?.photo_url}
								<img src={resolvePhotoUrl((v as any).photos[0].photo_url)} alt="{(v as any).brand ?? ''}" class="vehicle-photo" />
							{:else}
								<div class="thumb-label">{(v as any).brand ?? 'Brand'} {(v as any).model ?? 'Model'}</div>
							{/if}
						</div>
						<div class="vehicle-body">
							<h3 class="vehicle-name">{(v as any).brand ?? 'Brand New Model'} {(v as any).model ?? ''}</h3>
							<div class="vehicle-specs">
								<span>{(v as any).year ?? '2025'}</span>
								<span class="dot-sep">·</span>
								<span>{(v as any).body_type ?? 'SUV'}</span>
								<span class="dot-sep">·</span>
								<span>{(v as any).transmission ?? 'Automatic'}</span>
							</div>
							<div class="vehicle-price-row">
								<span class="vehicle-price">
									{(v as any).price ? `₱${Number((v as any).price).toLocaleString()}` : 'Call for Pricing'}
								</span>
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
</section>

<!-- ─── STATS BAND ───────────────────────────────────── -->
<section class="stats-band">
	<div class="stats-inner">
		{#each [['500+', 'Vehicles Available'], ['98%', 'Customer Satisfaction'], ['< 1hr', 'Avg. Approval Time'], ['0', 'Hidden Fees']] as [val, lbl]}
			<div class="stat-item">
				<span class="stat-val">{val}</span>
				<span class="stat-lbl">{lbl}</span>
			</div>
		{/each}
	</div>
</section>

<!-- ─── WHY AUTOMATIK ────────────────────────────────── -->
<section class="section why-section">
	<div class="section-inner">
		<div class="section-eyebrow">Why Automatik</div>
		<h2 class="section-title">Built for the Modern Buyer</h2>
		<p class="section-sub">Simple, fast, and completely transparent — every step of the way.</p>

		<div class="features-grid">
			{#each features as f, i}
				<div class="feature-card">
					<div class="feature-num">0{i + 1}</div>
					<div class="feature-icon-wrap">
						<f.icon size={26} />
					</div>
					<h3 class="feature-title">{f.title}</h3>
					<p class="feature-desc">{f.desc}</p>
				</div>
			{/each}
		</div>
	</div>
</section>


<!-- ─── TESTIMONIALS ─────────────────────────────────── -->
<section class="section testimonials-section">
	<div class="section-inner">
		<div class="section-eyebrow">Reviews</div>
		<h2 class="section-title">What Our Customers Say</h2>

		<div class="testimonials-grid">
			{#each testimonials as t}
				<div class="testimonial-card">
					<div class="t-quote-mark">"</div>
					<p class="t-text">{t.quote}</p>
					<div class="t-author">
						<div class="t-avatar">{t.initials}</div>
						<div>
							<div class="t-name">{t.name}</div>
							<div class="t-role">{t.role}</div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- ─── CTA BANNER ───────────────────────────────────── -->
<section class="cta-banner">
	<div class="cta-inner">
		<h2 class="cta-title">Ready to Drive Home Today?</h2>
		<p class="cta-sub">Start your application — get approved in under an hour.</p>
		<div class="cta-btns">
			<a href="/vehicles" class="btn-primary large">Browse Vehicles</a>
			<a href="/contact" class="btn-ghost-light large">Contact</a>
		</div>
	</div>
</section>

<!-- ─── MODALS ────────────────────────────────────────────── -->

{#if activeModal && activeModal.type === 'inquire'}
	<div class="modal-overlay" onclick={closeModal} role="presentation" />
	<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
		<div class="modal-head">
			<h3>Inquire About {(activeModal.vehicle as any).brand ?? ''} {(activeModal.vehicle as any).model ?? ''}</h3>
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

{#if activeModal && activeModal.type === 'reserve'}
	<div class="modal-overlay" onclick={closeModal} role="presentation" />
	<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
		<div class="modal-head">
			<h3>Reserve {(activeModal.vehicle as any).brand ?? ''} {(activeModal.vehicle as any).model ?? ''}</h3>
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

{#if activeModal && activeModal.type === 'test_drive'}
	<div class="modal-overlay" onclick={closeModal} role="presentation" />
	<div class="modal modal-wide" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
		<div class="modal-head">
			<h3>Test Drive {(activeModal.vehicle as any).brand ?? ''} {(activeModal.vehicle as any).model ?? ''}</h3>
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
							<button
								class="date-chip"
								class:selected={tdSelectedDate === date}
								onclick={() => { tdSelectedDate = date; tdSelectedSlot = null; }}
							>
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
								<button
									class="slot-item"
									class:selected={tdSelectedSlot === s.slot_id}
									onclick={() => (tdSelectedSlot = s.slot_id as number)}
								>
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
	/* ─── Tokens ─── */
	:global(:root) {
		--navy: #0d1b2a;
		--navy-mid: #132236;
		--navy-light: #1c3352;
		--gold: #c9a84c;
		--gold-light: #e2c97e;
		--gold-dim: rgba(201, 168, 76, 0.15);
		--text-off: rgba(255,255,255,0.55);
		--text-mid: rgba(255,255,255,0.75);
		--font-display: 'Syne', sans-serif;
		--font-body: 'DM Mono', monospace;
		--transition: 0.35s cubic-bezier(0.4, 0, 0.2, 1);
	}

	/* ─── Hero ─── */
	.hero {
		position: relative;
		height: 100svh;
		min-height: 640px;
		overflow: hidden;
		background: var(--navy);
	}

	.hero-slide {
		position: absolute;
		inset: 0;
		display: grid;
		grid-template-columns: 1fr 1fr;
		align-items: center;
		padding: 0 8vw;
		gap: 3rem;
		opacity: 0;
		transition: opacity 0.9s ease;
		pointer-events: none;
	}
	.hero-slide.active {
		opacity: 1;
		pointer-events: auto;
	}

	.hero-bg {
		position: absolute;
		inset: 0;
		background:
			radial-gradient(ellipse 70% 60% at 65% 50%, rgba(201,168,76,0.08) 0%, transparent 70%),
			radial-gradient(ellipse 40% 50% at 20% 80%, rgba(52,232,158,0.05) 0%, transparent 60%),
			linear-gradient(160deg, #0d1b2a 0%, #132236 60%, #1a2e4a 100%);
	}

	.hero-grid-overlay {
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
			linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
		background-size: 60px 60px;
		mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black, transparent);
	}

	.hero-content {
		position: relative;
		z-index: 2;
		max-width: 600px;
	}

	/* ─── Hero Image Panel ─── */
	.hero-image-panel {
		position: relative;
		z-index: 2;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 60%;
		max-height: 480px;
	}

	.hero-img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		border-radius: 20px;
		border: 1px solid rgba(201,168,76,0.2);
		box-shadow:
			0 0 0 1px rgba(201,168,76,0.1),
			0 32px 64px rgba(0,0,0,0.5),
			0 8px 16px rgba(0,0,0,0.3);
	}

	.hero-img-placeholder {
		width: 100%;
		height: 100%;
		border-radius: 20px;
		border: 2px dashed rgba(201,168,76,0.25);
		background: rgba(201,168,76,0.03);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		position: relative;
		overflow: hidden;
	}

	.placeholder-ring {
		position: absolute;
		width: 300px;
		height: 300px;
		border-radius: 50%;
		border: 1px solid rgba(201,168,76,0.08);
	}
	.ring-2 {
		width: 200px;
		height: 200px;
		border-color: rgba(201,168,76,0.12);
	}

	.placeholder-label {
		font-family: var(--font-body);
		font-size: 0.72rem;
		letter-spacing: 2px;
		text-transform: uppercase;
		color: rgba(201,168,76,0.4);
		position: relative;
		z-index: 1;
	}

	.hero-tag {
		display: inline-block;
		font-family: var(--font-body);
		font-size: 0.72rem;
		letter-spacing: 3px;
		text-transform: uppercase;
		color: var(--gold);
		background: var(--gold-dim);
		border: 1px solid rgba(201,168,76,0.3);
		border-radius: 4px;
		padding: 5px 14px;
		margin-bottom: 1.5rem;
	}

	.hero-title {
		font-family: var(--font-display);
		font-size: clamp(3rem, 7vw, 5.5rem);
		font-weight: 800;
		line-height: 1.05;
		color: #fff;
		margin: 0 0 1.25rem;
		letter-spacing: -1px;
	}

	.hero-subtitle {
		font-family: var(--font-body);
		font-size: clamp(0.9rem, 1.4vw, 1.05rem);
		color: var(--text-mid);
		max-width: 520px;
		line-height: 1.75;
		margin: 0 0 2.5rem;
	}

	.hero-cta-row {
		display: flex;
		gap: 1rem;
		align-items: center;
		flex-wrap: wrap;
	}

	/* ─── Carousel Controls ─── */
	.carousel-btn {
		position: absolute;
		bottom: 3rem;
		z-index: 10;
		width: 44px;
		height: 44px;
		border-radius: 50%;
		border: 1px solid rgba(255,255,255,0.15);
		background: rgba(255,255,255,0.06);
		color: #fff;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		backdrop-filter: blur(8px);
		transition: var(--transition);
	}
	.carousel-btn:hover { background: rgba(255,255,255,0.15); border-color: rgba(255,255,255,0.3); }
	.carousel-prev { right: calc(8vw + 52px); }
	.carousel-next { right: 8vw; }

	.carousel-track {
		position: absolute;
		bottom: 0;
		left: 8vw;
		z-index: 10;
		display: flex;
		gap: 0;
	}

	.track-item {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 1.25rem 2rem 1.25rem 0;
		border: none;
		background: transparent;
		cursor: pointer;
		opacity: 0.4;
		transition: opacity var(--transition);
		position: relative;
	}
	.track-item::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 2rem;
		height: 2px;
		background: rgba(255,255,255,0.1);
		transition: background var(--transition);
	}
	.track-item.active { opacity: 1; }
	.track-item.active::before { background: var(--gold); }

	.track-number {
		font-family: var(--font-body);
		font-size: 0.65rem;
		color: var(--gold);
		letter-spacing: 1px;
	}
	.track-line { display: none; }
	.track-title {
		font-family: var(--font-display);
		font-size: 0.78rem;
		font-weight: 600;
		color: #fff;
		white-space: nowrap;
	}

	/* ─── Buttons ─── */
	.btn-primary {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		font-family: var(--font-display);
		font-weight: 700;
		font-size: 0.9rem;
		letter-spacing: 0.5px;
		color: var(--navy);
		background: var(--gold);
		border: none;
		border-radius: 8px;
		padding: 0.85rem 2rem;
		text-decoration: none;
		transition: var(--transition);
		cursor: pointer;
	}
	.btn-primary:hover { background: var(--gold-light); transform: translateY(-1px); }
	.btn-primary.large { padding: 1rem 2.5rem; font-size: 1rem; }

	.btn-ghost {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		font-family: var(--font-display);
		font-weight: 600;
		font-size: 0.9rem;
		color: rgba(255,255,255,0.8);
		background: transparent;
		border: 1px solid rgba(255,255,255,0.2);
		border-radius: 8px;
		padding: 0.85rem 2rem;
		text-decoration: none;
		transition: var(--transition);
		cursor: pointer;
	}
	.btn-ghost:hover { border-color: rgba(255,255,255,0.5); color: #fff; background: rgba(255,255,255,0.05); }

	.btn-ghost-light {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		font-family: var(--font-display);
		font-weight: 600;
		font-size: 0.9rem;
		color: #fff;
		background: transparent;
		border: 1px solid rgba(255,255,255,0.3);
		border-radius: 8px;
		padding: 0.85rem 2rem;
		text-decoration: none;
		transition: var(--transition);
	}
	.btn-ghost-light:hover { border-color: rgba(255,255,255,0.7); background: rgba(255,255,255,0.08); }
	.btn-ghost-light.large { padding: 1rem 2.5rem; font-size: 1rem; }

	/* ─── Search Dock ─── */
	.search-dock {
		background: #fff;
		border-bottom: 1px solid #eee;
		padding: 1.5rem 0;
	}
	.dock-inner {
		max-width: 1100px;
		margin: 0 auto;
		padding: 0 2rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	.search-row {
		display: flex;
		gap: 0.75rem;
	}
	.search-input-wrap {
		flex: 1;
		position: relative;
	}
	:global(.search-ico) {
		position: absolute;
		left: 14px;
		top: 50%;
		transform: translateY(-50%);
		color: #999;
		pointer-events: none;
	}
	.search-input {
		width: 100%;
		height: 46px;
		padding: 0 1rem 0 2.75rem;
		border: 1.5px solid #e0e0e0;
		border-radius: 10px;
		font-family: var(--font-body);
		font-size: 0.9rem;
		color: #222;
		outline: none;
		transition: border-color 0.2s;
		box-sizing: border-box;
		background: #fafafa;
	}
	.search-input:focus { border-color: var(--navy); background: #fff; }
	.search-btn {
		height: 46px;
		padding: 0 1.75rem;
		background: var(--navy);
		color: #fff;
		border: none;
		border-radius: 10px;
		font-family: var(--font-display);
		font-weight: 700;
		font-size: 0.9rem;
		cursor: pointer;
		transition: var(--transition);
		white-space: nowrap;
	}
	.search-btn:hover { background: var(--navy-light); }

	.filter-row {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem 1.5rem;
		align-items: center;
	}
	.filter-cluster {
		display: flex;
		align-items: center;
		gap: 6px;
	}
	.filter-lbl {
		font-family: var(--font-body);
		font-size: 0.7rem;
		letter-spacing: 1.5px;
		text-transform: uppercase;
		color: #999;
		min-width: 36px;
	}
	.chip {
		padding: 5px 14px;
		border-radius: 20px;
		border: 1px solid #e0e0e0;
		background: transparent;
		font-family: var(--font-body);
		font-size: 0.78rem;
		color: #555;
		cursor: pointer;
		transition: all 0.2s;
	}
	.chip.on {
		background: var(--navy);
		color: #fff;
		border-color: var(--navy);
	}
	.chip:hover:not(.on) { border-color: var(--navy); color: var(--navy); }

	/* ─── Stats Band ─── */
	.stats-band {
		background: var(--navy);
		padding: 2rem 0;
	}
	.stats-inner {
		max-width: 1100px;
		margin: 0 auto;
		padding: 0 2rem;
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1rem;
	}
	.stat-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
		padding: 1rem;
		border-right: 1px solid rgba(255,255,255,0.08);
	}
	.stat-item:last-child { border-right: none; }
	.stat-val {
		font-family: var(--font-display);
		font-size: 2rem;
		font-weight: 800;
		color: var(--gold);
		line-height: 1;
	}
	.stat-lbl {
		font-family: var(--font-body);
		font-size: 0.72rem;
		letter-spacing: 1.5px;
		text-transform: uppercase;
		color: var(--text-off);
	}

	/* ─── Sections ─── */
	.section { padding: 5.5rem 0; }
	.section-inner {
		max-width: 1100px;
		margin: 0 auto;
		padding: 0 2rem;
	}
	.section-eyebrow {
		font-family: var(--font-body);
		font-size: 0.72rem;
		letter-spacing: 3px;
		text-transform: uppercase;
		color: var(--gold);
		margin-bottom: 0.75rem;
		text-align: center;
	}
	.section-title {
		font-family: var(--font-display);
		font-size: clamp(1.8rem, 3.5vw, 2.8rem);
		font-weight: 800;
		color: var(--navy);
		text-align: center;
		margin: 0 0 1rem;
		letter-spacing: -0.5px;
	}
	.section-title.left { text-align: left; }
	.section-sub {
		font-family: var(--font-body);
		font-size: 0.95rem;
		color: #666;
		text-align: center;
		max-width: 520px;
		margin: 0 auto 3.5rem;
		line-height: 1.7;
	}

	.section-header-row {
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		margin-bottom: 2.5rem;
	}
	.section-header-row .section-eyebrow { text-align: left; }

	.link-all {
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 700;
		color: var(--navy);
		text-decoration: none;
		border-bottom: 2px solid var(--gold);
		padding-bottom: 2px;
		transition: color 0.2s;
	}
	.link-all:hover { color: var(--gold); }

	/* ─── Why Section ─── */
	.why-section { background: #f6f7fb; }

	.features-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1.25rem;
	}

	.feature-card {
		background: #fff;
		border-radius: 14px;
		padding: 2rem 1.5rem;
		border: 1px solid #eee;
		position: relative;
		overflow: hidden;
		transition: transform 0.3s, box-shadow 0.3s;
	}
	.feature-card::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: linear-gradient(90deg, var(--gold), transparent);
		transform: scaleX(0);
		transform-origin: left;
		transition: transform 0.4s ease;
	}
	.feature-card:hover { transform: translateY(-5px); box-shadow: 0 12px 32px rgba(0,0,0,0.08); }
	.feature-card:hover::after { transform: scaleX(1); }

	.feature-num {
		font-family: var(--font-body);
		font-size: 0.65rem;
		letter-spacing: 2px;
		color: var(--gold);
		margin-bottom: 1.25rem;
	}

	.feature-icon-wrap {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 52px;
		height: 52px;
		border-radius: 12px;
		background: linear-gradient(135deg, #f0f4ff, #e8ecff);
		color: var(--navy);
		margin-bottom: 1.25rem;
	}

	.feature-title {
		font-family: var(--font-display);
		font-size: 1rem;
		font-weight: 700;
		color: var(--navy);
		margin: 0 0 0.5rem;
	}
	.feature-desc {
		font-family: var(--font-body);
		font-size: 0.82rem;
		color: #777;
		line-height: 1.65;
		margin: 0;
	}

	/* ─── Vehicles ─── */
	.vehicles-section { background: #fff; }

	.loading-row {
		display: flex;
		gap: 10px;
		justify-content: center;
		padding: 4rem;
	}
	.loading-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--gold);
		animation: pulse 1.4s ease-in-out infinite;
	}
	.loading-dot:nth-child(2) { animation-delay: 0.2s; }
	.loading-dot:nth-child(3) { animation-delay: 0.4s; }
	@keyframes pulse { 0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); } 40% { opacity: 1; transform: scale(1); } }

	.vehicles-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1.25rem;
	}

	.vehicle-card {
		border-radius: 14px;
		overflow: hidden;
		border: 1px solid #eee;
		transition: transform 0.3s, box-shadow 0.3s;
		background: #fff;
		cursor: pointer;
	}
	.vehicle-card:hover { transform: translateY(-5px); box-shadow: 0 12px 32px rgba(0,0,0,0.1); }

	.vehicle-thumb {
		position: relative;
		height: 190px;
		background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
		display: flex;
		align-items: flex-end;
		padding: 1rem;
		overflow: hidden;
	}
	.vehicle-photo {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.badge-new {
		position: absolute;
		top: 12px;
		left: 12px;
		background: var(--gold);
		color: var(--navy);
		font-family: var(--font-body);
		font-size: 0.65rem;
		font-weight: 700;
		letter-spacing: 1.5px;
		text-transform: uppercase;
		padding: 4px 10px;
		border-radius: 4px;
	}

	.thumb-label {
		font-family: var(--font-display);
		font-size: 1.1rem;
		font-weight: 700;
		color: rgba(255,255,255,0.25);
	}

	.vehicle-body {
		padding: 1.1rem 1.25rem 1.25rem;
	}
	.vehicle-name {
		font-family: var(--font-display);
		font-size: 1rem;
		font-weight: 700;
		color: var(--navy);
		margin: 0 0 0.4rem;
	}
	.vehicle-specs {
		font-family: var(--font-body);
		font-size: 0.75rem;
		color: #999;
		display: flex;
		align-items: center;
		gap: 5px;
		margin-bottom: 1rem;
		flex-wrap: wrap;
	}
	.dot-sep { color: var(--gold); }

	.vehicle-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.vehicle-price {
		font-family: var(--font-display);
		font-size: 1.05rem;
		font-weight: 800;
		color: var(--navy);
	}
	.card-cta {
		font-family: var(--font-body);
		font-size: 0.78rem;
		color: var(--gold);
		text-decoration: none;
		font-weight: 600;
		letter-spacing: 0.5px;
		transition: letter-spacing 0.2s;
	}
	.card-cta:hover { letter-spacing: 1.5px; }

	/* ─── Testimonials ─── */
	.testimonials-section { background: #f6f7fb; }

	.testimonials-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1.25rem;
		margin-top: 0.5rem;
	}

	.testimonial-card {
		background: #fff;
		border-radius: 14px;
		padding: 2rem;
		border: 1px solid #eee;
		position: relative;
	}
	.t-quote-mark {
		font-family: Georgia, serif;
		font-size: 4.5rem;
		line-height: 0.8;
		color: var(--gold);
		opacity: 0.2;
		position: absolute;
		top: 16px;
		left: 20px;
	}
	.t-text {
		font-family: var(--font-body);
		font-size: 0.85rem;
		color: #555;
		line-height: 1.8;
		margin: 0.75rem 0 1.5rem;
		position: relative;
		z-index: 1;
	}
	.t-author {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}
	.t-avatar {
		width: 42px;
		height: 42px;
		border-radius: 50%;
		background: var(--navy);
		color: var(--gold);
		display: flex;
		align-items: center;
		justify-content: center;
		font-family: var(--font-display);
		font-weight: 700;
		font-size: 0.9rem;
		flex-shrink: 0;
	}
	.t-name {
		font-family: var(--font-display);
		font-weight: 700;
		font-size: 0.88rem;
		color: var(--navy);
	}
	.t-role {
		font-family: var(--font-body);
		font-size: 0.72rem;
		color: #aaa;
		letter-spacing: 0.5px;
	}

	/* ─── CTA Banner ─── */
	.cta-banner {
		background: linear-gradient(135deg, var(--navy) 0%, #1c3352 60%, #0f2a45 100%);
		padding: 5rem 0;
		position: relative;
		overflow: hidden;
	}
	.cta-banner::before {
		content: '';
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(rgba(201,168,76,0.04) 1px, transparent 1px),
			linear-gradient(90deg, rgba(201,168,76,0.04) 1px, transparent 1px);
		background-size: 48px 48px;
	}
	.cta-inner {
		position: relative;
		max-width: 700px;
		margin: 0 auto;
		padding: 0 2rem;
		text-align: center;
	}
	.cta-title {
		font-family: var(--font-display);
		font-size: clamp(2rem, 4vw, 3rem);
		font-weight: 800;
		color: #fff;
		margin: 0 0 1rem;
		letter-spacing: -0.5px;
	}
	.cta-sub {
		font-family: var(--font-body);
		font-size: 0.95rem;
		color: var(--text-mid);
		margin: 0 0 2.5rem;
		line-height: 1.7;
	}
	.cta-btns {
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
	}

	/* ─── Responsive ─── */
	@media (max-width: 1024px) {
		.features-grid { grid-template-columns: repeat(2, 1fr); }
		.vehicles-grid { grid-template-columns: repeat(2, 1fr); }
		.testimonials-grid { grid-template-columns: 1fr; }
		.stats-inner { grid-template-columns: repeat(2, 1fr); }
	}
	@media (max-width: 768px) {
		.hero { height: auto; min-height: 100svh; }
		.hero-slide {
			grid-template-columns: 1fr;
			padding: 6rem 1.5rem 12rem;
			align-items: flex-start;
		}
		.hero-image-panel { display: none; }
		.carousel-track { left: 1.5rem; }
		.track-title { display: none; }
		.carousel-btn { bottom: 2rem; }
		.carousel-prev { right: calc(1.5rem + 52px); }
		.carousel-next { right: 1.5rem; }
		.features-grid { grid-template-columns: 1fr; }
		.vehicles-grid { grid-template-columns: 1fr; }
		.stats-inner { grid-template-columns: repeat(2, 1fr); }
		.section-header-row { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
		.hero-cta-row { flex-direction: column; align-items: flex-start; }
		.search-row { flex-direction: column; }
		.filter-row { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
	}
	@media (max-width: 480px) {
		.stats-inner { grid-template-columns: 1fr; }
		.testimonials-grid { grid-template-columns: 1fr; }
	}

	/* Vehicle action buttons */
	.vehicle-actions {
		display: flex;
		gap: 6px;
		margin-top: 10px;
	}
	.act-btn {
		flex: 1;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 4px;
		padding: 7px 6px;
		border: none;
		border-radius: 8px;
		font-family: var(--font-sans);
		font-size: 11px;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.2s;
		min-width: 0;
		white-space: nowrap;
	}
	.act-inquire { background: #eef2ff; color: #4338ca; }
	.act-inquire:hover { background: #e0e7ff; }
	.act-reserve { background: #f0fdf4; color: #166534; }
	.act-reserve:hover { background: #dcfce7; }
	.act-testdrive { background: #fef3c7; color: #92400e; }
	.act-testdrive:hover { background: #fde68a; }

	/* Modals */
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.45);
		z-index: 1000;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1rem;
	}
	.modal {
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 460px;
		max-width: calc(100vw - 2rem);
		max-height: 85vh;
		background: #fff;
		border-radius: 14px;
		box-shadow: 0 20px 60px rgba(0,0,0,0.15);
		z-index: 1010;
		display: flex;
		flex-direction: column;
		overflow-y: auto;
	}
	.modal-wide { width: 520px; }
	.modal-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.25rem 1.5rem;
		border-bottom: 1px solid #e5e7eb;
		flex-shrink: 0;
	}
	.modal-head h3 { margin: 0; font-size: 16px; font-weight: 700; color: #1a1a2e; }
	.modal-close { background: none; border: none; cursor: pointer; color: #9ca3af; padding: 4px; border-radius: 4px; }
	.modal-close:hover { color: #1a1a2e; background: #f3f4f6; }
	.modal-body { padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 10px; }
	.modal-label { font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.3px; }
	.req { color: #dc2626; }
	.modal-input, .modal-textarea {
		padding: 10px 12px;
		border: 1px solid #d1d5db;
		border-radius: 8px;
		font-family: var(--font-sans);
		font-size: 13px;
		outline: none;
	}
	.modal-input:focus, .modal-textarea:focus { border-color: var(--primary); }
	.modal-textarea { resize: vertical; min-height: 80px; }
	.modal-btn {
		padding: 10px 20px;
		background: var(--primary);
		color: #fff;
		border: none;
		border-radius: 8px;
		font-family: var(--font-sans);
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.2s;
	}
	.modal-btn:hover:not(:disabled) { background: var(--primary-dark); }
	.modal-btn:disabled { opacity: 0.5; cursor: not-allowed; }
	.modal-btn-secondary {
		padding: 10px 20px;
		background: #fff;
		color: #374151;
		border: 1px solid #d1d5db;
		border-radius: 8px;
		font-family: var(--font-sans);
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.2s;
	}
	.modal-btn-secondary:hover { background: #f9fafb; }
	.done-msg {
		text-align: center;
		padding: 1.5rem 0;
		color: #065f46;
		font-size: 14px;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
	}
	.done-icon { color: #059669; }
	.pay-prompt {
		text-align: center;
		padding: 1rem 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 10px;
	}
	.pay-prompt p { margin: 0; color: #374151; font-size: 14px; }
	.pay-actions { display: flex; gap: 10px; margin-top: 8px; }
	.date-group-list, .slot-list { display: flex; flex-direction: column; gap: 6px; }
	.hint { color: #9ca3af; font-size: 13px; text-align: center; padding: 1rem 0; margin: 0; }
	.date-chip {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 10px 14px;
		border: 1px solid #e5e7eb;
		border-radius: 10px;
		background: #fff;
		cursor: pointer;
		font-family: var(--font-sans);
		font-size: 13px;
		text-align: left;
		transition: border-color 0.2s;
	}
	.date-chip:hover { border-color: var(--primary); }
	.date-chip.selected { border-color: var(--primary); background: #eef2ff; }
	.date-label { font-weight: 600; color: #1a1a2e; }
	.slot-count { font-size: 11px; color: #6b7280; }
	.slot-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 8px 14px;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		background: #fff;
		cursor: pointer;
		font-family: var(--font-sans);
		font-size: 13px;
		text-align: left;
		transition: border-color 0.2s;
	}
	.slot-item:hover { border-color: var(--primary); }
	.slot-item.selected { border-color: var(--primary); background: #eef2ff; }
	.remaining { font-size: 11px; color: #6b7280; }
</style>