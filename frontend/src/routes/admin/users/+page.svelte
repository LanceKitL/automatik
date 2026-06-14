<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { X } from '@lucide/svelte';
  import DataTable from '$lib/components/DataTable.svelte';
  import { getUsers, updateUser, deleteUser } from '$lib/services/api';
  import { Search, Plus, Shield, Users, User, Eye, Pencil, Trash2 } from '@lucide/svelte';
  import CreateEditModal from './CreateEditModal.svelte';
  import AgentDetail from './AgentDetail.svelte';
  import CustomerDetail from './CustomerDetail.svelte';

  let loading = $state(true);
  let error = $state<string | null>(null);
  let rows = $state<Record<string, unknown>[]>([]);
  let search = $state('');
  let activeFilter = $state<'all' | 'admin' | 'agent' | 'customer'>('all');

  let showCreateEdit = $state(false);
  let editUser = $state<Record<string, unknown> | null>(null);
  let showAgentDetail = $state(false);
  let agentDetailId = $state<number | null>(null);
  let showCustomerDetail = $state(false);
  let customerDetailId = $state<number | null>(null);
  let showDeleteConfirm = $state(false);
  let deleteTargetId = $state<number | null>(null);
  let showCaution = $state(
    typeof localStorage !== 'undefined' ? localStorage.getItem('admin_users_caution_hidden') !== 'true' : true
  );

  function dismissCaution() {
    showCaution = false;
    localStorage.setItem('admin_users_caution_hidden', 'true');
  }

  const columns = [
    { key: 'user_id',    label: 'ID' },
    { key: 'full_name',  label: 'Name' },
    { key: 'email',      label: 'Email' },
    { key: 'role',       label: 'Role' },
    { key: 'is_active',  label: 'Active' },
    { key: 'last_login', label: 'Last Login' },
    { key: 'actions',    label: 'Actions' },
  ];

  const roleBadgeClass: Record<string, string> = {
    admin:    'badge-admin',
    agent:    'badge-agent',
    customer: 'badge-customer',
  };

  let filteredRows = $derived(
    rows.filter(r => {
      const matchRole   = activeFilter === 'all' || r.role === activeFilter;
      const s           = search.toLowerCase();
      const matchSearch = !s
        || String(r.full_name).toLowerCase().includes(s)
        || String(r.email).toLowerCase().includes(s);
      return matchRole && matchSearch;
    })
  );

  function countByRole(role: string) {
    return rows.filter(r => r.role === role).length;
  }

  async function toggleActive(userId: number, current: boolean) {
    try {
      await updateUser(userId, { is_active: !current });
      toast.success(`User ${current ? 'deactivated' : 'activated'}.`);
      await loadUsers();
    } catch (e) {
      toast.error((e as Error).message || 'Failed to update user.');
    }
  }

  async function handleDelete() {
    if (deleteTargetId === null) return;
    try {
      await deleteUser(deleteTargetId);
      toast.success('User deleted.');
      showDeleteConfirm = false;
      deleteTargetId = null;
      await loadUsers();
    } catch (e) {
      toast.error((e as Error).message || 'Failed to delete user.');
      showDeleteConfirm = false;
      deleteTargetId = null;
    }
  }

  function promptDelete(userId: number) {
    deleteTargetId = userId;
    showDeleteConfirm = true;
  }

  function openEdit(user: Record<string, unknown>) {
    editUser = user;
    showCreateEdit = true;
  }

  function openCreate() {
    editUser = null;
    showCreateEdit = true;
  }

  function viewDetail(user: Record<string, unknown>) {
    const role = user.role as string;
    const id   = user.user_id as number;
    if (role === 'agent')         { agentDetailId = id;    showAgentDetail    = true; }
    else if (role === 'customer') { customerDetailId = id; showCustomerDetail = true; }
    else                          { openEdit(user); }
  }

  async function loadUsers() {
    loading = true;
    error = null;
    try {
      const res = await getUsers();
      rows = res.data as Record<string, unknown>[];
    } catch (e) {
      error = (e as Error).message;
    } finally {
      loading = false;
    }
  }

  onMount(loadUsers);
</script>

<div class="page">
  <!-- Caution banner -->
  {#if showCaution}
    <div class="caution-banner">
      <span class="caution-icon">⚠️</span>
      <span class="caution-text">
        <strong>Caution:</strong> Changes to user accounts (role, active status, profile) take effect immediately.
        Review carefully before saving — incorrect modifications may affect system access and permissions.
      </span>
      <button class="caution-close" onclick={dismissCaution} aria-label="Dismiss"><X size={16} /></button>
    </div>
  {/if}

  <!-- Top bar -->
  <div class="top-bar">
    <div class="title-row">
      <div>
        <h1>User Management</h1>
        <p class="title-subtitle">Create and manage system users</p>
      </div>
    </div>
    <div class="toolbar">
      <div class="search-wrap">
        <Search class="search-icon" size={14} />
        <input class="search-input" type="text" placeholder="Search users…" bind:value={search} />
      </div>
      <button class="create-btn" onclick={openCreate}>
        <Plus size={14} />
        Create User
      </button>
    </div>
  </div>

  <!-- Mini stats -->
  <div class="stats-row">
    <div class="mini-stat s-admin">
      <Shield size={18} />
      <div><span class="mini-val">{countByRole('admin')}</span><span class="mini-lbl">Admins</span></div>
    </div>
    <div class="mini-stat s-agent">
      <Users size={18} />
      <div><span class="mini-val">{countByRole('agent')}</span><span class="mini-lbl">Agents</span></div>
    </div>
    <div class="mini-stat s-customer">
      <User size={18} />
      <div><span class="mini-val">{countByRole('customer')}</span><span class="mini-lbl">Customers</span></div>
    </div>
  </div>

  <!-- Filter pills -->
  <div class="filter-row">
    {#each (['all','admin','agent','customer'] as const) as f}
      <button
        class="filter-btn"
        class:active={activeFilter === f}
        onclick={() => activeFilter = f}
      >{f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}</button>
    {/each}
  </div>

  <!-- Table -->
  {#if loading}
    <div class="loading-state"><span class="spinner"></span><p>Loading users…</p></div>
  {:else if error}
    <div class="error-msg">{error}</div>
  {:else if filteredRows.length === 0}
    <div class="empty-state">No users found.</div>
  {:else}
    <DataTable {columns}>
      {#each filteredRows as row (row.user_id)}
        <tr>
          <td><span class="cell-id">#{row.user_id}</span></td>
          <td class="cell-name">{row.full_name}</td>
          <td class="cell-email">{row.email}</td>
          <td>
            <span class="badge {roleBadgeClass[row.role as string] ?? 'badge-default'}">
              {row.role}
            </span>
          </td>
          <td>
            <label class="toggle" title={row.is_active ? 'Active' : 'Inactive'}>
              <input
                type="checkbox"
                checked={!!row.is_active}
                onchange={() => toggleActive(row.user_id as number, !!row.is_active)}
              />
              <span class="slider"></span>
            </label>
          </td>
          <td class="cell-login">{row.last_login ?? 'Never'}</td>
          <td>
            <div class="actions-cell">
              <button class="btn-view" onclick={() => viewDetail(row)}>
                <Eye size={11} /> View
              </button>
              <button class="btn-edit" onclick={() => openEdit(row)}>
                <Pencil size={11} /> Edit
              </button>
              <button class="btn-delete" onclick={() => promptDelete(row.user_id as number)} aria-label="Delete">
                <Trash2 size={11} />
              </button>
            </div>
          </td>
        </tr>
      {/each}
    </DataTable>
  {/if}
</div>

<CreateEditModal show={showCreateEdit} {editUser} onClose={() => showCreateEdit = false} onSaved={loadUsers} />
<AgentDetail show={showAgentDetail} agentId={agentDetailId} onClose={() => showAgentDetail = false} />
<CustomerDetail show={showCustomerDetail} customerId={customerDetailId} onClose={() => showCustomerDetail = false} />

<!-- Delete confirmation modal -->
{#if showDeleteConfirm}
	<div class="modal-overlay" onclick={() => { showDeleteConfirm = false; deleteTargetId = null; }} role="presentation">
		<div class="delete-modal" onclick={(e) => e.stopPropagation()} role="alertdialog">
			<div class="delete-modal-header">
				<h3>Delete User</h3>
				<button class="close-btn" onclick={() => { showDeleteConfirm = false; deleteTargetId = null; }}>×</button>
			</div>
			<div class="delete-modal-body">
				<p>Are you sure you want to delete user <strong>#{deleteTargetId}</strong>? This cannot be undone.</p>
			</div>
			<div class="delete-modal-footer">
				<button class="btn-cancel" onclick={() => { showDeleteConfirm = false; deleteTargetId = null; }}>Cancel</button>
				<button class="btn-danger" onclick={handleDelete}>Delete</button>
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
  .create-btn { display: flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px; background: #1a1a2e; color: #e8c97e; border: none; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; cursor: pointer; letter-spacing: 0.2px; transition: opacity .15s; white-space: nowrap; }
  .create-btn:hover { opacity: 0.85; }

  /* Mini stats */
  .stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 1.25rem; }
  .mini-stat { background: #f8f7f4; border-radius: 10px; padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
  .s-admin :global(svg) { color: #1a1a2e; flex-shrink: 0; }
  .s-agent :global(svg) { color: #7c9df7; flex-shrink: 0; }
  .s-customer :global(svg) { color: #059669; flex-shrink: 0; }
  .mini-stat div { display: flex; flex-direction: column; }
  .mini-val { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; line-height: 1; }
  .mini-lbl { font-size: 10px; font-weight: 500; color: #9ca3af; letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

  /* Filter pills */
  .filter-row { display: flex; gap: 6px; margin-bottom: 1rem; flex-wrap: wrap; }
  .filter-btn { height: 28px; padding: 0 12px; border: 0.5px solid #e5e7eb; border-radius: 20px; background: #f9fafb; font-family: 'Syne', sans-serif; font-size: 11px; color: #6b7280; cursor: pointer; transition: .15s; }
  .filter-btn.active { background: #1a1a2e; color: #e8c97e; border-color: #1a1a2e; }

  /* Loading & Error */
  .loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: #9ca3af; font-size: 13px; }
  .spinner { width: 24px; height: 24px; border: 2px solid #e5e7eb; border-top-color: #1a1a2e; border-radius: 50%; animation: spin .7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .error-msg { color: #A32D2D; font-size: 13px; padding: 1rem; background: #FCEBEB; border-radius: 8px; margin-bottom: 1rem; }
  .empty-state { text-align: center; padding: 2.5rem; color: #9ca3af; font-size: 13px; }

  /* Table cells */
  .cell-id { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #7c9df7; }
  .cell-name { font-size: 13px; font-weight: 600; color: #1a1a2e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 160px; }
  .cell-email { font-family: 'DM Mono', monospace; font-size: 11px; color: #6b7280; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px; }
  .cell-login { font-family: 'DM Mono', monospace; font-size: 11px; color: #9ca3af; }

  /* Role badges */
  .badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
  .badge-admin { background: #1a1a2e; color: #e8c97e; }
  .badge-agent { background: #eef2ff; color: #4f46e5; }
  .badge-customer { background: #ecfdf5; color: #059669; }
  .badge-default { background: #f3f4f6; color: #6b7280; }

  /* Toggle switch */
  .toggle { position: relative; display: inline-block; width: 34px; height: 18px; cursor: pointer; }
  .toggle input { opacity: 0; width: 0; height: 0; }
  .slider { position: absolute; inset: 0; background: #d1d5db; border-radius: 20px; transition: .2s; }
  .slider::before { content: ''; position: absolute; width: 14px; height: 14px; left: 2px; top: 2px; background: #fff; border-radius: 50%; transition: .2s; }
  .toggle input:checked + .slider { background: #059669; }
  .toggle input:checked + .slider::before { transform: translateX(16px); }

  /* Action buttons */
  .actions-cell { display: flex; gap: 4px; }
  .btn-view, .btn-edit, .btn-delete { display: inline-flex; align-items: center; gap: 3px; border: none; padding: 4px 8px; border-radius: 6px; cursor: pointer; font-family: 'Syne', sans-serif; font-size: 10px; font-weight: 600; letter-spacing: 0.2px; transition: opacity .15s; }
  .btn-view:hover, .btn-edit:hover, .btn-delete:hover { opacity: .7; }
  .btn-view { background: #eef2ff; color: #4f46e5; }
  .btn-edit { background: #fef3c7; color: #b45309; }
  .btn-delete { background: #fcebeb; color: #dc2626; }

  /* Delete modal */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
  .delete-modal { background: var(--bg-card); border-radius: var(--radius-lg); width: 400px; max-width: 90vw; box-shadow: var(--shadow-lg); }
  .delete-modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border); }
  .delete-modal-header h3 { font-size: 16px; font-weight: 700; margin: 0; color: var(--text-primary); }
  .close-btn { background: none; border: none; cursor: pointer; color: var(--text-muted); padding: 4px; font-size: 20px; }
  .close-btn:hover { color: var(--text-primary); }
  .delete-modal-body { padding: 1.25rem 1.5rem; }
  .delete-modal-body p { margin: 0; font-size: 14px; color: var(--text-primary); line-height: 1.5; }
  .delete-modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 1rem 1.5rem; border-top: 1px solid var(--border); }
  .btn-cancel { background: none; border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; color: var(--text-muted); font-family: inherit; }
  .btn-cancel:hover { background: var(--bg-hover); }
  .btn-danger { background: #dc2626; color: #fff; border: none; border-radius: var(--radius-sm); padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; }
  .btn-danger:hover { opacity: 0.85; }

  /* Caution banner */
  .caution-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    margin-bottom: 1.25rem;
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 4px solid #f59e0b;
    border-radius: var(--radius-sm);
    font-size: 13px;
    color: #92400e;
    line-height: 1.5;
  }
  .caution-icon { font-size: 16px; flex-shrink: 0; }
  .caution-text { flex: 1; }
  .caution-close {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border: none;
    border-radius: 6px;
    background: transparent;
    color: #d97706;
    cursor: pointer;
    flex-shrink: 0;
    transition: background 0.15s;
  }
  .caution-close:hover { background: #fde68a; }

  @media (max-width: 640px) {
    .stats-row { grid-template-columns: 1fr; }
    .top-bar { flex-direction: column; align-items: flex-start; }
  }
</style>
