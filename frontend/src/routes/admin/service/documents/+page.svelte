<script lang="ts">
	import { onMount } from 'svelte';
	import { PUBLIC_API } from '$env/static/public';
	import DataTable from '$lib/components/DataTable.svelte';
	import {
		getAdminDocuments,
		getAdminSales,
		createDocument,
		updateDocument,
		deleteDocument,
		uploadDocumentFile,
		type ListResponse
	} from '$lib/services/api';
	import { Search, Plus, FileText, ExternalLink, Pencil, Trash2, X } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<Record<string, unknown>[]>([]);
	let sales = $state<Record<string, unknown>[]>([]);
	let search = $state('');
	let activeFilter = $state('all');

	let showNewModal = $state(false);
	let showEditModal = $state(false);
	let showDeleteModal = $state(false);
	let editTarget = $state<Record<string, unknown> | null>(null);
	let deleteTarget = $state<Record<string, unknown> | null>(null);
	let submitting = $state(false);

	let formSaleId = $state<number | ''>('');
	let formDocType = $state('OR');
	let formFileUrl = $state('');
	let formIsAccessible = $state(true);
	let fileUploading = $state(false);
	let uploadedFileName = $state('');

	const DOC_TYPE_LABELS: Record<string, string> = {
		OR: 'OR',
		CR: 'CR',
		warranty_cert: 'Warranty Cert',
		amortization_schedule: 'Amortization Schedule',
		sales_contract: 'Sales Contract',
		other: 'Other',
	};

	const DOC_TYPES = Object.keys(DOC_TYPE_LABELS);

	const columns = [
		{ key: 'document_id', label: 'ID' },
		{ key: 'sale_id', label: 'Sale' },
		{ key: 'document_type', label: 'Type' },
		{ key: 'file_url', label: 'File' },
		{ key: 'created_at', label: 'Uploaded' },
		{ key: 'actions', label: 'Actions' },
	];

	let stats = $derived({
		total: rows.length,
		or: rows.filter(r => r.document_type === 'OR').length,
		cr: rows.filter(r => r.document_type === 'CR').length,
		sales_contract: rows.filter(r => r.document_type === 'sales_contract').length,
		other: rows.filter(r => !['OR', 'CR', 'sales_contract'].includes(r.document_type as string)).length,
	});

	let filteredRows = $derived(
		rows.filter(r => {
			const matchFilter = activeFilter === 'all' || r.document_type === activeFilter;
			if (!matchFilter) return false;
			if (!search.trim()) return true;
			const q = search.toLowerCase();
			return (
				String(r.document_id ?? '').includes(q) ||
				String(r.sale_id ?? '').includes(q) ||
				String(r.document_type ?? '').toLowerCase().includes(q)
			);
		})
	);

	const FILTERS = ['all', 'OR', 'CR', 'warranty_cert', 'sales_contract', 'other'] as const;

	function filterLabel(f: string): string {
		if (f === 'all') return 'All';
		return DOC_TYPE_LABELS[f] ?? f.charAt(0).toUpperCase() + f.slice(1);
	}

	async function load() {
		loading = true;
		error = null;
		try {
			const res = await getAdminDocuments();
			rows = (Array.isArray(res) ? res : (res as ListResponse).data ?? []) as Record<string, unknown>[];
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function loadSales() {
		try {
			const res = await getAdminSales();
			sales = (res.data ?? []) as Record<string, unknown>[];
		} catch { /* silent */ }
	}

	onMount(() => {
		load();
		loadSales();
	});

	function formatDate(d: string): string {
		if (!d) return '—';
		return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	function resetForm() {
		formSaleId = '';
		formDocType = 'OR';
		formFileUrl = '';
		formIsAccessible = true;
		uploadedFileName = '';
	}

	function openNew() {
		resetForm();
		showNewModal = true;
		console.log('showNewModal:', showNewModal); // should log true
	}

	function openEdit(row: Record<string, unknown>) {
		editTarget = row;
		formSaleId = (row.sale_id as number) ?? '';
		formDocType = (row.document_type as string) ?? 'OR';
		formFileUrl = (row.file_url as string) ?? '';
		formIsAccessible = (row.is_accessible as boolean) ?? true;
		showEditModal = true;
	}

	function openDelete(row: Record<string, unknown>) {
		deleteTarget = row;
		showDeleteModal = true;
	}

	function closeModals() {
		showNewModal = false;
		showEditModal = false;
		showDeleteModal = false;
		editTarget = null;
		deleteTarget = null;
	}

	async function handleCreate() {
		if (!formSaleId) {
			toast.error('Please select a sale');
			return;
		}
		submitting = true;
		try {
			await createDocument(Number(formSaleId), {
				document_type: formDocType,
				file_url: formFileUrl || undefined,
				is_accessible: formIsAccessible,
			});
			toast.success('Document created');
			closeModals();
			load();
		} catch (e) {
			toast.error((e as Error).message);
		} finally {
			submitting = false;
		}
	}

	async function handleEdit() {
		if (!editTarget) return;
		submitting = true;
		try {
			await updateDocument(editTarget.document_id as number, {
				sale_id: Number(formSaleId),
				document_type: formDocType,
				file_url: formFileUrl || undefined,
				is_accessible: formIsAccessible,
			});
			toast.success('Document updated');
			closeModals();
			load();
		} catch (e) {
			toast.error((e as Error).message);
		} finally {
			submitting = false;
		}
	}

	async function handleDelete() {
		if (!deleteTarget) return;
		submitting = true;
		try {
			await deleteDocument(deleteTarget.document_id as number);
			toast.success('Document deleted');
			closeModals();
			load();
		} catch (e) {
			toast.error((e as Error).message);
		} finally {
			submitting = false;
		}
	}

	async function handleFileUpload(e: Event) {
		const input = e.target as HTMLInputElement;
		if (!input.files?.length) return;
		const file = input.files[0];
		fileUploading = true;
		try {
			const res = await uploadDocumentFile(file);
			formFileUrl = res.file_url;
			uploadedFileName = file.name;
			toast.success('File uploaded');
		} catch (e) {
			toast.error((e instanceof Error ? e.message : 'Upload failed'));
		} finally {
			fileUploading = false;
			input.value = '';
		}
	}

	function saleLabel(s: Record<string, unknown>): string {
		const saleData = (s.sales as Record<string, unknown>) ?? {};
		const customer = (s.customer as Record<string, unknown>) ?? {};
		const vehicle = (s.vehicle as Record<string, unknown>) ?? {};
		return `#${saleData.sale_id} — ${customer.username ?? '?'} (${vehicle.brand ?? ''} ${vehicle.model ?? ''})`.trim();
	}

	function resolveFileUrl(url: string | null | undefined): string | null {
		if (!url) return null;
		if (url.startsWith('/')) return `${PUBLIC_API}${url}`;
		return url;
	}
</script>

<div class="page">
	<div class="top-bar">
		<div class="title-row">
			<div>
				<h1>Documents</h1>
				<p class="title-subtitle">Manage vehicle and customer documents</p>
			</div>
		</div>
		<div class="toolbar">
			<div class="search-wrap">
				<Search class="search-icon" size={14} />
				<input
					type="text"
					class="search-input"
					placeholder="Search by sale, type…"
					bind:value={search}
				/>
			</div>
			<button class="create-btn" onclick={(e) => { e.stopPropagation(); openNew(); }}>
				<Plus size={14} />New Document
			</button>
		</div>
	</div>

	<div class="stats-row">
		<div class="mini-stat s-total">
			<FileText size={18} />
			<div>
				<span class="mini-val">{stats.total}</span>
				<span class="mini-lbl">Total</span>
			</div>
		</div>
		<div class="mini-stat s-or">
			<FileText size={18} />
			<div>
				<span class="mini-val">{stats.or}</span>
				<span class="mini-lbl">OR</span>
			</div>
		</div>
		<div class="mini-stat s-cr">
			<FileText size={18} />
			<div>
				<span class="mini-val">{stats.cr}</span>
				<span class="mini-lbl">CR</span>
			</div>
		</div>
		<div class="mini-stat s-sc">
			<FileText size={18} />
			<div>
				<span class="mini-val">{stats.sales_contract}</span>
				<span class="mini-lbl">Sales Contract</span>
			</div>
		</div>
		<div class="mini-stat s-other">
			<FileText size={18} />
			<div>
				<span class="mini-val">{stats.other}</span>
				<span class="mini-lbl">Other</span>
			</div>
		</div>
	</div>

	<div class="filter-row">
		{#each FILTERS as f}
			<button
				class="filter-btn"
				class:active={activeFilter === f}
				onclick={() => (activeFilter = f)}
			>
				{filterLabel(f)}
			</button>
		{/each}
	</div>

	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading documents…</span>
		</div>
	{:else if error}
		<div class="error-msg">{error}</div>
	{:else if filteredRows.length === 0}
		<div class="empty-state">No documents found.</div>
	{:else}
		<DataTable {columns}>
			{#each filteredRows as row (row.document_id as number)}
				<tr>
					<td><span class="cell-id">#{row.document_id}</span></td>
					<td><a href="/admin/sales/{row.sale_id}" class="cell-sale-link">#{row.sale_id}</a></td>
					<td>
						<span class="badge badge-doc">{DOC_TYPE_LABELS[row.document_type as string] ?? row.document_type as string}</span>
					</td>
					<td>
						{#if row.file_url}
							<a href={resolveFileUrl(row.file_url as string)} target="_blank" rel="noopener" class="file-link">
								<ExternalLink size={12} /> View
							</a>
						{:else}
							<span class="cell-na">—</span>
						{/if}
					</td>
					<td class="cell-date">{formatDate(row.created_at as string)}</td>
					<td class="cell-actions">
						<button class="icon-btn" title="Edit" onclick={(e) => { e.stopPropagation(); openEdit(row); }}>
							<Pencil size={14} />
						</button>
						<button class="icon-btn icon-btn-danger" title="Delete" onclick={(e) => { e.stopPropagation(); openDelete(row); }}>
							<Trash2 size={14} />
						</button>
					</td>
				</tr>
			{/each}
		</DataTable>
	{/if}
</div>

<!-- ─── New Document Modal ─────────────────────────────────────────── -->
{#if showNewModal}
	<div class="modal-overlay" onclick={(e) => { if (e.target === e.currentTarget) closeModals(); }} role="presentation">
		<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
		<div class="modal-card" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>New Document</h2>
				<button class="icon-btn" onclick={closeModals}><X size={16} /></button>
			</div>
			<div class="modal-body">
				<label class="field">
					<span>Sale</span>
					<select bind:value={formSaleId}>
						<option value="">Select a sale…</option>
						{#each sales as s ((s.sales as Record<string, unknown>)?.sale_id)}
							<option value={(s.sales as Record<string, unknown>)?.sale_id as number}>{saleLabel(s)}</option>
						{/each}
					</select>
				</label>
				<label class="field">
					<span>Document Type</span>
					<select bind:value={formDocType}>
						{#each DOC_TYPES as dt}
							<option value={dt}>{DOC_TYPE_LABELS[dt]}</option>
						{/each}
					</select>
				</label>
				<label class="field">
					<span>File</span>
					<div class="file-upload-wrap">
						<input type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" onchange={handleFileUpload} disabled={fileUploading} />
						{#if fileUploading}
							<span class="upload-status">Uploading…</span>
						{/if}
					</div>
					{#if formFileUrl}
						<div class="file-info">
							<span class="file-name">{uploadedFileName || formFileUrl.split('/').pop()}</span>
							<a href={resolveFileUrl(formFileUrl)} target="_blank" rel="noopener" class="file-link">
								<ExternalLink size={12} /> View
							</a>
						</div>
					{/if}
				</label>
				<label class="field field-checkbox">
					<input type="checkbox" bind:checked={formIsAccessible} />
					<span>Is accessible</span>
				</label>
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={closeModals}>Cancel</button>
				<button class="btn-primary" onclick={handleCreate} disabled={submitting || !formFileUrl}>
					{submitting ? 'Creating…' : 'Create'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- ─── Edit Document Modal ────────────────────────────────────────── -->
{#if showEditModal && editTarget}
	<div class="modal-overlay" onclick={(e) => { if (e.target === e.currentTarget) closeModals(); }} role="presentation">
		<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
		<div class="modal-card" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Edit Document #{editTarget.document_id}</h2>
				<button class="icon-btn" onclick={closeModals}><X size={16} /></button>
			</div>
			<div class="modal-body">
				<label class="field">
					<span>Sale</span>
					<select bind:value={formSaleId}>
						<option value="">Select a sale…</option>
						{#each sales as s ((s.sales as Record<string, unknown>)?.sale_id)}
							<option value={(s.sales as Record<string, unknown>)?.sale_id as number}>{saleLabel(s)}</option>
						{/each}
					</select>
				</label>
				<label class="field">
					<span>Document Type</span>
					<select bind:value={formDocType}>
						{#each DOC_TYPES as dt}
							<option value={dt}>{DOC_TYPE_LABELS[dt]}</option>
						{/each}
					</select>
				</label>
				<label class="field">
					<span>File</span>
					<div class="file-upload-wrap">
						<input type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" onchange={handleFileUpload} disabled={fileUploading} />
						{#if fileUploading}
							<span class="upload-status">Uploading…</span>
						{/if}
					</div>
					{#if formFileUrl}
						<div class="file-info">
							<span class="file-name">{uploadedFileName || formFileUrl.split('/').pop()}</span>
							<a href={resolveFileUrl(formFileUrl)} target="_blank" rel="noopener" class="file-link">
								<ExternalLink size={12} /> View
							</a>
						</div>
					{/if}
				</label>
				<label class="field field-checkbox">
					<input type="checkbox" bind:checked={formIsAccessible} />
					<span>Is accessible</span>
				</label>
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={closeModals}>Cancel</button>
				<button class="btn-primary" onclick={handleEdit} disabled={submitting || !formFileUrl}>
					{submitting ? 'Saving…' : 'Save'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- ─── Delete Confirmation Modal ──────────────────────────────────── -->
{#if showDeleteModal && deleteTarget}
	<div class="modal-overlay" onclick={(e) => { if (e.target === e.currentTarget) closeModals(); }} role="presentation">
		<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
		<div class="modal-card modal-card-sm" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Delete Document</h2>
				<button class="icon-btn" onclick={closeModals}><X size={16} /></button>
			</div>
			<div class="modal-body">
				<p class="delete-text">
					Are you sure you want to delete document <strong>#{deleteTarget.document_id}</strong>?
					This action cannot be undone.
				</p>
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={closeModals}>Cancel</button>
				<button class="btn-danger" onclick={handleDelete} disabled={submitting}>
					{submitting ? 'Deleting…' : 'Delete'}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

	.page { font-family: 'Syne', sans-serif; padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; align-items: center; gap: 10px; }
	.title-subtitle { font-size: 13px; color: #9ca3af; margin: 2px 0 0; font-weight: 400; }
	h1 { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; margin: 0; }
	.toolbar { display: flex; align-items: center; gap: 10px; }
	.search-wrap { position: relative; }
	.search-wrap :global(.search-icon) { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; pointer-events: none; }
	.search-input { height: 34px; padding: 0 12px 0 32px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; color: #1a1a2e; background: #f9fafb; outline: none; width: 220px; }
	.search-input:focus { border-color: #7c9df7; background: #fff; }
	.create-btn { display: flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px; background: #1a1a2e; color: #e8c97e; border: none; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; cursor: pointer; letter-spacing: 0.2px; transition: opacity .15s; }
	.create-btn:hover { opacity: 0.85; }

	.stats-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 1.25rem; }
	.mini-stat { background: #f8f7f4; border-radius: 10px; padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
	.s-total :global(svg) { color: #1a1a2e; flex-shrink: 0; }
	.s-or :global(svg) { color: #4f46e5; flex-shrink: 0; }
	.s-cr :global(svg) { color: #b45309; flex-shrink: 0; }
	.s-sc :global(svg) { color: #059669; flex-shrink: 0; }
	.s-other :global(svg) { color: #9ca3af; flex-shrink: 0; }
	.mini-stat div { display: flex; flex-direction: column; }
	.mini-val { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; line-height: 1; }
	.mini-lbl { font-size: 10px; font-weight: 500; color: #9ca3af; letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

	.filter-row { display: flex; gap: 6px; margin-bottom: 1rem; flex-wrap: wrap; }
	.filter-btn { height: 28px; padding: 0 12px; border: 0.5px solid #e5e7eb; border-radius: 20px; background: #f9fafb; font-family: 'Syne', sans-serif; font-size: 11px; color: #6b7280; cursor: pointer; transition: .15s; }
	.filter-btn.active { background: #1a1a2e; color: #e8c97e; border-color: #1a1a2e; }

	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: #9ca3af; font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid #e5e7eb; border-top-color: #1a1a2e; border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.error-msg { color: #A32D2D; font-size: 13px; padding: 1rem; background: #FCEBEB; border-radius: 8px; }
	.empty-state { text-align: center; padding: 2.5rem; color: #9ca3af; font-size: 13px; }

	.cell-id { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #7c9df7; }
	.cell-sale-link { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #7c9df7; text-decoration: none; }
	.cell-sale-link:hover { text-decoration: underline; }
	.cell-date { font-size: 12px; color: #6b7280; }
	.cell-na { font-size: 12px; color: #d1d5db; }
	.cell-actions { display: flex; gap: 6px; }
	.file-link { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: #4f46e5; text-decoration: none; }
	.file-link:hover { text-decoration: underline; }

	.icon-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border: none; border-radius: 6px; background: #f3f4f6; color: #6b7280; cursor: pointer; transition: .15s; }
	.icon-btn:hover { background: #e5e7eb; color: #1a1a2e; }
	.icon-btn-danger:hover { background: #fcebeb; color: #dc2626; }

	.badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
	.badge-doc { background: #eef2ff; color: #4f46e5; }

	/* ─── Modal ───────────────────────────────────────────────────── */
	.modal-overlay { position: fixed; inset: 0; z-index: 99999; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; padding: 1rem; }
	.modal-card { background: #fff; border-radius: 12px; width: 100%; max-width: 480px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
	.modal-card-sm { max-width: 400px; }
	.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 0.5px solid #e5e7eb; }
	.modal-header h2 { margin: 0; font-size: 15px; font-weight: 700; color: #1a1a2e; }
	.modal-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 14px; }
	.modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 1rem 1.25rem; border-top: 0.5px solid #e5e7eb; }
	.field { display: flex; flex-direction: column; gap: 4px; }
	.field span { font-size: 11px; font-weight: 600; color: #374151; letter-spacing: 0.3px; text-transform: uppercase; }
	.field select { height: 36px; padding: 0 10px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; color: #1a1a2e; background: #f9fafb; outline: none; }
	.field select:focus { border-color: #7c9df7; background: #fff; }
	.field input[type="file"] { font-family: 'Syne', sans-serif; font-size: 12px; color: #1a1a2e; }
	.field-checkbox { flex-direction: row; align-items: center; gap: 8px; }
	.field-checkbox span { text-transform: none; font-weight: 500; color: #374151; }
	.file-upload-wrap { display: flex; align-items: center; gap: 8px; }
	.upload-status { font-size: 11px; color: #7c9df7; font-weight: 600; }
	.file-info { display: flex; align-items: center; gap: 8px; padding: 6px 10px; background: #f3f4f6; border-radius: 6px; margin-top: 4px; }
	.file-name { font-size: 11px; color: #374151; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.delete-text { font-size: 13px; color: #6b7280; line-height: 1.5; margin: 0; }
	.btn-primary { height: 34px; padding: 0 16px; background: #1a1a2e; color: #e8c97e; border: none; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; cursor: pointer; transition: opacity .15s; }
	.btn-primary:hover { opacity: 0.85; }
	.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn-secondary { height: 34px; padding: 0 16px; background: #f3f4f6; color: #374151; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 500; cursor: pointer; transition: .15s; }
	.btn-secondary:hover { background: #e5e7eb; }
	.btn-danger { height: 34px; padding: 0 16px; background: #dc2626; color: #fff; border: none; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; cursor: pointer; transition: opacity .15s; }
	.btn-danger:hover { opacity: 0.85; }
	.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

	@media (max-width: 640px) {
		.stats-row { grid-template-columns: 1fr 1fr; }
		.top-bar { flex-direction: column; align-items: flex-start; }
	}
</style>
