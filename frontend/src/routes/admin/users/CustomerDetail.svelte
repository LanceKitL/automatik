<script lang="ts">
	import { onMount } from 'svelte';
	import { getCustomerSalesHistory, getUserById } from '$lib/services/api';

	let {
		show,
		customerId,
		onClose
	}: {
		show: boolean;
		customerId: number | null;
		onClose: () => void;
	} = $props();

	let loading = $state(false);
	let error = $state<string | null>(null);
	let customer = $state<Record<string, unknown> | null>(null);
	let sales = $state<unknown[]>([]);

	const salesColumns = ['sale_id', 'brand', 'model', 'selling_price', 'payment_type', 'sale_date', 'status'];

	$effect(() => {
		if (show && customerId) {
			loadCustomer(customerId);
		}
	});

	async function loadCustomer(id: number) {
		loading = true;
		error = null;
		try {
			const [userRes, salesRes] = await Promise.all([
				getUserById(id),
				getCustomerSalesHistory(id),
			]);
			customer = userRes.data;
			sales = salesRes.data;
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
			<h2>Customer Details</h2>

			{#if loading}
				<p>Loading…</p>
			{:else if error}
				<p class="error">{error}</p>
			{:else if customer}
				<div class="info">
					<div class="row"><span>Customer Number</span><span>{customer.customer_number ?? 'N/A'}</span></div>
					<div class="row"><span>Name</span><span>{customer.full_name}</span></div>
					<div class="row"><span>Email</span><span>{customer.email}</span></div>
					<div class="row"><span>Phone</span><span>{customer.phone_number ?? 'N/A'}</span></div>
					<div class="row"><span>Preferred Contact</span><span>{customer.preferred_contact_method ?? 'N/A'}</span></div>
					<div class="row"><span>Preferred Payment</span><span>{customer.preferred_payment_method ?? 'N/A'}</span></div>
				</div>

				<h3>Sales History ({sales.length})</h3>
				{#if sales.length > 0}
					<div class="table-wrap">
						<table>
							<thead>
								<tr>
									{#each salesColumns as col}
										<th>{col.replace(/_/g, ' ')}</th>
									{/each}
								</tr>
							</thead>
							<tbody>
								{#each sales as sale, i (i)}
									<tr>
										{#each salesColumns as col}
											<td>{sale[col] ?? ''}</td>
										{/each}
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{:else}
					<p class="empty">No sales yet.</p>
				{/if}
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
		max-width: 700px;
		width: 90%;
		max-height: 90vh;
		overflow-y: auto;
	}
	h2 { margin: 0 0 16px; }
	h3 { margin: 16px 0 8px; font-size: 1rem; }
	.error { color: var(--danger); }
	.empty { color: var(--text-muted); font-size: 0.875rem; }
	.info { margin-bottom: 12px; }
	.row {
		display: flex;
		justify-content: space-between;
		padding: 6px 0;
		border-bottom: 1px solid var(--border-light);
		font-size: 0.875rem;
	}
	.row span:first-child { font-weight: 600; color: var(--text-light); }
	.table-wrap { overflow-x: auto; margin-bottom: 12px; }
	table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
	th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--border-light); }
	th { background: var(--bg-hover); font-weight: 600; }
	.actions { display: flex; justify-content: flex-end; }
	button {
		padding: 8px 16px;
		border: none;
		border-radius: var(--radius-sm);
		cursor: pointer;
		background: var(--bg-hover);
	}
</style>
