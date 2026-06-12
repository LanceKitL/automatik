<script lang="ts">
	import { onMount } from 'svelte';
	import { getServiceAdvisorDashboard } from '$lib/services/api';
	import StatCard from '$lib/components/StatCard.svelte';
	import type { ServiceAdvisorDashboardResponse } from '$lib/services/api';

	let data = $state<ServiceAdvisorDashboardResponse['data'] | null>(null);
	let loading = $state(true);

	onMount(async () => {
		try {
			const res = await getServiceAdvisorDashboard();
			data = res.data;
		} catch {
			// offline / error
		} finally {
			loading = false;
		}
	});
</script>

{#if loading}
	<p>Loading dashboard…</p>
{:else if data}
	<h1>Service Advisor Dashboard</h1>

	<div class="cards">
		<StatCard value={data.pending_bookings} label="Pending Bookings" />
		<StatCard value={data.unassigned_bookings} label="Unassigned" />
		<StatCard value={data.my_assigned} label="My Assignments" />
		<StatCard value={data.today_bookings} label="Today's Bookings" />
	</div>

	<div class="actions">
		<a href="/service_advisor/bookings" class="btn">View All Bookings</a>
		<a href="/service_advisor/warranty" class="btn">Warranty Claims</a>
	</div>
{/if}

<style>
	h1 {
		padding: 1.5rem 1.5rem 0;
		margin: 0;
	}
	.cards {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
		gap: 1rem;
		padding: 1.5rem;
	}
	.actions {
		padding: 1.5rem;
		display: flex;
		gap: 1rem;
	}
	.btn {
		display: inline-block;
		padding: 0.6rem 1.2rem;
		background: var(--primary);
		color: var(--text-white);
		text-decoration: none;
		border-radius: var(--radius-sm);
	}
</style>
