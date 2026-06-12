<script lang="ts">
	import { onMount } from 'svelte';
	import { getAllDocuments } from '$lib/services/api';
	import { FolderKanban, Eye, Download, FileText } from '@lucide/svelte';
	import Loader from '$lib/components/Loader.svelte';

	let docs = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			const res = await getAllDocuments();
			docs = Array.isArray(res) ? res : (res.data ?? []);
		} catch {
			// ignore
		} finally {
			loading = false;
		}
	});

	function viewDoc(d: Record<string, unknown>) {
		const url = d.file_url as string;
		if (url) window.open(url, '_blank');
	}

	function downloadDoc(d: Record<string, unknown>) {
		const url = d.file_url as string;
		if (url) {
			const a = document.createElement('a');
			a.href = url;
			a.download = d.document_type + '_' + d.document_id + '.pdf';
			a.click();
		}
	}

	function docLabel(d: Record<string, unknown>) {
		const t = d.document_type as string;
		if (!t) return `Document #${d.document_id}`;
		const labels: Record<string, string> = {
			'OR': 'Official Receipt',
			'CR': 'Certificate of Registration',
			'sales_contract': 'Sales Contract',
			'warranty_cert': 'Warranty Certificate',
			'amortization_schedule': 'Amortization Schedule',
			'other': 'Other Document',
		};
		return labels[t] ?? t.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase());
	}
</script>

<div class="page-header">
	<h1>Documents</h1>
	<p class="subtitle">View and manage your important documents.</p>
</div>

{#if loading}
	<div class="loader"><Loader /></div>
{:else if docs.length === 0}
	<div class="empty">No documents available yet.</div>
{:else}
	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					<th>Document Name</th>
					<th>Type</th>
					<th>Date Added</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each docs as d (d.document_id)}
					<tr>
						<td class="doc-name"><FileText size={16} class="doc-icon" /> {docLabel(d)}</td>
						<td><span class="type-tag">{d.document_type as string}</span></td>
						<td>{d.created_at ? String(d.created_at).slice(0, 10) : '—'}</td>
						<td class="actions">
							<button class="action-btn" title="View" onclick={() => viewDoc(d)}><Eye size={16} /></button>
							<button class="action-btn" title="Download" onclick={() => downloadDoc(d)}><Download size={16} /></button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

<style>
	.page-header { margin-bottom:24px; }
	h1 { font-size:24px; font-weight:700; color:var(--text-dark); margin:0; }
	.subtitle { font-size:14px; color:var(--text-muted); margin-top:4px; }
	.loader { display:grid; place-items:center; height:50vh; }
	.empty { text-align:center; padding:60px 20px; color:var(--text-muted); font-size:14px; }
	.table-wrapper { overflow-x:auto; background:var(--bg-card); border-radius:var(--radius-md); border:1px solid var(--border); box-shadow:var(--shadow-sm); }
	table { width:100%; border-collapse:collapse; font-size:0.85rem; }
	th { text-align:left; padding:0.75rem 1rem; color:var(--text-muted); font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid var(--border); background:var(--bg-muted); }
	td { padding:0.65rem 1rem; border-bottom:1px solid var(--border-lighter); color:var(--text-primary); }
	tr:last-child td { border-bottom:none; }
	.doc-name { display:flex; align-items:center; gap:8px; font-weight:500; }
	.doc-icon { color:var(--primary); flex-shrink:0; }
	.type-tag { display:inline-block; padding:2px 8px; border-radius:var(--radius-sm); background:var(--bg-muted); color:var(--text-dark); font-size:11px; font-weight:600; }
	.actions { display:flex; gap:4px; }
	.action-btn { background:var(--bg-hover); border:1px solid var(--border); border-radius:var(--radius-sm); padding:4px 8px; cursor:pointer; color:var(--text-light); display:inline-flex; align-items:center; transition:all 0.15s; }
	.action-btn:hover { border-color:var(--primary); color:var(--primary); background:var(--primary-bg); }
</style>
