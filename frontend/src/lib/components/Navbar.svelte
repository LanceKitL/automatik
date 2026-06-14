<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { auth } from '$lib/stores/auth.svelte';
	import { Menu, X, Bot } from '@lucide/svelte';
	import { getChatbotStatus } from '$lib/services/api';
	import logo from '$lib/assets/LOGO.png';
	import logoWhite from '$lib/assets/LOGO_WHITE.png';
	import ChatBot from './ChatBot.svelte';

	let scrolled = $state(false);
	let mobileOpen = $state(false);
	let chatOpen = $state(false);
	let chatToggle = $state(0);
	let chatbotEnabled = $state(true);
	let isHome = $derived($page.url.pathname === '/');
	let showScrolled = $derived(scrolled || !isHome);

	function toggleChat() {
		chatToggle++;
	}

	onMount(async () => {
		try {
			const res = await getChatbotStatus();
			chatbotEnabled = res.enabled;
		} catch {
			chatbotEnabled = true;
		}
	});

	onMount(() => {
		const onScroll = () => {
			scrolled = window.scrollY > 40;
		};
		window.addEventListener('scroll', onScroll, { passive: true });
		return () => window.removeEventListener('scroll', onScroll);
	});

	const links = [
		{ label: 'Home', href: '/' },
		{ label: 'Browse Vehicles', href: '/vehicles' },
		{ label: 'Loan Calculator', href: '/loan-calculator' },
		{ label: 'Contact', href: '/contact' },
		{ label: 'About', href: '/about' },
	];
</script>

<nav class="navbar" class:scrolled={showScrolled}>
	<div class="nav-inner">
		<a href="/" class="logo"><img src={$page.url.pathname === '/' && !scrolled ? logoWhite : logo} alt="AutoMatik" class="logo-img" /></a>

		<button class="hamburger" onclick={() => (mobileOpen = !mobileOpen)}>
			{#if mobileOpen}
				<X size={24} />
			{:else}
				<Menu size={24} />
			{/if}
		</button>

		<div class="nav-right" class:open={mobileOpen}>
			<div class="nav-links">
				{#each links as link}
					<a href={link.href} class="nav-link">{link.label}</a>
				{/each}
			</div>
			{#if chatbotEnabled}
				<button class="btn-autobot" onclick={toggleChat}>
					<Bot size={14} /> AutoBot
				</button>
			{/if}
			{#if auth.isAuthenticated}
				<a href="/portal" class="btn-dashboard">Dashboard</a>
			{:else}
				<a href="/auth/login" class="btn-login">Login</a>
			{/if}
		</div>
	</div>
</nav>

{#if mobileOpen}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="mobile-overlay" onclick={() => (mobileOpen = false)} />
{/if}

<ChatBot bind:open={chatOpen} toggle={chatToggle} enabled={chatbotEnabled} />

<style>
	.navbar {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 100;
		background: transparent;
		transition: background 0.3s, box-shadow 0.3s;
		padding: 1rem 0;
	}
	.navbar.scrolled {
		background: rgba(255, 255, 255, 0.97);
		box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
		backdrop-filter: blur(8px);
		padding: 0.6rem 0;
	}
	.nav-inner {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 1.5rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.logo {
		font-family: var(--font-sans);
		font-size: 1.5rem;
		font-weight: 700;
		color: #fff;
		text-decoration: none;
		letter-spacing: 2px;
		transition: color 0.3s;
	}
	.scrolled .logo {
		color: var(--primary);
	}
	.logo-img {
		width: 200px;
		height: auto;
		display: block;
	}
	.hamburger {
		display: none;
		background: none;
		border: none;
		cursor: pointer;
		color: #fff;
		padding: 4px;
	}
	.scrolled .hamburger {
		color: var(--text-dark);
	}
	.nav-right {
		display: flex;
		align-items: center;
		gap: 2rem;
	}
	.nav-links {
		display: flex;
		align-items: center;
		gap: 1.5rem;
	}
	.nav-link {
		font-family: var(--font-sans);
		font-size: 0.9rem;
		font-weight: 500;
		color: rgba(255, 255, 255, 0.85);
		text-decoration: none;
		transition: color 0.2s;
		white-space: nowrap;
	}
	.scrolled .nav-link {
		color: var(--text-light);
	}
	.nav-link:hover {
		color: #fff;
	}
	.scrolled .nav-link:hover {
		color: var(--primary);
	}
	.btn-autobot {
		font-family: var(--font-sans);
		font-size: 0.85rem;
		font-weight: 600;
		padding: 0.5rem 1.1rem;
		border: 2px solid rgba(255,255,255,0.5);
		border-radius: 6px;
		background: transparent;
		color: rgba(255,255,255,0.9);
		cursor: pointer;
		white-space: nowrap;
		display: inline-flex;
		align-items: center;
		gap: 6px;
		transition: all 0.2s;
	}
	.scrolled .btn-autobot {
		border-color: var(--primary);
		color: var(--primary);
	}
	.btn-autobot:hover {
		border-color: #e8c97e;
		color: #e8c97e;
		box-shadow: 0 0 12px rgba(232,201,126,0.4);
		animation: botPulse 0.8s ease-in-out infinite alternate;
	}
	.scrolled .btn-autobot:hover {
		border-color: var(--primary);
		color: var(--primary);
		box-shadow: 0 0 12px rgba(65,105,225,0.4);
		animation: botPulseBlue 0.8s ease-in-out infinite alternate;
	}
	@keyframes botPulse {
		from { box-shadow: 0 0 6px rgba(232,201,126,0.2); transform: scale(1); }
		to { box-shadow: 0 0 18px rgba(232,201,126,0.5); transform: scale(1.04); }
	}
	@keyframes botPulseBlue {
		from { box-shadow: 0 0 6px rgba(65,105,225,0.2); transform: scale(1); }
		to { box-shadow: 0 0 18px rgba(65,105,225,0.5); transform: scale(1.04); }
	}

	.btn-login {
		font-family: var(--font-sans);
		font-size: 0.9rem;
		font-weight: 600;
		padding: 0.5rem 1.5rem;
		border: 2px solid #fff;
		border-radius: 6px;
		color: #fff;
		text-decoration: none;
		transition: all 0.2s;
		white-space: nowrap;
	}
	.scrolled .btn-login {
		border-color: var(--primary);
		color: var(--primary);
	}
	.btn-login:hover {
		background: #fff;
		color: var(--primary);
	}
	.scrolled .btn-login:hover {
		background: var(--primary);
		color: #fff;
	}
	.btn-dashboard {
		font-family: var(--font-sans);
		font-size: 0.9rem;
		font-weight: 600;
		padding: 0.5rem 1.5rem;
		background: var(--primary);
		border-radius: 6px;
		color: #fff;
		text-decoration: none;
		transition: background 0.2s;
		white-space: nowrap;
	}
	.btn-dashboard:hover {
		background: var(--primary-dark);
	}
	.mobile-overlay {
		position: fixed;
		inset: 0;
		z-index: 99;
		background: rgba(0, 0, 0, 0.4);
	}

	@media (max-width: 768px) {
		.hamburger {
			display: block;
		}
		.nav-right {
			position: fixed;
			top: 0;
			right: -100%;
			width: 280px;
			height: 100vh;
			flex-direction: column;
			justify-content: flex-start;
			align-items: stretch;
			gap: 0;
			background: #fff;
			padding: 5rem 2rem 2rem;
			box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
			transition: right 0.3s ease;
			z-index: 100;
		}
		.nav-right.open {
			right: 0;
		}
		.nav-links {
			flex-direction: column;
			gap: 0;
		}
		.nav-link {
			color: var(--text-light);
			padding: 0.8rem 0;
			border-bottom: 1px solid var(--border-lighter);
			width: 100%;
		}
		.nav-link:hover {
			color: var(--primary);
		}
		.btn-autobot, .btn-login, .btn-dashboard {
			margin-top: 0.75rem;
			text-align: center;
		}
		.btn-autobot { border-color: var(--primary); color: var(--primary); width: 100%; justify-content: center; }
		.btn-login {
			border-color: var(--primary);
			color: var(--primary);
		}
	}
</style>
