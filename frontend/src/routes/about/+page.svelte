<script lang="ts">
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { ShieldCheck, Zap, Eye, HeartHandshake, Award, Users, Building2, TrendingUp } from '@lucide/svelte';
</script>

<Navbar />

<section class="about-hero">
	<div class="about-hero-inner">
		<span class="about-hero-tag">Who We Are</span>
		<h1 class="about-hero-title">About AutoMatik</h1>
		<p class="about-hero-sub">
			Philippines' most trusted dealership for brand-new vehicles.
			Simple applications, fast approvals, and transparent pricing.
		</p>
	</div>
</section>

<section class="section story">
	<div class="section-inner">
		<div class="story-grid">
			<div class="story-text">
				<h2>Our Story</h2>
				<p>
					Founded in 2015, AutoMatik set out to change the way Filipinos buy cars.
					We believed that purchasing a brand-new vehicle should be simple, transparent,
					and stress-free — not a maze of hidden fees and endless negotiations.
				</p>
				<p>
					Today, we serve thousands of happy customers across <b>Metro Manila and beyond</b>.
					With integrated financing, in-house service centers, and a dedicated team of
					agents, we make the journey from application to approval as seamless as possible.
				</p>
			</div>
			<div class="story-stats">
				<div class="stat-card"><span class="stat-num">10+</span><span class="stat-lbl">Years in Service</span></div>
				<div class="stat-card"><span class="stat-num">5,000+</span><span class="stat-lbl">Vehicles Delivered</span></div>
				<div class="stat-card"><span class="stat-num">4</span><span class="stat-lbl">Branch Locations</span></div>
				<div class="stat-card"><span class="stat-num">98%</span><span class="stat-lbl">Customer Satisfaction</span></div>
			</div>
		</div>
	</div>
</section>

<section class="section mission">
	<div class="section-inner">
		<h2 class="section-title">Mission, Vision &amp; Values</h2>
		<div class="mvv-grid">
			<div class="mvv-card">
				<Award size={28} />
				<h3>Mission</h3>
				<p>To provide every Filipino with a simple, transparent, and hassle-free path to owning a brand-new vehicle.</p>
			</div>
			<div class="mvv-card">
				<TrendingUp size={28} />
				<h3>Vision</h3>
				<p>To be the most trusted automotive marketplace in the Philippines, known for fairness, speed, and integrity.</p>
			</div>
			<div class="mvv-card">
				<HeartHandshake size={28} />
				<h3>Values</h3>
				<p>Integrity, transparency, customer-first mindset, and continuous innovation in everything we do.</p>
			</div>
		</div>
	</div>
</section>

<section class="section features">
	<div class="section-inner">
		<h2 class="section-title">Why Choose Us</h2>
		<div class="features-grid">
			<div class="feature-card">
				<ShieldCheck size={22} />
				<h4>Brand New Only</h4>
				<p>Zero mileage, full manufacturer warranty on every vehicle we sell.</p>
			</div>
			<div class="feature-card">
				<Zap size={22} />
				<h4>Fast Approvals</h4>
				<p>Financing decisions in minutes, not days. Drive home the same day.</p>
			</div>
			<div class="feature-card">
				<Eye size={22} />
				<h4>Transparent Pricing</h4>
				<p>No hidden fees, no trade-ins, no negotiations. What you see is what you pay.</p>
			</div>
			<div class="feature-card">
				<Users size={22} />
				<h4>Dedicated Support</h4>
				<p>Personal agents guide you from inquiry to delivery and beyond.</p>
			</div>
			<div class="feature-card">
				<Building2 size={22} />
				<h4>Full-Service Centers</h4>
				<p>In-house maintenance, repairs, and warranty claims at every branch.</p>
			</div>
			<div class="feature-card">
				<HeartHandshake size={22} />
				<h4>Hassle-Free Process</h4>
				<p>Simple online application, minimal requirements, no pressure.</p>
			</div>
		</div>
	</div>
</section>



<Footer />

<style>
	.about-hero { padding: 8rem 1.5rem 4rem; background: linear-gradient(135deg, #1a1a2e 0%, #282854 100%); text-align: center; }
	.about-hero-inner { max-width: 700px; margin: 0 auto; }
	.about-hero-tag { display: inline-block; background: rgba(232,201,126,0.15); color: #e8c97e; font-size: 11px; font-weight: 600; padding: 4px 14px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; }
	.about-hero-title { font-size: 2.5rem; font-weight: 700; color: #fff; margin: 0 0 0.75rem; }
	.about-hero-sub { font-size: 1rem; color: rgba(255,255,255,0.65); max-width: 500px; margin: 0 auto; line-height: 1.6; }

	.section { padding: 4rem 1.5rem; }
	.section-inner { max-width: 1100px; margin: 0 auto; }
	.section-title { font-size: 1.6rem; font-weight: 700; color: #1a1a2e; text-align: center; margin: 0 0 2.5rem; }

	/* Story */
	.story { background: #f9fafb; }
	.story-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; align-items: center; }
	.story-text h2 { font-size: 1.5rem; font-weight: 700; color: #1a1a2e; margin: 0 0 1rem; }
	.story-text p { color: #6b7280; font-size: 14px; line-height: 1.7; margin: 0 0 1rem; }
	.story-text p:last-child { margin-bottom: 0; }
	.story-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
	.stat-card { text-align: center; padding: 1.5rem; background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; }
	.stat-num { display: block; font-size: 1.75rem; font-weight: 700; color: var(--primary); }
	.stat-lbl { font-size: 12px; color: #6b7280; margin-top: 4px; display: block; }

	/* MVV */
	.mission { background: #fff; }
	.mvv-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
	.mvv-card { text-align: center; padding: 2rem 1.5rem; border-radius: 14px; border: 1px solid #e5e7eb; background: #f9fafb; }
	.mvv-card :global(svg) { color: var(--primary); }
	.mvv-card h3 { font-size: 1.1rem; font-weight: 700; color: #1a1a2e; margin: 0.75rem 0 0.5rem; }
	.mvv-card p { font-size: 13px; color: #6b7280; line-height: 1.6; margin: 0; }

	/* Features */
	.features { background: #f9fafb; }
	.features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; }
	.feature-card { padding: 1.5rem; background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; }
	.feature-card :global(svg) { color: var(--primary); }
	.feature-card h4 { font-size: 14px; font-weight: 700; color: #1a1a2e; margin: 0.6rem 0 0.4rem; }
	.feature-card p { font-size: 13px; color: #6b7280; line-height: 1.6; margin: 0; }

	@media (max-width: 768px) {
		.story-grid { grid-template-columns: 1fr; }
		.mvv-grid { grid-template-columns: 1fr; }
		.features-grid { grid-template-columns: 1fr; }
		.about-hero-title { font-size: 1.75rem; }
	}
</style>
