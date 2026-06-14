<script lang="ts">
	import { auth } from '$lib/stores/auth.svelte';
	import logo from '$lib/assets/LOGO.png';
	import {
		LayoutDashboard,
		Users,
		Package,
		MessageCircle,
		ShoppingCart,
		Landmark,
		CreditCard,
		DollarSign,
		Warehouse,
		Wrench,
		ShieldCheck,
		FileText,
		Bell,
		ClipboardList,
		Settings,
		ClipboardCheck,
		Calculator,
		Shield,
		User,
		Car,
		CalendarCheck,
		CarFront,
		MessageSquareText,
		FolderKanban,
		LifeBuoy,
		CarIcon,
		History
	} from '@lucide/svelte';
	import type { SvelteComponent } from 'svelte';
	import { page } from '$app/stores';

	let role = $derived(auth.role);
	let currentPath = $derived($page.url.pathname);

	function isActive(href: string): boolean {
		return currentPath === href;
	}

	type NavItem = { label: string; href: string; icon: typeof SvelteComponent<{ size?: number }> };

	let links: NavItem[] = $derived(
		role === 'admin'
			? [
					{ label: 'Dashboard', href: '/admin', icon: LayoutDashboard },
					{ label: 'User Management', href: '/admin/users', icon: Users },
					{ label: 'Inventory', href: '/admin/vehicles', icon: Package },
					{ label: 'Inquiries', href: '/admin/inquiries', icon: MessageCircle },
					{ label: 'Sales', href: '/admin/sales', icon: ShoppingCart },
					{ label: 'Payments', href: '/admin/payments', icon: CreditCard },
					{ label: 'Commissions', href: '/admin/commissions', icon: DollarSign },
					{ label: 'Service Bookings', href: '/admin/service/bookings', icon: Wrench },
					{ label: 'Warranty Claims', href: '/admin/service/warranty', icon: ShieldCheck },
					{ label: 'Documents', href: '/admin/service/documents', icon: FileText },
					{ label: 'Notifications', href: '/admin/notifications', icon: Bell },
					{ label: 'Audit Logs', href: '/admin/audit_logs', icon: ClipboardList },
					{ label: 'System Settings', href: '/admin/settings', icon: Settings }
				]
: role === 'agent'
			? [
						{ label: 'Dashboard', href: '/agent', icon: LayoutDashboard },
						{ label: 'Create Inquiry', href: '/agent/vehicles', icon: CarIcon },
						{ label: 'Inquiries', href: '/agent/inquiries', icon: MessageCircle },
						{ label: 'Test Drives', href: '/agent/test-drives', icon: CarFront },
						{ label: 'Tasks', href: '/agent/tasks', icon: ClipboardCheck },
						{ label: 'Sales', href: '/agent/sales', icon: DollarSign }
					]
				: role === 'customer'
					? [
							{ label: 'Dashboard', href: '/portal', icon: LayoutDashboard },
							{ label: 'My Vehicles', href: '/portal/my-vehicles', icon: Car },
							{ label: 'Browse Vehicles', href: '/portal/vehicles', icon: CarIcon },
							{ label: 'Payments History', href: '/portal/payments', icon: CreditCard },
							{ label: 'Amortization', href: '/portal/amortization', icon: Calculator },
							{ label: 'Inquiries', href: '/portal/inquiries', icon: MessageSquareText },
							{ label: 'Documents', href: '/portal/documents', icon: FolderKanban },
							{ label: 'Test Drives', href: '/portal/appointments', icon: CalendarCheck },
							{ label: 'Service Appointments', href: '/portal/service', icon: Wrench },
							{ label: 'Warranty', href: '/portal/warranty', icon: LifeBuoy },
							{ label: 'Notifications', href: '/portal/notifications', icon: Bell },
							{ label: 'Profile', href: '/portal/profile', icon: User }
						]
					: role === 'finance_staff'
						? [
								{ label: 'Dashboard', href: '/finance_staff', icon: LayoutDashboard },
								{ label: 'Loans & Amortization', href: '/finance_staff/loans', icon: Landmark },
								{ label: 'Payments', href: '/finance_staff/payments', icon: CreditCard },
								{ label: 'Overdue Payments', href: '/finance_staff/amortization', icon: Calculator },
								{ label: 'Insurance', href: '/finance_staff/insurance', icon: Shield }
							]
						: role === 'service_staff' || role === 'service_advisor'
							? [
									{ label: 'Dashboard', href: '/service_staff', icon: LayoutDashboard },
									{ label: 'Maintenance', href: '/service_staff/maintenance', icon: Warehouse },
									{ label: 'Repairs', href: '/service_staff/repairs', icon: Wrench },
									{ label: 'Warranty Claims', href: '/service_staff/warranty_claims', icon: ShieldCheck },
									{ label: 'History', href: '/service_staff/history', icon: History }
								]
							: []
	);
</script>

<aside>
	<img src={logo} alt="AutoMatik" class="brand-logo" />

	<nav>
		{#each links as link}
			<a href={link.href} class:active={isActive(link.href)}>
				<svelte:component this={link.icon} size={16} />
				{link.label}
			</a>
		{/each}
	</nav>

	<div class="footer">
		<span class="email">{auth.user?.email}</span>
		<button onclick={() => auth.logout()}>Sign Out</button>
	</div>
</aside>

<style>
	aside {
		width: 16rem;
		height: 100vh;
		display: flex;
		flex-direction: column;
		background: var(--bg-card);
		color: var(--text-primary);
		position: fixed;
		top: 0;
		left: 0;
		padding: .5rem;
		z-index: 50;
	}
	.brand-logo {
		display: block;
		height: 70px;
		width: auto;
		margin: 1rem 1.25rem;
		border-bottom: 1px solid var(--border);
		padding-bottom: 1rem;
	}
	nav {
		flex: 1;
		overflow-y: auto;
		padding: 0.5rem 0;

	}
	nav a {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1.25rem;
		color: var(--text-primary);
		text-decoration: none;
		transition: all 0.30s;
		margin-top: .5rem;
		border-left: 3px transparent;
	}
	nav a:hover{
		border-left: 3px solid var(--primary);
		color: var(--primary);
		border-radius: .5rem;
	}
	nav a.active{
		background-color: var(--primary);
		color: var(--text-white);
		border-radius: .5rem;
	}
	nav a :global(svg) {
		flex-shrink: 0;
	}
	.footer {
		padding: 1rem 1.25rem;
		border-top: 1px solid var(--border);
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	.email {
		font-size: 0.85rem;
		color: var(--text-muted);
		overflow: hidden;
		text-overflow: ellipsis;
	}
	button {
		padding: 0.4rem 0.75rem;
		background: var(--danger);
		color: var(--text-white);
		border: none;
		border-radius: var(--radius-sm);
		cursor: pointer;
		font-size: 0.85rem;
	}
	button:hover {
		background: var(--danger-hover);
	}
</style>
