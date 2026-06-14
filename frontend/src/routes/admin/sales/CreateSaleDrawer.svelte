<script lang="ts">
	import { onMount } from 'svelte';
	import {
		createSale,
		getAvailableVehicles,
		getCustomersList,
		getAgentsList,
		type ListResponse
	} from '$lib/services/api';

	let {
		onclose,
		oncreated
	}: {
		onclose: () => void;
		oncreated: () => void;
	} = $props();

	// ── Form state ────────────────────────────────────────────────────────────
	let vehicleId = $state<number | ''>('');
	let customerId = $state<number | ''>('');
	let agentId = $state<number | ''>('');
	let paymentType = $state<'full_payment' | 'installment'>('full_payment');
	let sellingPrice = $state<number | ''>('');
	let inquiryId = $state<number | ''>('');

	// Installment fields
	let loanAmount = $state<number | ''>('');
	let interestRate = $state<number | ''>('');
	let termMonths = $state<number | ''>('');
	let downPayment = $state<number | ''>('');

	// ── Dropdown data ─────────────────────────────────────────────────────────
	let vehicles = $state<{ vehicle_id: number; brand: string; model: string; year: number; price: string }[]>([]);
	let customers = $state<{ user_id: number; username: string; email: string }[]>([]);
	let agents = $state<{ _id: number; username: string }[]>([]);

	let loading = $state(true);
	let submitting = $state(false);
	let formError = $state('');

	onMount(async () => {
		try {
			const [vRes, cRes, aRes] = await Promise.all([
				getAvailableVehicles(),
				getCustomersList(),
				getAgentsList()
			]);
			vehicles = (vRes as unknown as { data: unknown[] }).data as typeof vehicles;
			customers = (cRes as unknown as { data: unknown[] }).data as typeof customers;
			agents = (aRes as unknown as { data: unknown[] }).data as typeof agents;
		} catch {
			formError = 'Failed to load form data.';
		} finally {
			loading = false;
		}
	});

	// ── Submit ────────────────────────────────────────────────────────────────
	async function handleSubmit() {
		formError = '';
		if (!vehicleId || !customerId || !agentId || !sellingPrice) {
			formError = 'Please fill in all required fields.';
			return;
		}
		if (paymentType === 'installment' && (!loanAmount || !interestRate || !termMonths || !downPayment)) {
			formError = 'Installment requires loan amount, interest rate, term, and down payment.';
			return;
		}

		submitting = true;
		try {
			const payload: Record<string, unknown> = {
				vehicle_id: vehicleId,
				customer_id: customerId,
				agent_id: agentId,
				payment_type: paymentType,
				selling_price: sellingPrice
			};
			if (inquiryId) payload.inquiry_id = inquiryId;
			if (paymentType === 'installment') {
				payload.loan_amount = loanAmount;
				payload.interest_rate = interestRate;
				payload.term_months = termMonths;
				payload.down_payment = downPayment;
			}
			await createSale(payload);
			oncreated();
		} catch (e: unknown) {
			formError = e instanceof Error ? e.message : 'Failed to create sale.';
		} finally {
			submitting = false;
		}
	}

	function handleOverlayClick(e: MouseEvent) {
		if (e.target === e.currentTarget) onclose();
	}
</script>

<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
<div class="overlay" onclick={handleOverlayClick} role="presentation">
	<div class="drawer" onclick={(e) => e.stopPropagation()} role="dialog">
		<div class="drawer-header">
			<h2>New Sale</h2>
			<button class="close-btn" onclick={onclose}>×</button>
		</div>

		<div class="drawer-body">
			{#if loading}
				<div class="loading-state"><div class="spinner"></div><span>Loading form…</span></div>
			{:else}
				{#if formError}
					<div class="form-error">{formError}</div>
				{/if}

				<!-- Vehicle -->
				<div class="field">
					<label for="vehicle">Vehicle *</label>
					<select id="vehicle" bind:value={vehicleId}>
						<option value={''}>— Select vehicle —</option>
						{#each vehicles as v}
							<option value={v.vehicle_id}>{v.brand} {v.model} ({v.year}) — ${Number(v.price).toLocaleString()}</option>
						{/each}
					</select>
				</div>

				<!-- Customer -->
				<div class="field">
					<label for="customer">Customer *</label>
					<select id="customer" bind:value={customerId}>
						<option value={''}>— Select customer —</option>
						{#each customers as c}
							<option value={c.user_id}>{c.username} ({c.email})</option>
						{/each}
					</select>
				</div>

				<!-- Agent -->
				<div class="field">
					<label for="agent">Agent *</label>
					<select id="agent" bind:value={agentId}>
						<option value={''}>— Select agent —</option>
						{#each agents as a}
							<option value={a._id}>{a.username}</option>
						{/each}
					</select>
				</div>

				<!-- Payment Type -->
				<div class="field">
					<label for="payment_type">Payment Type *</label>
					<select id="payment_type" bind:value={paymentType}>
						<option value="full_payment">Full Payment</option>
						<option value="installment">Installment</option>
					</select>
				</div>

				<!-- Selling Price -->
				<div class="field">
					<label for="selling_price">Selling Price ($) *</label>
					<input id="selling_price" type="number" step="0.01" min="0" bind:value={sellingPrice} placeholder="0.00" />
				</div>

				<!-- Inquiry ID (optional) -->
				<div class="field">
					<label for="inquiry_id">Inquiry ID (optional)</label>
					<input id="inquiry_id" type="number" min="1" bind:value={inquiryId} placeholder="Leave blank if not from an inquiry" />
				</div>

				<!-- Installment fields -->
				{#if paymentType === 'installment'}
					<div class="installment-section">
						<h3>Installment Details</h3>
						<div class="field">
							<label for="loan_amount">Loan Amount ($) *</label>
							<input id="loan_amount" type="number" step="0.01" min="0" bind:value={loanAmount} placeholder="0.00" />
						</div>
						<div class="field">
							<label for="interest_rate">Interest Rate (%) *</label>
							<input id="interest_rate" type="number" step="0.01" min="0" bind:value={interestRate} placeholder="e.g. 5.5" />
						</div>
						<div class="field">
							<label for="term_months">Term (months) *</label>
							<input id="term_months" type="number" min="1" bind:value={termMonths} placeholder="e.g. 36" />
						</div>
						<div class="field">
							<label for="down_payment">Down Payment ($) *</label>
							<input id="down_payment" type="number" step="0.01" min="0" bind:value={downPayment} placeholder="0.00" />
						</div>
					</div>
				{/if}

				<!-- Submit -->
				<div class="actions">
					<button
						class="btn-submit"
						onclick={handleSubmit}
						disabled={submitting}
					>
						{submitting ? 'Creating…' : 'Create Sale'}
					</button>
					<button class="btn-cancel" onclick={onclose} disabled={submitting}>Cancel</button>
				</div>
			{/if}
		</div>
	</div>
</div>

<style>
	.overlay {
		position: fixed; inset: 0; background: rgba(0,0,0,0.35);
		z-index: 1000; display: flex; align-items: center; justify-content: center;
	}

	.drawer {
		width: 28rem; max-width: 95vw; max-height: 85vh;
		background: var(--bg-card); box-shadow: 0 20px 60px rgba(0,0,0,0.15);
		display: flex; flex-direction: column; overflow: hidden;
		animation: fadeIn 0.2s ease-out;
		font-family: var(--font-sans);
	}
	@keyframes fadeIn {
		from { opacity: 0; transform: scale(0.96); }
		to { opacity: 1; transform: scale(1); }
	}

	.drawer-header {
		display: flex; align-items: center; justify-content: space-between;
		padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border); flex-shrink: 0;
	}
	.drawer-header h2 { margin: 0; font-size: 1.15rem; color: var(--text-primary); }
	.close-btn {
		background: none; border: none; font-size: 1.5rem; cursor: pointer;
		color: var(--text-muted); padding: 0.25rem; line-height: 1;
	}
	.close-btn:hover { color: var(--text-dark); }

	.drawer-body {
		padding: 1.25rem 1.5rem; overflow-y: auto; flex: 1;
	}

	.form-error {
		background: var(--danger-bg); color: var(--danger); padding: 0.5rem 0.75rem;
		border-radius: var(--radius-sm); font-size: 0.8rem; margin-bottom: 0.75rem;
	}

	.field { margin-bottom: 1rem; }
	.field label { display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-dark); margin-bottom: 0.35rem; }
	.field input, .field select {
		width: 100%; padding: 0.5rem 0.65rem;
		border: 1px solid #d1d5db; border-radius: var(--radius-sm);
		font-family: var(--font-sans); font-size: 0.85rem;
		color: var(--text-primary); background: var(--bg-muted);
		box-sizing: border-box;
	}
	.field input:focus, .field select:focus {
		outline: none; border-color: var(--primary-light); background: var(--bg-card);
	}

	.installment-section {
		margin-top: 1rem; padding-top: 1rem;
		border-top: 1px solid var(--border);
	}
	.installment-section h3 {
		font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;
		color: var(--text-muted); margin: 0 0 0.75rem;
	}

	.actions {
		margin-top: 1.25rem; display: flex; gap: 0.5rem;
	}
	.btn-submit, .btn-cancel {
		flex: 1; padding: 0.6rem; border: none; border-radius: var(--radius-sm);
		font-family: var(--font-sans); font-size: 0.9rem;
		font-weight: 600; cursor: pointer; transition: opacity .15s;
	}
	.btn-submit { background: var(--primary); color: var(--accent); }
	.btn-submit:hover:not(:disabled) { opacity: 0.85; }
	.btn-cancel { background: var(--bg-hover); color: var(--text-dark); }
	.btn-cancel:hover:not(:disabled) { background: var(--border); }
	.btn-submit:disabled, .btn-cancel:disabled { opacity: 0.5; cursor: not-allowed; }

	.loading-state {
		display: flex; flex-direction: column; align-items: center;
		gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px;
	}
	.spinner {
		width: 24px; height: 24px; border: 2px solid var(--border);
		border-top-color: var(--primary); border-radius: 50%;
		animation: spin .7s linear infinite;
	}
	@keyframes spin { to { transform: rotate(360deg); } }
</style>
