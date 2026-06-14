<script lang="ts">
	const links = {
		quick: [
			{ label: 'Home', href: '/' },
			{ label: 'Browse Vehicles', href: '/vehicles' },
			{ label: 'Loan Calculator', href: '/loan-calculator' },
			{ label: 'Contact', href: '/contact' },
			{ label: 'About', href: '/about' },
		],
		legal: [
			{ label: 'Privacy Policy', href: '/privacy-policy' },
			{ label: 'Terms & Conditions', href: '/terms-and-conditions' },
		],
		services: [
			{ label: 'New Cars', href: '/vehicles' },
			{ label: 'Financing', href: '/loan-calculator' },
			{ label: 'Service Center', href: '/portal/service' },
		],
	};
</script>

<footer class="footer">
	<div class="footer-inner">
		<div class="footer-grid">
			<div class="footer-brand">
				<h3 class="footer-logo">AUTOMATIK</h3>
				<p class="footer-desc">
					Your trusted dealership for brand-new vehicles. Simple applications, fast approvals,
					and transparent pricing — no trade-ins, no hassle.
				</p>
			</div>

			<div class="footer-col">
				<h4 class="footer-heading">Quick Links</h4>
				<ul>
					{#each links.quick as link}
						<li><a href={link.href}>{link.label}</a></li>
					{/each}
				</ul>
			</div>

			<div class="footer-col">
				<h4 class="footer-heading">Services</h4>
				<ul>
					{#each links.services as link}
						<li><a href={link.href}>{link.label}</a></li>
					{/each}
				</ul>
			</div>

			<div class="footer-col">
				<h4 class="footer-heading">Legal</h4>
				<ul>
					{#each links.legal as link}
						<li><a href={link.href}>{link.label}</a></li>
					{/each}
				</ul>
			</div>

			<div class="footer-col">
				<h4 class="footer-heading">Contact</h4>
				<ul class="contact-list">
					<li>123 AutoMall Drive</li>
					<li>Makati City, Philippines</li>
					<li><a href="tel:+63281234567">+63 (2) 8123 4567</a></li>
					<li><a href="mailto:info@automatik.com">info@automatik.com</a></li>
				</ul>
			</div>
		</div>

		<div class="footer-bottom">
			<p>&copy; {new Date().getFullYear()} AutoMatik. All rights reserved.</p>
		</div>
	</div>
</footer>

<style>
	.footer {
		background: #1a1a2e;
		color: rgba(255, 255, 255, 0.8);
		padding: 4rem 0 0;
	}
	.footer-inner {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 1.5rem;
	}
	.footer-grid {
		display: grid;
		grid-template-columns: 1.5fr 1fr 1fr 1fr;
		gap: 3rem;
	}
	.footer-logo {
		font-family: var(--font-sans);
		font-size: 1.4rem;
		font-weight: 700;
		color: #fff;
		letter-spacing: 2px;
		margin: 0 0 1rem;
	}
	.footer-desc {
		font-size: 0.9rem;
		line-height: 1.6;
		color: rgba(255, 255, 255, 0.6);
		margin: 0;
	}
	.footer-heading {
		font-family: var(--font-sans);
		font-size: 0.95rem;
		font-weight: 600;
		color: #fff;
		margin: 0 0 1rem;
		text-transform: uppercase;
		letter-spacing: 1px;
	}
	.footer-col ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	.footer-col li {
		margin-bottom: 0.6rem;
	}
	.footer-col a {
		color: rgba(255, 255, 255, 0.6);
		text-decoration: none;
		font-size: 0.9rem;
		transition: color 0.2s;
	}
	.footer-col a:hover {
		color: #fff;
	}
	.contact-list li {
		color: rgba(255, 255, 255, 0.6);
		font-size: 0.9rem;
	}
	.footer-bottom {
		border-top: 1px solid rgba(255, 255, 255, 0.1);
		padding: 1.5rem 0;
		margin-top: 3rem;
		text-align: center;
	}
	.footer-bottom p {
		margin: 0;
		font-size: 0.85rem;
		color: rgba(255, 255, 255, 0.4);
	}

	@media (max-width: 768px) {
		.footer-grid {
			grid-template-columns: 1fr;
			gap: 2rem;
		}
	}
</style>
