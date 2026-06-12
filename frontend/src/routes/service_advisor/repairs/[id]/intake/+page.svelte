<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { getAdvisorServiceBookings, createEstimate, transmitEstimate } from '$lib/services/api';

	let bookingId = $derived(Number($page.params.id));
	let booking = $state<Record<string, unknown> | null>(null);
	let loading = $state(true);
	let message = $state('');
	let transmitted = $state(false);
	let readOnly = $state(false);

	// Estimate form data
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

	onMount(async () => {
		try {
			const res = await getAdvisorServiceBookings();
			const all = res.data as Record<string, unknown>[];
			booking = all.find((b) => b.booking_id === bookingId) ?? null;

			if (booking) {
				// If estimate already exists, load it
				const est = booking.estimate_data as Record<string, unknown> | null;
				if (est) {
					parts = (est.parts as typeof parts) ?? [];
					labor = (est.labor as typeof labor) ?? [];
					misc = (est.misc as typeof misc) ?? [];
					if (est.tax_rate) taxRate = Number(est.tax_rate);
				}

				if (booking.status === 'awaiting_signature' || booking.status === 'in_progress' || booking.status === 'completed') {
					transmitted = true;
					readOnly = true;
				}
				if (booking.status === 'awaiting_signature') {
					transmitted = true;
				}
			}
		} catch {
			// error
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

	async function handleSave() {
		const estimateData = {
			parts,
			labor,
			misc,
			subtotal: subTotal,
			tax_rate: taxRate,
			tax: taxAmount,
			total,
			customer_notes: booking?.notes ?? ''
		};
		try {
			await createEstimate(bookingId, estimateData);
			message = 'Estimate saved.';
		} catch (e: unknown) {
			message = e instanceof Error ? e.message : 'Error saving estimate.';
		}
	}

	async function handleTransmit() {
		if (!confirm('Lock estimate and transmit for digital signature?')) return;
		try {
			// Save first, then transmit
			const estimateData = {
				parts, labor, misc,
				subtotal: subTotal,
				tax_rate: taxRate,
				tax: taxAmount,
				total,
				customer_notes: booking?.notes ?? ''
			};
			await createEstimate(bookingId, estimateData);
			await transmitEstimate(bookingId);
			message = 'Estimate transmitted for signature.';
			transmitted = true;
			readOnly = true;
		} catch (e: unknown) {
			message = e instanceof Error ? e.message : 'Error.';
		}
	}

	function formatId(id: number): string {
		return `BK-${String(id).padStart(4, '0')}`;
	}
</script>

<h1>Intake & Estimate — {formatId(bookingId)}</h1>

{#if message}
	<p class="msg">{message}</p>
{/if}

{#if loading}
	<p>Loading…</p>
{:else if booking}
	<div class="split">
		<!-- LEFT: Customer Narrative + Estimate Form -->
		<div class="left">
			<section class="narrative">
				<h3>Customer Narrative</h3>
				<p class="narrative-text">{(booking.notes as string) || 'No notes provided.'}</p>
			</section>

			{#if !readOnly}
				<!-- PARTS -->
				<section>
					<h3>Parts</h3>
					{#each parts as part, i}
						<div class="line-row">
							<input bind:value={part.description} placeholder="Part name" disabled={readOnly} />
							<input type="number" bind:value={part.unit_cost} placeholder="Unit cost" disabled={readOnly} min="0" step="0.01" />
							<input type="number" bind:value={part.qty} placeholder="Qty" disabled={readOnly} min="1" />
							<span class="line-total">₱{((part.unit_cost || 0) * (part.qty || 0)).toLocaleString()}</span>
							<button onclick={() => removePart(i)} disabled={readOnly}>×</button>
						</div>
					{/each}
					<button onclick={addPart} disabled={readOnly}>+ Add Part</button>
				</section>

				<!-- LABOR -->
				<section>
					<h3>Labor</h3>
					{#each labor as item, i}
						<div class="line-row">
							<input bind:value={item.description} placeholder="Labor description" disabled={readOnly} />
							<input type="number" bind:value={item.hours} placeholder="Hours" disabled={readOnly} min="0" step="0.5" />
							<input type="number" bind:value={item.rate} placeholder="Rate/hr" disabled={readOnly} min="0" step="0.01" />
							<span class="line-total">₱{((item.hours || 0) * (item.rate || 0)).toLocaleString()}</span>
							<button onclick={() => removeLabor(i)} disabled={readOnly}>×</button>
						</div>
					{/each}
					<button onclick={addLabor} disabled={readOnly}>+ Add Labor</button>
				</section>

				<!-- MISC -->
				<section>
					<h3>Miscellaneous</h3>
					{#each misc as item, i}
						<div class="line-row">
							<input bind:value={item.description} placeholder="Description" disabled={readOnly} />
							<input type="number" bind:value={item.amount} placeholder="Amount" disabled={readOnly} min="0" step="0.01" />
							<span class="line-total">₱{(item.amount || 0).toLocaleString()}</span>
							<button onclick={() => removeMisc(i)} disabled={readOnly}>×</button>
						</div>
					{/each}
					<button onclick={addMisc} disabled={readOnly}>+ Add Misc</button>
				</section>

				<div class="actions">
					<button onclick={handleSave} disabled={readOnly}>Save Estimate</button>
					<button onclick={handleTransmit} class="btn-primary" disabled={readOnly}>
						Transmit for Digital Signature
					</button>
				</div>
			{:else}
				<!-- READ-ONLY VIEW -->
				<section>
					<h3>Parts</h3>
					{#each parts as part}
						<div class="line-row ro">
							<span>{part.description || '—'}</span>
							<span>₱{Number(part.unit_cost).toLocaleString()} × {part.qty}</span>
							<span class="line-total">₱{((part.unit_cost || 0) * (part.qty || 0)).toLocaleString()}</span>
						</div>
					{/each}
				</section>
				<section>
					<h3>Labor</h3>
					{#each labor as item}
						<div class="line-row ro">
							<span>{item.description || '—'}</span>
							<span>{item.hours}h × ₱{Number(item.rate).toLocaleString()}/hr</span>
							<span class="line-total">₱{((item.hours || 0) * (item.rate || 0)).toLocaleString()}</span>
						</div>
					{/each}
				</section>
				<section>
					<h3>Miscellaneous</h3>
					{#each misc as item}
						<div class="line-row ro">
							<span>{item.description || '—'}</span>
							<span></span>
							<span class="line-total">₱{(item.amount || 0).toLocaleString()}</span>
						</div>
					{/each}
				</section>
				{#if transmitted}
					<p class="badge-info">✓ Estimate locked — awaiting digital signature</p>
				{/if}
			{/if}
		</div>

		<!-- RIGHT: Live Summary Card -->
		<div class="right">
			<div class="summary-card">
				<h3>Estimate Summary</h3>
				<div class="summary-line"><span>Parts</span><span>₱{partsSubtotal.toLocaleString()}</span></div>
				<div class="summary-line"><span>Labor</span><span>₱{laborSubtotal.toLocaleString()}</span></div>
				<div class="summary-line"><span>Miscellaneous</span><span>₱{miscSubtotal.toLocaleString()}</span></div>
				<hr>
				<div class="summary-line"><strong>Subtotal</strong><strong>₱{subTotal.toLocaleString()}</strong></div>
				<div class="summary-line">
					<span>Tax ({taxRate}%)</span>
					<span>₱{taxAmount.toLocaleString()}</span>
				</div>
				<hr>
				<div class="summary-line total-line">
					<strong>Total</strong>
					<strong class="total-amount">₱{total.toLocaleString()}</strong>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	h1 { padding: 1.5rem 1.5rem 0; margin: 0; }
	.msg { padding: 0.5rem 1.5rem; color: var(--success); }
	.split { display: flex; gap: 1.5rem; padding: 1.5rem; }
	.left { flex: 1; }
	.right { width: 22rem; position: sticky; top: 1.5rem; align-self: flex-start; }
	section { margin-bottom: 1.5rem; }
	.narrative { background: var(--bg-card); padding: 1rem; border-radius: var(--radius-sm); border: 1px solid #ddd; }
	.narrative-text { color: var(--text-light); font-style: italic; margin: 0.5rem 0 0; }
	.line-row { display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem; }
	.line-row input { flex: 1; padding: 0.4rem; border: 1px solid var(--border); border-radius: var(--radius-sm); }
	.line-row input[type="number"] { max-width: 7rem; }
	.line-row button { padding: 0.25rem 0.5rem; cursor: pointer; }
	.line-total { min-width: 6rem; text-align: right; font-weight: 600; }
	.line-row.ro { display: flex; gap: 0.5rem; padding: 0.25rem 0; border-bottom: 1px solid var(--border-light); }
	.line-row.ro span { flex: 1; }
	.actions { display: flex; gap: 0.75rem; margin-top: 1rem; }
	.actions button { padding: 0.5rem 1rem; cursor: pointer; border-radius: var(--radius-sm); }
	.btn-primary { background: var(--primary); color: var(--text-white); border: none; }
	.badge-info { background: #fef9e7; border: 1px solid #f9e79f; padding: 0.5rem; border-radius: var(--radius-sm); color: #7d6608; }
	.summary-card {
		background: var(--bg-card);
		border: 2px solid var(--primary);
		border-radius: var(--radius-md);
		padding: 1.5rem;
		position: sticky;
		top: 1.5rem;
	}
	.summary-card h3 { margin: 0 0 1rem; }
	.summary-line { display: flex; justify-content: space-between; padding: 0.25rem 0; }
	.total-line { margin-top: 0.5rem; padding-top: 0.5rem; border-top: 2px solid var(--text-primary); }
	.total-amount { font-size: 1.4rem; color: var(--success); }
	hr { border: none; border-top: 1px solid #ddd; margin: 0.5rem 0; }
</style>
