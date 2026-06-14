<script lang="ts">
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { ShieldCheck } from '@lucide/svelte';
</script>

<Navbar />

<section class="legal-hero">
	<div class="legal-hero-inner">
		<span class="legal-hero-tag">Legal</span>
		<h1 class="legal-hero-title">Privacy Policy</h1>
		<p class="legal-hero-sub">Last updated: 2026 &mdash; Based on the Philippine Data Privacy Act of 2012 (RA 10173)</p>
	</div>
</section>

<section class="legal-section">
	<div class="legal-content">
		<div class="legal-intro">
			<ShieldCheck size={28} />
			<p>AutoMatik recognizes the importance of protecting its users' personal information. In accordance with the Data Privacy Act of 2012 (RA 10173), the system collects only the information needed for transactions and other related services. This policy informs users about how their data is collected, used, and protected while using the system.</p>
		</div>

		<h2>I. Introduction</h2>
		<p>AutoMatik recognizes the importance of protecting its users' personal information. In accordance with the Data Privacy Act of 2012 (RA 10173), the system collects only the information needed for transactions and other related services. The purpose of this policy is to inform users about how their data is collected, used, and protected while using the system.</p>

		<h2>II. Data Collection</h2>
		<p>We collect the following personal information necessary for our system:</p>
		<ul>
			<li><strong>Personal information:</strong> Full Name, Address, Email, and Contact numbers.</li>
			<li><strong>Sensitive Personal Information:</strong> Birthdate, government-issued IDs, and health or financial records.</li>
			<li><strong>Financial and Legal Data:</strong> TIN, Proof of Income, and valid Government IDs for vehicle registration and financing.</li>
			<li><strong>Vehicle Data:</strong> Vehicle Identification Number (VIN), model, and maintenance history.</li>
		</ul>

		<h2>III. Purpose of Data Processing</h2>
		<p>The information we gather is used for the following purposes:</p>
		<ul>
			<li><strong>Service delivery</strong> — including vehicle sales, insurances, and warranty claims. AutoMatik does not maintain a direct API integration with the LTO. Instead, we assist the registration process by organizing the necessary documentation, which our dealership personnel then process manually. This ensures that all details on your OR/CR are accurate and fully compliant with legal requirements.</li>
			<li><strong>System Features</strong> — providing personalized assistance through our Chatbot and calculating estimates via our Payment Calculator. The Payment Calculator is for estimation only and does not store any of your financial data unless you proceed with an official inquiry.</li>
			<li><strong>Communications</strong> — important updates, maintenance reminders, and responding to inquiries.</li>
			<li>Follow applicable <strong>Philippine laws and obligations</strong>, specifically Republic Act No. 10173 (Data Privacy Act of 2012) and its Implementing Rules and Regulations (IRR).</li>
		</ul>

		<h2>IV. User Rights</h2>
		<p>Under Section 16 of the Data Privacy Act of 2012 (RA 10173), you have the following rights:</p>
		<div class="rights-grid">
			<div class="right-card">
				<h3>Right to be Informed</h3>
				<p>You have the right to know if your personal data is being processed, how it is collected, and for what purpose it will be used.</p>
			</div>
			<div class="right-card">
				<h3>Right to Access</h3>
				<p>You can request a copy of any personal data we hold about yourself.</p>
			</div>
			<div class="right-card">
				<h3>Right to Erasure or Blocking</h3>
				<p>Our Data Compliance Officer can perform a permanent, irreversible deletion of your personal data from our central database upon verified request.</p>
			</div>
			<div class="right-card">
				<h3>Right to Damages</h3>
				<p>You may claim compensation if you suffered damages due to inaccurate, incomplete, outdated, or unlawfully obtained data.</p>
			</div>
			<div class="right-card">
				<h3>Right to Data Portability</h3>
				<p>You can obtain an electronic copy of your data in a structured, commonly used format.</p>
			</div>
		</div>

		<h2>V. Retention</h2>
		<p>We use strict security measures to protect your information. Financial records (such as sales contracts and payment receipts) are kept for ten (10) years to comply with the National Internal Revenue Code (NIRC) of 1997, Section 235 (as amended), and related accounting standards. Once this mandatory period ends, your records are either securely disposed of or anonymized.</p>

		<h2>VI. Changes to this Policy</h2>
		<p>We may update this privacy policy from time to time to reflect changes in our practices or legal obligations. We encourage you to review the policy periodically.</p>

		<h2>VII. Government Disclosure</h2>
		<p>AutoMatik complies with the Data Privacy Act of 2012 (Republic Act No. 10173) and its Implementing Rules and Regulations (IRR). The system supports the directives of the National Privacy Commission (NPC) and, where applicable, the regulations of the Bangko Sentral ng Pilipinas (BSP) for financial transactions and the Land Transportation Office (LTO) for vehicle documentation. Any data breach will be reported to the NPC within 72 hours of discovery, in accordance with NPC Circular No. 16-03.</p>

		<h2>VIII. Contact Us</h2>
		<p>For questions, concerns, or requests regarding your personal data, contact:</p>
		<div class="contact-box">
			<p><strong>Data Compliance Officer &mdash; AutoMatik</strong></p>
			<p>Polytechnic University of the Philippines</p>
			<p>Email: <a href="mailto:automatik.compliance@pup.edu.ph">automatik.compliance@pup.edu.ph</a></p>
		</div>
		<p>You may also file a complaint directly to the National Privacy Commission at <a href="mailto:complaints@privacy.gov.ph">complaints@privacy.gov.ph</a> or visit <a href="https://privacy.gov.ph" target="_blank">privacy.gov.ph</a>.</p>

		<h2>References</h2>
		<ul class="refs">
			<li>Data Privacy Act of 2012 (RA 10173) — <a href="https://privacy.gov.ph" target="_blank">privacy.gov.ph</a></li>
			<li>Implementing Rules and Regulations — <a href="https://privacy.gov.ph/implementing-rules-regulations-data-privacy-act-2012/" target="_blank">privacy.gov.ph/irr</a></li>
			<li>National Internal Revenue Code (NIRC) of 1997, Section 235 — <a href="https://www.bir.gov.ph" target="_blank">bir.gov.ph</a></li>
		</ul>
	</div>
</section>

<Footer />

<style>
	.legal-hero { padding: 8rem 1.5rem 3rem; background: linear-gradient(135deg, #1a1a2e 0%, #282854 100%); text-align: center; }
	.legal-hero-inner { max-width: 700px; margin: 0 auto; }
	.legal-hero-tag { display: inline-block; background: rgba(232,201,126,0.15); color: #e8c97e; font-size: 11px; font-weight: 600; padding: 4px 14px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; }
	.legal-hero-title { font-size: 2.5rem; font-weight: 700; color: #fff; margin: 0 0 0.75rem; }
	.legal-hero-sub { font-size: 0.9rem; color: rgba(255,255,255,0.5); }

	.legal-section { padding: 3rem 1.5rem 4rem; }
	.legal-content { max-width: 800px; margin: 0 auto; }
	.legal-content h2 { font-size: 1.35rem; font-weight: 700; color: #1a1a2e; margin: 2rem 0 0.75rem; padding-top: 0.5rem; border-top: 1px solid #e5e7eb; }
	.legal-content h2:first-of-type { border-top: none; margin-top: 0; }
	.legal-content p { font-size: 15px; color: #4b5563; line-height: 1.7; margin: 0 0 1rem; }
	.legal-content ul { padding-left: 1.25rem; margin: 0 0 1rem; }
	.legal-content li { font-size: 15px; color: #4b5563; line-height: 1.7; margin-bottom: 6px; }
	.legal-content a { color: var(--primary); text-decoration: underline; }

	.legal-intro { display: flex; align-items: flex-start; gap: 14px; padding: 1.25rem; background: #eef2ff; border-radius: 12px; margin-bottom: 1.5rem; }
	.legal-intro :global(svg) { color: var(--primary); flex-shrink: 0; margin-top: 2px; }
	.legal-intro p { margin: 0; font-size: 14px; color: #4338ca; }

	.rights-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 1rem 0; }
	.right-card { padding: 1rem 1.15rem; border: 1px solid #e5e7eb; border-radius: 10px; background: #f9fafb; }
	.right-card h3 { font-size: 13px; font-weight: 700; color: #1a1a2e; margin: 0 0 4px; }
	.right-card p { font-size: 13px; color: #6b7280; margin: 0; line-height: 1.5; }

	.contact-box { padding: 1rem 1.25rem; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; margin: 1rem 0; }
	.contact-box p { margin: 0 0 4px; font-size: 14px; }
	.contact-box p:last-child { margin-bottom: 0; }

	.refs { margin-top: 0.5rem; }
	.refs li { font-size: 14px; }

	@media (max-width: 768px) {
		.rights-grid { grid-template-columns: 1fr; }
		.legal-hero-title { font-size: 1.75rem; }
	}
</style>
