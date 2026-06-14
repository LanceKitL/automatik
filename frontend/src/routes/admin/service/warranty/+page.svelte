<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import DataTable from '$lib/components/DataTable.svelte';
	import {
		getAdminWarrantyClaims,
		adminReviewWarrantyClaim,
		adminApproveWarrantyClaim,
		adminRejectWarrantyClaim,
		adminResolveWarrantyClaim
	} from '$lib/services/api';
	import type { ListResponse } from '$lib/services/api';
	import { Search, ShieldCheck, Clock, CheckCircle, CheckCheck, ThumbsUp, ThumbsDown, X } from '@lucide/svelte';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let claims = $state<Record<string, unknown>[]>([]);
	let searchQuery = $state('');
	let activeFilter = $state('all');

	let rejectingId = $state<number | null>(null);
	let resolutionText = $state('');
	let actionLoadingSet = $state<Set<number>>(new Set());

	const filters = ['all', 'pending', 'under_review', 'approved', 'rejected', 'resolved'] as const;

	const tableColumns = [
		{ key: 'id', label: 'ID' },
		{ key: 'customer', label: 'Customer' },
		{ key: 'vehicle', label: 'Vehicle' },
		{ key: 'sale_id', label: 'Sale ID' },
		{ key: 'type', label: 'Type' },
		{ key: 'description', label: 'Description' },
		{ key: 'status', label: 'Status' },
		{ key: 'submitted', label: 'Submitted' },
		{ key: 'actions', label: 'Actions' }
	];

	onMount(loadClaims);

	async function loadClaims() {
		loading = true;
		error = null;
		try {
			const res = await getAdminWarrantyClaims();
			claims = (res as ListResponse).data as Record<string, unknown>[];
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	let stats = $derived({
		total: claims.length,
		pending: claims.filter((c) => c.status === 'pending').length,
		under_review: claims.filter((c) => c.status === 'under_review').length,
		approved: claims.filter((c) => c.status === 'approved').length,
		resolved: claims.filter((c) => c.status === 'resolved').length
	});

	let filteredClaims = $derived.by(() => {
		let list = claims;
		if (activeFilter !== 'all') {
			list = list.filter((c) => (c.status as string) === activeFilter);
		}
		if (searchQuery.trim()) {
			const q = searchQuery.toLowerCase();
			list = list.filter(
				(c) =>
					String(c.customer_name ?? '').toLowerCase().includes(q) ||
					String(c.brand ?? '').toLowerCase().includes(q) ||
					String(c.model ?? '').toLowerCase().includes(q) ||
					String(c.claim_type ?? '').toLowerCase().includes(q) ||
					String(c.claim_id).includes(q)
			);
		}
		const priorityStatuses = new Set(['pending', 'under_review']);
		return [...list].sort((a, b) => {
			const aPrio = priorityStatuses.has(a.status as string);
			const bPrio = priorityStatuses.has(b.status as string);
			if (aPrio && !bPrio) return -1;
			if (!aPrio && bPrio) return 1;
			const aDate = new Date(a.submitted_at as string).getTime();
			const bDate = new Date(b.submitted_at as string).getTime();
			return aPrio ? aDate - bDate : bDate - aDate;
		});
	});

	function formatDate(d: unknown): string {
		if (!d) return '—';
		return new Date(d as string).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}

	function formatId(id: number): string {
		return `WC-${String(id).padStart(5, '0')}`;
	}

	function truncate(text: string, max = 50): string {
		if (!text) return '—';
		return text.length > max ? text.slice(0, max) + '…' : text;
	}

	function filterLabel(f: string): string {
		return f === 'all' ? 'All' : f.replace(/_/g, ' ');
	}

	function isActionLoading(id: number): boolean {
		return actionLoadingSet.has(id);
	}

	async function handleReview(id: number) {
		actionLoadingSet.add(id);
		try {
			await adminReviewWarrantyClaim(id);
			toast.success(`Claim moved to under review.`);
			await loadClaims();
		} catch (e) {
			toast.error((e as Error).message || 'Failed to review claim.');
		} finally {
			actionLoadingSet.delete(id);
		}
	}

	async function handleApprove(id: number) {
		actionLoadingSet.add(id);
		try {
			await adminApproveWarrantyClaim(id);
			toast.success(`Claim approved.`);
			await loadClaims();
		} catch (e) {
			toast.error((e as Error).message || 'Failed to approve claim.');
		} finally {
			actionLoadingSet.delete(id);
		}
	}

	async function handleReject() {
		if (rejectingId === null) return;
		if (!resolutionText.trim()) {
			toast.error('Please provide a resolution note.');
			return;
		}
		const id = rejectingId;
		actionLoadingSet.add(id);
		try {
			await adminRejectWarrantyClaim(id, resolutionText.trim());
			toast.success(`Claim rejected.`);
			rejectingId = null;
			resolutionText = '';
			await loadClaims();
		} catch (e) {
			toast.error((e as Error).message || 'Failed to reject claim.');
		} finally {
			actionLoadingSet.delete(id);
		}
	}

	async function handleResolve(id: number) {
		actionLoadingSet.add(id);
		try {
			await adminResolveWarrantyClaim(id);
			toast.success(`Claim resolved.`);
			await loadClaims();
		} catch (e) {
			toast.error((e as Error).message || 'Failed to resolve claim.');
		} finally {
			actionLoadingSet.delete(id);
		}
	}

	function openRejectModal(id: number) {
		rejectingId = id;
		resolutionText = '';
	}

	function closeRejectModal() {
		rejectingId = null;
		resolutionText = '';
	}
</script>

<div class="page">
	<!-- Top bar -->
	<div class="top-bar">
		<div class="title-row">
			<div>
				<h1>Warranty Claims</h1>
				<p class="title-subtitle">Review and process warranty claims</p>
			</div>
		</div>
		<div class="toolbar">
			<div class="search-wrap">
				<Search class="search-icon" size={14} />
				<input
					type="text"
					class="search-input"
					placeholder="Search by customer, vehicle, type&hellip;"
					bind:value={searchQuery}
				/>
			</div>
		</div>
	</div>

	<!-- Stats row -->
	<div class="stats-row">
		<div class="mini-stat s-total">
			<ShieldCheck size={18} />
			<div>
				<span class="mini-val">{stats.total}</span>
				<span class="mini-lbl">Total</span>
			</div>
		</div>
		<div class="mini-stat s-pending">
			<Clock size={18} />
			<div>
				<span class="mini-val">{stats.pending}</span>
				<span class="mini-lbl">Pending</span>
			</div>
		</div>
		<div class="mini-stat s-review">
			<Search size={18} />
			<div>
				<span class="mini-val">{stats.under_review}</span>
				<span class="mini-lbl">Under Review</span>
			</div>
		</div>
		<div class="mini-stat s-approved">
			<CheckCircle size={18} />
			<div>
				<span class="mini-val">{stats.approved}</span>
				<span class="mini-lbl">Approved</span>
			</div>
		</div>
		<div class="mini-stat s-resolved">
			<CheckCheck size={18} />
			<div>
				<span class="mini-val">{stats.resolved}</span>
				<span class="mini-lbl">Resolved</span>
			</div>
		</div>
	</div>

	<!-- Filter pills -->
	<div class="filter-row">
		{#each filters as f}
			<button
				class="filter-btn"
				class:active={activeFilter === f}
				onclick={() => (activeFilter = f)}
			>
				{filterLabel(f)}
			</button>
		{/each}
	</div>

	<!-- Loading / Error / Empty / Table -->
	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading warranty claims&hellip;</span>
		</div>
	{:else if error}
		<div class="error-msg">{error}</div>
	{:else if filteredClaims.length === 0}
		<div class="empty-state">No warranty claims found.</div>
	{:else}
		<DataTable columns={tableColumns}>
			{#each filteredClaims as c (c.claim_id)}
				<tr>
					<td><span class="cell-id">{formatId(c.claim_id as number)}</span></td>
					<td class="cell-name">{c.customer_name as string ?? '—'}</td>
					<td class="cell-vehicle">{c.brand as string ?? ''} {c.model as string ?? ''}</td>
					<td><span class="cell-sale">#{c.sale_id as number}</span></td>
					<td>
						<span class="type-badge">{(c.claim_type as string)?.replace(/_/g, ' ') ?? '—'}</span>
					</td>
					<td class="cell-desc" title={(c.description as string) ?? ''}>
						{truncate(c.description as string)}
					</td>
					<td>
						<span class="badge badge-{c.status as string}">
							{(c.status as string)?.replace(/_/g, ' ') ?? '—'}
						</span>
					</td>
					<td class="cell-date">{formatDate(c.submitted_at)}</td>
					<td class="actions-cell">
						{#if (c.status as string) === 'pending'}
							<button
								class="action-btn btn-review"
								disabled={isActionLoading(c.claim_id as number)}
								onclick={() => handleReview(c.claim_id as number)}
							>
								<Search size={13} /> Review
							</button>
						{/if}
						{#if (c.status as string) === 'under_review'}
							<button
								class="action-btn btn-approve"
								disabled={isActionLoading(c.claim_id as number)}
								onclick={() => handleApprove(c.claim_id as number)}
							>
								<ThumbsUp size={13} /> Approve
							</button>
							<button
								class="action-btn btn-reject"
								disabled={isActionLoading(c.claim_id as number)}
								onclick={() => openRejectModal(c.claim_id as number)}
							>
								<ThumbsDown size={13} /> Reject
							</button>
						{/if}
						{#if (c.status as string) === 'approved'}
							<button
								class="action-btn btn-resolve"
								disabled={isActionLoading(c.claim_id as number)}
								onclick={() => handleResolve(c.claim_id as number)}
							>
								<CheckCheck size={13} /> Resolve
							</button>
						{/if}
					</td>
				</tr>
			{/each}
		</DataTable>
	{/if}
</div>

<!-- Rejection Modal -->
{#if rejectingId !== null}
	<div class="modal-overlay" onclick={closeRejectModal}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h3><ThumbsDown size={18} /> Reject Claim {formatId(rejectingId)}</h3>
				<button class="modal-close" onclick={closeRejectModal}>
					<X size={16} />
				</button>
			</div>
			<div class="modal-body">
				<p>Provide a resolution note explaining why this claim is being rejected.</p>
				<textarea
					bind:value={resolutionText}
					rows="4"
					placeholder="Enter resolution note&hellip;"
				></textarea>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" onclick={closeRejectModal}>Cancel</button>
				<button
					class="btn-danger"
					disabled={isActionLoading(rejectingId)}
					onclick={handleReject}
				>
					Confirm Reject
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

	.page { font-family: 'Syne', sans-serif; padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

	/* Top bar */
	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; align-items: center; gap: 10px; }
	.title-subtitle { font-size: 13px; color: #9ca3af; margin: 2px 0 0; font-weight: 400; }
	h1 { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; margin: 0; }
	.toolbar { display: flex; align-items: center; gap: 10px; }
	.search-wrap { position: relative; }
	.search-wrap :global(.search-icon) { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; pointer-events: none; }
	.search-input { height: 34px; padding: 0 12px 0 32px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; color: #1a1a2e; background: #f9fafb; outline: none; width: 220px; }
	.search-input:focus { border-color: #7c9df7; background: #fff; }

	/* Mini stats */
	.stats-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 1.25rem; }
	.mini-stat { background: #f8f7f4; border-radius: 10px; padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
	.s-total :global(svg) { color: #1a1a2e; flex-shrink: 0; }
	.s-pending :global(svg) { color: #b45309; flex-shrink: 0; }
	.s-review :global(svg) { color: #3b82f6; flex-shrink: 0; }
	.s-approved :global(svg) { color: #059669; flex-shrink: 0; }
	.s-resolved :global(svg) { color: #6b7280; flex-shrink: 0; }
	.mini-stat div { display: flex; flex-direction: column; }
	.mini-val { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; line-height: 1; }
	.mini-lbl { font-size: 10px; font-weight: 500; color: #9ca3af; letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

	/* Filter pills */
	.filter-row { display: flex; gap: 6px; margin-bottom: 1rem; flex-wrap: wrap; }
	.filter-btn { height: 28px; padding: 0 12px; border: 0.5px solid #e5e7eb; border-radius: 20px; background: #f9fafb; font-family: 'Syne', sans-serif; font-size: 11px; color: #6b7280; cursor: pointer; transition: .15s; text-transform: capitalize; }
	.filter-btn.active { background: #1a1a2e; color: #e8c97e; border-color: #1a1a2e; }

	/* Loading & Error */
	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: #9ca3af; font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid #e5e7eb; border-top-color: #1a1a2e; border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.error-msg { color: #a32d2d; font-size: 13px; padding: 1rem; background: #fcebeb; border-radius: 8px; margin-bottom: 1rem; }
	.empty-state { text-align: center; padding: 2.5rem; color: #9ca3af; font-size: 13px; }

	/* Table cells */
	.cell-id { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #7c9df7; }
	.cell-name { font-size: 13px; font-weight: 600; color: #1a1a2e; }
	.cell-vehicle { font-size: 12px; color: #374151; }
	.cell-sale { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 500; color: #6b7280; }
	.cell-desc { font-size: 12px; color: #374151; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.cell-date { font-size: 12px; color: #6b7280; white-space: nowrap; }

	/* Type badge */
	.type-badge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; color: #6b7280; background: #f3f4f6; text-transform: capitalize; letter-spacing: 0.3px; }

	/* Status badges */
	.badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
	.badge-pending { background: #fffbeb; color: #b45309; }
	.badge-under_review { background: #eef2ff; color: #4f46e5; }
	.badge-approved { background: #ecfdf5; color: #059669; }
	.badge-rejected { background: #fef2f2; color: #ef4444; }
	.badge-resolved { background: #f3f4f6; color: #6b7280; }

	/* Actions */
	.actions-cell { display: flex; gap: 4px; flex-wrap: nowrap; }
	.action-btn { display: inline-flex; align-items: center; gap: 3px; padding: 4px 8px; border-radius: 6px; font-size: 10px; font-weight: 600; cursor: pointer; border: none; font-family: 'Syne', sans-serif; white-space: nowrap; transition: all .12s; }
	.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn-review { background: #eef2ff; color: #4f46e5; }
	.btn-review:hover:not(:disabled) { background: #dde4ff; }
	.btn-approve { background: #ecfdf5; color: #059669; }
	.btn-approve:hover:not(:disabled) { background: #d1fae5; }
	.btn-reject { background: #fef2f2; color: #ef4444; }
	.btn-reject:hover:not(:disabled) { background: #fee2e2; }
	.btn-resolve { background: #f3f4f6; color: #374151; }
	.btn-resolve:hover:not(:disabled) { background: #e5e7eb; }

	/* Modal */
	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
	.modal { background: #fff; border-radius: 12px; width: 460px; max-width: 90vw; box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
	.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #e5e7eb; }
	.modal-header h3 { font-size: 16px; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; color: #1a1a2e; }
	.modal-close { background: none; border: none; cursor: pointer; color: #9ca3af; padding: 4px; border-radius: 6px; }
	.modal-close:hover { background: #f3f4f6; }
	.modal-body { padding: 20px 24px; }
	.modal-body p { margin: 0 0 8px; font-size: 14px; color: #1a1a2e; }
	.modal-body textarea { width: 100%; padding: 10px 12px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 13px; font-family: 'Syne', sans-serif; resize: vertical; background: #fff; color: #1a1a2e; box-sizing: border-box; outline: none; }
	.modal-body textarea:focus { border-color: #7c9df7; }
	.modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 16px 24px; border-top: 1px solid #e5e7eb; }
	.btn-cancel { background: none; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; color: #6b7280; font-family: 'Syne', sans-serif; }
	.btn-cancel:hover { background: #f3f4f6; }
	.btn-danger { background: #dc2626; color: #fff; border: none; border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Syne', sans-serif; }
	.btn-danger:hover:not(:disabled) { background: #b91c1c; }
	.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

	@media (max-width: 640px) {
		.stats-row { grid-template-columns: 1fr 1fr; }
		.top-bar { flex-direction: column; align-items: flex-start; }
	}
</style>
