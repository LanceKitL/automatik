<script lang="ts">
	import { onMount } from 'svelte';
	import { assignInquiry, closeInquiry, getAgentsList } from '$lib/services/api';
	import type { InquiryItem } from '$lib/services/api';

	let {
		show,
		inquiry,
		onclose,
		onupdated
	}: {
		show: boolean;
		inquiry: InquiryItem | null;
		onclose: () => void;
		onupdated: () => void;
	} = $props();

	let agents = $state<{ _id: number; username: string }[]>([]);
	let selectedAgentId = $state<number | null>(null);
	let actionLoading = $state(false);
	let actionError = $state('');

	$effect(() => {
		if (show && inquiry) {
			loadAgents();
			selectedAgentId = null;
			actionError = '';
		}
	});

	async function loadAgents() {
		try {
			const res = await getAgentsList();
			agents = (res.data as { _id: number; username: string }[]) ?? [];
		} catch {
			agents = [];
		}
	}

	async function handleAssign() {
		if (!inquiry || !selectedAgentId) return;
		actionLoading = true;
		actionError = '';
		try {
			await assignInquiry(inquiry.inquiry_id, selectedAgentId);
			onupdated();
		} catch (e: unknown) {
			actionError = e instanceof Error ? e.message : 'Failed to assign.';
		} finally {
			actionLoading = false;
		}
	}

	async function handleClose() {
		if (!inquiry) return;
		actionLoading = true;
		actionError = '';
		try {
			await closeInquiry(inquiry.inquiry_id);
			onupdated();
		} catch (e: unknown) {
			actionError = e instanceof Error ? e.message : 'Failed to close.';
		} finally {
			actionLoading = false;
		}
	}

	function formatDate(dateStr: string): string {
		if (!dateStr) return '—';
		const d = new Date(dateStr);
		return d.toLocaleString('en-US', {
			month: 'short', day: 'numeric', year: 'numeric',
			hour: '2-digit', minute: '2-digit'
		});
	}

	function handleOverlayClick(e: MouseEvent) {
		if (e.target === e.currentTarget) onclose();
	}
</script>

<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
{#if show && inquiry}
	<div class="overlay" onclick={handleOverlayClick} role="presentation">
		<div class="drawer" onclick={(e) => e.stopPropagation()} role="dialog">
			<div class="drawer-header">
				<h2>Inquiry #{inquiry.inquiry_id}</h2>
				<button class="close-btn" onclick={onclose}>×</button>
			</div>

			<div class="drawer-body">
				<!-- Contact Info -->
				<section class="section">
					<h3>Contact</h3>
					<div class="info-grid">
						<div class="info-row">
							<span class="label">Name</span>
							<span class="value">{inquiry.contacts.name ?? 'Guest'}</span>
						</div>
						<div class="info-row">
							<span class="label">Email</span>
							<span class="value">{inquiry.contacts.email ?? '—'}</span>
						</div>
						<div class="info-row">
							<span class="label">Phone</span>
							<span class="value">{inquiry.contacts.number ?? '—'}</span>
						</div>
						<div class="info-row">
							<span class="label">Type</span>
							<span class="value">{inquiry.user_type === 'customer' ? 'Registered Customer' : 'Guest'}</span>
						</div>
					</div>
				</section>

				<!-- Vehicle Info Card -->
				<section class="section">
					<h3>Vehicle</h3>
					<div class="vehicle-card">
						<div class="v-row">
							<span class="label">Brand</span>
							<span class="value">{inquiry.vehicle.brand}</span>
						</div>
						<div class="v-row">
							<span class="label">Model</span>
							<span class="value">{inquiry.vehicle.model}</span>
						</div>
						<div class="v-row">
							<span class="label">Price</span>
							<span class="value price">{inquiry.vehicle.price}</span>
						</div>
					</div>
				</section>

				<!-- Message -->
				<section class="section">
					<h3>Message</h3>
					<div class="message-box">
						<p class="message-text">{inquiry.message}</p>
						<span class="message-date">{formatDate(inquiry.created_at)}</span>
					</div>
				</section>

				<!-- Status -->
				<section class="section">
					<h3>Status</h3>
					<span class="badge badge-{inquiry.status}">{inquiry.status}</span>
				</section>

				<!-- Assigned Agent Info -->
				<section class="section">
					<h3>Assigned Agent</h3>
					<p class="agent-info">{inquiry.agent_name ?? 'Not assigned yet'}</p>
				</section>

				<!-- Action area -->
				<div class="actions-section">
					{#if actionError}
						<div class="action-error">{actionError}</div>
					{/if}

					{#if inquiry.status === 'open'}
						<div class="assign-block">
							<label for="agent-select">Assign to Agent</label>
							<div class="assign-row">
								<select id="agent-select" bind:value={selectedAgentId}>
									<option value={null}>— Select agent —</option>
									{#each agents as agent}
										<option value={agent._id}>{agent.username}</option>
									{/each}
								</select>
								<button
									class="btn-action btn-primary"
									onclick={handleAssign}
									disabled={actionLoading || !selectedAgentId}
								>
									{actionLoading ? 'Assigning…' : 'Assign & Open'}
								</button>
							</div>
						</div>
					{/if}

					{#if inquiry.status === 'assigned'}
						<p class="assigned-note">Assigned to <strong>{inquiry.agent_name}</strong>. Awaiting agent resolution.</p>
					{/if}

					{#if inquiry.status === 'resolved'}
						<button
							class="btn-action btn-secondary"
							onclick={handleClose}
							disabled={actionLoading}
						>
							{actionLoading ? 'Closing…' : 'Close Inquiry'}
						</button>
					{/if}

					{#if inquiry.status === 'closed'}
						<p class="closed-note">This inquiry is closed.</p>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	/* ── Overlay ────────────────────────────── */
	.overlay {
		position: fixed; inset: 0; background: rgba(0,0,0,0.35);
		z-index: 1000; display: flex; justify-content: flex-end;
	}

	/* ── Drawer panel ───────────────────────── */
	.drawer {
		width: 28rem; max-width: 95vw; height: 100vh;
		background: var(--bg-card); box-shadow: -4px 0 24px rgba(0,0,0,0.12);
		display: flex; flex-direction: column; overflow: hidden;
		animation: slideIn 0.2s ease-out;
		font-family: var(--font-sans);
	}
	@keyframes slideIn {
		from { transform: translateX(100%); }
		to { transform: translateX(0); }
	}

	.drawer-header {
		display: flex; align-items: center; justify-content: space-between;
		padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border); flex-shrink: 0;
	}
	.drawer-header h2 { margin: 0; font-size: 1.15rem; color: var(--text-primary); font-family: var(--font-sans); }
	.close-btn {
		background: none; border: none; font-size: 1.5rem; cursor: pointer;
		color: var(--text-muted); padding: 0.25rem; line-height: 1;
	}
	.close-btn:hover { color: var(--text-dark); }

	.drawer-body {
		padding: 1.25rem 1.5rem; overflow-y: auto; flex: 1;
	}

	/* ── Sections ───────────────────────────── */
	.section { margin-bottom: 1.25rem; }
	.section h3 {
		font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;
		color: var(--text-muted); margin: 0 0 0.5rem;
	}

	.info-grid { display: flex; flex-direction: column; gap: 0.35rem; }
	.info-row { display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid var(--border-lighter); }
	.label { color: var(--text-light); font-size: 0.8rem; }
	.value { font-weight: 600; font-size: 0.85rem; color: var(--text-primary); text-align: right; }

	.vehicle-card {
		background: var(--bg-muted); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 0.75rem 1rem;
	}
	.v-row { display: flex; justify-content: space-between; padding: 0.3rem 0; }
	.price { color: #059669; font-size: 1rem; }

	.message-box {
		background: var(--bg-muted); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 0.75rem 1rem;
	}
	.message-text { margin: 0 0 0.5rem; font-size: 0.9rem; line-height: 1.5; color: var(--text-dark); }
	.message-date { font-size: 0.75rem; color: var(--text-muted); }

	.agent-info { color: var(--text-dark); font-size: 0.9rem; margin: 0; }

	/* ── Status badge ───────────────────────── */
	.badge {
		display: inline-block; padding: 3px 12px; border-radius: 12px;
		font-size: 0.75rem; font-weight: 600; text-transform: capitalize;
	}
	.badge-open { background: #eef2ff; color: #4f46e5; }
	.badge-assigned { background: var(--warning-bg-light); color: var(--warning); }
	.badge-resolved { background: #ecfdf5; color: #059669; }
	.badge-closed { background: var(--bg-hover); color: var(--text-light); }

	/* ── Actions ────────────────────────────── */
	.actions-section { margin-top: 1.5rem; border-top: 1px solid var(--border); padding-top: 1.25rem; }
	.action-error {
		background: var(--danger-bg); color: var(--danger); padding: 0.5rem 0.75rem;
		border-radius: var(--radius-sm); font-size: 0.8rem; margin-bottom: 0.75rem;
	}
	.assign-block label { display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-dark); margin-bottom: 0.4rem; }
	.assign-row { display: flex; gap: 0.5rem; }
	.assign-row select { flex: 1; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: var(--radius-sm); font-size: 0.85rem; }
	.assign-row select:focus { outline: none; border-color: var(--primary-light); }

	.btn-action {
		width: 100%; padding: 0.6rem; border: none; border-radius: var(--radius-sm);
		font-size: 0.9rem; font-weight: 600; cursor: pointer; margin-bottom: 0.5rem;
	}
	.btn-action:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn-primary { background: var(--primary-light); color: var(--text-white); }
	.btn-primary:hover:not(:disabled) { background: #6b8ce8; }
	.btn-success { background: #6de0b0; color: var(--text-primary); }
	.btn-success:hover:not(:disabled) { background: #5dcca0; }
	.btn-secondary { background: var(--border); color: var(--text-dark); }
	.btn-secondary:hover:not(:disabled) { background: #d1d5db; }
	.closed-note { text-align: center; color: var(--text-muted); font-style: italic; font-size: 0.85rem; }
	.assigned-note { text-align: center; color: var(--warning); font-size: 0.85rem; background: var(--warning-bg-light); padding: 0.5rem; border-radius: var(--radius-sm); }
</style>
