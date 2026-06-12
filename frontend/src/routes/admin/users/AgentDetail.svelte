<script lang="ts">
	import { onMount } from 'svelte';
	import { getAgentDetail } from '$lib/services/api';

	let {
		show,
		agentId,
		onClose
	}: {
		show: boolean;
		agentId: number | null;
		onClose: () => void;
	} = $props();

	let loading = $state(false);
	let error = $state<string | null>(null);
	let agent = $state<Record<string, unknown> | null>(null);

	$effect(() => {
		if (show && agentId) {
			loadAgent(agentId);
		}
	});

	async function loadAgent(id: number) {
		loading = true;
		error = null;
		try {
			const res = await getAgentDetail(id);
			agent = res.data;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}
</script>

{#if show}
	<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
	<div class="overlay" onclick={onClose}>
		<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<h2>Agent Details</h2>

			{#if loading}
				<p>Loading…</p>
			{:else if error}
				<p class="error">{error}</p>
			{:else if agent}
				<div class="info">
					<div class="row"><span>Username</span><span>{agent.username}</span></div>
					<div class="row"><span>Email</span><span>{agent.email}</span></div>
					<div class="row"><span>Employee Number</span><span>{agent.employee_number}</span></div>
					<div class="row"><span>Hire Date</span><span>{agent.hire_date}</span></div>
					<div class="row"><span>Commission Rate</span><span>{agent.default_commission_rate}%</span></div>
					<div class="row"><span>Total Sales</span><span>{agent.total_sales}</span></div>
					<div class="row"><span>Active</span><span>{agent.is_active ? 'Yes' : 'No'}</span></div>
				</div>
			{/if}

			<div class="actions">
				<button onclick={onClose}>Close</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.overlay {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.4);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}
	.modal {
		background: var(--bg-card);
		border-radius: var(--radius-md);
		padding: 24px;
		max-width: 480px;
		width: 90%;
	}
	h2 { margin: 0 0 16px; }
	.error { color: var(--danger); }
	.info { margin-bottom: 16px; }
	.row {
		display: flex;
		justify-content: space-between;
		padding: 8px 0;
		border-bottom: 1px solid var(--border-light);
		font-size: 0.875rem;
	}
	.row span:first-child { font-weight: 600; color: var(--text-light); }
	.actions { display: flex; justify-content: flex-end; }
	button {
		padding: 8px 16px;
		border: none;
		border-radius: var(--radius-sm);
		cursor: pointer;
		background: var(--bg-hover);
	}
</style>
