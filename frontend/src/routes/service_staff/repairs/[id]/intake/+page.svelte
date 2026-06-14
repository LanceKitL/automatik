<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { page } from '$app/stores';
	import { getServiceStaffBookings, createEstimate, transmitEstimate } from '$lib/services/api';
	import { formatSlotDateTime } from '$lib/utils/format';
	import { Send, Lock } from '@lucide/svelte';

	let bookingId = $derived(Number($page.params.id));
	let booking = $state<Record<string, unknown> | null>(null);
	let loading = $state(true);
	let transmitted = $state(false);
	let readOnly = $state(false);
	let showTransmitConfirm = $state(false);

	let parts = $state<{ description: string; unit_cost: number; qty: number }[]>([]);
	let labor = $state<{ description: string; hours: number; rate: number }[]>([]);
	let misc = $state<{ description: string; amount: number }[]>([]);
	let taxRate = $state(12);

	let partsSubtotal = $derived(
		parts.reduce((sum, p) => sum + (p.unit_cost || 0) * (p.qty || 0), 0)
	);
	let laborSubtotal = $derived(
		labor.reduce((sum, l) => sum + (l.hours || 0) * (l.rate || 0), 0)
	);
	let miscSubtotal = $derived(
		misc.reduce((sum, m) => sum + (m.amount || 0), 0)
	);
	let subTotal = $derived(partsSubtotal + laborSubtotal + miscSubtotal);
	let taxAmount = $derived(subTotal * (taxRate / 100));
	let total = $derived(subTotal + taxAmount);

	let partsPct = $derived(subTotal > 0 ? Math.round((partsSubtotal / subTotal) * 100) : 0);
	let laborPct = $derived(subTotal > 0 ? Math.round((laborSubtotal / subTotal) * 100) : 0);
	let miscPct = $derived(subTotal > 0 ? Math.round((miscSubtotal / subTotal) * 100) : 0);

	let hasItems = $derived(parts.length > 0 || labor.length > 0 || misc.length > 0);

	onMount(async () => {
		try {
			const res = await getServiceStaffBookings();
			const all = res.data as Record<string, unknown>[];
			booking = all.find((b) => b.booking_id === bookingId) ?? null;
			if (booking) {
				const raw = booking.estimate_data;
				const est = raw ? (typeof raw === 'string' ? JSON.parse(raw) : raw) : null;
				if (est) {
					parts = (est.parts as typeof parts) ?? [];
					labor = (est.labor as typeof labor) ?? [];
					misc = (est.misc as typeof misc) ?? [];
					if (est.tax_rate) taxRate = Number(est.tax_rate);
				}
				if (booking.status === 'confirmed' || booking.status === 'awaiting_signature' || booking.status === 'in_progress' || booking.status === 'completed') {
					readOnly = true;
				}
				if (booking.status === 'awaiting_signature') transmitted = true;
			}
		} catch {
			toast.error('Failed to load booking.');
		} finally {
			loading = false;
		}
	});

	function addPart() { parts = [...parts, { description: '', unit_cost: 0, qty: 1 }]; }
	function removePart(i: number) { parts = parts.filter((_, idx) => idx !== i); }
	function addLabor() { labor = [...labor, { description: '', hours: 1, rate: 0 }]; }
	function removeLabor(i: number) { labor = labor.filter((_, idx) => idx !== i); }
	function addMisc() { misc = [...misc, { description: '', amount: 0 }]; }
	function removeMisc(i: number) { misc = misc.filter((_, idx) => idx !== i); }

	function buildEstimateData() {
		return {
			parts, labor, misc,
			subtotal: subTotal,
			tax_rate: taxRate,
			tax: taxAmount,
			total,
			customer_notes: booking?.notes ?? ''
		};
	}

	async function handleSave(notifyCustomer = false) {
		try {
			await createEstimate(bookingId, buildEstimateData(), notifyCustomer);
			toast.success(notifyCustomer ? 'Estimate saved and customer notified.' : 'Estimate saved.');
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Error saving estimate.');
		}
	}

	async function handleTransmit() {
		showTransmitConfirm = true;
	}

	async function confirmTransmit() {
		showTransmitConfirm = false;
		try {
			await createEstimate(bookingId, buildEstimateData(), false);
			await transmitEstimate(bookingId);
			toast.success('Estimate transmitted for signature.');
			transmitted = true;
			readOnly = true;
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Error transmitting estimate.');
		}
	}

	function handlePrint() { window.print(); }

	function formatId(id: number): string {
		return `BK-${String(id).padStart(4, '0')}`;
	}

	function statusLabel(status: string): string {
		return status?.replace(/_/g, ' ') ?? '—';
	}

	function statusClass(status: string): string {
		const s = status?.toLowerCase() ?? '';
		if (s === 'confirmed' || s === 'approved') return 's-confirmed';
		if (s === 'pending' || s === 'submitted') return 's-pending';
		if (s === 'cancelled' || s === 'rejected') return 's-cancelled';
		if (s === 'draft_estimate') return 's-review';
		if (s === 'awaiting_signature' || s === 'in_progress') return 's-progress';
		if (s === 'completed') return 's-completed';
		return 's-default';
	}
</script>

<div class="page">
	<div class="top-bar no-print">
		<h1>Intake & Estimate</h1>
		<div class="top-actions">
			<button class="btn-print" onclick={handlePrint} disabled={!hasItems && !readOnly}>
				Print
			</button>
		</div>
	</div>

	{#if loading}
		<div class="loading-state"><div class="spinner"></div><span>Loading booking…</span></div>
	{:else if booking}
		<div class="info-banner">
			<div class="banner-left">
				<span class="banner-id">{formatId(bookingId)}</span>
				<div class="banner-customer">
					<strong>{booking.customer_name as string ?? '—'}</strong>
					<span class="banner-vehicle">
						{((booking.year as string) ? (booking.year as string) + ' ' : '') + (booking.brand as string ?? '') + ' ' + (booking.model as string ?? '')}
					</span>
				</div>
			</div>
			<div class="banner-right">
				<span class="badge badge-type">{(booking.slot_type as string ?? 'repair').replace(/_/g, ' ')}</span>
				<span class="status-badge {statusClass(booking.status as string)}">{statusLabel(booking.status as string)}</span>
				<span class="banner-slot">{formatSlotDateTime(booking.slot_datetime as string)}</span>
			</div>
		</div>

		<div class="split">
			<div class="left">
				<section class="card narrative-card">
					<h3>Customer Narrative</h3>
					<p class="narrative-text">{(booking.notes as string) || 'No notes provided.'}</p>
				</section>

				{#if !readOnly}
					<section class="card">
						<div class="section-header">
							<h3>Parts & Supplies</h3>
							<button class="btn-add no-print" onclick={addPart}>+ Add Part</button>
						</div>
						{#if parts.length === 0}
							<p class="empty-lines">No parts added yet.</p>
						{/if}
						{#each parts as part, i}
							<div class="line-row">
								<input bind:value={part.description} placeholder="Part name" class="inp-desc" />
								<div class="num-group">
									<span class="curr-prefix">₱</span>
									<input type="number" bind:value={part.unit_cost} placeholder="Cost" min="0" step="0.01" class="inp-num" />
								</div>
								<input type="number" bind:value={part.qty} placeholder="Qty" min="1" class="inp-qty" />
								<span class="line-total">₱{((part.unit_cost || 0) * (part.qty || 0)).toLocaleString()}</span>
								<button class="btn-remove no-print" onclick={() => removePart(i)} title="Remove">×</button>
							</div>
						{/each}
					</section>

					<section class="card">
						<div class="section-header">
							<h3>Labor</h3>
							<button class="btn-add no-print" onclick={addLabor}>+ Add Labor</button>
						</div>
						{#if labor.length === 0}
							<p class="empty-lines">No labor items added yet.</p>
						{/if}
						{#each labor as item, i}
							<div class="line-row">
								<input bind:value={item.description} placeholder="Service description" class="inp-desc" />
								<div class="num-group">
									<input type="number" bind:value={item.hours} placeholder="Hours" min="0" step="0.5" class="inp-hours" />
									<span class="hours-suffix">hrs</span>
								</div>
								<div class="num-group">
									<span class="curr-prefix">₱</span>
									<input type="number" bind:value={item.rate} placeholder="Rate" min="0" step="0.01" class="inp-num" />
									<span class="hours-suffix">/hr</span>
								</div>
								<span class="line-total">₱{((item.hours || 0) * (item.rate || 0)).toLocaleString()}</span>
								<button class="btn-remove no-print" onclick={() => removeLabor(i)} title="Remove">×</button>
							</div>
						{/each}
					</section>

					<section class="card">
						<div class="section-header">
							<h3>Miscellaneous</h3>
							<button class="btn-add no-print" onclick={addMisc}>+ Add Misc</button>
						</div>
						{#if misc.length === 0}
							<p class="empty-lines">No miscellaneous charges added yet.</p>
						{/if}
						{#each misc as item, i}
							<div class="line-row">
								<input bind:value={item.description} placeholder="Description" class="inp-desc" />
								<div class="num-group">
									<span class="curr-prefix">₱</span>
									<input type="number" bind:value={item.amount} placeholder="Amount" min="0" step="0.01" class="inp-num" />
								</div>
								<span class="line-total">₱{(item.amount || 0).toLocaleString()}</span>
								<button class="btn-remove no-print" onclick={() => removeMisc(i)} title="Remove">×</button>
							</div>
						{/each}
					</section>

					<div class="actions no-print">
						<button class="btn-save" onclick={() => handleSave(false)} disabled={!hasItems}>
							Save Estimate
						</button>
						<button class="btn-save-notify" onclick={() => handleSave(true)} disabled={!hasItems}>
							Save & Notify Customer
						</button>
						<button class="btn-transmit" onclick={handleTransmit} disabled={!hasItems}>
							Transmit for Digital Signature
						</button>
					</div>
				{:else}
					<section class="card">
						<h3>Parts & Supplies</h3>
						{#if parts.length === 0}
							<p class="empty-lines">None</p>
						{:else}
							<div class="ro-table">
								{#each parts as part}
									<div class="ro-row">
										<span class="ro-desc">{part.description || '—'}</span>
										<span class="ro-detail">{Number(part.unit_cost).toLocaleString()} × {part.qty}</span>
										<span class="ro-total">₱{((part.unit_cost || 0) * (part.qty || 0)).toLocaleString()}</span>
									</div>
								{/each}
							</div>
						{/if}
					</section>
					<section class="card">
						<h3>Labor</h3>
						{#if labor.length === 0}
							<p class="empty-lines">None</p>
						{:else}
							<div class="ro-table">
								{#each labor as item}
									<div class="ro-row">
										<span class="ro-desc">{item.description || '—'}</span>
										<span class="ro-detail">{item.hours}h × ₱{Number(item.rate).toLocaleString()}/hr</span>
										<span class="ro-total">₱{((item.hours || 0) * (item.rate || 0)).toLocaleString()}</span>
									</div>
								{/each}
							</div>
						{/if}
					</section>
					<section class="card">
						<h3>Miscellaneous</h3>
						{#if misc.length === 0}
							<p class="empty-lines">None</p>
						{:else}
							<div class="ro-table">
								{#each misc as item}
									<div class="ro-row">
										<span class="ro-desc">{item.description || '—'}</span>
										<span class="ro-detail"></span>
										<span class="ro-total">₱{(item.amount || 0).toLocaleString()}</span>
									</div>
								{/each}
							</div>
						{/if}
					</section>
					{#if transmitted}
						<div class="transmitted-badge no-print">
							Estimate locked — awaiting digital signature
						</div>
					{/if}
					{#if booking.status === 'confirmed'}
						<div class="confirmed-badge no-print">
							Customer confirmed — ready to proceed
						</div>
					{/if}
				{/if}
			</div>

			<div class="right">
				<div class="summary-card">
					<h3>Estimate Summary</h3>
					{#if subTotal > 0}
						<div class="breakdown-bar">
							<div class="bar-seg bar-parts" style="width: {partsPct}%"></div>
							<div class="bar-seg bar-labor" style="width: {laborPct}%"></div>
							<div class="bar-seg bar-misc" style="width: {miscPct}%"></div>
						</div>
						<div class="breakdown-labels">
							<span><span class="dot dot-parts"></span> Parts {partsPct}%</span>
							<span><span class="dot dot-labor"></span> Labor {laborPct}%</span>
							<span><span class="dot dot-misc"></span> Misc {miscPct}%</span>
						</div>
					{/if}
					<div class="summary-body">
						<div class="s-row"><span>Parts</span><span>₱{partsSubtotal.toLocaleString()}</span></div>
						<div class="s-row"><span>Labor</span><span>₱{laborSubtotal.toLocaleString()}</span></div>
						<div class="s-row"><span>Miscellaneous</span><span>₱{miscSubtotal.toLocaleString()}</span></div>
						<div class="s-divider"></div>
						<div class="s-row s-sub"><span>Subtotal</span><span>₱{subTotal.toLocaleString()}</span></div>
						<div class="s-row s-tax">
							<span>Tax ({(taxRate)}%)</span>
							<span>₱{taxAmount.toLocaleString()}</span>
						</div>
						<div class="s-divider thick"></div>
						<div class="s-row s-total">
							<span>Total</span>
							<span class="total-amount">₱{total.toLocaleString()}</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<!-- Transmit Confirm Modal -->
{#if showTransmitConfirm}
	<div class="modal-overlay no-print" onclick={() => showTransmitConfirm = false}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h3><Lock size={18} /> Transmit Estimate</h3>
				<button class="modal-close" onclick={() => showTransmitConfirm = false}>×</button>
			</div>
			<div class="modal-body">
				<p>Lock this estimate and transmit it to the customer for digital signature?</p>
				<p class="field-hint">Once transmitted, the estimate becomes read-only until the customer responds.</p>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" onclick={() => showTransmitConfirm = false}>Cancel</button>
				<button class="btn-primary" onclick={confirmTransmit}>
					<Send size={14} /> Transmit
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.page {
		padding: 1.5rem 2rem;
		max-width: 1400px;
		margin: 0 auto;
		font-family: var(--font-sans);
	}

	/* ── Top Bar ────────────────────────────── */
	.top-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 0.75rem;
	}
	.top-bar h1 {
		margin: 0;
		font-size: 1.35rem;
		font-weight: 700;
		color: var(--text-primary);
		letter-spacing: -0.3px;
	}
	.top-actions { display: flex; gap: 0.5rem; }
	.btn-print {
		padding: 0.45rem 1rem;
		font-size: 0.8rem;
		font-weight: 600;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: var(--bg-card);
		color: var(--text-dark);
		cursor: pointer;
		font-family: inherit;
	}
	.btn-print:hover:not(:disabled) { background: var(--bg-hover); }
	.btn-print:disabled { opacity: 0.4; cursor: not-allowed; }

	/* ── Loading ────────────────────────────── */
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 40vh;
		gap: 0.75rem;
		color: var(--text-light);
		font-size: 0.9rem;
	}
	.spinner {
		width: 28px; height: 28px;
		border: 2.5px solid var(--border);
		border-top-color: var(--primary);
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
	}
	@keyframes spin { to { transform: rotate(360deg); } }

	/* ── Info Banner ────────────────────────── */
	.info-banner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		padding: 1rem 1.25rem;
		margin-bottom: 1.25rem;
	}
	.banner-left { display: flex; align-items: center; gap: 1rem; }
	.banner-id {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		font-weight: 700;
		background: var(--primary);
		color: #fff;
		padding: 0.3rem 0.7rem;
		border-radius: var(--radius-sm);
		white-space: nowrap;
	}
	.banner-customer { display: flex; flex-direction: column; gap: 0.15rem; }
	.banner-customer strong { font-size: 0.95rem; color: var(--text-primary); }
	.banner-vehicle { font-size: 0.8rem; color: var(--text-light); }
	.banner-right { display: flex; align-items: center; gap: 0.6rem; flex-shrink: 0; }
	.badge-type {
		font-size: 0.7rem;
		font-weight: 600;
		padding: 0.2rem 0.6rem;
		border-radius: 10px;
		background: #dbeafe;
		color: #1e40af;
		text-transform: capitalize;
		white-space: nowrap;
	}
	.status-badge {
		font-size: 0.7rem;
		font-weight: 600;
		padding: 0.2rem 0.6rem;
		border-radius: 10px;
		text-transform: capitalize;
		white-space: nowrap;
	}
	:global(.s-pending) { background: #fef3c7; color: #92400e; }
	:global(.s-confirmed) { background: #dbeafe; color: #1e40af; }
	:global(.s-review) { background: #e0e7ff; color: #3730a3; }
	:global(.s-progress) { background: #d1fae5; color: #065f46; }
	:global(.s-completed) { background: #d1fae5; color: #166534; }
	:global(.s-cancelled) { background: #fee2e2; color: #991b1b; }
	:global(.s-default) { background: var(--bg-muted); color: var(--text-muted); }
	.banner-slot { font-size: 0.78rem; color: var(--text-muted); white-space: nowrap; }

	/* ── Split Layout ───────────────────────── */
	.split { display: flex; gap: 1.5rem; align-items: flex-start; }
	.left { flex: 1; min-width: 0; }
	.right { width: 20rem; position: sticky; top: 1.5rem; flex-shrink: 0; }

	/* ── Card ───────────────────────────────── */
	.card {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		padding: 1rem 1.25rem;
		margin-bottom: 1rem;
	}
	.card h3 {
		margin: 0 0 0.75rem;
		font-size: 0.82rem;
		font-weight: 700;
		color: var(--text-primary);
		text-transform: uppercase;
		letter-spacing: 0.03em;
	}
	.section-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 0.75rem;
	}
	.section-header h3 { margin: 0; }
	.narrative-card { background: #fafbfc; }
	.narrative-text {
		margin: 0;
		color: var(--text-dark);
		font-size: 0.88rem;
		line-height: 1.6;
		font-style: italic;
	}
	.empty-lines { color: var(--text-muted); font-size: 0.82rem; margin: 0.5rem 0; }

	/* ── Line Rows (Edit) ───────────────────── */
	.line-row {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.35rem 0;
		border-bottom: 1px solid var(--border-lighter, #f0f0f0);
	}
	.line-row:last-child { border-bottom: none; }
	.line-row:hover { background: var(--bg-hover); border-radius: var(--radius-sm); }

	.inp-desc { flex: 1; min-width: 0; }
	.num-group { display: inline-flex; align-items: center; gap: 0; }
	.curr-prefix {
		padding: 0.3rem 0 0.3rem 0.4rem;
		font-size: 0.8rem;
		color: var(--text-muted);
		background: var(--bg-muted);
		border: 1px solid var(--border);
		border-right: none;
		border-radius: var(--radius-sm) 0 0 var(--radius-sm);
		line-height: 1;
	}
	.hours-suffix {
		padding: 0.3rem 0.4rem 0.3rem 0;
		font-size: 0.75rem;
		color: var(--text-muted);
		background: var(--bg-muted);
		border: 1px solid var(--border);
		border-left: none;
		border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
		line-height: 1;
	}
	.inp-num {
		width: 5.5rem;
		border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
	}
	.num-group .inp-num:first-child { border-radius: var(--radius-sm) 0 0 var(--radius-sm); }
	.num-group .inp-num:only-child {
		border-radius: var(--radius-sm);
		border: 1px solid var(--border);
	}

	.inp-hours { width: 3.5rem; border-radius: var(--radius-sm) 0 0 var(--radius-sm); }
	.inp-qty { width: 3rem; }

	.line-row input {
		padding: 0.35rem 0.45rem;
		font-size: 0.82rem;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: var(--bg-card);
		color: var(--text-primary);
		font-family: inherit;
	}
	.line-row input:focus {
		outline: none;
		border-color: var(--primary);
		box-shadow: 0 0 0 2px rgba(99,102,241,0.12);
	}
	.line-row input::placeholder { color: var(--text-muted); font-size: 0.78rem; }

	.line-total {
		min-width: 5.5rem;
		text-align: right;
		font-weight: 700;
		font-size: 0.85rem;
		color: var(--text-primary);
		font-variant-numeric: tabular-nums;
	}

	.btn-remove {
		width: 1.5rem; height: 1.5rem;
		display: flex; align-items: center; justify-content: center;
		border: none;
		background: transparent;
		color: var(--text-muted);
		font-size: 1rem;
		cursor: pointer;
		border-radius: 50%;
		flex-shrink: 0;
	}
	.btn-remove:hover { background: #fee2e2; color: #dc2626; }

	.btn-add {
		padding: 0.25rem 0.6rem;
		font-size: 0.75rem;
		font-weight: 600;
		border: 1px dashed var(--border);
		border-radius: var(--radius-sm);
		background: transparent;
		color: var(--text-muted);
		cursor: pointer;
		font-family: inherit;
	}
	.btn-add:hover { border-color: var(--primary); color: var(--primary); background: #eef2ff; }

	/* ── Read-only Table ────────────────────── */
	.ro-table { font-size: 0.85rem; }
	.ro-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.35rem 0;
		border-bottom: 1px solid var(--border-lighter, #f0f0f0);
	}
	.ro-row:last-child { border-bottom: none; }
	.ro-row:nth-child(even) { background: var(--bg-muted); }
	.ro-desc { flex: 1; font-weight: 500; color: var(--text-dark); }
	.ro-detail { width: 8rem; color: var(--text-light); font-size: 0.8rem; }
	.ro-total { min-width: 5.5rem; text-align: right; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; }

	/* ── Transmitted Badge ──────────────────── */
	.transmitted-badge {
		background: #fef9e7;
		border: 1px solid #f9e79f;
		padding: 0.6rem 1rem;
		border-radius: var(--radius-sm);
		color: #7d6608;
		font-size: 0.82rem;
		font-weight: 600;
		text-align: center;
	}
	.confirmed-badge {
		background: #d1fae5;
		border: 1px solid #a7f3d0;
		padding: 0.6rem 1rem;
		border-radius: var(--radius-sm);
		color: #065f46;
		font-size: 0.82rem;
		font-weight: 600;
		text-align: center;
	}

	/* ── Actions ────────────────────────────── */
	.actions { display: flex; gap: 0.75rem; margin-top: 1.5rem; }
	.btn-save, .btn-save-notify, .btn-transmit {
		padding: 0.6rem 1.25rem;
		font-size: 0.85rem;
		font-weight: 600;
		border-radius: var(--radius-sm);
		cursor: pointer;
		font-family: inherit;
		border: none;
	}
	.btn-save { background: var(--bg-muted); color: var(--text-dark); border: 1px solid var(--border); }
	.btn-save:hover:not(:disabled) { background: var(--bg-hover); }
	.btn-save-notify { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
	.btn-save-notify:hover:not(:disabled) { background: #fde68a; }
	.btn-transmit { background: var(--primary); color: #fff; }
	.btn-transmit:hover:not(:disabled) { opacity: 0.85; }
	.btn-save:disabled, .btn-transmit:disabled { opacity: 0.4; cursor: not-allowed; }

	/* ── Summary Card ───────────────────────── */
	.summary-card {
		background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%);
		border: 1.5px solid #dce6f5;
		border-radius: var(--radius-md);
		padding: 1.25rem;
	}
	.summary-card h3 {
		margin: 0 0 0.75rem;
		font-size: 0.85rem;
		font-weight: 700;
		color: var(--text-primary);
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.breakdown-bar {
		display: flex;
		height: 6px;
		border-radius: 3px;
		overflow: hidden;
		margin-bottom: 0.4rem;
		background: var(--bg-muted);
	}
	.bar-seg { transition: width 0.25s; }
	.bar-parts { background: #6366f1; }
	.bar-labor { background: #06b6d4; }
	.bar-misc { background: #f59e0b; }

	.breakdown-labels {
		display: flex;
		gap: 0.75rem;
		font-size: 0.7rem;
		color: var(--text-muted);
		margin-bottom: 0.75rem;
		flex-wrap: wrap;
	}
	.dot {
		display: inline-block;
		width: 7px; height: 7px;
		border-radius: 50%;
		margin-right: 3px;
	}
	.dot-parts { background: #6366f1; }
	.dot-labor { background: #06b6d4; }
	.dot-misc { background: #f59e0b; }

	.summary-body { font-size: 0.85rem; }
	.s-row {
		display: flex;
		justify-content: space-between;
		padding: 0.3rem 0;
		color: var(--text-dark);
	}
	.s-row span:last-child { font-variant-numeric: tabular-nums; }
	.s-divider { border-top: 1px solid #e2e8f0; margin: 0.35rem 0; }
	.s-divider.thick { border-top: 2px solid #cbd5e1; }
	.s-sub { font-weight: 600; }
	.s-tax { color: var(--text-muted); font-size: 0.8rem; }
	.s-total { padding-top: 0.25rem; }
	.total-amount { font-size: 1.3rem; font-weight: 800; color: #059669; }

	/* ── Modal ──────────────────────────────── */
	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
	.modal { background: var(--bg-card); border-radius: var(--radius-lg); width: 460px; max-width: 90vw; box-shadow: var(--shadow-lg); }
	.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--border); }
	.modal-header h3 { font-size: 16px; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; }
	.modal-close { background: none; border: none; cursor: pointer; color: var(--text-muted); padding: 4px; border-radius: var(--radius-sm); font-size: 20px; }
	.modal-close:hover { background: var(--bg-hover); }
	.modal-body { padding: 20px 24px; }
	.modal-body p { margin: 0 0 8px; font-size: 14px; color: var(--text-primary); }
	.field-hint { font-size: 12px; color: var(--text-muted); margin: 0; }
	.modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 16px 24px; border-top: 1px solid var(--border); }
	.btn-cancel { background: none; border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; color: var(--text-muted); font-family: inherit; }
	.btn-cancel:hover { background: var(--bg-hover); }
	.btn-primary { background: var(--primary); color: var(--text-white); border: none; border-radius: var(--radius-sm); padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; display: inline-flex; align-items: center; gap: 6px; }
	.btn-primary:hover { opacity: 0.85; }

	/* ── Print Styles ───────────────────────── */
	@media print {
		.no-print { display: none !important; }
		.page { padding: 0.5in !important; max-width: none !important; }
		.info-banner { break-inside: avoid; border: 1px solid #ccc; }
		.split { display: block !important; }
		.left { max-width: none !important; }
		.right { width: 100% !important; position: static !important; margin-top: 1rem; }
		.card { break-inside: avoid; border: 1px solid #ddd; }
		.summary-card { background: #f9fafb !important; border: 1px solid #999; }
		.ro-row:nth-child(even) { background: #f3f4f6 !important; }
		.banner-id { background: #333 !important; }
	}
</style>
