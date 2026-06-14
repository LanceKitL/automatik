<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import {
		getAgentTasks,
		createAgentTask,
		updateAgentTask,
		deleteAgentTask,
		getAgentInquiries
	} from '$lib/services/api';
	import type { AgentTaskItem, InquiryItem } from '$lib/services/api';
	import {
		Plus,
		X,
		Check,
		Trash2,
		Pencil,
		Link,
		Unlink,
		Calendar,
		ClipboardList,
		LoaderCircle
	} from '@lucide/svelte';

	let tasks = $state<AgentTaskItem[]>([]);
	let inquiries = $state<InquiryItem[]>([]);
	let loading = $state(true);
	let statusFilter = $state('all');
	let typeFilter = $state('all');

	const now = new Date();
	const timestamp = now.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
		+ ' · ' + now.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });

	let totalCount = $derived(tasks.length);
	let pendingCount = $derived(tasks.filter(t => t.status === 'pending').length);
	let inProgressCount = $derived(tasks.filter(t => t.status === 'in_progress').length);
	let doneCount = $derived(tasks.filter(t => t.status === 'done').length);

	const statusList = ['all', 'pending', 'in_progress', 'done', 'cancelled'];
	const typeList = ['all', 'follow_up', 'appointment', 'demo', 'document_prep', 'other'];

	let displayTasks = $derived.by(() => {
		let list = tasks;
		if (statusFilter !== 'all') list = list.filter(t => t.status === statusFilter);
		if (typeFilter !== 'all') list = list.filter(t => t.task_type === typeFilter);
		return list;
	});

	let showModal = $state(false);
	let editTask = $state<AgentTaskItem | null>(null);
	let form = $state({
		title: '',
		task_type: 'follow_up' as string,
		due_date: '',
		inquiry_id: null as number | null,
		notes: ''
	});
	let saving = $state(false);

	let deleteId = $state<number | null>(null);
	let deleting = $state(false);

	let bindableInquiries = $derived(
		inquiries.filter(i => i.status === 'open' || i.status === 'assigned')
	);

	onMount(loadAll);

	async function loadAll() {
		loading = true;
		try {
			const [taskRes, inqRes] = await Promise.all([
				getAgentTasks(),
				getAgentInquiries()
			]);
			tasks = taskRes.data;
			inquiries = inqRes.data;
		} catch {
			toast.error('Failed to load tasks.');
		} finally {
			loading = false;
		}
	}

	function openCreate() {
		editTask = null;
		form = { title: '', task_type: 'follow_up', due_date: '', inquiry_id: null, notes: '' };
		showModal = true;
	}

	function openEdit(task: AgentTaskItem) {
		editTask = task;
		form = {
			title: task.title,
			task_type: task.task_type,
			due_date: task.due_date ? task.due_date.slice(0, 10) : '',
			inquiry_id: task.inquiry?.inquiry_id ?? null,
			notes: task.notes ?? ''
		};
		showModal = true;
	}

	async function save() {
		if (!form.title.trim() || !form.due_date) {
			toast.error('Title and due date are required.');
			return;
		}
		saving = true;
		try {
			if (editTask) {
				const payload: Record<string, string | null> = {};
				if (form.title !== editTask.title) payload.title = form.title.trim();
				if (form.task_type !== editTask.task_type) payload.task_type = form.task_type;
				if (form.due_date !== editTask.due_date?.slice(0, 10)) payload.due_date = form.due_date;
				if ((form.notes ?? '') !== (editTask.notes ?? '')) payload.notes = form.notes ?? '';
				if (Object.keys(payload).length) {
					await updateAgentTask(editTask.task_id, payload as Parameters<typeof updateAgentTask>[1]);
				}
				toast.success('Task updated.');
			} else {
				await createAgentTask({
					title: form.title.trim(),
					task_type: form.task_type,
					due_date: form.due_date,
					inquiry_id: form.inquiry_id,
					notes: form.notes || null
				});
				toast.success('Task created.');
			}
			showModal = false;
			await loadAll();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to save task.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete(id: number) {
		deleting = true;
		try {
			await deleteAgentTask(id);
			toast.success(`Task #${id} deleted.`);
			deleteId = null;
			await loadAll();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to delete task.');
		} finally {
			deleting = false;
		}
	}

	async function handleStatus(task: AgentTaskItem, newStatus: string) {
		try {
			await updateAgentTask(task.task_id, { status: newStatus });
			toast.success(`Task #${task.task_id} → ${newStatus.replace(/_/g, ' ')}`);
			await loadAll();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to update status.');
		}
	}

	function nextStatus(current: string): string | null {
		const flow: Record<string, string> = {
			pending: 'in_progress',
			in_progress: 'done',
			done: 'pending'
		};
		return flow[current] ?? null;
	}

	function statusClass(status: string): string {
		const m: Record<string, string> = {
			pending: 's-pending',
			in_progress: 's-progress',
			done: 's-done',
			cancelled: 's-cancelled'
		};
		return m[status] ?? 's-default';
	}

	function typeLabel(t: string): string {
		const m: Record<string, string> = {
			follow_up: 'Follow Up',
			appointment: 'Appointment',
			demo: 'Demo',
			document_prep: 'Doc Prep',
			other: 'Other'
		};
		return m[t] ?? t;
	}

	function typeClass(t: string): string {
		const m: Record<string, string> = {
			follow_up: 'badge-follow-up',
			appointment: 'badge-appointment',
			demo: 'badge-demo',
			document_prep: 'badge-doc-prep',
			other: 'badge-other'
		};
		return m[t] ?? 'badge-default';
	}

	function formatDate(d: string): string {
		if (!d) return '—';
		const dt = new Date(d + (d.includes('T') ? '' : 'T00:00:00'));
		return dt.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	function formatDateShort(d: string): string {
		if (!d) return '—';
		const dt = new Date(d + (d.includes('T') ? '' : 'T00:00:00'));
		const today = new Date();
		const diff = Math.ceil((dt.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
		if (diff < 0) return `${Math.abs(diff)}d overdue`;
		if (diff === 0) return 'Today';
		if (diff === 1) return 'Tomorrow';
		return `${diff}d left`;
	}

	function isOverdue(d: string): boolean {
		if (!d) return false;
		const dt = new Date(d + (d.includes('T') ? '' : 'T00:00:00'));
		return dt < new Date() && dt.toDateString() !== new Date().toDateString();
	}

	function inquiryLabel(inq: AgentTaskItem['inquiry']): string {
		if (!inq) return '';
		const name = inq.customer_name ?? 'Guest';
		const vehicle = inq.vehicle ? `${inq.vehicle.brand} ${inq.vehicle.model}` : '';
		return `#${inq.inquiry_id} ${name}${vehicle ? ' · ' + vehicle : ''}`;
	}
</script>

<div class="page">

	<div class="top-bar">
		<div class="title-row">
			<h1>Tasks</h1>
			<p class="subtitle">Manage your to-do list and bind tasks to inquiries.</p>
		</div>
		<span class="timestamp">{timestamp}</span>
	</div>

	{#if loading}
		<div class="loading-state"><span class="spinner"></span><p>Loading tasks…</p></div>
	{:else}

		<!-- Stat cards -->
		<div class="stats-row">
			<div class="sc s1">
				<ClipboardList size={20} />
				<div><span class="sc-val">{totalCount}</span><span class="sc-lbl">Total Tasks</span></div>
			</div>
			<div class="sc s2">
				<LoaderCircle size={20} />
				<div><span class="sc-val">{pendingCount}</span><span class="sc-lbl">Pending</span></div>
			</div>
			<div class="sc s3">
				<Pencil size={20} />
				<div><span class="sc-val">{inProgressCount}</span><span class="sc-lbl">In Progress</span></div>
			</div>
			<div class="sc s4">
				<Check size={20} />
				<div><span class="sc-val">{doneCount}</span><span class="sc-lbl">Done</span></div>
			</div>
		</div>

		<!-- Toolbar -->
		<div class="toolbar">
			<button class="btn-primary" onclick={openCreate}>
				<Plus size={14} /> New Task
			</button>
			<div class="filter-group">
				<span class="filter-label">Status:</span>
				<div class="pills">
					{#each statusList as s}
						<button class="pill" class:active={statusFilter === s} onclick={() => statusFilter = s}>
							{s === 'all' ? 'All' : s.replace(/_/g, ' ')}
						</button>
					{/each}
				</div>
			</div>
			<div class="filter-group">
				<span class="filter-label">Type:</span>
				<div class="pills">
					{#each typeList as t}
						<button class="pill" class:active={typeFilter === t} onclick={() => typeFilter = t}>
							{t === 'all' ? 'All' : typeLabel(t)}
						</button>
					{/each}
				</div>
			</div>
		</div>

		<!-- Table -->
		<div class="card">
			<table>
				<thead>
					<tr>
						<th>ID</th>
						<th>Title</th>
						<th>Type</th>
						<th>Inquiry</th>
						<th>Due Date</th>
						<th>Status</th>
						<th class="cell-actions">Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each displayTasks as task (task.task_id)}
						<tr>
							<td class="cell-id">{task.task_id}</td>
							<td class="cell-title">{task.title}</td>
							<td>
								<span class="type-badge {typeClass(task.task_type)}">{typeLabel(task.task_type)}</span>
							</td>
							<td>
								{#if task.inquiry}
									<span class="inq-badge" title={task.inquiry.message}>
										<Link size={11} />
										{inquiryLabel(task.inquiry)}
									</span>
								{:else}
									<span class="no-inq">—</span>
								{/if}
							</td>
							<td>
								<span class="due {isOverdue(task.due_date) ? 'overdue' : ''}">
									<Calendar size={11} />
									{formatDate(task.due_date)}
									<span class="due-label">{formatDateShort(task.due_date)}</span>
								</span>
							</td>
							<td>
								<button
									class="status-badge {statusClass(task.status)}"
									onclick={() => {
										const next = nextStatus(task.status);
										if (next) handleStatus(task, next);
									}}
									title="Click to change status"
								>
									<span class="sdot"></span>
									{task.status.replace(/_/g, ' ')}
								</button>
							</td>
							<td class="cell-actions">
								<button class="action-btn" onclick={() => openEdit(task)} title="Edit">
									<Pencil size={14} />
								</button>
								<button class="action-btn danger" onclick={() => deleteId = task.task_id} title="Delete">
									<Trash2 size={14} />
								</button>
							</td>
						</tr>
					{:else}
						<tr>
							<td colspan="7" class="empty-state">No tasks found. Create one to get started.</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<!-- Create / Edit Modal -->
{#if showModal}
	<div class="modal-overlay" onclick={showModal = false} role="presentation">
		<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
			<div class="modal-head">
				<h2>{editTask ? 'Edit Task' : 'New Task'}</h2>
				<button class="close-btn" onclick={() => showModal = false}><X size={18} /></button>
			</div>
			<div class="modal-body">
				<label>
					<span>Title <span class="req">*</span></span>
					<input bind:value={form.title} placeholder="e.g. Follow up with Juan" />
				</label>
				<div class="form-row">
					<label>
						<span>Task Type <span class="req">*</span></span>
						<select bind:value={form.task_type}>
							{#each typeList.slice(1) as t}
								<option value={t}>{typeLabel(t)}</option>
							{/each}
						</select>
					</label>
					<label>
						<span>Due Date <span class="req">*</span></span>
						<input type="date" bind:value={form.due_date} />
					</label>
				</div>
				<label>
					<span>Bind Inquiry</span>
					<select bind:value={form.inquiry_id}>
						<option value={null}>— None —</option>
						{#each bindableInquiries as inq}
							<option value={inq.inquiry_id}>
								#{inq.inquiry_id} {inq.contacts?.name ?? 'Guest'} — {inq.vehicle?.brand} {inq.vehicle?.model}
							</option>
						{/each}
					</select>
				</label>
				{#if editTask && editTask.inquiry && form.inquiry_id === null}
					<button class="btn-unbind" onclick={() => form.inquiry_id = null}>
						<Unlink size={12} /> Unbind inquiry
					</button>
				{/if}
				<label>
					<span>Notes</span>
					<textarea bind:value={form.notes} rows="3" placeholder="Optional notes…"></textarea>
				</label>
			</div>
			<div class="modal-foot">
				<button class="btn-cancel" onclick={() => showModal = false}>Cancel</button>
				<button class="btn-primary" onclick={save} disabled={saving}>
					{saving ? 'Saving…' : editTask ? 'Update Task' : 'Create Task'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Delete confirmation -->
{#if deleteId !== null}
	<div class="modal-overlay" onclick={deleteId = null} role="presentation">
		<div class="modal modal-sm" onclick={(e) => e.stopPropagation()} role="alertdialog">
			<div class="modal-head">
				<h2>Delete Task</h2>
				<button class="close-btn" onclick={() => deleteId = null}><X size={18} /></button>
			</div>
			<div class="modal-body">
				<p>Are you sure you want to delete task <strong>#{deleteId}</strong>? This action cannot be undone.</p>
			</div>
			<div class="modal-foot">
				<button class="btn-cancel" onclick={() => deleteId = null}>Cancel</button>
				<button class="btn-danger" onclick={() => handleDelete(deleteId)} disabled={deleting}>
					{deleting ? 'Deleting…' : 'Delete'}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.page { font-family: var(--font-sans); padding: 2rem; max-width: 1500px; margin: 0 auto; }

	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; flex-direction: column; align-items: start; gap: 10px; }
	.subtitle { font-size: 14px; color: var(--text-muted); margin-top: 4px; }
	h1 { font-size: 20px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; margin: 0; }
	.timestamp { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); background: var(--bg-muted); border: 0.5px solid var(--border); padding: 4px 12px; border-radius: 20px; }

	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }

	.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 1.25rem; }
	.sc { background: var(--bg-stat); border-radius: 12px; padding: .9rem 1.1rem; display: flex; align-items: center; gap: 12px; position: relative; overflow: hidden; transition: transform .18s; }
	.sc:hover { transform: translateY(-2px); }
	.sc::before { content: ''; position: absolute; top: -10px; right: -10px; width: 56px; height: 56px; border-radius: 50%; opacity: .12; }
	.sc.s1::before { background: var(--accent); } .sc.s2::before { background: var(--primary-light); } .sc.s3::before { background: #6de0b0; } .sc.s4::before { background: var(--success); }
	.sc.s1 svg { color: var(--accent-dark); } .sc.s2 svg { color: var(--primary-dark); } .sc.s3 svg { color: var(--success); } .sc.s4 svg { color: var(--success-dark); }
	.sc div { display: flex; flex-direction: column; }
	.sc-val { font-size: 26px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; line-height: 1; }
	.sc-lbl { font-size: 10px; font-weight: 500; color: var(--text-muted); letter-spacing: .6px; text-transform: uppercase; margin-top: 3px; }

	.toolbar { display: flex; align-items: center; gap: 16px; margin-bottom: 1rem; flex-wrap: wrap; }
	.filter-group { display: flex; align-items: center; gap: 6px; }
	.filter-label { font-size: 10px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; }
	.pills { display: flex; gap: 4px; flex-wrap: wrap; }
	.pill { font-size: 11px; padding: 4px 12px; border-radius: 20px; border: 0.5px solid var(--border); background: var(--bg-card); color: var(--text-light); cursor: pointer; transition: all .15s; font-weight: 500; }
	.pill:hover { background: var(--bg-hover); }
	.pill.active { background: var(--primary); color: var(--accent); border-color: var(--primary); }

	.btn-primary { display: inline-flex; align-items: center; gap: 6px; padding: 7px 16px; border-radius: 8px; border: none; background: var(--primary); color: var(--accent); font-size: 12px; font-weight: 600; cursor: pointer; transition: opacity .15s; white-space: nowrap; }
	.btn-primary:hover { opacity: 0.85; }
	.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn-cancel { padding: 7px 16px; border-radius: 8px; border: 0.5px solid var(--border); background: var(--bg-card); color: var(--text-light); font-size: 12px; font-weight: 500; cursor: pointer; }
	.btn-cancel:hover { background: var(--bg-hover); }
	.btn-danger { padding: 7px 16px; border-radius: 8px; border: none; background: var(--danger); color: #fff; font-size: 12px; font-weight: 600; cursor: pointer; }
	.btn-danger:hover { opacity: 0.85; }
	.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn-unbind { display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 6px; border: 0.5px solid var(--border); background: var(--bg-card); color: var(--text-light); font-size: 11px; cursor: pointer; margin-top: 4px; }
	.btn-unbind:hover { background: var(--danger-bg); color: var(--danger-text); }

	.card { background: var(--bg-card); border: 0.5px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; }
	table { width: 100%; border-collapse: collapse; }
	th { padding: 9px 1rem; text-align: left; font-size: 10px; font-weight: 600; color: var(--text-muted); letter-spacing: .6px; text-transform: uppercase; background: var(--bg-canvas); border-bottom: .5px solid var(--chart-grid); }
	td { padding: 10px 1rem; font-size: 12px; color: var(--text-light); border-top: .5px solid var(--border-lighter); vertical-align: middle; }
	tr:hover td { background: var(--bg-canvas); }
	.cell-id { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); width: 50px; }
	.cell-title { font-weight: 600; color: var(--text-primary); }
	.cell-actions { text-align: right; width: 80px; }
	.cell-actions th { text-align: right; }
	.empty-state { padding: 2rem; text-align: center; color: var(--text-muted); font-size: 13px; }

	.action-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 6px; border: 0.5px solid var(--border); background: var(--bg-card); color: var(--text-light); cursor: pointer; transition: all .15s; }
	.action-btn:hover { background: var(--bg-hover); color: var(--text-primary); }
	.action-btn.danger:hover { background: var(--danger-bg); color: var(--danger-text); border-color: var(--danger); }

	.status-badge { display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 20px; font-size: 10px; font-weight: 600; border: none; cursor: pointer; transition: opacity .15s; }
	.status-badge:hover { opacity: 0.75; }
	.sdot { width: 5px; height: 5px; border-radius: 50%; }
	.s-pending { background: var(--warning-bg); color: var(--warning-text); }
	.s-pending .sdot { background: var(--warning-dark); }
	.s-progress { background: var(--info-bg); color: var(--info-text); }
	.s-progress .sdot { background: var(--info); }
	.s-done { background: var(--success-bg); color: var(--success-text); }
	.s-done .sdot { background: var(--success-dark); }
	.s-cancelled { background: var(--danger-bg); color: var(--danger-text); }
	.s-cancelled .sdot { background: var(--danger); }
	.s-default { background: var(--bg-hover); color: var(--text-light); }
	.s-default .sdot { background: #888; }

	.type-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; }
	.badge-follow-up { background: #e8f4fd; color: #185fa5; }
	.badge-appointment { background: #fef3e2; color: #854f0b; }
	.badge-demo { background: #eaf3de; color: #3b6d11; }
	.badge-doc-prep { background: #f3e8ff; color: #6b21a8; }
	.badge-other { background: var(--bg-hover); color: var(--text-light); }

	.inq-badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; border-radius: 6px; background: var(--info-bg); color: var(--info-text); font-size: 10px; font-weight: 500; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.inq-badge svg { flex-shrink: 0; }
	.no-inq { color: var(--text-muted); font-size: 11px; }

	.due { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-family: var(--font-mono); color: var(--text-light); }
	.due svg { color: var(--text-muted); }
	.due-label { font-size: 9px; padding: 1px 5px; border-radius: 4px; background: var(--bg-hover); color: var(--text-muted); }
	.overdue { color: var(--danger); }
	.overdue svg { color: var(--danger); }
	.overdue .due-label { background: var(--danger-bg); color: var(--danger-text); }

	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; }
	.modal { background: var(--bg-card); border-radius: var(--radius-lg); width: 100%; max-width: 520px; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,.15); }
	.modal-sm { max-width: 400px; }
	.modal-head { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: .5px solid var(--chart-grid); }
	.modal-head h2 { font-size: 15px; font-weight: 700; color: var(--text-primary); margin: 0; }
	.close-btn { display: flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 6px; border: none; background: transparent; color: var(--text-muted); cursor: pointer; }
	.close-btn:hover { background: var(--bg-hover); }
	.modal-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 14px; }
	.modal-body label { display: flex; flex-direction: column; gap: 4px; }
	.modal-body label span { font-size: 11px; font-weight: 600; color: var(--text-primary); }
	.req { color: var(--danger); }
	.modal-body input, .modal-body select, .modal-body textarea { padding: 8px 10px; border-radius: 6px; border: 0.5px solid var(--border); background: var(--bg-canvas); color: var(--text-primary); font-size: 12px; outline: none; font-family: inherit; }
	.modal-body input:focus, .modal-body select:focus, .modal-body textarea:focus { border-color: var(--primary); }
	.modal-body textarea { resize: vertical; min-height: 60px; }
	.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
	.modal-foot { display: flex; align-items: center; justify-content: flex-end; gap: 8px; padding: 1rem 1.25rem; border-top: .5px solid var(--chart-grid); }

	@media (max-width: 680px) {
		.stats-row { grid-template-columns: 1fr 1fr; }
		.toolbar { flex-direction: column; align-items: stretch; }
		.filter-group { flex-wrap: wrap; }
		.form-row { grid-template-columns: 1fr; }
	}
</style>
