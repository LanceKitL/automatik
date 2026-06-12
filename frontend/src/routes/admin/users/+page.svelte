<script lang="ts">
  import { onMount } from 'svelte';
  import DataTable from '$lib/components/DataTable.svelte';
  import { getUsers, updateUser, deleteUser } from '$lib/services/api';
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

  function filteredRows() {
    return rows.filter(r => {
      const matchRole   = activeFilter === 'all' || r.role === activeFilter;
      const s           = search.toLowerCase();
      const matchSearch = !s
        || String(r.full_name).toLowerCase().includes(s)
        || String(r.email).toLowerCase().includes(s);
      return matchRole && matchSearch;
    });
  }

  function countByRole(role: string) {
    return rows.filter(r => r.role === role).length;
  }

  async function toggleActive(userId: number, current: boolean) {
    try {
      await updateUser(userId, { is_active: !current });
      await loadUsers();
    } catch (e) { error = (e as Error).message; }
  }

  async function handleDelete(userId: number) {
    if (!confirm('Delete this user? This cannot be undone.')) return;
    try {
      await deleteUser(userId);
      await loadUsers();
    } catch (e) { error = (e as Error).message; }
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

  <!-- Top bar -->
  <div class="top-bar">
    <div class="title-row">
      <h1>User Management</h1>
    </div>
    <div class="toolbar">
      <div class="search-wrap">
        <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input class="search-input" type="text" placeholder="Search users…" bind:value={search} />
      </div>
      <button class="create-btn" onclick={openCreate}>
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
        Create User
      </button>
    </div>
  </div>

  <!-- Mini stats -->
  <div class="stats-row">
    <div class="mini-stat s-admin">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
      <div><span class="mini-val">{countByRole('admin')}</span><span class="mini-lbl">Admins</span></div>
    </div>
    <div class="mini-stat s-agent">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M7 20h10M12 4v16"/></svg>
      <div><span class="mini-val">{countByRole('agent')}</span><span class="mini-lbl">Agents</span></div>
    </div>
    <div class="mini-stat s-customer">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/><path d="m16 11 2 2 4-4"/></svg>
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
    <p class="error-msg">{error}</p>
  {:else}
    <DataTable {columns}>
      {#each filteredRows() as row (row.user_id)}
        <tr>
          <td class="cell-id">#{row.user_id}</td>
          <td class="cell-name">{row.full_name}</td>
          <td class="cell-email">{row.email}</td>
          <td>
            <span class="badge {roleBadgeClass[row.role as string] ?? 'badge-default'}">
              {row.role}
            </span>
          </td>
          <td>
            <label class="toggle" title="{row.is_active ? 'Active' : 'Inactive'}">
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
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>
                View
              </button>
              <button class="btn-edit" onclick={() => openEdit(row)}>
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                Edit
              </button>
              <button class="btn-delete" onclick={() => handleDelete(row.user_id as number)} aria-label="Delete user">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
              </button>
            </div>
          </td>
        </tr>
      {:else}
        <tr>
          <td colspan="7" class="empty-state">No users found.</td>
        </tr>
      {/each}
    </DataTable>
  {/if}
</div>

<CreateEditModal show={showCreateEdit} {editUser} onClose={() => showCreateEdit = false} onSaved={loadUsers} />
<AgentDetail show={showAgentDetail} agentId={agentDetailId} onClose={() => showAgentDetail = false} />
<CustomerDetail show={showCustomerDetail} customerId={customerDetailId} onClose={() => showCustomerDetail = false} />

<style>
  .page { font-family: var(--font-sans); padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

  /* Top bar */
  .top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
  .title-row { display: flex; align-items: center; gap: 10px; }
  .logo-badge { width: 36px; height: 36px; background: var(--primary); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700; color: var(--accent); flex-shrink: 0; }
  h1 { font-size: 20px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; margin: 0; }
  .toolbar { display: flex; align-items: center; gap: 10px; }
  .search-wrap { position: relative; }
  .search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
  .search-input { height: 34px; padding: 0 12px 0 32px; border: 0.5px solid var(--border); border-radius: var(--radius-md); font-family: var(--font-sans); font-size: 12px; color: var(--text-primary); background: var(--bg-muted); outline: none; width: 200px; }
  .search-input:focus { border-color: var(--primary-light); background: var(--bg-card); }
  .create-btn { display: flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px; background: var(--primary); color: var(--accent); border: none; border-radius: var(--radius-md); font-family: var(--font-sans); font-size: 12px; font-weight: 600; cursor: pointer; letter-spacing: 0.2px; transition: opacity .15s; }
  .create-btn:hover { opacity: 0.85; }

  /* Mini stats */
  .stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 1.25rem; }
  .mini-stat { background: var(--bg-stat); border-radius: var(--radius-md); padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
  .mini-stat svg { flex-shrink: 0; }
  .s-admin svg  { color: var(--accent); }
  .s-agent svg  { color: var(--primary-light); }
  .s-customer svg { color: #6de0b0; }
  .mini-stat div { display: flex; flex-direction: column; }
  .mini-val { font-size: 20px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; line-height: 1; }
  .mini-lbl { font-size: 10px; font-weight: 500; color: var(--text-muted); letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

  /* Filter pills */
  .filter-row { display: flex; gap: 6px; margin-bottom: 1rem; flex-wrap: wrap; }
  .filter-btn { height: 28px; padding: 0 12px; border: 0.5px solid var(--border); border-radius: 20px; background: var(--bg-muted); font-family: var(--font-sans); font-size: 11px; color: var(--text-light); cursor: pointer; transition: .15s; }
  .filter-btn.active { background: var(--primary); color: var(--accent); border-color: var(--primary); }

  /* Loading */
  .loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px; }
  .spinner { width: 24px; height: 24px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .error-msg { color: var(--danger); font-size: 13px; padding: 1rem; background: var(--danger-bg); border-radius: var(--radius-md); }

  /* Table cells */
  :global(.cell-id) { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); }
  :global(.cell-name) { font-size: 13px; font-weight: 600; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 160px; }
  :global(.cell-email) { font-family: var(--font-mono); font-size: 11px; color: var(--text-light); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px; }
  :global(.cell-login) { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); }
  .empty-state { text-align: center; padding: 2.5rem; color: var(--text-muted); font-size: 13px; }

  /* Role badges */
  .badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
  .badge-admin    { background: var(--primary); color: var(--accent); }
  .badge-agent    { background: var(--info-bg); color: var(--info-text); }
  .badge-customer { background: var(--success-bg); color: var(--success-text); }
  .badge-default  { background: var(--bg-hover); color: var(--text-light); }

  /* Toggle */
  .toggle { position: relative; display: inline-block; width: 34px; height: 18px; cursor: pointer; }
  .toggle input { display: none; }
  .slider { position: absolute; inset: 0; background: var(--border); border-radius: 20px; transition: .2s; }
  .slider::before { content: ''; position: absolute; width: 14px; height: 14px; left: 2px; top: 2px; background: var(--bg-card); border-radius: 50%; transition: .2s; }
  .toggle input:checked + .slider { background: #6de0b0; }
  .toggle input:checked + .slider::before { transform: translateX(16px); }

  /* Action buttons */
  .actions-cell { display: flex; gap: 4px; }
  .btn-view, .btn-edit, .btn-delete { display: inline-flex; align-items: center; gap: 3px; border: none; padding: 4px 8px; border-radius: var(--radius-sm); cursor: pointer; font-family: var(--font-sans); font-size: 10px; font-weight: 600; letter-spacing: 0.2px; transition: opacity .15s; }
  .btn-view:hover, .btn-edit:hover, .btn-delete:hover { opacity: .7; }
  .btn-view   { background: var(--info-bg); color: var(--info-text); }
  .btn-edit   { background: var(--warning-bg); color: var(--warning-text); }
  .btn-delete { background: var(--danger-bg); color: var(--danger-text); }

  /* Responsive */
  @media (max-width: 640px) {
    .stats-row { grid-template-columns: 1fr; }
    .top-bar   { flex-direction: column; align-items: flex-start; }
  }
</style>