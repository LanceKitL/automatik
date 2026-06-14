<script lang="ts">
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { FileText } from '@lucide/svelte';
</script>

<Navbar />

<section class="legal-hero">
	<div class="legal-hero-inner">
		<span class="legal-hero-tag">Legal</span>
		<h1 class="legal-hero-title">Terms &amp; Conditions</h1>
		<p class="legal-hero-sub">Last updated: 2026 &mdash; Governing your access to and use of the AutoMatik System</p>
	</div>
</section>

<section class="legal-section">
	<div class="legal-content">
		<div class="legal-intro">
			<FileText size={28} />
			<p>By creating an account, accessing, or using the system, you acknowledge that you have read, understood, and agreed to be bound by these Terms and Conditions, as well as the Privacy Policy of AutoMatik.</p>
		</div>

		<h2>I. Introduction and Acceptance</h2>
		<p>Welcome to AutoMatik. These Terms and Conditions govern your access to and use of the AutoMatik System, including its services, features, and functionalities.</p>
		<p>By creating an account, accessing, or using the system, you acknowledge that you have read, understood, and agreed to be bound by these Terms and Conditions, as well as the Privacy Policy of AutoMatik. If you do not agree with any part of these terms, you must discontinue the use of the system.</p>

		<h2>II. Definitions</h2>
		<p>For the purposes of these Terms and Conditions:</p>
		<ul>
			<li><strong>"AutoMatik"</strong> refers to the web-based dealership management system developed for vehicle sales, inventory management, inquiries, and financial tracking.</li>
			<li><strong>"Company"</strong> refers to the organization, administrators, and authorized personnel managing the AutoMatik System.</li>
			<li><strong>"Service"</strong> refers to all features, functions, tools, and services provided through the system.</li>
			<li><strong>"User," "You," or "Your"</strong> refers to any individual accessing or using the system, including administrators, sales agents, and customers.</li>
			<li><strong>"Content"</strong> refers to all information, documents, text, images, records, and data submitted or displayed within the system.</li>
		</ul>

		<h2>III. User Accounts and Rules</h2>
		<p>Users are responsible for maintaining the confidentiality of their account credentials and all activities conducted under their accounts.</p>
		<p>By using the system, users agree to:</p>
		<ul>
			<li>Provide accurate, complete, and updated information;</li>
			<li>Use the system only for lawful and authorized purposes;</li>
			<li>Avoid unauthorized access, misuse, or disruption of the platform;</li>
			<li>Refrain from submitting fraudulent, misleading, or false information; and</li>
			<li>Follow all applicable Philippine laws and regulations.</li>
		</ul>
		<p>AutoMatik reserves the right to suspend or restrict accounts that violate these Terms and Conditions.</p>

		<h2>IV. Intellectual Property</h2>
		<p>All system content, including logos, layouts, databases, system designs, graphics, text, and functionalities, are the intellectual property of AutoMatik and are protected under applicable intellectual property laws.</p>
		<p><strong>Intellectual Property Disclaimer:</strong> All vehicle brand names, model names, trademarks, service marks, logos, and other proprietary identifiers displayed within the system remain the intellectual property of their respective owners. Their use within the AutoMatik system is solely for identification, inventory management, sales, and informational purposes and does not imply ownership, endorsement, sponsorship, or affiliation with AutoMatik unless otherwise stated.</p>
		<p>Users may not reproduce, modify, distribute, reverse engineer, or exploit any part of the system without prior written permission from the administrators of AutoMatik.</p>

		<h2>V. Payments and Financial Services</h2>
		<p>AutoMatik includes financial tracking and payment estimation features for dealership transactions.</p>
		<p>The payment calculator and amortization tools provided by the system are intended solely for estimation purposes. Actual payment computations may vary depending on financing institutions, dealership policies, and approved transaction terms.</p>
		<p>AutoMatik does not directly process banking transactions and does not maintain direct integration with banks or third-party financing institutions.</p>

		<h2>VI. Limitation of Liability</h2>
		<p>AutoMatik shall not be held liable for:</p>
		<ul>
			<li>Temporary interruptions, errors, or unavailability of the system;</li>
			<li>Losses resulting from unauthorized access caused by user negligence;</li>
			<li>Delays related to manual document processing or third-party institutions;</li>
			<li>Inaccurate information submitted by users; or</li>
			<li>Indirect, incidental, or consequential damages arising from the use of the system.</li>
		</ul>
		<p>Users access and use the system at their own responsibility and risk.</p>

		<h2>VII. Disclaimer of Warranties</h2>
		<p>The AutoMatik System is provided on an "as is" and "as available" basis without warranties of any kind, whether expressed or implied.</p>
		<p>While reasonable efforts are made to maintain system accuracy, functionality, and security, AutoMatik does not guarantee uninterrupted service, error-free operation, or absolute protection from technical issues and cybersecurity threats.</p>

		<h2>VIII. Termination</h2>
		<p>AutoMatik reserves the right to suspend, restrict, or permanently terminate user access without prior notice if a user:</p>
		<ul>
			<li>Violates these Terms and Conditions;</li>
			<li>Engages in fraudulent, abusive, or unlawful activities;</li>
			<li>Attempts unauthorized access to system resources; or</li>
			<li>Compromises the security and integrity of the platform.</li>
		</ul>
		<p>Terminated users may lose access to their accounts, records, and system privileges.</p>

		<h2>IX. Governing Law</h2>
		<p>These Terms and Conditions shall be governed by and interpreted in accordance with the laws of the Republic of the Philippines, including the Data Privacy Act of 2012 (RA 10173) and other applicable laws and regulations.</p>
		<p>Any disputes arising from the use of the system shall be resolved under the jurisdiction of the appropriate courts in the Philippines.</p>

		<h2>X. Contact Information</h2>
		<p>For questions, concerns, or legal inquiries regarding these Terms and Conditions, users may contact:</p>
		<div class="contact-box">
			<p><strong>Data Compliance Officer &mdash; AutoMatik</strong></p>
			<p>Polytechnic University of the Philippines</p>
			<p>Email: <a href="mailto:automatik.compliance@pup.edu.ph">automatik.compliance@pup.edu.ph</a></p>
		</div>
		<p>Users may also contact the National Privacy Commission through <a href="mailto:complaints@privacy.gov.ph">complaints@privacy.gov.ph</a> or visit <a href="https://privacy.gov.ph" target="_blank">privacy.gov.ph</a>.</p>

		<h2>XI. Changes to the Terms and Conditions</h2>
		<p>AutoMatik reserves the right to update or modify these Terms and Conditions at any time to reflect operational, legal, or policy changes.</p>
		<p>Continued use of the system after changes are implemented constitutes acceptance of the revised Terms and Conditions.</p>
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

	.contact-box { padding: 1rem 1.25rem; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; margin: 1rem 0; }
	.contact-box p { margin: 0 0 4px; font-size: 14px; }
	.contact-box p:last-child { margin-bottom: 0; }

	@media (max-width: 768px) {
		.legal-hero-title { font-size: 1.75rem; }
	}
</style>
