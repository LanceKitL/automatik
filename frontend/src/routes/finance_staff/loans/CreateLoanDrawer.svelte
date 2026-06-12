<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getEligibleSalesForLoan,
		createFinanceLoan,
		type EligibleSaleItem
	} from '$lib/services/api';
	import { X } from '@lucide/svelte';

	let { show, onClose }: { show: boolean; onClose: () => void } = $props();

	// ── Data ────────────────────────────────────────────────────────────
	let eligibleSales = $state<EligibleSaleItem[]>([]);
	let loadingSales = $state(false);

	// ── Form fields ─────────────────────────────────────────────────────
	let selectedSaleId = $state<number | null>(null);
	let loanAmount = $state<number | null>(null);
	let interestRate = $state<number | null>(null);
	let termMonths = $state<number | null>(null);
	let downPayment = $state<number>(0);

	let submitting = $state(false);
	let error = $state<string | null>(null);

	// ── Selected sale display ────────────────────────────────────────────
	let selectedSale = $derived(
		eligibleSales.find((s) => s.sale_id === selectedSaleId) ?? null
	);

	// ── Fetch eligible sales when drawer opens ──────────────────────────
	$effect(() => {
		if (show) {
			loadEligibleSales();
		}
	});

	async function loadEligibleSales() {
		loadingSales = true;
		error = null;
		try {
			const res = await getEligibleSalesForLoan();
			eligibleSales = res.data ?? [];
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loadingSales = false;
		}
	}

	// ── Auto-compute loan amount ──────────────────────────────────────────
	// loanAmount is kept in sync with (selling_price - down_payment) unless
	// the user has manually typed into the loan amount field.
	let loanAmountAuto = $state(true);
	let prevSaleId = $state<number | null>(null);

	$effect(() => {
		const sale = selectedSale;
		const dp = downPayment;
		const saleId = sale?.sale_id ?? null;

		if (!sale) return;

		// Always re-sync when the sale changes
		if (saleId !== prevSaleId) {
			prevSaleId = saleId;
			loanAmountAuto = true;
		}

		if (loanAmountAuto) {
			loanAmount = Number(sale.selling_price) - dp;
		}
	});

	function onLoanAmountInput() {
		loanAmountAuto = false;
	}

	// ── Validation ──────────────────────────────────────────────────────
	let validationError = $derived.by(() => {
		if (!selectedSaleId) return 'Please select a sale.';
		if (loanAmount == null || loanAmount <= 0) return 'Loan amount must be greater than 0.';
		if (selectedSale && loanAmount > Number(selectedSale.selling_price))
			return 'Loan amount cannot exceed selling price.';
		if (interestRate == null || interestRate < 0 || interestRate > 30)
			return 'Interest rate must be between 0 and 30.';
		if (termMonths == null || termMonths < 6 || termMonths > 60)
			return 'Term must be between 6 and 60 months.';
		if (downPayment < 0) return 'Down payment cannot be negative.';
		return null;
	});

	// ── Submit ──────────────────────────────────────────────────────────
	async function handleSubmit() {
		if (validationError || !selectedSaleId) return;
		submitting = true;
		error = null;
		try {
			await createFinanceLoan({
				sale_id: selectedSaleId,
				loan_amount: loanAmount!,
				interest_rate: interestRate!,
				term_months: termMonths!,
				down_payment: downPayment
			});
			onClose();
		} catch (e) {
			error = (e as Error).message;
		} finally {
			submitting = false;
		}
	}

	function resetForm() {
		selectedSaleId = null;
		loanAmount = null;
		interestRate = null;
		termMonths = null;
		downPayment = 0;
		error = null;
	}

	function handleOverlayClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			onClose();
		}
	}

	// ── Loan Calculator ──────────────────────────────────────────────────
	/** Effective principal = selling price minus down payment */
	let effectivePrincipal = $derived.by(() => {
		if (!selectedSale) return null;
		return Number(selectedSale.selling_price) - downPayment;
	});

	let calcMonthly = $derived.by(() => {
		const P = effectivePrincipal;
		const annualRate = interestRate;
		const n = termMonths;
		if (P == null || annualRate == null || n == null || P <= 0 || n < 1) return null;
		const r = (annualRate / 100) / 12;
		if (r === 0) return P / n;
		return (P * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
	});

	let calcTotalPayment = $derived(
		calcMonthly != null && termMonths != null ? calcMonthly * termMonths : null
	);

	let calcTotalInterest = $derived(
		calcMonthly != null && effectivePrincipal != null ? calcTotalPayment! - effectivePrincipal : null
	);

	function fmt(n: string | number): string {
		return `₱${Number(n).toLocaleString()}`;
	}

	function fmtMoney(n: number | null): string {
		if (n == null || isNaN(n) || !isFinite(n)) return '—';
		return `₱${n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
	}
</script>

<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
{#if show}
	<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
	<div class="overlay" onclick={handleOverlayClick} role="presentation">
		<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
		<div class="drawer" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
			<div class="drawer-header">
				<h2>Create New Loan</h2>
				<button class="close-btn" onclick={onClose}><X size={16} /></button>
			</div>

			<div class="drawer-body">
				{#if error}
					<div class="error-msg">{error}</div>
				{/if}

				<!-- Sale selection -->
				<div class="field">
					<label for="sale-select">Sale</label>
					{#if loadingSales}
						<div class="loading-hint">Loading eligible sales…</div>
					{:else if eligibleSales.length === 0}
						<div class="empty-hint">No installment sales without loans.</div>
					{:else}
						<select id="sale-select" bind:value={selectedSaleId}>
							<option value={null} disabled>Select a sale…</option>
							{#each eligibleSales as sale (sale.sale_id)}
								<option value={sale.sale_id}>
									#{sale.sale_id} — {sale.customer_name} — {sale.brand} {sale.model} ({sale.year}) — {fmt(sale.selling_price)}
								</option>
							{/each}
						</select>
					{/if}
				</div>

				{#if selectedSale}
					<div class="sale-preview">
						<div class="preview-item">
							<span class="p-label">Customer</span>
							<span class="p-value">{selectedSale.customer_name}</span>
						</div>
						<div class="preview-item">
							<span class="p-label">Vehicle</span>
							<span class="p-value">{selectedSale.brand} {selectedSale.model} ({selectedSale.year})</span>
						</div>
						<div class="preview-item">
							<span class="p-label">Selling Price</span>
							<span class="p-value mono">{fmt(selectedSale.selling_price)}</span>
						</div>
					</div>
				{/if}

				<!-- Loan fields -->
				<div class="field">
					<label for="loan-amount">Loan Amount (₱)</label>
					<div class="input-hint-wrap">
						<input
							id="loan-amount"
							type="number"
							step="0.01"
							min="0"
							placeholder="e.g. 500000"
							bind:value={loanAmount}
							oninput={onLoanAmountInput}
							class:auto={loanAmountAuto}
						/>
						{#if loanAmountAuto && selectedSale}
							<span class="auto-badge">auto</span>
						{/if}
					</div>
					{#if selectedSale && loanAmount != null && loanAmount > Number(selectedSale.selling_price)}
						<span class="field-error">Exceeds selling price ({fmt(selectedSale.selling_price)})</span>
					{/if}
				</div>

				<div class="field">
					<label for="interest-rate">Interest Rate (%)</label>
					<input
						id="interest-rate"
						type="number"
						step="0.1"
						min="0"
						max="30"
						placeholder="e.g. 8.5"
						bind:value={interestRate}
					/>
				</div>

				<div class="field">
					<label for="term-months">Term (months)</label>
					<input
						id="term-months"
						type="number"
						min="6"
						max="60"
						placeholder="e.g. 24"
						bind:value={termMonths}
					/>
				</div>

				<div class="field">
					<label for="down-payment">Down Payment (₱)</label>
					<input
						id="down-payment"
						type="number"
						step="0.01"
						min="0"
						placeholder="e.g. 50000"
						bind:value={downPayment}
					/>
				</div>

				<!-- Loan Calculator -->
				<div class="calc-card">
					<div class="calc-title">📐 Loan Calculator</div>

					{#if selectedSale}
						<div class="calc-row">
							<span class="calc-label">Selling Price</span>
							<span class="calc-value mono">{fmt(selectedSale.selling_price)}</span>
						</div>
						<div class="calc-row">
							<span class="calc-label">Down Payment</span>
							<span class="calc-value mono down-pay">− {fmtMoney(downPayment)}</span>
						</div>
						<div class="calc-divider"></div>
						<div class="calc-row highlight">
							<span class="calc-label">Amount to Finance</span>
							<span class="calc-value mono">{fmtMoney(effectivePrincipal)}</span>
						</div>
						<div class="calc-divider"></div>
					{/if}

					<div class="calc-row">
						<span class="calc-label">Monthly Amortization</span>
						<span class="calc-value mono primary">{fmtMoney(calcMonthly)}</span>
					</div>
					<div class="calc-row">
						<span class="calc-label">Total Payment</span>
						<span class="calc-value mono">{fmtMoney(calcTotalPayment)}</span>
					</div>
					<div class="calc-row">
						<span class="calc-label">Total Interest</span>
						<span class="calc-value mono interest">{fmtMoney(calcTotalInterest)}</span>
					</div>
				</div>
			</div>

			<div class="drawer-footer">
				<button class="btn-cancel" onclick={onClose}>Cancel</button>
				<button
					class="btn-submit"
					onclick={handleSubmit}
					disabled={submitting || !!validationError}
				>
					{submitting ? 'Creating…' : 'Create Loan'}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.35);
		display: flex;
		justify-content: flex-end;
		z-index: 1000;
		font-family: var(--font-sans);
	}

	.drawer {
		width: 420px;
		max-width: 100vw;
		height: 100vh;
		background: var(--bg-card);
		display: flex;
		flex-direction: column;
		box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
		overflow-y: auto;
	}

	.drawer-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.25rem 1.5rem;
		border-bottom: 1px solid var(--border);
	}

	.drawer-header h2 {
		font-size: 16px;
		font-weight: 700;
		color: var(--text-primary);
		margin: 0;
	}

	.close-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--text-muted);
		padding: 4px;
		border-radius: var(--radius-sm);
	}

	.close-btn:hover { color: var(--text-primary); background: var(--bg-hover); }

	.drawer-body {
		flex: 1;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.drawer-footer {
		padding: 1rem 1.5rem;
		border-top: 1px solid var(--border);
		display: flex;
		gap: 10px;
		justify-content: flex-end;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.field label {
		font-size: 11px;
		font-weight: 600;
		color: var(--text-dark);
		letter-spacing: 0.4px;
		text-transform: uppercase;
	}

	.input-hint-wrap {
		position: relative;
		display: flex;
		align-items: center;
	}

	.input-hint-wrap input {
		flex: 1;
	}

	.input-hint-wrap input.auto {
		padding-right: 44px;
	}

	.auto-badge {
		position: absolute;
		right: 8px;
		font-size: 9px;
		font-weight: 700;
		letter-spacing: 0.5px;
		text-transform: uppercase;
		color: var(--primary-light);
		background: #eef2ff;
		padding: 2px 5px;
		border-radius: var(--radius-sm);
		pointer-events: none;
	}

	.field input,
	.field select {
		height: 38px;
		padding: 0 10px;
		border: 0.5px solid #d1d5db;
		border-radius: var(--radius-sm);
		font-family: var(--font-sans);
		font-size: 13px;
		color: var(--text-primary);
		background: var(--bg-muted);
		outline: none;
	}

	.field input:focus,
	.field select:focus {
		border-color: var(--primary-light);
		background: var(--bg-card);
	}

	.field-error {
		font-size: 10px;
		color: var(--red);
		font-weight: 500;
	}

	.loading-hint,
	.empty-hint {
		font-size: 12px;
		color: var(--text-muted);
		padding: 8px 0;
	}

	/* Sale preview card */
	.sale-preview {
		background: var(--bg-stat);
		border-radius: var(--radius-md);
		padding: 0.75rem 1rem;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.preview-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.p-label {
		font-size: 10px;
		color: var(--text-muted);
		font-weight: 500;
		letter-spacing: 0.3px;
		text-transform: uppercase;
	}

	.p-value {
		font-size: 12px;
		color: var(--text-primary);
		font-weight: 600;
	}

	.p-value.mono {
		font-family: var(--font-mono);
		color: #059669;
	}

	/* Calculator card */
	.calc-card {
		background: linear-gradient(135deg, var(--primary-bg) 0%, var(--bg-stat) 100%);
		border: 0.5px solid #d1d9f0;
		border-radius: var(--radius-md);
		padding: 0.875rem 1rem;
		display: flex;
		flex-direction: column;
		gap: 8px;
		margin-top: 4px;
	}

	.calc-title {
		font-size: 11px;
		font-weight: 700;
		color: var(--text-primary);
		letter-spacing: 0.4px;
		text-transform: uppercase;
		padding-bottom: 4px;
		border-bottom: 0.5px solid rgba(26, 26, 46, 0.08);
	}

	.calc-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.calc-label {
		font-size: 11px;
		color: var(--text-light);
		font-weight: 500;
	}

	.calc-value {
		font-size: 13px;
		font-weight: 700;
		color: var(--text-primary);
	}

	.calc-value.mono {
		font-family: var(--font-mono);
		color: #059669;
	}

	.calc-value.interest {
		color: var(--warning);
	}

	.calc-value.down-pay {
		color: var(--red);
	}

	.calc-value.primary {
		color: var(--text-primary);
		font-size: 15px;
	}

	.calc-row.highlight {
		background: rgba(124, 157, 247, 0.08);
		padding: 4px 8px;
		margin: 0 -8px;
		border-radius: var(--radius-sm);
	}

	.calc-divider {
		height: 0.5px;
		background: rgba(26, 26, 46, 0.08);
		margin: 1px 0;
	}

	.error-msg {
		font-size: 12px;
		color: var(--danger);
		padding: 8px 12px;
		background: var(--danger-bg);
		border-radius: var(--radius-sm);
	}

	.btn-cancel {
		height: 34px;
		padding: 0 16px;
		border: 0.5px solid #d1d5db;
		border-radius: var(--radius-sm);
		background: var(--bg-card);
		font-family: var(--font-sans);
		font-size: 12px;
		color: var(--text-dark);
		cursor: pointer;
	}

	.btn-cancel:hover { background: var(--bg-hover); }

	.btn-submit {
		height: 34px;
		padding: 0 16px;
		border: none;
		border-radius: var(--radius-sm);
		background: var(--primary);
		color: var(--accent);
		font-family: var(--font-sans);
		font-size: 12px;
		font-weight: 600;
		cursor: pointer;
	}

	.btn-submit:hover { opacity: 0.9; }
	.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
