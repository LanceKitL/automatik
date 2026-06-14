<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import {
		getServiceStaffWarranty,
		reviewWarrantyClaim,
		approveWarrantyClaim,
		rejectWarrantyClaim,
		resolveWarrantyClaim
	} from '$lib/services/api';
	import { ShieldAlert, X, Check, Search, ThumbsUp, ThumbsDown } from '@lucide/svelte';

	let claims = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);
	let statusFilter = $state('all');
	let searchQuery = $state('');

	let rejectingId = $state<number | null>(null);
	let resolutionText = $state('');
	let loadingAction = $state(false);

	const statuses = ['all', 'submitted', 'under_review', 'approved', 'rejected'];

	onMount(loadData);

	async function loadData() {
		loading = true;
		try {
			const res = await getServiceStaffWarranty();
			claims = res.data as Record<string, unknown>[];
		} catch {
			toast.error('Failed to load warranty claims.');
		} finally {
			loading = false;
		}
	}

	let displayClaims = $derived.by(() => {
		let list = claims.filter(c => c.status !== 'resolved' && c.status !== 'rejected');
		if (statusFilter !== 'all') list = list.filter(c => (c.status as string) === statusFilter);
		if (searchQuery) {
			const q = searchQuery.toLowerCase();
			list = list.filter(c =>
				String(c.claim_id).includes(q) ||
				String(c.customer_name ?? '').toLowerCase().includes(q) ||
				String(c.brand ?? '').toLowerCase().includes(q) ||
				String(c.model ?? '').toLowerCase().includes(q)
			);
		}
		return list;
	});

	let totalCount = $derived(claims.length);
	let reviewCount = $derived(claims.filter(c => c.status === 'under_review').length);
	let approvedCount = $derived(claims.filter(c => c.status === 'approved').length);

	function statusClass(status: string | null | undefined): string {
		if (!status) return 's-default';
		const s = status.toLowerCase();
		if (s === 'submitted') return 's-pending';
		if (s === 'under_review' || s === 'review') return 's-review';
		if (s === 'approved') return 's-confirmed';
		if (s === 'rejected') return 's-cancelled';
		if (s === 'resolved') return 's-completed';
		return 's-default';
	}

	function typeClass(t: string | null | undefined): string {
		if (!t) return 'badge-default';
		const v = t.toLowerCase();
		if (v === 'repair') return 'badge-repair';
		if (v === 'replacement') return 'badge-maintenance';
		if (v === 'refund') return 'badge-test-drive';
		return 'badge-default';
	}

	function formatId(id: number): string {
		return `WC-${String(id).padStart(5, '0')}`;
	}

	function formatDate(d: unknown): string {
		if (!d) return '—';
		return String(d).slice(0, 10);
	}

	async function handleReview(id: number) {
		loadingAction = true;
		try {
			await reviewWarrantyClaim(id);
			toast.success(`Claim ${formatId(id)} moved to under review.`);
			await loadData();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to review claim.');
		} finally {
			loadingAction = false;
		}
	}

	async function handleApprove(id: number) {
		loadingAction = true;
		try {
			await approveWarrantyClaim(id);
			toast.success(`Claim ${formatId(id)} approved.`);
			await loadData();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to approve claim.');
		} finally {
			loadingAction = false;
		}
	}

	async function handleReject() {
		if (rejectingId === null) return;
		if (!resolutionText.trim()) {
			toast.error('Please provide a resolution note.');
			return;
		}
		loadingAction = true;
		try {
			await rejectWarrantyClaim(rejectingId, resolutionText.trim());
			toast.success(`Claim ${formatId(rejectingId)} rejected.`);
			rejectingId = null;
			resolutionText = '';
			await loadData();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to reject claim.');
		} finally {
			loadingAction = false;
		}
	}

	async function handleResolve(id: number) {
		loadingAction = true;
		try {
			await resolveWarrantyClaim(id);
			toast.success(`Claim ${formatId(id)} resolved.`);
			await loadData();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to resolve claim.');
		} finally {
			loadingAction = false;
		}
	}
</script>

<div class="dash">
	<div class="top-bar">
		<div class="logo-row">
			<h1>Warranty Claims</h1>
			<p class="subtitle">Monitor and track customers repair booking.</p>
		</div>
	</div>

	<div class="cards">
		<div class="stat-card c-total">
			<div class="stat-value">{totalCount}</div>
			<div class="stat-label">Total Claims</div>
		</div>
		<div class="stat-card c-review">
			<div class="stat-value">{reviewCount}</div>
			<div class="stat-label">Under Review</div>
		</div>
		<div class="stat-card c-approved">
			<div class="stat-value">{approvedCount}</div>
			<div class="stat-label">Approved</div>
		</div>
	</div>

	<div class="toolbar">
		<div class="status-tabs">
			{#each statuses as s}
				<button class:active={statusFilter === s} onclick={() => statusFilter = s}>
					{s === 'all' ? 'All' : s.replace(/_/g, ' ')}
				</button>
			{/each}
		</div>
		<div class="search-wrap">
			<Search size={14} />
			<input bind:value={searchQuery} placeholder="Search ID, customer, vehicle…" />
		</div>
	</div>

	{#if loading}
		<div class="loading-state"><div class="spinner"></div><span>Loading warranty claims…</span></div>
	{:else if displayClaims.length === 0}
		<div class="empty-state">
			<ShieldAlert size={32} />
			<p>No warranty claims found.</p>
		</div>
	{:else}
		<div class="table-wrap">
			<table class="data-table">
				<thead>
					<tr>
						<th>Claim ID</th>
						<th>Customer</th>
						<th>Vehicle</th>
						<th>Type</th>
						<th>Status</th>
						<th>Submitted</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each displayClaims as c}
						<tr>
							<td class="id-cell">{formatId(c.claim_id as number)}</td>
							<td>{c.customer_name ?? '—'}</td>
							<td><small>{c.year ?? ''} {c.brand ?? ''} {c.model ?? ''}</small></td>
							<td>
								<span class={typeClass(c.claim_type as string)}>
									{(c.claim_type as string)?.replace(/_/g, ' ') ?? '—'}
								</span>
							</td>
							<td><span class="status-badge {statusClass(c.status as string)}">{(c.status as string)?.replace(/_/g, ' ') ?? '—'}</span></td>
							<td>{formatDate(c.submitted_at)}</td>
							<td class="actions-cell">
								{#if c.status === 'submitted'}
									<button class="btn-sm btn-primary" onclick={() => handleReview(c.claim_id as number)} disabled={loadingAction}>
										<Search size={13} /> Review
									</button>
								{/if}
								{#if c.status === 'under_review'}
									<button class="btn-sm btn-success" onclick={() => handleApprove(c.claim_id as number)} disabled={loadingAction}>
										<ThumbsUp size={13} /> Approve
									</button>
									<button class="btn-sm btn-ghost-danger" onclick={() => { rejectingId = c.claim_id as number; resolutionText = ''; }} disabled={loadingAction}>
										<ThumbsDown size={13} /> Reject
									</button>
								{/if}
								{#if c.status === 'approved'}
									<button class="btn-sm btn-success" onclick={() => handleResolve(c.claim_id as number)} disabled={loadingAction}>
										<Check size={13} /> Resolve
									</button>
								{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<!-- Rejection Modal -->
{#if rejectingId !== null}
	<div class="modal-overlay" onclick={() => { rejectingId = null; resolutionText = ''; }}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h3><ThumbsDown size={18} /> Reject Claim {formatId(rejectingId)}</h3>
				<button class="modal-close" onclick={() => { rejectingId = null; resolutionText = ''; }}>×</button>
			</div>
			<div class="modal-body">
				<p>Provide a resolution note explaining why this claim is being rejected.</p>
				<textarea bind:value={resolutionText} rows="4" placeholder="Enter resolution note…"></textarea>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" onclick={() => { rejectingId = null; resolutionText = ''; }}>Cancel</button>
				<button class="btn-danger" onclick={handleReject}>Reject Claim</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.dash { padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; font-family: var(--font-sans); }

	.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 40vh; gap: 1rem; color: var(--text-light); }
	.spinner { width: 28px; height: 28px; border: 2.5px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin 0.7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.empty-state { text-align: center; padding: 4rem 0; color: var(--text-muted); display: flex; flex-direction: column; align-items: center; gap: 8px; }

	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
	.logo-row { display: flex; flex-direction: column; align-items: start; justify-content: start; margin-bottom: 10px;}
	.subtitle {
		font-size: 14px;
		color: var(--text-muted);
		margin-top: 4px;
	}
	h1 { font-size: 24px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; margin: 0; }

	.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 14px; margin-bottom: 1.25rem; }
	.stat-card { background: var(--bg-stat); border-radius: var(--radius-lg); padding: 1.25rem 1.4rem; position: relative; overflow: hidden; transition: transform 0.18s ease, box-shadow 0.18s ease; }
	.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.07); }
	.stat-card::before { content: ''; position: absolute; top: -12px; right: -12px; width: 70px; height: 70px; border-radius: 50%; opacity: 0.12; }
	.c-total::before { background: #6b7280; }
	.c-review::before { background: #3b82f6; }
	.c-approved::before { background: #10b981; }
	.c-resolved::before { background: #6366f1; }
	.stat-value { font-size: 30px; font-weight: 700; color: var(--text-primary); letter-spacing: -1px; line-height: 1; margin-bottom: 6px; font-variant-numeric: tabular-nums; }
	.stat-label { font-size: 11px; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }

	.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 0.75rem; }
	.search-wrap { display: flex; align-items: center; gap: 6px; background: var(--bg-card); border: 0.5px solid var(--border); border-radius: var(--radius-sm); padding: 6px 10px; }
	.search-wrap input { border: none; background: none; outline: none; font-size: 12px; color: var(--text-primary); font-family: inherit; min-width: 160px; }
	.search-wrap svg { color: var(--text-muted); flex-shrink: 0; }

	.status-tabs { display: flex; gap: 4px; flex-wrap: wrap; }
	.status-tabs button { padding: 4px 10px; border: 0.5px solid var(--border); background: var(--bg-card); border-radius: 12px; font-size: 11px; font-weight: 600; cursor: pointer; color: var(--text-muted); font-family: inherit; transition: all 0.15s; text-transform: capitalize; }
	.status-tabs button.active { background: var(--primary); color: var(--text-white); border-color: var(--primary); }
	.status-tabs button:hover:not(.active) { background: var(--bg-hover); }

	.table-wrap { background: var(--bg-card); border-radius: var(--radius-lg); border: 0.5px solid var(--border); overflow: auto; }
	.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
	.data-table th { text-align: left; padding: 10px 14px; font-weight: 600; color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); background: var(--bg-muted); white-space: nowrap; }
	.data-table td { padding: 10px 14px; border-bottom: 1px solid var(--border); color: var(--text-primary); }
	.data-table tbody tr:hover { background: var(--bg-hover); }
	.data-table tbody tr:last-child td { border-bottom: none; }
	.id-cell { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); white-space: nowrap; }
	small { color: var(--text-light); font-size: 11px; }

	.status-badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; text-transform: capitalize; white-space: nowrap; }

	.actions-cell { display: flex; gap: 4px; flex-wrap: wrap; }
	.btn-sm { display: inline-flex; align-items: center; gap: 3px; padding: 4px 8px; border-radius: var(--radius-sm); font-size: 11px; font-weight: 600; cursor: pointer; border: none; font-family: inherit; text-decoration: none; white-space: nowrap; transition: all 0.12s; }
	.btn-primary { background: var(--primary); color: var(--text-white); }
	.btn-primary:hover { opacity: 0.85; }
	.btn-success { background: #16a34a; color: #fff; }
	.btn-success:hover { background: #15803d; }
	.btn-ghost-danger { background: none; color: var(--text-muted); }
	.btn-ghost-danger:hover { background: #fee2e2; color: #dc2626; }

	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
	.modal { background: var(--bg-card); border-radius: var(--radius-lg); width: 460px; max-width: 90vw; box-shadow: var(--shadow-lg); }
	.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--border); }
	.modal-header h3 { font-size: 16px; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; }
	.modal-close { background: none; border: none; cursor: pointer; color: var(--text-muted); padding: 4px; border-radius: var(--radius-sm); font-size: 20px; }
	.modal-close:hover { background: var(--bg-hover); }
	.modal-body { padding: 20px 24px; }
	.modal-body p { margin: 0 0 8px; font-size: 14px; color: var(--text-primary); }
	.modal-body textarea { width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 13px; font-family: inherit; resize: vertical; background: var(--bg-card); color: var(--text-primary); box-sizing: border-box; }
	.modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 16px 24px; border-top: 1px solid var(--border); }
	.btn-cancel { background: none; border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; color: var(--text-muted); font-family: inherit; }
	.btn-cancel:hover { background: var(--bg-hover); }
	.btn-danger { background: #dc2626; color: #fff; border: none; border-radius: var(--radius-sm); padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; }
	.btn-danger:hover { background: #b91c1c; }
</style>
