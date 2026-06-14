<script lang="ts">
	import { onMount } from 'svelte';
	import { getCustomerInquiries } from '$lib/services/api';
	import type { CustomerInquiryItem } from '$lib/services/api';
	import { toast } from 'svelte-sonner';
	import { MessageSquareText, Send, X, Clock, CheckCircle, XCircle } from '@lucide/svelte';
	import Loader from '$lib/components/Loader.svelte';

	let inquiries: CustomerInquiryItem[] = $state([]);
	let loading = $state(true);
	let filter = $state('all');
	let replyModal = $state<CustomerInquiryItem | null>(null);
	let replyText = $state('');

	onMount(async () => {
		try {
			inquiries = await getCustomerInquiries();
		} catch {
			toast.error('Failed to load inquiries.');
			inquiries = [];
		} finally {
			loading = false;
		}
	});

	let filtered = $derived(
		filter === 'all' ? inquiries : inquiries.filter(i => i.status === filter)
	);

	function sendReply() {
		if (!replyText.trim() || !replyModal) return;
		replyText = '';
		replyModal = null;
	}

	const statusConfig: Record<string, { class: string; icon: any; label: string }> = {
		'open': { class: 'status-open', icon: Clock, label: 'Open' },
		'assigned': { class: 'status-assigned', icon: CheckCircle, label: 'Assigned' },
		'resolved': { class: 'status-resolved', icon: CheckCircle, label: 'Resolved' },
		'closed': { class: 'status-closed', icon: XCircle, label: 'Closed' },
	};
</script>

<div class="page-header">
	<div>
		<h1>Inquiries</h1>
		<p class="subtitle">View and manage your inquiries.</p>
	</div>
</div>

<div class="filters">
	<button class="filter-tab" class:active={filter === 'all'} onclick={() => filter = 'all'}>All ({inquiries.length})</button>
	{#each ['open', 'assigned', 'resolved', 'closed'] as s}
		<button class="filter-tab" class:active={filter === s} onclick={() => filter = s}>
			{s.charAt(0).toUpperCase() + s.slice(1)} ({inquiries.filter(i => i.status === s).length})
		</button>
	{/each}
</div>

{#if loading}
	<div class="loader"><Loader /></div>
{:else if filtered.length === 0}
	<div class="empty">No inquiries found.</div>
{:else}
	<div class="inquiry-list">
		{#each filtered as i}
			<div class="inquiry-card">
				<div class="card-header">
					<div class="card-title">
						<span class="id-badge">#{i.inquiry_id}</span>
						<span class="vehicle-name">{i.vehicle.brand} {i.vehicle.model}</span>
						<span class="status-badge {statusConfig[i.status]?.class ?? 'status-open'}">
							<svelte:component this={statusConfig[i.status]?.icon ?? Clock} size={12} />
							{statusConfig[i.status]?.label ?? i.status}
						</span>
					</div>
					<div class="card-meta">
						<span class="date">{i.created_at ? String(i.created_at).slice(0, 10) : '—'}</span>
					</div>
				</div>
				<div class="card-body">
					<p class="message">{i.message ?? 'No message.'}</p>
				</div>
				{#if i.vehicle.price}
					<div class="card-footer">
						<span class="price">{i.vehicle.price}</span>
					</div>
				{/if}
			</div>
		{/each}
	</div>
{/if}

{#if replyModal}
	<div class="modal-overlay" onclick={() => replyModal = null}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Inquiry #{replyModal.inquiry_id}</h2>
				<button class="modal-close" onclick={() => replyModal = null}><X size={20} /></button>
			</div>
			<div class="modal-body">
				<div class="vehicle-info">
					<strong>Vehicle:</strong> {replyModal.vehicle.brand} {replyModal.vehicle.model}
				</div>
				<div class="original-msg">
					<strong>Message:</strong>
					<p>{replyModal.message}</p>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={() => replyModal = null}>Close</button>
			</div>
		</div>
	</div>
{/if}

<style>
	h1 { font-size:24px; font-weight:700; color:var(--text-dark); margin:0; }
	.subtitle { font-size:14px; color:var(--text-muted); margin-top:4px; }
	.page-header { margin-bottom:20px; }
	.loader { display:grid; place-items:center; height:50vh; }
	.empty { text-align:center; padding:60px 20px; color:var(--text-muted); font-size:14px; }
	.filters { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:16px; }
	.filter-tab { padding:6px 14px; border:1px solid var(--border); border-radius:20px; background:var(--bg-card); font-size:12px; color:var(--text-dark); cursor:pointer; font-family:inherit; font-weight:500; }
	.filter-tab.active { background:var(--primary); color:var(--text-white); border-color:var(--primary); }
	.inquiry-list { display:flex; flex-direction:column; gap:12px; }
	.inquiry-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); overflow:hidden; box-shadow:var(--shadow-sm); }
	.card-header { display:flex; justify-content:space-between; align-items:flex-start; padding:14px 20px; background:var(--bg-muted); border-bottom:1px solid var(--border); }
	.card-title { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
	.id-badge { font-family:monospace; font-size:11px; color:var(--primary); font-weight:700; background:var(--primary-bg); padding:2px 8px; border-radius:var(--radius-sm); }
	.vehicle-name { font-weight:600; font-size:14px; color:var(--text-dark); }
	.status-badge { display:inline-flex; align-items:center; gap:4px; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
	.status-badge.status-open { background:#fef3c7; color:#92400e; }
	.status-badge.status-assigned { background:#e0e7ff; color:#3730a3; }
	.status-badge.status-resolved { background:#d1fae5; color:#065f46; }
	.status-badge.status-closed { background:#f3f4f6; color:#6b7280; }
	.card-meta .date { font-size:11px; color:var(--text-muted); }
	.card-body { padding:14px 20px; }
	.message { font-size:13px; color:var(--text-dark); line-height:1.5; margin:0; }
	.card-footer { padding:10px 20px; border-top:1px solid var(--border-lighter); }
	.price { font-size:13px; font-weight:600; color:var(--primary); }
	.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:100; }
	.modal { background:var(--bg-card); border-radius:var(--radius-lg); width:520px; max-width:90vw; box-shadow:var(--shadow-lg); }
	.modal-header { display:flex; justify-content:space-between; align-items:center; padding:20px 24px; border-bottom:1px solid var(--border); }
	.modal-header h2 { font-size:18px; font-weight:700; margin:0; }
	.modal-close { background:none; border:none; cursor:pointer; color:var(--text-muted); padding:4px; border-radius:var(--radius-sm); }
	.modal-close:hover { background:var(--bg-hover); }
	.modal-body { padding:20px 24px; }
	.modal-footer { padding:16px 24px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; gap:8px; }
	.btn-secondary { padding:8px 16px; border:1px solid var(--border); border-radius:var(--radius-md); background:var(--bg-card); color:var(--text-dark); font-size:14px; font-weight:500; cursor:pointer; }
	.btn-primary { display:inline-flex; align-items:center; gap:6px; padding:8px 16px; background:var(--primary); color:var(--text-white); border:none; border-radius:var(--radius-md); font-size:14px; font-weight:600; cursor:pointer; }
	.btn-primary:disabled { opacity:0.5; cursor:not-allowed; }
	.original-msg { background:var(--bg-muted); padding:12px; border-radius:var(--radius-sm); margin-top:12px; }
	.original-msg strong { font-size:12px; color:var(--text-muted); }
	.original-msg p { margin:6px 0 0; font-size:13px; color:var(--text-dark); }
	.vehicle-info { font-size:13px; color:var(--text-dark); }
</style>
