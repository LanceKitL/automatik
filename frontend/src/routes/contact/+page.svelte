<script lang="ts">
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { submitContactForm } from '$lib/services/api';
	import { MapPin, Phone, Mail, Clock, Send } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';

	let form = $state({ name: '', email: '', phone: '', subject: '', message: '' });
	let sending = $state(false);
	let sent = $state(false);

	async function handleSubmit() {
		if (!form.name || !form.email || !form.message) return;
		sending = true;
		try {
			await submitContactForm({
				name: form.name,
				email: form.email,
				phone: form.phone || undefined,
				subject: form.subject || undefined,
				message: form.message,
			});
			sent = true;
			toast.success('Message sent! We will get back to you shortly.');
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to send message.');
		} finally {
			sending = false;
		}
	}
</script>

<Navbar />

<section class="contact-hero">
	<div class="contact-hero-inner">
		<span class="contact-hero-tag">Get in Touch</span>
		<h1 class="contact-hero-title">Contact Us</h1>
		<p class="contact-hero-sub">
			Have a question? Want to book a test drive? Our team is here to help.
		</p>
	</div>
</section>

<section class="section">
	<div class="section-inner">
		<div class="contact-layout">
			<!-- Info cards -->
			<div class="contact-info">
				<h2>Visit or Reach Us</h2>
				<div class="info-cards">
					<div class="info-card">
						<MapPin size={20} />
						<div>
							<span class="info-label">Address</span>
							<span class="info-value">123 AutoMall Drive<br />Makati City, Philippines</span>
						</div>
					</div>
					<div class="info-card">
						<Phone size={20} />
						<div>
							<span class="info-label">Phone</span>
							<a href="tel:+63281234567" class="info-value">+63 (2) 8123 4567</a>
						</div>
					</div>
					<div class="info-card">
						<Mail size={20} />
						<div>
							<span class="info-label">Email</span>
							<a href="mailto:info@automatik.com" class="info-value">info@automatik.com</a>
						</div>
					</div>
					<div class="info-card">
						<Clock size={20} />
						<div>
							<span class="info-label">Business Hours</span>
							<span class="info-value">Mon – Sat: 8:00 AM – 6:00 PM<br />Sunday: Closed</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Contact form -->
			<div class="contact-form-wrap">
				<h2>Send Us a Message</h2>
				{#if sent}
					<div class="sent-msg">
						<Send size={32} />
						<strong>Message Sent!</strong>
						<p>Thank you for reaching out. Our team will respond within 24 hours.</p>
					</div>
				{:else}
					<form class="contact-form" onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
						<div class="form-row">
							<div class="form-group">
								<label>Name <span class="req">*</span></label>
								<input type="text" bind:value={form.name} placeholder="Your full name" required />
							</div>
							<div class="form-group">
								<label>Email <span class="req">*</span></label>
								<input type="email" bind:value={form.email} placeholder="your@email.com" required />
							</div>
						</div>
						<div class="form-row">
							<div class="form-group">
								<label>Phone</label>
								<input type="tel" bind:value={form.phone} placeholder="+63 912 345 6789" />
							</div>
							<div class="form-group">
								<label>Subject</label>
								<input type="text" bind:value={form.subject} placeholder="How can we help?" />
							</div>
						</div>
						<div class="form-group">
							<label>Message <span class="req">*</span></label>
							<textarea rows="4" bind:value={form.message} placeholder="Tell us more about your inquiry…" required></textarea>
						</div>
						<button class="submit-btn" disabled={sending || !form.name || !form.email || !form.message}>
							{sending ? 'Sending…' : 'Send Message'}
						</button>
					</form>
				{/if}
			</div>
		</div>
	</div>
</section>

<Footer />

<style>
	.contact-hero { padding: 8rem 1.5rem 4rem; background: linear-gradient(135deg, #1a1a2e 0%, #282854 100%); text-align: center; }
	.contact-hero-inner { max-width: 700px; margin: 0 auto; }
	.contact-hero-tag { display: inline-block; background: rgba(232,201,126,0.15); color: #e8c97e; font-size: 11px; font-weight: 600; padding: 4px 14px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; }
	.contact-hero-title { font-size: 2.5rem; font-weight: 700; color: #fff; margin: 0 0 0.75rem; }
	.contact-hero-sub { font-size: 1rem; color: rgba(255,255,255,0.65); max-width: 500px; margin: 0 auto; line-height: 1.6; }

	.section { padding: 4rem 1.5rem; }
	.section-inner { max-width: 1100px; margin: 0 auto; }

	.contact-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 2.5rem; align-items: start; }

	.contact-info h2, .contact-form-wrap h2 { font-size: 1.3rem; font-weight: 700; color: #1a1a2e; margin: 0 0 1.25rem; }

	.info-cards { display: flex; flex-direction: column; gap: 1rem; }
	.info-card { display: flex; align-items: flex-start; gap: 14px; padding: 1.1rem 1.25rem; border: 1px solid #e5e7eb; border-radius: 12px; background: #f9fafb; }
	.info-card :global(svg) { color: var(--primary); flex-shrink: 0; margin-top: 2px; }
	.info-label { display: block; font-size: 10px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px; }
	.info-value { font-size: 14px; color: #1a1a2e; line-height: 1.5; }
	a.info-value { color: var(--primary); text-decoration: none; }
	a.info-value:hover { text-decoration: underline; }

	/* Form */
	.contact-form-wrap { background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 1.5rem; }
	.contact-form { display: flex; flex-direction: column; gap: 14px; }
	.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
	.form-group { display: flex; flex-direction: column; gap: 5px; }
	.form-group label { font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.4px; }
	.req { color: #dc2626; }
	.form-group input, .form-group textarea { padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-family: var(--font-sans); font-size: 14px; outline: none; }
	.form-group input:focus, .form-group textarea:focus { border-color: var(--primary); }
	.form-group textarea { resize: vertical; min-height: 100px; }
	.submit-btn { padding: 12px 24px; background: var(--primary); color: #fff; border: none; border-radius: 8px; font-family: var(--font-sans); font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
	.submit-btn:hover:not(:disabled) { background: var(--primary-dark); }
	.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

	.sent-msg { text-align: center; padding: 2rem 0; display: flex; flex-direction: column; align-items: center; gap: 10px; }
	.sent-msg :global(svg) { color: #059669; }
	.sent-msg strong { font-size: 16px; color: #065f46; }
	.sent-msg p { font-size: 14px; color: #6b7280; margin: 0; }

	@media (max-width: 768px) {
		.contact-layout { grid-template-columns: 1fr; }
		.form-row { grid-template-columns: 1fr; }
		.contact-hero-title { font-size: 1.75rem; }
	}
</style>
