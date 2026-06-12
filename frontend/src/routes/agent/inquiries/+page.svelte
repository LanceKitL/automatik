<script lang="ts">
	import { onMount } from 'svelte';
	import { getInquiries, getAgentInquiries, resolveInquiry, convertInquiryToSale, selfAssignInquiry, sendInquiryEmail } from '$lib/services/api';
	import type { InquiryItem } from '$lib/services/api';
	import { X, DollarSign, Mail } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';

	let inquiries = $state<InquiryItem[]>([]);
	let agentInquiries = $state<InquiryItem[]>([]);
	let loading = $state(true);
	let selectedInquiry = $state<InquiryItem | null>(null);
	let actionId = $state<number | null>(null);

	let emailForm = $state<{ subject: string; body: string } | null>(null);

	let convertForm = $state<{
		selling_price: number;
		payment_type: string;
		interest_rate: number;
		term_months: number;
		down_payment: number;
	} | null>(null);

	let computedLoan = $derived(
		convertForm && convertForm.payment_type === 'installment'
			? Math.max(0, convertForm.selling_price - convertForm.down_payment)
			: 0
	);

	let dragItem = $state<InquiryItem | null>(null);
	let dragSource = $state<string | null>(null);
	let dropTarget = $state<string | null>(null);

	let openInquiries = $derived(inquiries.filter((i) => i.status === 'open'));
	let pendingInquiries = $derived(inquiries.filter((i) => i.status === 'assigned'));
	let resolvedInquiries = $derived(agentInquiries.filter((i) => i.status === 'resolved'));

	const now = new Date();
	const timestamp = now.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
		+ ' · ' + now.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });

	// on initial render, load the inquiries
	onMount(() => {
		fetchAll();
	});
    
	async function fetchAll() {
		loading = true;
		try {
			const [shared, agentData] = await Promise.all([getInquiries(), getAgentInquiries()]);
			inquiries = shared;
			agentInquiries = agentData.data;
		} catch {
			inquiries = [];
			agentInquiries = [];
		} finally {
			loading = false;
		}
	}

	async function handleSelfAssign(id: number) {
		actionId = id;
		try {
			await selfAssignInquiry(id);
			await fetchAll();
			toast.success(`Inquiry #${id} assigned to you`);
		} catch {
			toast.error('Failed to assign inquiry.');
		} finally {
			actionId = null;
		}
	}

	async function handleResolve(id: number) {
		actionId = id;
		try {
			await resolveInquiry(id);
			await fetchAll();
			toast.success(`Inquiry #${id} resolved`);
		} catch {
			toast.error('Failed to resolve inquiry.');
		} finally {
			actionId = null;
		}
	}

	async function handleSendEmail(inquiryId: number) {
		if (!emailForm) return;
		actionId = inquiryId;
		try {
			await sendInquiryEmail(inquiryId, { subject: emailForm.subject, body: emailForm.body });
			selectedInquiry = null;
			emailForm = null;
			await fetchAll();
		} catch (e: unknown) {
			alert(e instanceof Error ? e.message : 'Failed to send email.');
		} finally {
			actionId = null;
		}
	}

	async function handleConvertToSale(inquiryId: number) {
		if (!convertForm) return;
		actionId = inquiryId;
		try {
			const payload: Record<string, unknown> = {
				selling_price: convertForm.selling_price,
				payment_type: convertForm.payment_type,
			};
			if (convertForm.payment_type === 'installment') {
				payload.loan_amount = computedLoan;
				payload.interest_rate = convertForm.interest_rate;
				payload.term_months = convertForm.term_months;
				payload.down_payment = convertForm.down_payment;
			}
			await convertInquiryToSale(inquiryId, payload as any);
			selectedInquiry = null;
			convertForm = null;
			await fetchAll();
		} catch (e: unknown) {
			alert(e instanceof Error ? e.message : 'Failed to convert inquiry.');
		} finally {
			actionId = null;
		}
	}

	function openConvertForm(i: InquiryItem) {
		selectedInquiry = i;
		convertForm = {
			selling_price: 0,
			payment_type: 'full_payment',
			interest_rate: 6.5,
			term_months: 36,
			down_payment: 0,
		};
		emailForm = null;
	}

	function openDetail(i: InquiryItem) {
		selectedInquiry = i;
		convertForm = null;
		emailForm = null;
	}

	function closeModal() {
		selectedInquiry = null;
		convertForm = null;
		emailForm = null;
	}

	/* ── Drag and Drop ── */

	function canDrop(source: string | null, target: string): boolean {
		if (!source) return false;
		return (source === 'open' && target === 'pending') ||
			(source === 'pending' && target === 'resolved');
	}

	function handleDragStart(e: DragEvent, item: InquiryItem, source: string) {
		dragItem = item;
		dragSource = source;
		if (e.dataTransfer) {
			e.dataTransfer.effectAllowed = 'move';
			e.dataTransfer.setData('text/plain', String(item.inquiry_id));
		}
	}

	function handleDragEnd() {
		dragItem = null;
		dragSource = null;
		dropTarget = null;
	}

	function handleDragOver(e: DragEvent, target: string) {
		if (canDrop(dragSource, target)) {
			e.preventDefault();
			if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
			dropTarget = target;
		} else {
			if (e.dataTransfer) e.dataTransfer.dropEffect = 'none';
		}
	}

	function handleDragLeave(target: string) {
		if (dropTarget === target) {
			dropTarget = null;
		}
	}

	async function handleDrop(e: DragEvent, target: string) {
		e.preventDefault();
		dropTarget = null;
		if (!dragItem || !dragSource) return;
		if (dragSource === 'open' && target === 'pending') {
			await handleSelfAssign(dragItem.inquiry_id);
		} else if (dragSource === 'pending' && target === 'resolved') {
			await handleResolve(dragItem.inquiry_id);
		}
		dragItem = null;
		dragSource = null;
	}

	function statusBadgeClass(s: string): string {
		const m: Record<string, string> = {
			open: 'sb-open', assigned: 'sb-pending', resolved: 'sb-closed', closed: 'sb-closed',
		};
		return m[s] ?? 'sb-def';
	}

	function formatTime(iso: string) {
		const d = new Date(iso);
		const diff = Date.now() - d.getTime();
		const mins = Math.floor(diff / 60000);
		if (mins < 1) return 'Just now';
		if (mins < 60) return `${mins}m ago`;
		const hrs = Math.floor(mins / 60);
		if (hrs < 24) return `${hrs}h ago`;
		const days = Math.floor(hrs / 24);
		return `${days}d ago`;
	}

	function formatDate(iso: string) {
		return new Date(iso).toLocaleDateString('en-US', {
			year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
		});
	}
</script>

<div class="page">
	<div class="top-bar">
		<div class="title-row">
			<h1>Inquiries</h1>
			<p class="kanban-hint" style="font-size: 14px;">
				Drag cards between columns to update status. Click a card to view details or convert to a sale.
			</p>
		</div>
		<span class="timestamp">{timestamp}</span>
	</div>

	{#if loading}
		<div class="loading-state"><span class="spinner"></span><p>Loading inquiries…</p></div>
	{:else}
		<div class="kanban-grid">
			<!-- Open -->
			<div class="kanban-col">
				<div class="col-header col-open">
					<span class="col-title">Open</span>
					<span class="col-count">{openInquiries.length}</span>
				</div>
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<div
					class="col-body"
					class:drag-over={dropTarget === 'open'}
					ondragover={(e) => handleDragOver(e, 'open')}
					ondragleave={() => handleDragLeave('open')}
					ondrop={(e) => handleDrop(e, 'open')}
					role="region"
				>
					{#if openInquiries.length === 0}
						<p class="empty-col">No open inquiries.</p>
					{:else}
						{#each openInquiries as i (i.inquiry_id)}
							<!-- svelte-ignore a11y_no_static_element_interactions -->
							<div
								class="inq-card"
								class:dragging={dragItem?.inquiry_id === i.inquiry_id}
								draggable="true"
								onclick={() => openDetail(i)}
								onkeydown={(e) => e.key === 'Enter' && openDetail(i)}
								role="button"
								tabindex="0"
								ondragstart={(e) => handleDragStart(e, i, 'open')}
								ondragend={handleDragEnd}
							>
								<div class="inq-head">
									<span class="inq-id">#{i.inquiry_id}</span>
									<span class="inq-status {statusBadgeClass(i.status)}"><span class="sdot"></span>{i.status}</span>
								</div>
								<div class="inq-customer">{i.contacts.name ?? 'Unknown'}</div>
								<div class="inq-vehicle">{i.vehicle.brand} {i.vehicle.model}</div>
								<div class="inq-msg">{(i.message ?? '').slice(0, 80)}{(i.message ?? '').length > 80 ? '…' : ''}</div>
								<div class="inq-footer">
									<span class="inq-time">{formatTime(i.created_at)}</span>
								</div>
							</div>
						{/each}
					{/if}
				</div>
			</div>

			<!-- Pending -->
			<div class="kanban-col">
				<div class="col-header col-pending">
					<span class="col-title">Pending</span>
					<span class="col-count">{pendingInquiries.length}</span>
				</div>
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<div
					class="col-body"
					class:drag-over={dropTarget === 'pending'}
					ondragover={(e) => handleDragOver(e, 'pending')}
					ondragleave={() => handleDragLeave('pending')}
					ondrop={(e) => handleDrop(e, 'pending')}
					role="region"
				>
					{#if pendingInquiries.length === 0}
						<p class="empty-col">No pending inquiries.</p>
					{:else}
						{#each pendingInquiries as i (i.inquiry_id)}
							<!-- svelte-ignore a11y_no_static_element_interactions -->
							<div
								class="inq-card pending-card"
								class:dragging={dragItem?.inquiry_id === i.inquiry_id}
								draggable="true"
								onclick={() => openDetail(i)}
								onkeydown={(e) => e.key === 'Enter' && openDetail(i)}
								role="button"
								tabindex="0"
								ondragstart={(e) => handleDragStart(e, i, 'pending')}
								ondragend={handleDragEnd}
							>
								<div class="inq-head">
									<span class="inq-id">#{i.inquiry_id}</span>
									<span class="inq-status {statusBadgeClass(i.status)}"><span class="sdot"></span>{i.status}</span>
								</div>
								<div class="inq-customer">{i.contacts.name ?? 'Unknown'}</div>
								<div class="inq-vehicle">{i.vehicle.brand} {i.vehicle.model}</div>
								<div class="inq-msg">{(i.message ?? '').slice(0, 80)}{(i.message ?? '').length > 80 ? '…' : ''}</div>
								<div class="inq-footer">
									<span class="inq-time">{formatTime(i.created_at)}</span>
								</div>
							</div>
						{/each}
					{/if}
				</div>
			</div>
			<!-- Resolved -->
			<div class="kanban-col">
				<div class="col-header col-completed">
					<span class="col-title">Resolved</span>
					<span class="col-count">{resolvedInquiries.length}</span>
				</div>
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<div
					class="col-body"
					class:drag-over={dropTarget === 'resolved'}
					ondragover={(e) => handleDragOver(e, 'resolved')}
					ondragleave={() => handleDragLeave('resolved')}
					ondrop={(e) => handleDrop(e, 'resolved')}
					role="region"
				>
					{#if resolvedInquiries.length === 0}
						<p class="empty-col">No resolved inquiries.</p>
					{:else}
						{#each resolvedInquiries as i (i.inquiry_id)}
							<!-- svelte-ignore a11y_no_static_element_interactions -->
							<div
								class="inq-card"
								onclick={() => openDetail(i)}
								onkeydown={(e) => e.key === 'Enter' && openDetail(i)}
								role="button"
								tabindex="0"
							>
								<div class="inq-head">
									<span class="inq-id">#{i.inquiry_id}</span>
									<span class="inq-status {statusBadgeClass(i.status)}"><span class="sdot"></span>{i.status}</span>
								</div>
								<div class="inq-customer">{i.contacts.name ?? 'Unknown'}</div>
								<div class="inq-vehicle">{i.vehicle.brand} {i.vehicle.model}</div>
								<div class="inq-msg">{(i.message ?? '').slice(0, 80)}{(i.message ?? '').length > 80 ? '…' : ''}</div>
								<div class="inq-footer">
									<span class="inq-time">{formatTime(i.created_at)}</span>
								</div>
							</div>
						{/each}
					{/if}
				</div>
			</div>
		</div>
	{/if}
</div>

<!-- Detail modal -->
{#if selectedInquiry}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="modal-overlay" onclick={closeModal} role="presentation" />
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
		<div class="modal-head">
			<h2>Inquiry #{selectedInquiry.inquiry_id}</h2>
			<button class="modal-close" onclick={closeModal}><X size={16} /></button>
		</div>
		<div class="modal-body">
			<div class="detail-section">
				<span class="detail-label">Status</span>
				<span class="inq-status {statusBadgeClass(selectedInquiry.status)}"><span class="sdot"></span>{selectedInquiry.status}</span>
			</div>
			<div class="detail-section">
				<span class="detail-label">Customer</span>
				<div class="detail-value">{selectedInquiry.contacts.name ?? 'Unknown'}</div>
			</div>
			{#if selectedInquiry.contacts.email}
				<div class="detail-section">
					<span class="detail-label">Email</span>
					<div class="detail-value">{selectedInquiry.contacts.email}</div>
				</div>
			{/if}
			{#if selectedInquiry.contacts.number}
				<div class="detail-section">
					<span class="detail-label">Phone</span>
					<div class="detail-value">{selectedInquiry.contacts.number}</div>
				</div>
			{/if}
			<div class="detail-section">
				<span class="detail-label">Vehicle</span>
				<div class="detail-value">{selectedInquiry.vehicle.brand} {selectedInquiry.vehicle.model}</div>
				<div class="detail-sub">{selectedInquiry.vehicle.price}</div>
			</div>
			<div class="detail-section">
				<span class="detail-label">Message</span>
				<div class="detail-msg">{selectedInquiry.message}</div>
			</div>
			<div class="detail-section">
				<span class="detail-label">Submitted</span>
				<div class="detail-value">{formatDate(selectedInquiry.created_at)}</div>
			</div>
			<div class="detail-section">
				<span class="detail-label">User Type</span>
				<div class="detail-value">{selectedInquiry.user_type}</div>
			</div>

		<!-- Send Email / Convert to Sale -->
		{#if selectedInquiry.status === 'assigned'}
			<hr class="modal-divider" />
			{#if emailForm}
				<div class="email-section">
					<h3 class="email-title">Send Email</h3>
					<div class="form-row">
						<label class="form-label">To</label>
						<div class="form-static">{selectedInquiry.contacts.email ?? 'No email'}</div>
					</div>
					<div class="form-row">
						<label class="form-label">Subject</label>
						<input type="text" class="form-input" bind:value={emailForm.subject} placeholder="Enter subject" />
					</div>
					<div class="form-row">
						<label class="form-label">Message</label>
						<textarea class="form-textarea" bind:value={emailForm.body} rows="4" placeholder="Write your message..."></textarea>
					</div>
					<div class="form-actions">
						<button class="btn-cancel" onclick={() => emailForm = null}>Cancel</button>
						<button
							class="btn-submit"
							onclick={() => handleSendEmail(selectedInquiry.inquiry_id)}
							disabled={actionId === selectedInquiry.inquiry_id || !emailForm.subject || !emailForm.body}
						>
							{actionId === selectedInquiry.inquiry_id ? 'Sending…' : 'Send Email'}
						</button>
					</div>
				</div>
			{:else if convertForm}
				<div class="convert-section">
					<h3 class="convert-title">Convert to Sale</h3>
					<div class="form-row">
						<label class="form-label">Selling Price (₱)</label>
						<input type="number" class="form-input" bind:value={convertForm.selling_price} min="0" step="0.01" />
					</div>
					<div class="form-row">
						<label class="form-label">Payment Type</label>
						<select class="form-input" bind:value={convertForm.payment_type}>
							<option value="full_payment">Full Payment</option>
							<option value="installment">Installment</option>
						</select>
					</div>
					{#if convertForm.payment_type === 'installment'}
						<div class="form-row">
							<label class="form-label">Loan Amount (auto)</label>
							<div class="form-static">₱{computedLoan.toLocaleString('en-PH', { minimumFractionDigits: 2 })}</div>
						</div>
						<div class="form-row">
							<label class="form-label">Interest Rate (%)</label>
							<input type="number" class="form-input" bind:value={convertForm.interest_rate} min="0" max="30" step="0.1" />
						</div>
						<div class="form-row">
							<label class="form-label">Term (months)</label>
							<input type="number" class="form-input" bind:value={convertForm.term_months} min="6" max="60" step="1" />
						</div>
						<div class="form-row">
							<label class="form-label">Down Payment (₱)</label>
							<input type="number" class="form-input" bind:value={convertForm.down_payment} min="0" step="0.01" />
						</div>
					{/if}
					<div class="form-actions">
						<button class="btn-cancel" onclick={closeModal}>Cancel</button>
						<button
							class="btn-submit"
							onclick={() => handleConvertToSale(selectedInquiry.inquiry_id)}
							disabled={actionId === selectedInquiry.inquiry_id || !convertForm.selling_price}
						>
							{actionId === selectedInquiry.inquiry_id ? 'Creating…' : 'Create Sale'}
						</button>
					</div>
				</div>
			{:else}
				<div class="action-row">
					<button class="email-trigger-btn" onclick={() => { emailForm = { subject: '', body: '' }; convertForm = null; }}>
						<Mail size={14} />
						Send Email
					</button>
					<button class="convert-trigger-btn" onclick={() => openConvertForm(selectedInquiry)}>
						<DollarSign size={14} />
						Convert to Sale
					</button>
				</div>
			{/if}
		{/if}
		</div>
	</div>
{/if}

<style>
	.page { font-family: var(--font-sans); padding: 1.5rem 1.5rem; max-width: 1500px; margin: 0 auto; flex: 1; min-height: 0; overflow: hidden; box-sizing: border-box; display: flex; flex-direction: column; }

	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; flex-shrink: 0; }
	.title-row { display: flex; align-items: baseline; gap: 12px; flex-direction: column;}
	h1 { font-size: 24px; font-weight: 700; color: var(--text-primary);  margin: 0; }
	.kanban-hint { font-size: 11px; color: var(--text-muted); margin: 0; }
	.timestamp { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); background: var(--bg-muted); border: 0.5px solid var(--border); padding: 4px 12px; border-radius: 20px; }

	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }

	.kanban-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 14px;
		flex: 1;
		min-height: 0;
		overflow: hidden;
	}

	.kanban-col {
		display: flex;
		flex-direction: column;
		background: var(--bg-card);
		border: 0.5px solid var(--border);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.col-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 14px;
		border-bottom: 0.5px solid var(--chart-grid);
		flex-shrink: 0;
	}
	.col-open { background: var(--info-bg); }
	.col-pending { background: var(--warning-bg); }
	.col-completed { background: var(--success-bg); }
	.col-title { font-size: 13px; font-weight: 700; color: var(--text-primary); text-transform: uppercase; letter-spacing: 0.4px; }
	.col-count { font-family: var(--font-mono); font-size: 12px; font-weight: 600; padding: 1px 8px; border-radius: 8px; background: rgba(0,0,0,0.06); color: var(--text-primary); }

	.col-body {
		flex: 1;
		overflow-y: auto;
		overflow-x: hidden;
		padding: 10px;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}
	.empty-col { padding: 24px 0; text-align: center; color: var(--text-muted); font-size: 12px; }

	.inq-card {
		display: flex;
		flex-direction: column;
		gap: 4px;
		padding: 10px 12px;
		background: var(--bg-card);
		border: 0.5px solid var(--border);
		border-radius: var(--radius-md);
		cursor: pointer;
		font-family: inherit;
		font-size: inherit;
		text-align: left;
		transition: box-shadow 0.15s;
		width: 100%;
		box-sizing: border-box;
	}
	.inq-card:hover {
		box-shadow: var(--shadow-sm);
		border-color: #d1d5db;
	}
	.inq-card[draggable="true"] { cursor: grab; }
	.inq-card[draggable="true"]:active { cursor: grabbing; }
	.inq-card.dragging { opacity: 0.3; }

	.pending-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 16px rgba(0,0,0,0.10);
		border-color: var(--primary);
	}

	.col-body.drag-over {
		background: var(--primary-bg);
		border-color: var(--primary-light);
		border-style: dashed;
	}

	.inq-head { display: flex; align-items: center; justify-content: space-between; gap: 6px; }
	.inq-id { font-family: var(--font-mono); font-size: 10px; color: var(--text-muted); font-weight: 500; }
	.inq-customer { font-size: 13px; font-weight: 600; color: var(--text-primary); }
	.inq-vehicle { font-size: 11px; color: var(--text-light); }
	.inq-msg { font-size: 11px; color: var(--text-muted); line-height: 1.4; margin-top: 2px; overflow-wrap: break-word; word-break: break-word; }
	.inq-footer { display: flex; align-items: center; justify-content: space-between; margin-top: 4px; }
	.inq-time { font-size: 10px; color: var(--text-muted); font-family: var(--font-mono); }

	/* Status badges (from dashboard) */
	.inq-status { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 20px; font-size: 10px; font-weight: 600; }
	.sdot { width: 5px; height: 5px; border-radius: 50%; }
	.sb-open { background: var(--info-bg); color: var(--info-text); }
	.sb-open .sdot { background: var(--info); }
	.sb-pending { background: var(--warning-bg); color: var(--warning-text); }
	.sb-pending .sdot { background: var(--warning-dark); }
	.sb-closed { background: var(--success-bg); color: var(--success-text); }
	.sb-closed .sdot { background: var(--success-dark); }
	.sb-def { background: var(--bg-hover); color: var(--text-light); }
	.sb-def .sdot { background: #888; }

	/* Modal */
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.45);
		z-index: 1000;
	}
	.modal {
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 520px;
		max-width: calc(100vw - 2rem);
		max-height: 85vh;
		background: var(--bg-card);
		border: 0.5px solid var(--border);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg);
		z-index: 1010;
		display: flex;
		flex-direction: column;
		overflow-y: auto;
		font-family: var(--font-sans);
	}
	.modal-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.25rem 1.5rem;
		border-bottom: 0.5px solid var(--border);
		flex-shrink: 0;
	}
	.modal-head h2 { font-size: 16px; font-weight: 700; color: var(--text-primary); margin: 0; }
	.modal-close { background: none; border: none; cursor: pointer; color: var(--text-muted); padding: 4px; border-radius: 4px; }
	.modal-close:hover { color: var(--text-primary); background: var(--bg-hover); }
	.modal-body { padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 12px; }
	.detail-section { display: flex; flex-direction: column; gap: 2px; }
	.detail-label { font-size: 10px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.4px; }
	.detail-value { font-size: 13px; color: var(--text-primary); font-weight: 500; }
	.detail-sub { font-size: 12px; color: var(--text-light); }
	.detail-msg { font-size: 13px; color: var(--text-light); line-height: 1.5; background: var(--bg-muted); padding: 10px 12px; border-radius: 8px; border: 0.5px solid var(--chart-grid); }
	.modal-divider { border: none; border-top: 0.5px solid var(--border); margin: 4px 0; }

	.action-row { display: flex; gap: 8px; }

	.email-trigger-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 6px;
		flex: 1;
		padding: 10px;
		border: 0.5px solid #d1d5db;
		border-radius: 8px;
		background: var(--bg-card);
		color: var(--text-primary);
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
		transition: background 0.15s;
	}
	.email-trigger-btn:hover { background: var(--bg-hover); }

	.email-section { display: flex; flex-direction: column; gap: 10px; }
	.email-title { font-size: 14px; font-weight: 700; color: var(--text-primary); margin: 0; }

	.convert-trigger-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 6px;
		flex: 1;
		padding: 10px;
		border: none;
		border-radius: 8px;
		background: var(--primary);
		color: var(--accent);
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
		transition: opacity 0.15s;
	}
	.convert-trigger-btn:hover { opacity: 0.85; }

	.convert-section { display: flex; flex-direction: column; gap: 10px; }
	.convert-title { font-size: 14px; font-weight: 700; color: var(--text-primary); margin: 0; }

	.form-textarea {
		padding: 8px 10px;
		border: 0.5px solid #d1d5db;
		border-radius: var(--radius-sm);
		font-size: 13px;
		font-family: inherit;
		background: var(--bg-card);
		transition: border-color 0.15s;
		resize: vertical;
		min-height: 80px;
	}
	.form-textarea:focus { outline: none; border-color: var(--primary); }

	.form-row { display: flex; flex-direction: column; gap: 3px; }
	.form-label { font-size: 11px; font-weight: 600; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.3px; }
	.form-input {
		padding: 8px 10px;
		border: 0.5px solid #d1d5db;
		border-radius: var(--radius-sm);
		font-size: 13px;
		font-family: inherit;
		background: var(--bg-card);
		transition: border-color 0.15s;
	}
	.form-input:focus { outline: none; border-color: var(--primary); }
	.form-static {
		padding: 8px 10px;
		border: 0.5px solid var(--border);
		border-radius: var(--radius-sm);
		font-size: 13px;
		font-family: inherit;
		background: var(--bg-muted);
		color: var(--text-light);
		font-weight: 500;
	}
	.form-actions { display: flex; gap: 8px; margin-top: 4px; }
	.btn-cancel {
		flex: 1;
		padding: 9px;
		border: 0.5px solid #d1d5db;
		border-radius: var(--radius-sm);
		background: var(--bg-card);
		color: var(--text-light);
		font-size: 12px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
	}
	.btn-cancel:hover { background: var(--bg-muted); }
	.btn-submit {
		flex: 1;
		padding: 9px;
		border: none;
		border-radius: var(--radius-sm);
		background: var(--primary);
		color: var(--accent);
		font-size: 12px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
	}
	.btn-submit:hover:not(:disabled) { opacity: 0.85; }
	.btn-submit:disabled { opacity: 0.5; cursor: default; }

</style>
