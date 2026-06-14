<script lang="ts">
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { Calculator, DollarSign, Percent, CalendarDays, ArrowRight, PiggyBank } from '@lucide/svelte';

	let price = $state(1500000);
	let downPayment = $state(300000);
	let downPercent = $state(20);
	let usePercent = $state(true);
	let interestRate = $state(8);
	let termMonths = $state(60);

	let loanAmount = $derived(price - downPayment);
	let monthlyRate = $derived(interestRate / 100 / 12);
	let n = $derived(termMonths);

	let monthlyPayment = $derived.by(() => {
		if (monthlyRate === 0) return loanAmount / n;
		return loanAmount * monthlyRate / (1 - Math.pow(1 + monthlyRate, -n));
	});

	let totalPayment = $derived(monthlyPayment * n);
	let totalInterest = $derived(totalPayment - loanAmount);

	let schedule = $derived.by(() => {
		const rows: { period: number; payment: number; principal: number; interest: number; balance: number }[] = [];
		let bal = loanAmount;
		for (let i = 1; i <= n; i++) {
			const interest = bal * monthlyRate;
			let princ = monthlyPayment - interest;
			if (i === n) { princ = bal; }
			bal -= princ;
			rows.push({
				period: i,
				payment: i === n ? princ + interest : monthlyPayment,
				principal: princ,
				interest,
				balance: Math.max(bal, 0),
			});
		}
		return rows;
	});

	function toggleDownToggle() {
		if (usePercent) {
			usePercent = false;
			downPayment = Math.round(price * (downPercent / 100));
		} else {
			usePercent = true;
			downPercent = Math.round((downPayment / price) * 100);
		}
	}

	function onPriceChange() {
		if (usePercent) {
			downPayment = Math.round(price * (downPercent / 100));
		}
	}

	function onDownPercentChange(pct: number) {
		downPercent = pct;
		downPayment = Math.round(price * (pct / 100));
	}

	function fmt(n: number): string {
		return `₱${Math.round(n).toLocaleString()}`;
	}

	function fmtShort(n: number): string {
		if (n >= 1000000) return `₱${(n / 1000000).toFixed(2)}M`;
		if (n >= 1000) return `₱${(n / 1000).toFixed(1)}K`;
		return `₱${Math.round(n).toLocaleString()}`;
	}
</script>

<Navbar />

<section class="calc-hero">
	<div class="calc-hero-inner">
		<span class="calc-hero-tag">Financing Made Simple</span>
		<h1 class="calc-hero-title">Loan Calculator</h1>
		<p class="calc-hero-sub">
			Estimate your monthly payments and see the full amortization schedule.
			No obligations, no credit check.
		</p>
	</div>
</section>

<section class="calc-section">
	<div class="calc-layout">
		<!-- Form panel -->
		<div class="calc-form">
			<h2 class="panel-title">Enter Details</h2>

			<label class="calc-label">Vehicle Price</label>
			<div class="input-group">
				<span class="input-prefix">₱</span>
				<input type="number" class="calc-input" bind:value={price} oninput={onPriceChange} min="100000" step="10000" />
			</div>

			<label class="calc-label">Down Payment</label>
			<div class="down-toggle">
				<button class="toggle-btn" class:active={usePercent} onclick={() => toggleDownToggle()}>%</button>
				<button class="toggle-btn" class:active={!usePercent} onclick={() => toggleDownToggle()}>₱</button>
			</div>
			{#if usePercent}
				<div class="quick-pcts">
					{#each [10, 20, 30, 40, 50] as p}
						<button class="pct-chip" class:active={downPercent === p} onclick={() => onDownPercentChange(p)}>{p}%</button>
					{/each}
				</div>
				<input type="range" min="5" max="60" bind:value={downPercent} oninput={() => onDownPercentChange(downPercent)} class="calc-range" />
				<span class="range-val">{downPercent}% (₱{Math.round(price * downPercent / 100).toLocaleString()})</span>
			{:else}
				<div class="input-group">
					<span class="input-prefix">₱</span>
					<input type="number" class="calc-input" bind:value={downPayment} min="0" step="10000" />
				</div>
			{/if}

			<label class="calc-label">Interest Rate <span class="lbl-muted">(% per annum)</span></label>
			<div class="input-group">
				<span class="input-prefix"><Percent size={14} /></span>
				<input type="number" class="calc-input" bind:value={interestRate} min="1" max="36" step="0.5" />
			</div>

			<label class="calc-label">Loan Term</label>
			<div class="term-options">
				{#each [12, 24, 36, 48, 60, 72, 84] as m}
					<button class="term-chip" class:active={termMonths === m} onclick={() => (termMonths = m)}>
						{m < 12 ? `${m}mo` : `${m / 12}yr`}
					</button>
				{/each}
			</div>
		</div>

		<!-- Results panel -->
		<div class="calc-results">
			<h2 class="panel-title">Estimated Payments</h2>

			<div class="result-card highlight">
				<PiggyBank size={24} />
				<div class="result-body">
					<span class="result-lbl">Monthly Amortization</span>
					<span class="result-val">{fmt(isNaN(monthlyPayment) ? 0 : monthlyPayment)}</span>
				</div>
			</div>

			<div class="result-subgrid">
				<div class="result-card sub">
					<Calculator size={18} />
					<div class="result-body">
						<span class="result-lbl">Loan Amount</span>
						<span class="result-val-sm">{fmt(isNaN(loanAmount) ? 0 : loanAmount)}</span>
					</div>
				</div>
				<div class="result-card sub">
					<DollarSign size={18} />
					<div class="result-body">
						<span class="result-lbl">Total Interest</span>
						<span class="result-val-sm">{fmt(isNaN(totalInterest) ? 0 : totalInterest)}</span>
					</div>
				</div>
			</div>

			<div class="result-card total">
				<div class="result-body">
					<span class="result-lbl">Total Payment</span>
					<span class="result-val">{fmt(isNaN(totalPayment) ? 0 : totalPayment)}</span>
				</div>
			</div>

			<!-- Summary bar -->
			<div class="summary-bar-wrap">
				<div class="summary-bar">
					<div class="bar-principal" style="flex: {loanAmount}" />
					<div class="bar-interest" style="flex: {totalInterest > 0 ? totalInterest : 1}" />
				</div>
				<div class="bar-legend">
					<span class="legend-item"><span class="dot dot-p" /> Principal ({(loanAmount / totalPayment * 100).toFixed(0)}%)</span>
					<span class="legend-item"><span class="dot dot-i" /> Interest ({(totalInterest / totalPayment * 100).toFixed(0)}%)</span>
				</div>
			</div>

			<!-- Amortization Table -->
			<div class="schedule-section">
				<h3 class="schedule-title"><CalendarDays size={16} /> Full Amortization Schedule</h3>
				<div class="table-scroll">
					<table class="amort-table">
						<thead>
							<tr>
								<th>#</th>
								<th>Payment</th>
								<th>Principal</th>
								<th>Interest</th>
								<th>Balance</th>
							</tr>
						</thead>
						<tbody>
							{#each schedule as row}
								<tr>
									<td>{row.period}</td>
									<td>{fmtShort(row.payment)}</td>
									<td>{fmtShort(row.principal)}</td>
									<td>{fmtShort(row.interest)}</td>
									<td>{fmtShort(row.balance)}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
</section>

<section class="cta-section">
	<div class="cta-inner">
		<h2>Ready to Get Started?</h2>
		<p>Talk to our financing team and drive home today.</p>
		<a href="/contact" class="cta-btn">Contact Us</a>
	</div>
</section>

<Footer />

<style>
	/* ── Hero ── */
	.calc-hero {
		padding: 8rem 1.5rem 3rem;
		background: linear-gradient(135deg, #1a1a2e 0%, #282854 100%);
		text-align: center;
	}
	.calc-hero-inner { max-width: 700px; margin: 0 auto; }
	.calc-hero-tag { display: inline-block; background: rgba(232, 201, 126, 0.15); color: #e8c97e; font-size: 11px; font-weight: 600; padding: 4px 14px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; }
	.calc-hero-title { font-size: 2.5rem; font-weight: 700; color: #fff; margin: 0 0 0.75rem; }
	.calc-hero-sub { font-size: 1rem; color: rgba(255,255,255,0.65); max-width: 500px; margin: 0 auto; line-height: 1.6; }

	/* ── Layout ── */
	.calc-section { padding: 3rem 1.5rem 4rem; max-width: 1200px; margin: 0 auto; }
	.calc-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start; }

	.panel-title { font-size: 1.1rem; font-weight: 700; color: #1a1a2e; margin: 0 0 1.25rem; }

	/* ── Form ── */
	.calc-form { background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 1.5rem; }
	.calc-label { display: block; font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.4px; margin: 1rem 0 6px; }
	.calc-label:first-of-type { margin-top: 0; }
	.lbl-muted { font-weight: 400; text-transform: none; color: #9ca3af; }
	.input-group { position: relative; }
	.input-prefix { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #9ca3af; }
	.calc-input { width: 100%; padding: 10px 12px 10px 34px; border: 1px solid #d1d5db; border-radius: 8px; font-family: var(--font-sans); font-size: 14px; outline: none; box-sizing: border-box; }
	.calc-input:focus { border-color: var(--primary); }

	.down-toggle { display: flex; gap: 4px; margin-bottom: 8px; }
	.toggle-btn { padding: 5px 14px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; font-family: var(--font-sans); font-size: 12px; font-weight: 600; color: #6b7280; cursor: pointer; }
	.toggle-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); }

	.quick-pcts { display: flex; gap: 4px; margin-bottom: 8px; flex-wrap: wrap; }
	.pct-chip { padding: 4px 12px; border: 1px solid #e5e7eb; border-radius: 20px; background: #fff; font-family: var(--font-sans); font-size: 11px; color: #6b7280; cursor: pointer; }
	.pct-chip.active { background: var(--primary); color: #fff; border-color: var(--primary); }

	.calc-range { width: 100%; margin: 6px 0; accent-color: var(--primary); }
	.range-val { font-size: 12px; color: #6b7280; }

	.term-options { display: flex; gap: 4px; flex-wrap: wrap; }
	.term-chip { padding: 7px 14px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff; font-family: var(--font-sans); font-size: 12px; font-weight: 600; color: #374151; cursor: pointer; transition: all 0.15s; }
	.term-chip.active { background: var(--primary); color: #fff; border-color: var(--primary); }

	/* ── Results ── */
	.calc-results { display: flex; flex-direction: column; gap: 12px; }
	.result-card { display: flex; align-items: center; gap: 12px; padding: 1rem 1.25rem; border-radius: 12px; border: 1px solid #e5e7eb; background: #fff; }
	.result-card.highlight { background: linear-gradient(135deg, #eef2ff, #e0e7ff); border-color: var(--primary); }
	.result-card.sub { padding: 0.85rem 1rem; }
	.result-card.total { background: #f9fafb; border-color: #d1d5db; }
	.result-card :global(svg) { flex-shrink: 0; color: var(--primary); }
	.result-body { display: flex; flex-direction: column; }
	.result-lbl { font-size: 10px; font-weight: 500; color: #6b7280; text-transform: uppercase; letter-spacing: 0.4px; }
	.result-val { font-size: 1.4rem; font-weight: 700; color: #1a1a2e; }
	.result-val-sm { font-size: 1rem; font-weight: 700; color: #1a1a2e; }
	.result-subgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

	/* ── Summary bar ── */
	.summary-bar-wrap { margin-top: 4px; }
	.summary-bar { display: flex; height: 8px; border-radius: 4px; overflow: hidden; }
	.bar-principal { background: var(--primary); }
	.bar-interest { background: #f59e0b; }
	.bar-legend { display: flex; gap: 16px; margin-top: 6px; font-size: 11px; color: #6b7280; }
	.legend-item { display: flex; align-items: center; gap: 6px; }
	.dot { width: 8px; height: 8px; border-radius: 50%; }
	.dot-p { background: var(--primary); }
	.dot-i { background: #f59e0b; }

	/* ── Schedule table ── */
	.schedule-section { margin-top: 4px; }
	.schedule-title { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: #1a1a2e; margin: 0 0 8px; }
	.schedule-title :global(svg) { color: var(--primary); }
	.table-scroll { max-height: 360px; overflow-y: auto; border: 1px solid #e5e7eb; border-radius: 8px; }
	.table-scroll::-webkit-scrollbar { width: 5px; }
	.table-scroll::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
	.amort-table { width: 100%; border-collapse: collapse; font-size: 12px; }
	.amort-table th { position: sticky; top: 0; background: #f9fafb; padding: 8px 10px; text-align: right; font-size: 10px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.4px; border-bottom: 1px solid #e5e7eb; }
	.amort-table th:first-child { text-align: center; }
	.amort-table td { padding: 6px 10px; text-align: right; border-bottom: 1px solid #f3f4f6; color: #374151; font-variant-numeric: tabular-nums; }
	.amort-table td:first-child { text-align: center; color: #9ca3af; }
	.amort-table tr:last-child td { border-bottom: none; }
	.amort-table tr:hover td { background: #f9fafb; }

	/* ── CTA ── */
	.cta-section { padding: 4rem 1.5rem; text-align: center; background: #f9fafb; }
	.cta-inner { max-width: 500px; margin: 0 auto; }
	.cta-inner h2 { font-size: 1.5rem; font-weight: 700; color: #1a1a2e; margin: 0 0 8px; }
	.cta-inner p { color: #6b7280; font-size: 14px; margin: 0 0 1.25rem; }
	.cta-btn { display: inline-block; padding: 12px 32px; background: var(--primary); color: #fff; border-radius: 8px; font-family: var(--font-sans); font-size: 14px; font-weight: 600; text-decoration: none; }

	@media (max-width: 768px) {
		.calc-layout { grid-template-columns: 1fr; }
		.result-subgrid { grid-template-columns: 1fr; }
		.calc-hero-title { font-size: 1.75rem; }
	}
</style>
