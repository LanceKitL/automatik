<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import DataTable from '$lib/components/DataTable.svelte';
  import StatCard from '$lib/components/StatCard.svelte';
  import {
    getAdminInventory, createVehicle, updateVehicle, deleteVehicle,
    updateVehicleStatus, uploadVehiclePhoto,
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
    } catch (e) { vehicleError = (e as Error).message; }
    finally { vehicleSubmitting = false; }
  }

  async function handleDeleteVehicle(id: number) {
    if (!confirm('Delete this vehicle? This cannot be undone.')) return;
    try { await deleteVehicle(id); await loadAll(); }
    catch (e) { alert((e as Error).message); }
  }

  async function handleStatusTransition(id: number, current: string) {
    const next: Record<string, string> = { available: 'reserved', reserved: 'delivered' };
    if (!next[current]) return;
    try { await updateVehicleStatus(id, next[current]); await loadAll(); }
    catch (e) { alert((e as Error).message); }
  }

  async function handleDiscontinue(id: number) {
    if (!confirm('Mark as discontinued?')) return;
    try { await updateVehicleStatus(id, 'discontinued'); await loadAll(); }
    catch (e) { alert((e as Error).message); }
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
    } catch (e) { supplierError = (e as Error).message; }
    finally { supplierSubmitting = false; }
  }

  async function handleDeleteSupplier(id: number) {
    if (!confirm('Delete this supplier?')) return;
    try { await deleteSupplier(id); await loadAll(); }
    catch (e) { alert((e as Error).message); }
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
    } catch (e) { supplyError = (e as Error).message; }
    finally { supplySubmitting = false; }
  }

  async function handleDeleteSupply(id: number) {
    if (!confirm('Delete this supply item?')) return;
    try { await deleteSupply(id); await loadAll(); }
    catch (e) { alert((e as Error).message); }
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
      <h1>Inventory Management</h1>
    </div>
  </div>

  <!-- Stat cards -->
  <div class="stats-row">
    <div class="sc s1">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v3"/><rect x="9" y="11" width="14" height="10" rx="2"/><circle cx="12" cy="21" r="1"/><circle cx="20" cy="21" r="1"/></svg>
      <div><span class="sc-val">{totalVehicles}</span><span class="sc-lbl">Total Vehicles</span></div>
    </div>
    <div class="sc s2">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      <div><span class="sc-val">{availableCount}</span><span class="sc-lbl">Available</span></div>
    </div>
    <div class="sc s3">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m10.29 3.86-8.28 14.36A2 2 0 0 0 3.74 21h16.52a2 2 0 0 0 1.73-3l-8.28-14.14a2 2 0 0 0-3.46.03z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      <div><span class="sc-val">{lowStockModelCount}</span><span class="sc-lbl">Low Stock Models</span></div>
    </div>
    <div class="sc s4">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
      <div><span class="sc-val">{activeSupplierCount}</span><span class="sc-lbl">Active Suppliers</span></div>
    </div>
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
        <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
        Add Vehicle
      </button>
    {:else if activeTab === 'suppliers'}
      <button class="add-btn" onclick={openAddSupplier}>
        <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
        Add Supplier
      </button>
    {:else}
      <button class="add-btn" onclick={openAddSupply}>
        <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
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
        {key:'vehicle_id',label:'ID'},{key:'brand',label:'Brand/Model'},{key:'vin',label:'VIN'},
        {key:'year',label:'Year'},{key:'color',label:'Color'},{key:'body_type',label:'Body'},
        {key:'transmission',label:'Trans'},{key:'fuel_type',label:'Fuel'},{key:'price',label:'Price'},
        {key:'supplier_name',label:'Supplier'},{key:'status',label:'Status'},{key:'actions',label:'Actions'},
      ]}>
        {#each vehicles as v (v.vehicle_id)}
          <tr>
            <td class="cell-id">#{v.vehicle_id}</td>
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
            <td><span class="status-badge {statusClass(v.status)}"><span class="s-dot"></span>{v.status as string}</span></td>
            <td>
              <div class="act">
                {#if v.status === 'available'}
                  <button class="btn-sm btn-trans" onclick={() => handleStatusTransition(v.vehicle_id as number, 'available')}>→ Reserve</button>
                {:else if v.status === 'reserved'}
                  <button class="btn-sm btn-trans" onclick={() => handleStatusTransition(v.vehicle_id as number, 'reserved')}>→ Deliver</button>
                {/if}
                <button class="btn-sm btn-edit" onclick={() => openEditVehicle(v)}>Edit</button>
                <button class="btn-sm btn-disc" onclick={() => handleDiscontinue(v.vehicle_id as number)}>Discontinue</button>
                <button class="btn-sm btn-del" onclick={() => handleDeleteVehicle(v.vehicle_id as number)}>Delete</button>
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
        {#each suppliers as s (s.supplier_id)}
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
                <button class="btn-sm btn-edit" onclick={() => openEditSupplier(s)}>Edit</button>
                <button class="btn-sm btn-del" onclick={() => handleDeleteSupplier(s.supplier_id as number)}>Delete</button>
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
        {#each supplies as s (s.supply_id)}
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
                <button class="btn-sm btn-edit" onclick={() => openEditSupply(s)}>Edit</button>
                <button class="btn-sm btn-del" onclick={() => handleDeleteSupply(s.supply_id as number)}>Delete</button>
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
  <div class="modal-backdrop" onclick={() => showVehicleModal = false} role="presentation">
    <div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
      <div class="modal-head">
        <h2>{editingVehicle ? 'Edit Vehicle' : 'Add Vehicle'}</h2>
        <button class="modal-close" onclick={() => showVehicleModal = false} aria-label="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>
      {#if vehicleError}<p class="form-error">{vehicleError}</p>{/if}
      <form onsubmit={(e) => { e.preventDefault(); handleVehicleSubmit(); }}>
        <div class="form-grid">
          <label>Brand <input type="text" bind:value={vehicleForm.brand} required /></label>
          <label>Model <input type="text" bind:value={vehicleForm.model} required /></label>
          <label>Year <input type="number" bind:value={vehicleForm.year} required /></label>
          <label>Color <input type="text" bind:value={vehicleForm.color} /></label>
          <label>Body Type
            <select bind:value={vehicleForm.body_type}>
              <option value="">— Select —</option>
              {#each bodyTypes as bt}<option value={bt}>{bt}</option>{/each}
            </select>
          </label>
          <label>Transmission
            <select bind:value={vehicleForm.transmission} required>
              {#each transmissions as t}<option value={t}>{t}</option>{/each}
            </select>
          </label>
          <label>Fuel Type
            <select bind:value={vehicleForm.fuel_type} required>
              {#each fuelTypes as f}<option value={f}>{f}</option>{/each}
            </select>
          </label>
          <label>Price (₱) <input type="number" step="0.01" bind:value={vehicleForm.price} required /></label>
          <label>Seats <input type="number" bind:value={vehicleForm.seating_capacity} /></label>
          <label>VIN <input type="text" bind:value={vehicleForm.vin} required disabled={!!editingVehicle} /></label>
          <label>Status
            <select bind:value={vehicleForm.status}>
              {#each vStatuses as s}<option value={s}>{s}</option>{/each}
            </select>
          </label>
          <label>Supplier
            <select bind:value={vehicleForm.supplier_id} required>
              <option value="">— Select Supplier —</option>
              {#each suppliers as s}<option value={s.supplier_id}>{s.company_name as string}</option>{/each}
            </select>
          </label>
        </div>
        <label class="full-label">Specs (JSON) <textarea rows="4" bind:value={vehicleForm.specs_json}></textarea></label>
        <label class="full-label">Photos {#if !editingVehicle}<em class="hint">(add after saving)</em>{:else}<em class="hint">(add more)</em>{/if}
          <input type="file" multiple accept="image/*" onchange={(e) => {
            const input = e.target as HTMLInputElement;
            if (input.files) vehicleFiles = Array.from(input.files);
          }} />
        </label>
        <div class="modal-actions">
          <button type="button" class="btn-cancel" onclick={() => showVehicleModal = false}>Cancel</button>
          <button type="submit" class="btn-primary" disabled={vehicleSubmitting}>{vehicleSubmitting ? 'Saving…' : 'Save Vehicle'}</button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- ── Supplier Modal ───────────────────────────────────────────────────── -->
{#if showSupplierModal}
  <div class="modal-backdrop" onclick={() => showSupplierModal = false} role="presentation">
    <div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
      <div class="modal-head">
        <h2>{editingSupplier ? 'Edit Supplier' : 'Add Supplier'}</h2>
        <button class="modal-close" onclick={() => showSupplierModal = false} aria-label="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>
      {#if supplierError}<p class="form-error">{supplierError}</p>{/if}
      <form onsubmit={(e) => { e.preventDefault(); handleSupplierSubmit(); }}>
        <div class="form-grid">
          <label>Company Name <input type="text" bind:value={supplierForm.company_name} required /></label>
          <label>Contact Name <input type="text" bind:value={supplierForm.contact_name} /></label>
          <label>Contact Email <input type="email" bind:value={supplierForm.contact_email} /></label>
          <label>Contact Phone <input type="text" bind:value={supplierForm.contact_phone} /></label>
          <label>Address <input type="text" bind:value={supplierForm.address} /></label>
          <label>Status
            <select bind:value={supplierForm.is_active}>
              <option value={1}>Active</option>
              <option value={0}>Inactive</option>
            </select>
          </label>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-cancel" onclick={() => showSupplierModal = false}>Cancel</button>
          <button type="submit" class="btn-primary" disabled={supplierSubmitting}>{supplierSubmitting ? 'Saving…' : 'Save Supplier'}</button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- ── Supply Modal ─────────────────────────────────────────────────────── -->
{#if showSupplyModal}
  <div class="modal-backdrop" onclick={() => showSupplyModal = false} role="presentation">
    <div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
      <div class="modal-head">
        <h2>{editingSupply ? 'Edit Supply' : 'Add Supply'}</h2>
        <button class="modal-close" onclick={() => showSupplyModal = false} aria-label="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>
      {#if supplyError}<p class="form-error">{supplyError}</p>{/if}
      <form onsubmit={(e) => { e.preventDefault(); handleSupplySubmit(); }}>
        <div class="form-grid">
          <label>Part Name <input type="text" bind:value={supplyForm.part_name} required /></label>
          <label>Part Number <input type="text" bind:value={supplyForm.part_number} /></label>
          <label>Unit Cost (₱) <input type="number" step="0.01" bind:value={supplyForm.unit_cost} /></label>
          <label>Stock Qty <input type="number" bind:value={supplyForm.stock_qty} /></label>
          <label>Reorder Level <input type="number" bind:value={supplyForm.reorder_level} /></label>
          <label>Supplier
            <select bind:value={supplyForm.supplier_id} required>
              <option value="">— Select Supplier —</option>
              {#each suppliers as s}<option value={s.supplier_id}>{s.company_name as string}</option>{/each}
            </select>
          </label>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-cancel" onclick={() => showSupplyModal = false}>Cancel</button>
          <button type="submit" class="btn-primary" disabled={supplySubmitting}>{supplySubmitting ? 'Saving…' : 'Save Supply'}</button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
  .page { font-family: var(--font-sans); padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

  /* Top bar */
  .top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; }
  .title-row { display: flex; align-items: center; gap: 10px; }
  .logo-badge { width: 36px; height: 36px; background: var(--primary); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700; color: var(--accent); flex-shrink: 0; }
  h1 { font-size: 20px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; margin: 0; }

  /* Stats */
  .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 1.5rem; }
  .sc { background: var(--bg-stat); border-radius: 10px; padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
  .sc svg { flex-shrink: 0; }
  .sc.s1 svg { color: var(--accent-dark); } .sc.s2 svg { color: var(--success); }
  .sc.s3 svg { color: var(--danger); } .sc.s4 svg { color: var(--primary-dark); }
  .sc div { display: flex; flex-direction: column; }
  .sc-val { font-size: 22px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; line-height: 1; }
  .sc-lbl { font-size: 10px; font-weight: 500; color: var(--text-muted); letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

  /* Tabs */
  .tabs-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 8px; }
  .tabs { display: flex; background: var(--bg-stat); border-radius: 10px; padding: 3px; gap: 2px; }
  .tab-btn { height: 30px; padding: 0 14px; border: none; border-radius: 8px; background: transparent; font-family: var(--font-sans); font-size: 11px; font-weight: 600; color: var(--text-light); cursor: pointer; transition: .15s; white-space: nowrap; }
  .tab-btn.active { background: var(--primary); color: var(--accent); }
  .add-btn { display: flex; align-items: center; gap: 5px; height: 32px; padding: 0 14px; background: var(--primary); color: var(--accent); border: none; border-radius: 8px; font-family: var(--font-sans); font-size: 11px; font-weight: 600; cursor: pointer; transition: opacity .15s; }
  .add-btn:hover { opacity: .85; }

  /* Loading */
  .loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px; }
  .spinner { width: 24px; height: 24px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .error-msg { color: var(--danger); font-size: 13px; padding: 1rem; background: var(--danger-bg); border-radius: 8px; margin-bottom: 1rem; }

  /* Cells */
  :global(.cell-id)   { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); }
  :global(.cell-name) { font-size: 13px; font-weight: 600; color: var(--text-primary); }
  :global(.cell-mono) { font-family: var(--font-mono); font-size: 11px; color: var(--text-light); }
  :global(.capitalize){ text-transform: capitalize; }
  .low-badge { display: inline-block; background: var(--danger-bg); color: var(--danger-text); font-size: 9px; font-weight: 700; padding: 1px 6px; border-radius: 10px; margin-left: 5px; letter-spacing: 0.3px; }

  /* Status badges */
  .status-badge { display: inline-flex; align-items: center; gap: 5px; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.3px; text-transform: capitalize; }
  .s-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
  :global(.st-available)    { background: var(--success-bg); color: var(--success-text); }
  :global(.st-reserved)     { background: var(--warning-bg); color: var(--warning-text); }
  :global(.st-delivered)    { background: var(--info-bg); color: var(--info-text); }
  :global(.st-discontinued) { background: var(--danger-bg); color: var(--danger-text); }
  :global(.st-available .s-dot)    { background: var(--success-dark); }
  :global(.st-reserved .s-dot)     { background: var(--warning-dark); }
  :global(.st-delivered .s-dot)    { background: var(--info); }
  :global(.st-discontinued .s-dot) { background: var(--danger); }

  .active-badge { display: inline-block; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; }
  .ab-yes { background: var(--success-bg); color: var(--success-text); }
  .ab-no  { background: var(--bg-hover); color: var(--text-light); }

  /* Actions */
  .act { display: flex; gap: 4px; flex-wrap: nowrap; align-items: center; }
  .btn-sm { display: inline-flex; align-items: center; gap: 3px; border: none; padding: 3px 8px; border-radius: 6px; cursor: pointer; font-family: var(--font-sans); font-size: 10px; font-weight: 600; transition: opacity .15s; white-space: nowrap; }
  .btn-sm:hover { opacity: .7; }
  .btn-trans { background: var(--success-bg); color: var(--success-text); }
  .btn-edit  { background: var(--warning-bg); color: var(--warning-text); }
  .btn-disc  { background: #F1EFE8; color: #5F5E5A; }
  .btn-del   { background: var(--danger-bg); color: var(--danger-text); }

  /* Modals */
  .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.45); display: flex; align-items: flex-start; justify-content: center; padding-top: 2.5rem; z-index: 200; }
  .modal { background: var(--bg-card); border-radius: var(--radius-lg); padding: 1.5rem; width: 90%; max-width: 44rem; max-height: 82vh; overflow-y: auto; }
  .modal-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
  .modal-head h2 { font-size: 16px; font-weight: 700; color: var(--text-primary); margin: 0; }
  .modal-close { background: var(--bg-hover); border: none; border-radius: 8px; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--text-light); }
  .modal-close:hover { background: var(--border); }
  .form-error { color: var(--danger); background: var(--danger-bg); font-size: 12px; padding: .5rem .75rem; border-radius: 8px; margin-bottom: 1rem; }
  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin-bottom: .75rem; }
  .form-grid label { display: flex; flex-direction: column; gap: 4px; font-size: 11px; font-weight: 600; color: var(--text-muted); letter-spacing: .4px; text-transform: uppercase; }
  .form-grid input, .form-grid select { padding: .45rem .6rem; font-size: 13px; font-family: var(--font-sans); border: 0.5px solid var(--border); border-radius: 8px; color: var(--text-primary); background: var(--bg-canvas); outline: none; }
  .form-grid input:focus, .form-grid select:focus { border-color: var(--primary-light); background: var(--bg-card); }
  .form-grid input:disabled { background: var(--bg-hover); color: var(--text-muted); cursor: not-allowed; }
  .full-label { display: flex; flex-direction: column; gap: 4px; font-size: 11px; font-weight: 600; color: var(--text-muted); letter-spacing: .4px; text-transform: uppercase; margin-bottom: .75rem; }
  .full-label textarea { padding: .45rem .6rem; font-size: 12px; font-family: var(--font-mono); border: 0.5px solid var(--border); border-radius: 8px; resize: vertical; outline: none; }
  .full-label textarea:focus { border-color: var(--primary-light); }
  .hint { font-size: 11px; color: var(--text-muted); text-transform: none; letter-spacing: 0; margin-left: 4px; font-style: italic; }
  .modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 1.25rem; padding-top: 1rem; border-top: 0.5px solid var(--chart-grid); }
  .btn-primary { height: 34px; padding: 0 18px; background: var(--primary); color: var(--accent); border: none; border-radius: 8px; font-family: var(--font-sans); font-size: 12px; font-weight: 600; cursor: pointer; transition: opacity .15s; }
  .btn-primary:hover { opacity: .85; }
  .btn-primary:disabled { opacity: .5; cursor: not-allowed; }
  .btn-cancel { height: 34px; padding: 0 16px; background: var(--bg-hover); color: var(--text-light); border: none; border-radius: 8px; font-family: var(--font-sans); font-size: 12px; font-weight: 600; cursor: pointer; }
  .btn-cancel:hover { background: var(--border); }

  @media (max-width: 768px) {
    .stats-row { grid-template-columns: repeat(2, 1fr); }
    .form-grid  { grid-template-columns: 1fr; }
  }
</style>