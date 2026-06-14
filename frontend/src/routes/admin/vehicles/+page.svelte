<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import DataTable from '$lib/components/DataTable.svelte';
  import { toast } from 'svelte-sonner';
  import { Search, Plus, Package, Building2, Box, Eye, Pencil, Trash2, X, CheckCircle, AlertTriangle } from '@lucide/svelte';
  import {
    getAdminInventory, createVehicle, updateVehicle, deleteVehicle,
    updateVehicleStatus, uploadVehiclePhoto, deleteVehiclePhoto, resolvePhotoUrl,
    createSupplier, updateSupplier, deleteSupplier,
    createSupply, updateSupply, deleteSupply,
  } from '$lib/services/api';

  // ── Tab ──────────────────────────────────────────────────────────────
  let activeTab = $derived($page.url.searchParams.get('tab') || 'vehicles');
  function switchTab(tab: string) {
    goto(`/admin/vehicles?tab=${tab}`, { replaceState: true, noScroll: true });
  }

  // ── Data ─────────────────────────────────────────────────────────────
  let vehicles  = $state<Record<string, unknown>[]>([]);
  let suppliers = $state<Record<string, unknown>[]>([]);
  let supplies  = $state<Record<string, unknown>[]>([]);
  let lowStockThreshold = $state(5);
  let loading = $state(true);
  let error   = $state<string | null>(null);
  let photoModalVehicle = $state<Record<string, unknown> | null>(null);
  let deletingPhoto = $state<number | null>(null);

  async function handleDeletePhoto(photoId: number) {
    if (!confirm('Delete this photo?')) return;
    deletingPhoto = photoId;
    try {
      await deleteVehiclePhoto(photoId);
      const vehicle = photoModalVehicle!;
      vehicle.photos = (vehicle.photos as any[]).filter((p: any) => p.photo_id !== photoId);
      photoModalVehicle = { ...vehicle };
      if (!(vehicle.photos as any[]).length) photoModalVehicle = null;
      toast.success('Photo deleted');
    } catch (e) {
      alert((e as Error).message);
    } finally {
      deletingPhoto = null;
    }
  }

  async function loadAll() {
    loading = true; error = null;
    try {
      const inv = await getAdminInventory();
      vehicles  = inv.data.vehicles;
      suppliers = inv.data.suppliers;
      supplies  = inv.data.supplies;
      lowStockThreshold = inv.data.low_stock_threshold;
    } catch (e) { error = (e as Error).message; }
    finally { loading = false; }
  }

  // ── Search ─────────────────────────────────────────────────────────────
  let searchQuery = $state('');
  let statusFilter = $state('');

  let filteredVehicles = $derived(
    vehicles.filter(v => {
      if (statusFilter && v.status !== statusFilter) return false;
      if (!searchQuery) return true;
      const q = searchQuery.toLowerCase();
      return String(v.brand ?? '').toLowerCase().includes(q) ||
             String(v.model ?? '').toLowerCase().includes(q) ||
             String(v.vin ?? '').toLowerCase().includes(q);
    })
  );

  let filteredSuppliers = $derived(
    searchQuery ? suppliers.filter(s =>
      String(s.company_name ?? '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      String(s.contact_name ?? '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      String(s.contact_email ?? '').toLowerCase().includes(searchQuery.toLowerCase())
    ) : suppliers
  );

  let filteredSupplies = $derived(
    searchQuery ? supplies.filter(s =>
      String(s.part_name ?? '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      String(s.part_number ?? '').toLowerCase().includes(searchQuery.toLowerCase())
    ) : supplies
  );

  // ── Stats ─────────────────────────────────────────────────────────────
  let totalVehicles      = $derived(vehicles.length);
  let availableCount     = $derived(vehicles.filter(v => v.status === 'available').length);
  let lowStockModelCount = $derived(new Set(vehicles.filter(v => v.is_low_stock).map(v => `${v.brand}|${v.model}`)).size);
  let activeSupplierCount = $derived(suppliers.filter(s => s.is_active).length);

  // ── Vehicle CRUD ──────────────────────────────────────────────────────
  let showVehicleModal = $state(false);
  let editingVehicle: Record<string, unknown> | null = $state(null);
  let vehicleForm = $state<Record<string, unknown>>({});
  let vehicleFiles = $state<File[]>([]);
  let vehicleSubmitting = $state(false);
  let vehicleError = $state('');

  function openAddVehicle() {
    editingVehicle = null;
    vehicleForm = { supplier_id: '', vin: '', brand: '', model: '', year: new Date().getFullYear(),
      color: '', body_type: '', seating_capacity: 4, transmission: 'manual',
      fuel_type: 'gasoline', price: '', status: 'available', specs_json: '' };
    vehicleFiles = []; vehicleError = ''; showVehicleModal = true;
  }

  function openEditVehicle(v: Record<string, unknown>) {
    editingVehicle = v;
    vehicleForm = {
      supplier_id: v.supplier_id, vin: v.vin, brand: v.brand, model: v.model,
      year: v.year, color: v.color || '', body_type: v.body_type || '',
      seating_capacity: v.seating_capacity || 4, transmission: v.transmission || 'manual',
      fuel_type: v.fuel_type || 'gasoline', price: v.price, status: v.status || 'available',
      specs_json: (v.specs_json && typeof v.specs_json === 'string')
        ? v.specs_json : JSON.stringify(v.specs_json, null, 2) || '',
    };
    vehicleFiles = []; vehicleError = ''; showVehicleModal = true;
  }

  async function handleVehicleSubmit() {
    vehicleSubmitting = true; vehicleError = '';
    try {
      if (editingVehicle) {
        const payload: Record<string, unknown> = {};
        for (const k of ['brand','model','year','color','body_type','seating_capacity','transmission','fuel_type','price','status','specs_json']) {
          if (vehicleForm[k] !== undefined && vehicleForm[k] !== '') payload[k] = vehicleForm[k];
        }
        await updateVehicle(editingVehicle.vehicle_id as number, payload);
        for (const f of vehicleFiles) await uploadVehiclePhoto(editingVehicle.vehicle_id as number, f);
      } else {
        const payload = {
          supplier_id: Number(vehicleForm.supplier_id), vin: vehicleForm.vin,
          brand: vehicleForm.brand, model: vehicleForm.model, year: Number(vehicleForm.year),
          color: vehicleForm.color, body_type: vehicleForm.body_type,
          seating_capacity: Number(vehicleForm.seating_capacity), transmission: vehicleForm.transmission,
          fuel_type: vehicleForm.fuel_type, price: Number(vehicleForm.price),
          status: vehicleForm.status, specs_json: vehicleForm.specs_json,
        };
        const res = await createVehicle(payload);
        const msg = res.message as string;
        const idMatch = msg.match(/#(\d+)/);
        if (idMatch && vehicleFiles.length > 0) {
          const newId = parseInt(idMatch[1]);
          for (const f of vehicleFiles) await uploadVehiclePhoto(newId, f);
        }
      }
      showVehicleModal = false; await loadAll();
      toast.success(editingVehicle ? 'Vehicle updated' : 'Vehicle created');
    } catch (e) { vehicleError = (e as Error).message; toast.error((e as Error).message); }
    finally { vehicleSubmitting = false; }
  }

  async function handleDeleteVehicle(id: number) {
    if (!confirm('Delete this vehicle? This cannot be undone.')) return;
    try { await deleteVehicle(id); await loadAll(); toast.success('Vehicle removed from inventory'); }
    catch (e) { toast.error((e as Error).message); }
  }

  async function handleStatusTransition(id: number, current: string) {
    const next: Record<string, string> = { available: 'reserved', reserved: 'delivered' };
    if (!next[current]) return;
    try { await updateVehicleStatus(id, next[current]); await loadAll(); toast.success('Status updated to ' + next[current]); }
    catch (e) { toast.error((e as Error).message); }
  }

  async function handleDiscontinue(id: number) {
    if (!confirm('Mark as discontinued?')) return;
    try { await updateVehicleStatus(id, 'discontinued'); await loadAll(); toast.success('Vehicle discontinued'); }
    catch (e) { toast.error((e as Error).message); }
  }

  // ── Supplier CRUD ─────────────────────────────────────────────────────
  let showSupplierModal = $state(false);
  let editingSupplier: Record<string, unknown> | null = $state(null);
  let supplierForm = $state<Record<string, unknown>>({});
  let supplierSubmitting = $state(false);
  let supplierError = $state('');

  function openAddSupplier() {
    editingSupplier = null;
    supplierForm = { company_name: '', contact_name: '', contact_email: '', contact_phone: '', address: '', is_active: 1 };
    supplierError = ''; showSupplierModal = true;
  }

  function openEditSupplier(s: Record<string, unknown>) {
    editingSupplier = s;
    supplierForm = { company_name: s.company_name, contact_name: s.contact_name || '',
      contact_email: s.contact_email || '', contact_phone: s.contact_phone || '',
      address: s.address || '', is_active: s.is_active };
    supplierError = ''; showSupplierModal = true;
  }

  async function handleSupplierSubmit() {
    supplierSubmitting = true; supplierError = '';
    try {
      const payload: Record<string, unknown> = { is_active: supplierForm.is_active };
      for (const k of ['company_name','contact_name','contact_email','contact_phone','address']) {
        if (supplierForm[k] !== undefined && supplierForm[k] !== '') payload[k] = supplierForm[k];
      }
      editingSupplier
        ? await updateSupplier(editingSupplier.supplier_id as number, payload)
        : await createSupplier(payload);
      showSupplierModal = false; await loadAll();
      toast.success(editingSupplier ? 'Supplier updated' : 'Supplier created');
    } catch (e) { supplierError = (e as Error).message; toast.error((e as Error).message); }
    finally { supplierSubmitting = false; }
  }

  async function handleDeleteSupplier(id: number) {
    if (!confirm('Delete this supplier?')) return;
    try { await deleteSupplier(id); await loadAll(); toast.success('Supplier deleted'); }
    catch (e) { toast.error((e as Error).message); }
  }

  // ── Supply CRUD ───────────────────────────────────────────────────────
  let showSupplyModal = $state(false);
  let editingSupply: Record<string, unknown> | null = $state(null);
  let supplyForm = $state<Record<string, unknown>>({});
  let supplySubmitting = $state(false);
  let supplyError = $state('');

  function openAddSupply() {
    editingSupply = null;
    supplyForm = { part_name: '', part_number: '', unit_cost: '', stock_qty: '', reorder_level: '', supplier_id: '' };
    supplyError = ''; showSupplyModal = true;
  }

  function openEditSupply(s: Record<string, unknown>) {
    editingSupply = s;
    supplyForm = { part_name: s.part_name, part_number: s.part_number || '',
      unit_cost: s.unit_cost, stock_qty: s.stock_qty, reorder_level: s.reorder_level, supplier_id: s.supplier_id };
    supplyError = ''; showSupplyModal = true;
  }

  async function handleSupplySubmit() {
    supplySubmitting = true; supplyError = '';
    try {
      const payload: Record<string, unknown> = {};
      for (const k of ['part_name','part_number','supplier_id']) {
        if (supplyForm[k] !== undefined && supplyForm[k] !== '') payload[k] = supplyForm[k];
      }
      for (const k of ['unit_cost','stock_qty','reorder_level']) {
        if (supplyForm[k] !== undefined && supplyForm[k] !== '') payload[k] = Number(supplyForm[k]);
      }
      editingSupply
        ? await updateSupply(editingSupply.supply_id as number, payload)
        : await createSupply(payload);
      showSupplyModal = false; await loadAll();
      toast.success(editingSupply ? 'Supply item updated' : 'Supply item created');
    } catch (e) { supplyError = (e as Error).message; toast.error((e as Error).message); }
    finally { supplySubmitting = false; }
  }

  async function handleDeleteSupply(id: number) {
    if (!confirm('Delete this supply item?')) return;
    try { await deleteSupply(id); await loadAll(); toast.success('Supply item deleted'); }
    catch (e) { toast.error((e as Error).message); }
  }

  // ── Helpers ───────────────────────────────────────────────────────────
  onMount(loadAll);

  function statusClass(s: unknown): string {
    const m: Record<string, string> = {
      available: 'st-available', reserved: 'st-reserved',
      delivered: 'st-delivered', discontinued: 'st-discontinued',
    };
    return m[String(s ?? '')] ?? 'st-delivered';
  }

  const fuelTypes     = ['gasoline','diesel','electric','hybrid'];
  const transmissions = ['manual','automatic'];
  const bodyTypes     = ['sedan','suv','hatchback','coupe','convertible','pickup','van','wagon','other'];
  const vStatuses     = ['available','reserved','delivered','discontinued'];
</script>

<div class="page">

  <!-- Top bar -->
  <div class="top-bar">
    <div class="title-row">
      <div>
        <h1>Inventory Management</h1>
        <p class="title-subtitle">Manage vehicles, suppliers, and supplies</p>
      </div>
    </div>
    <div class="toolbar">
      <div class="search-wrap">
        <Search class="search-icon" size={14} />
        <input
          type="text"
          class="search-input"
          placeholder="Search vehicles, suppliers, supplies…"
          bind:value={searchQuery}
        />
      </div>
    </div>
  </div>

  <!-- Stat cards -->
  <div class="stats-row">
    <div class="mini-stat s1">
      <Package size={18} />
      <div><span class="mini-val">{totalVehicles}</span><span class="mini-lbl">Total Vehicles</span></div>
    </div>
    <div class="mini-stat s2">
      <CheckCircle size={18} />
      <div><span class="mini-val">{availableCount}</span><span class="mini-lbl">Available</span></div>
    </div>
    <div class="mini-stat s3">
      <AlertTriangle size={18} />
      <div><span class="mini-val">{lowStockModelCount}</span><span class="mini-lbl">Low Stock Models</span></div>
    </div>
    <div class="mini-stat s4">
      <Building2 size={18} />
      <div><span class="mini-val">{activeSupplierCount}</span><span class="mini-lbl">Active Suppliers</span></div>
    </div>
  </div>

  <!-- Status filter pills -->
  <div class="status-filters">
    <button class="status-pill" class:active={!statusFilter} onclick={() => statusFilter = ''}>All</button>
    {#each ['available','reserved','delivered','discontinued'] as s}
      <button class="status-pill" class:active={statusFilter === s} onclick={() => statusFilter = s}>{s}</button>
    {/each}
  </div>

  <!-- Tab bar -->
  <div class="tabs-row">
    <div class="tabs">
      {#each [['vehicles','Vehicle Inventory'],['suppliers','Suppliers'],['supplies','Supplies']] as [key, label]}
        <button class="tab-btn" class:active={activeTab === key} onclick={() => switchTab(key)}>{label}</button>
      {/each}
    </div>
    {#if activeTab === 'vehicles'}
      <button class="add-btn" onclick={openAddVehicle}>
        <Plus size={13} />
        Add Vehicle
      </button>
    {:else if activeTab === 'suppliers'}
      <button class="add-btn" onclick={openAddSupplier}>
        <Plus size={13} />
        Add Supplier
      </button>
    {:else}
      <button class="add-btn" onclick={openAddSupply}>
        <Plus size={13} />
        Add Supply
      </button>
    {/if}
  </div>

  {#if loading}
    <div class="loading-state"><span class="spinner"></span><p>Loading inventory…</p></div>
  {:else if error}
    <p class="error-msg">{error}</p>
  {:else}

    <!-- VEHICLES -->
    {#if activeTab === 'vehicles'}
      <DataTable columns={[
        {key:'vehicle_id',label:'ID'},{key:'photo',label:'Photo'},{key:'brand',label:'Brand/Model'},{key:'vin',label:'VIN'},
        {key:'year',label:'Year'},{key:'color',label:'Color'},{key:'body_type',label:'Body'},
        {key:'transmission',label:'Trans'},{key:'fuel_type',label:'Fuel'},{key:'price',label:'Price'},
        {key:'supplier_name',label:'Supplier'},{key:'status',label:'Status'},{key:'actions',label:'Actions'},
      ]}>
        {#each filteredVehicles as v (v.vehicle_id)}
          <tr>
            <td class="cell-id">#{v.vehicle_id}</td>
            <td>
              {#if (v.photos as any[])?.length}
                <button class="btn-view-photo" onclick={() => photoModalVehicle = v}>
                  <Eye size={12} /> View
                </button>
              {:else}
                <span class="no-photo-label">—</span>
              {/if}
            </td>
            <td class="cell-name">
              {v.brand as string} {v.model as string}
              {#if v.is_low_stock}<span class="low-badge">Low</span>{/if}
            </td>
            <td class="cell-mono" style="font-size:10px">{v.vin as string}</td>
            <td>{v.year}</td>
            <td>{v.color as string}</td>
            <td class="capitalize">{v.body_type as string}</td>
            <td class="capitalize">{v.transmission as string}</td>
            <td class="capitalize">{v.fuel_type as string}</td>
            <td class="cell-mono">₱{Number(v.price).toLocaleString()}</td>
            <td>{v.supplier_name as string}</td>
            <td><span class="badge {statusClass(v.status)}">{v.status as string}</span></td>
            <td>
              <div class="act">
                {#if v.status === 'available'}
                  <button class="btn-sm btn-trans" onclick={() => handleStatusTransition(v.vehicle_id as number, 'available')}>→ Reserve</button>
                {:else if v.status === 'reserved'}
                  <button class="btn-sm btn-trans" onclick={() => handleStatusTransition(v.vehicle_id as number, 'reserved')}>→ Deliver</button>
                {/if}
                <button class="btn-sm btn-edit" onclick={() => openEditVehicle(v)}><Pencil size={10} /> Edit</button>
                <button class="btn-sm btn-disc" onclick={() => handleDiscontinue(v.vehicle_id as number)}>Discontinue</button>
                <button class="btn-sm btn-del" onclick={() => handleDeleteVehicle(v.vehicle_id as number)}><Trash2 size={10} /> Delete</button>
              </div>
            </td>
          </tr>
        {/each}
      </DataTable>
    {/if}

    <!-- SUPPLIERS -->
    {#if activeTab === 'suppliers'}
      <DataTable columns={[
        {key:'supplier_id',label:'ID'},{key:'company_name',label:'Company'},{key:'contact_name',label:'Contact'},
        {key:'contact_phone',label:'Phone'},{key:'contact_email',label:'Email'},
        {key:'total_vehicles',label:'Vehicles'},{key:'is_active',label:'Status'},{key:'actions',label:'Actions'},
      ]}>
        {#each filteredSuppliers as s (s.supplier_id)}
          <tr>
            <td class="cell-id">#{s.supplier_id}</td>
            <td class="cell-name">{s.company_name as string}</td>
            <td>{s.contact_name as string}</td>
            <td class="cell-mono">{s.contact_phone as string}</td>
            <td class="cell-mono" style="font-size:11px">{s.contact_email as string}</td>
            <td style="text-align:center">{s.total_vehicles as number}</td>
            <td><span class="active-badge {s.is_active ? 'ab-yes' : 'ab-no'}">{s.is_active ? 'Active' : 'Inactive'}</span></td>
            <td>
              <div class="act">
                <button class="btn-sm btn-edit" onclick={() => openEditSupplier(s)}><Pencil size={10} /> Edit</button>
                <button class="btn-sm btn-del" onclick={() => handleDeleteSupplier(s.supplier_id as number)}><Trash2 size={10} /> Delete</button>
              </div>
            </td>
          </tr>
        {/each}
      </DataTable>
    {/if}

    <!-- SUPPLIES -->
    {#if activeTab === 'supplies'}
      <DataTable columns={[
        {key:'supply_id',label:'ID'},{key:'part_name',label:'Part Name'},{key:'part_number',label:'Part #'},
        {key:'unit_cost',label:'Unit Cost'},{key:'stock_qty',label:'Stock'},
        {key:'reorder_level',label:'Reorder'},{key:'company_name',label:'Supplier'},{key:'actions',label:'Actions'},
      ]}>
        {#each filteredSupplies as s (s.supply_id)}
          <tr>
            <td class="cell-id">#{s.supply_id}</td>
            <td class="cell-name">{s.part_name as string}</td>
            <td class="cell-mono">{s.part_number as string}</td>
            <td class="cell-mono">₱{Number(s.unit_cost).toLocaleString()}</td>
            <td>
              {s.stock_qty as number}
              {#if (s.stock_qty as number) <= (s.reorder_level as number)}<span class="low-badge">Low</span>{/if}
            </td>
            <td>{s.reorder_level as number}</td>
            <td>{s.company_name as string}</td>
            <td>
              <div class="act">
                <button class="btn-sm btn-edit" onclick={() => openEditSupply(s)}><Pencil size={10} /> Edit</button>
                <button class="btn-sm btn-del" onclick={() => handleDeleteSupply(s.supply_id as number)}><Trash2 size={10} /> Delete</button>
              </div>
            </td>
          </tr>
        {/each}
      </DataTable>
    {/if}
  {/if}
</div>

<!-- ── Vehicle Modal ────────────────────────────────────────────────────── -->
{#if showVehicleModal}
  <div class="modal-overlay" onclick={() => showVehicleModal = false} role="presentation">
    <div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
      <div class="modal-header">
        <h2>{editingVehicle ? 'Edit Vehicle' : 'Add Vehicle'}</h2>
        <button class="modal-close" onclick={() => showVehicleModal = false} aria-label="Close">
          <X size={16} />
        </button>
      </div>
      {#if vehicleError}<p class="form-error">{vehicleError}</p>{/if}
      <div class="modal-body">
        <form onsubmit={(e) => { e.preventDefault(); handleVehicleSubmit(); }}>
          <div class="form-grid">
            <label class="field">
              <span class="field-label">Brand</span>
              <input type="text" class="field-input" bind:value={vehicleForm.brand} required />
            </label>
            <label class="field">
              <span class="field-label">Model</span>
              <input type="text" class="field-input" bind:value={vehicleForm.model} required />
            </label>
            <label class="field">
              <span class="field-label">Year</span>
              <input type="number" class="field-input" bind:value={vehicleForm.year} required />
            </label>
            <label class="field">
              <span class="field-label">Color</span>
              <input type="text" class="field-input" bind:value={vehicleForm.color} />
            </label>
            <label class="field">
              <span class="field-label">Body Type</span>
              <select class="field-input" bind:value={vehicleForm.body_type}>
                <option value="">— Select —</option>
                {#each bodyTypes as bt}<option value={bt}>{bt}</option>{/each}
              </select>
            </label>
            <label class="field">
              <span class="field-label">Transmission</span>
              <select class="field-input" bind:value={vehicleForm.transmission} required>
                {#each transmissions as t}<option value={t}>{t}</option>{/each}
              </select>
            </label>
            <label class="field">
              <span class="field-label">Fuel Type</span>
              <select class="field-input" bind:value={vehicleForm.fuel_type} required>
                {#each fuelTypes as f}<option value={f}>{f}</option>{/each}
              </select>
            </label>
            <label class="field">
              <span class="field-label">Price (₱)</span>
              <input type="number" step="0.01" class="field-input" bind:value={vehicleForm.price} required />
            </label>
            <label class="field">
              <span class="field-label">Seats</span>
              <input type="number" class="field-input" bind:value={vehicleForm.seating_capacity} />
            </label>
            <label class="field">
              <span class="field-label">VIN</span>
              <input type="text" class="field-input" bind:value={vehicleForm.vin} required disabled={!!editingVehicle} />
            </label>
            <label class="field">
              <span class="field-label">Status</span>
              <select class="field-input" bind:value={vehicleForm.status}>
                {#each vStatuses as s}<option value={s}>{s}</option>{/each}
              </select>
            </label>
            <label class="field">
              <span class="field-label">Supplier</span>
              <select class="field-input" bind:value={vehicleForm.supplier_id} required>
                <option value="">— Select Supplier —</option>
                {#each suppliers as s}<option value={s.supplier_id}>{s.company_name as string}</option>{/each}
              </select>
            </label>
          </div>
          <label class="field full-field">
            <span class="field-label">Specs (JSON)</span>
            <textarea rows="4" class="field-textarea" bind:value={vehicleForm.specs_json}></textarea>
          </label>
          <label class="field full-field">
            <span class="field-label">Photos {#if !editingVehicle}<span class="optional">(add after saving)</span>{:else}<span class="optional">(add more)</span>{/if}</span>
            <input type="file" multiple accept="image/*" onchange={(e) => {
              const input = e.target as HTMLInputElement;
              if (input.files) vehicleFiles = Array.from(input.files);
            }} />
          </label>
          <div class="modal-footer">
            <button type="button" class="modal-cancel" onclick={() => showVehicleModal = false}>Cancel</button>
            <button type="submit" class="modal-submit" disabled={vehicleSubmitting}>{vehicleSubmitting ? 'Saving…' : 'Save Vehicle'}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
{/if}

<!-- ── Supplier Modal ───────────────────────────────────────────────────── -->
{#if showSupplierModal}
  <div class="modal-overlay" onclick={() => showSupplierModal = false} role="presentation">
    <div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
      <div class="modal-header">
        <h2>{editingSupplier ? 'Edit Supplier' : 'Add Supplier'}</h2>
        <button class="modal-close" onclick={() => showSupplierModal = false} aria-label="Close">
          <X size={16} />
        </button>
      </div>
      {#if supplierError}<p class="form-error">{supplierError}</p>{/if}
      <div class="modal-body">
        <form onsubmit={(e) => { e.preventDefault(); handleSupplierSubmit(); }}>
          <div class="form-grid two-col">
            <label class="field">
              <span class="field-label">Company Name</span>
              <input type="text" class="field-input" bind:value={supplierForm.company_name} required />
            </label>
            <label class="field">
              <span class="field-label">Contact Name</span>
              <input type="text" class="field-input" bind:value={supplierForm.contact_name} />
            </label>
            <label class="field">
              <span class="field-label">Contact Email</span>
              <input type="email" class="field-input" bind:value={supplierForm.contact_email} />
            </label>
            <label class="field">
              <span class="field-label">Contact Phone</span>
              <input type="text" class="field-input" bind:value={supplierForm.contact_phone} />
            </label>
            <label class="field">
              <span class="field-label">Address</span>
              <input type="text" class="field-input" bind:value={supplierForm.address} />
            </label>
            <label class="field">
              <span class="field-label">Status</span>
              <select class="field-input" bind:value={supplierForm.is_active}>
                <option value={1}>Active</option>
                <option value={0}>Inactive</option>
              </select>
            </label>
          </div>
          <div class="modal-footer">
            <button type="button" class="modal-cancel" onclick={() => showSupplierModal = false}>Cancel</button>
            <button type="submit" class="modal-submit" disabled={supplierSubmitting}>{supplierSubmitting ? 'Saving…' : 'Save Supplier'}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
{/if}

<!-- ── Supply Modal ─────────────────────────────────────────────────────── -->
{#if showSupplyModal}
  <div class="modal-overlay" onclick={() => showSupplyModal = false} role="presentation">
    <div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
      <div class="modal-header">
        <h2>{editingSupply ? 'Edit Supply' : 'Add Supply'}</h2>
        <button class="modal-close" onclick={() => showSupplyModal = false} aria-label="Close">
          <X size={16} />
        </button>
      </div>
      {#if supplyError}<p class="form-error">{supplyError}</p>{/if}
      <div class="modal-body">
        <form onsubmit={(e) => { e.preventDefault(); handleSupplySubmit(); }}>
          <div class="form-grid two-col">
            <label class="field">
              <span class="field-label">Part Name</span>
              <input type="text" class="field-input" bind:value={supplyForm.part_name} required />
            </label>
            <label class="field">
              <span class="field-label">Part Number</span>
              <input type="text" class="field-input" bind:value={supplyForm.part_number} />
            </label>
            <label class="field">
              <span class="field-label">Unit Cost (₱)</span>
              <input type="number" step="0.01" class="field-input" bind:value={supplyForm.unit_cost} />
            </label>
            <label class="field">
              <span class="field-label">Stock Qty</span>
              <input type="number" class="field-input" bind:value={supplyForm.stock_qty} />
            </label>
            <label class="field">
              <span class="field-label">Reorder Level</span>
              <input type="number" class="field-input" bind:value={supplyForm.reorder_level} />
            </label>
            <label class="field">
              <span class="field-label">Supplier</span>
              <select class="field-input" bind:value={supplyForm.supplier_id} required>
                <option value="">— Select Supplier —</option>
                {#each suppliers as s}<option value={s.supplier_id}>{s.company_name as string}</option>{/each}
              </select>
            </label>
          </div>
          <div class="modal-footer">
            <button type="button" class="modal-cancel" onclick={() => showSupplyModal = false}>Cancel</button>
            <button type="submit" class="modal-submit" disabled={supplySubmitting}>{supplySubmitting ? 'Saving…' : 'Save Supply'}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
{/if}

<!-- Photo Gallery Modal -->
{#if photoModalVehicle}
  {@const photos = (photoModalVehicle.photos as any[]) ?? []}
  <div class="modal-overlay" onclick={() => photoModalVehicle = null} role="presentation">
    <div class="modal modal-sm" onclick={(e) => e.stopPropagation()}>
      <div class="modal-header">
        <h3>{photoModalVehicle.brand as string} {photoModalVehicle.model as string} ({photos.length} photo{photos.length !== 1 ? 's' : ''})</h3>
        <button class="btn-icon" onclick={() => photoModalVehicle = null}><X size={18} /></button>
      </div>
      <div class="photo-gallery">
        {#each photos as photo}
          <div class="photo-item">
            <button class="photo-del-btn" onclick={() => handleDeletePhoto(photo.photo_id)} disabled={deletingPhoto === photo.photo_id}>
              <Trash2 size={12} />
            </button>
            <img src={resolvePhotoUrl(photo.photo_url)} alt="Vehicle photo" />
          </div>
        {/each}
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
  .toolbar { display: flex; align-items: center; gap: 10px; }
  .search-wrap { position: relative; }
  .search-wrap :global(.search-icon) { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; pointer-events: none; }
  .search-input { height: 34px; padding: 0 12px 0 32px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; color: #1a1a2e; background: #f9fafb; outline: none; width: 220px; }
  .status-filters { display: flex; gap: 4px; margin-bottom: 1rem; flex-wrap: wrap; }
  .status-pill { padding: 4px 14px; border-radius: 20px; border: 1px solid #e5e7eb; background: #fff; font-family: 'Syne', sans-serif; font-size: 11px; font-weight: 500; color: #6b7280; cursor: pointer; text-transform: capitalize; transition: all 0.15s; }
  .status-pill.active { background: var(--primary); color: #fff; border-color: var(--primary); }
  .status-pill:hover:not(.active) { border-color: var(--primary); color: var(--primary); }
  .search-input:focus { border-color: #7c9df7; background: #fff; }
  h1 { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; margin: 0; }

  /* Mini stats */
  .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 1.5rem; }
  .mini-stat { background: #f8f7f4; border-radius: 10px; padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
  .s1 :global(svg) { color: #1a1a2e; flex-shrink: 0; }
  .s2 :global(svg) { color: #059669; flex-shrink: 0; }
  .s3 :global(svg) { color: #dc2626; flex-shrink: 0; }
  .s4 :global(svg) { color: #7c9df7; flex-shrink: 0; }
  .mini-stat div { display: flex; flex-direction: column; }
  .mini-val { font-size: 22px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; line-height: 1; }
  .mini-lbl { font-size: 10px; font-weight: 500; color: #9ca3af; letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

  /* Tabs */
  .tabs-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 8px; }
  .tabs { display: flex; background: #f8f7f4; border-radius: 10px; padding: 3px; gap: 2px; }
  .tab-btn { height: 30px; padding: 0 14px; border: none; border-radius: 8px; background: transparent; font-family: 'Syne', sans-serif; font-size: 11px; font-weight: 600; color: #6b7280; cursor: pointer; transition: .15s; white-space: nowrap; }
  .tab-btn.active { background: #1a1a2e; color: #e8c97e; }
  .add-btn { display: flex; align-items: center; gap: 6px; height: 32px; padding: 0 14px; background: #1a1a2e; color: #e8c97e; border: none; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 11px; font-weight: 600; cursor: pointer; letter-spacing: 0.2px; transition: opacity .15s; }
  .add-btn:hover { opacity: .85; }

  /* Loading */
  .loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: #9ca3af; font-size: 13px; }
  .spinner { width: 24px; height: 24px; border: 2px solid #e5e7eb; border-top-color: #1a1a2e; border-radius: 50%; animation: spin .7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .error-msg { color: #A32D2D; font-size: 13px; padding: 1rem; background: #FCEBEB; border-radius: 8px; margin-bottom: 1rem; }

  /* Cells */
  :global(.cell-id)   { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #7c9df7; }
  :global(.cell-name) { font-size: 13px; font-weight: 600; color: #1a1a2e; }
  :global(.cell-mono) { font-family: 'DM Mono', monospace; font-size: 11px; color: #6b7280; }
  :global(.capitalize) { text-transform: capitalize; }
  .low-badge { display: inline-block; background: #FCEBEB; color: #dc2626; font-size: 9px; font-weight: 700; padding: 1px 6px; border-radius: 10px; margin-left: 5px; letter-spacing: 0.3px; }
  .photo-yes { color: #059669; }
  .photo-no { color: #d1d5db; }
  .btn-view-photo { display: inline-flex; align-items: center; gap: 3px; border: none; padding: 3px 8px; border-radius: 6px; cursor: pointer; font-family: 'Syne', sans-serif; font-size: 10px; font-weight: 600; background: #dbeafe; color: #2563eb; transition: opacity .15s; white-space: nowrap; }
  .btn-view-photo:hover { opacity: .7; }
  .no-photo-label { color: #d1d5db; font-size: 12px; }
  .photo-gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; padding: 1rem 1.25rem; }
  .photo-item { position: relative; }
  .photo-item img { width: 100%; height: 160px; object-fit: cover; border-radius: 8px; border: 1px solid #e5e7eb; display: block; }
  .photo-del-btn { position: absolute; top: 6px; right: 6px; background: rgba(0,0,0,0.5); color: #fff; border: none; border-radius: 4px; padding: 4px 6px; cursor: pointer; opacity: 0; transition: opacity 0.15s; }
  .photo-item:hover .photo-del-btn { opacity: 1; }
  .photo-del-btn:hover:not(:disabled) { background: #dc2626; }
  .photo-del-btn:disabled { opacity: 0.3; cursor: not-allowed; }

  /* Status badges */
  .badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
  :global(.st-available)    { background: #ecfdf5; color: #059669; }
  :global(.st-reserved)     { background: #fef3c7; color: #d97706; }
  :global(.st-delivered)    { background: #dbeafe; color: #2563eb; }
  :global(.st-discontinued) { background: #FCEBEB; color: #dc2626; }

  .active-badge { display: inline-block; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
  .ab-yes { background: #ecfdf5; color: #059669; }
  .ab-no  { background: #f3f4f6; color: #6b7280; }

  /* Actions */
  .act { display: flex; gap: 4px; flex-wrap: nowrap; align-items: center; }
  .btn-sm { display: inline-flex; align-items: center; gap: 3px; border: none; padding: 3px 8px; border-radius: 6px; cursor: pointer; font-family: 'Syne', sans-serif; font-size: 10px; font-weight: 600; transition: opacity .15s; white-space: nowrap; }
  .btn-sm:hover { opacity: .7; }
  .btn-trans { background: #ecfdf5; color: #059669; }
  .btn-edit  { background: #fef3c7; color: #d97706; }
  .btn-disc  { background: #f3f4f6; color: #6b7280; }
  .btn-del   { background: #FCEBEB; color: #dc2626; }

  /* Modals */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: flex-start; justify-content: center; padding-top: 2.5rem; z-index: 1000; }
  .modal { background: #fff; border-radius: 12px; width: 90%; max-width: 44rem; max-height: 82vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
  .modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 0.5px solid #e5e7eb; }
  .modal-header h2 { font-size: 16px; font-weight: 700; color: #1a1a2e; margin: 0; }
  .modal-close { display: flex; align-items: center; justify-content: center; width: 28px; height: 28px; border: none; border-radius: 6px; background: transparent; color: #9ca3af; cursor: pointer; transition: .15s; }
  .modal-close:hover { background: #f3f4f6; color: #1a1a2e; }
  .form-error { color: #A32D2D; background: #FCEBEB; font-size: 12px; padding: .5rem .75rem; border-radius: 8px; margin-bottom: 1rem; }
  .modal-body { padding: 1.25rem; }
  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin-bottom: .75rem; }
  .form-grid.two-col { grid-template-columns: 1fr 1fr; }
  .field { display: flex; flex-direction: column; gap: 4px; }
  .field-label { font-size: 11px; font-weight: 600; color: #374151; letter-spacing: 0.3px; text-transform: uppercase; }
  .optional { font-weight: 400; text-transform: none; color: #9ca3af; font-size: 10px; font-style: italic; }
  .field-input { height: 36px; padding: 0 10px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 13px; color: #1a1a2e; background: #f9fafb; outline: none; width: 100%; box-sizing: border-box; }
  .field-input:focus { border-color: #7c9df7; background: #fff; }
  .field-input:disabled { background: #f3f4f6; color: #9ca3af; cursor: not-allowed; }
  select.field-input { cursor: pointer; appearance: auto; }
  .full-field { margin-bottom: .75rem; }
  .field-textarea { padding: .45rem .6rem; font-size: 12px; font-family: 'DM Mono', monospace; border: 0.5px solid #e5e7eb; border-radius: 8px; resize: vertical; outline: none; width: 100%; box-sizing: border-box; }
  .field-textarea:focus { border-color: #7c9df7; }
  .modal-footer { display: flex; align-items: center; justify-content: flex-end; gap: 8px; padding-top: 1rem; border-top: 0.5px solid #e5e7eb; }
  .modal-submit { height: 34px; padding: 0 18px; background: #1a1a2e; color: #e8c97e; border: none; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; cursor: pointer; transition: opacity .15s; }
  .modal-submit:hover { opacity: .85; }
  .modal-submit:disabled { opacity: .4; cursor: not-allowed; }
  .modal-cancel { height: 34px; padding: 0 16px; border: 0.5px solid #e5e7eb; border-radius: 8px; background: #fff; font-family: 'Syne', sans-serif; font-size: 12px; color: #6b7280; cursor: pointer; transition: .15s; }
  .modal-cancel:hover { background: #f9fafb; }

  @media (max-width: 768px) {
    .stats-row { grid-template-columns: repeat(2, 1fr); }
    .form-grid { grid-template-columns: 1fr; }
    .form-grid.two-col { grid-template-columns: 1fr; }
  }
</style>
