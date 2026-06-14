<script lang="ts">
	import { onMount } from 'svelte';
	import { getSettings, updateSetting, addSetting, type SettingsResponse } from '$lib/services/api';
	import { Plus, Save, X, Settings as SettingsIcon } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let settings = $state<SettingsResponse['data'][string][]>([]);
	let editValues = $state<Record<string, string>>({});
	let savingKeys = $state<Record<string, boolean>>({});

	let showAddModal = $state(false);
	let addForm = $state({ setting_key: '', setting_value: '', description: '' });
	let adding = $state(false);

	async function loadSettings(showLoader = false) {
		if (showLoader) loading = true;
		error = null;
		try {
			const res = await getSettings();
			const items = Object.values(res.data);
			settings = items;
			const edits: Record<string, string> = {};
			for (const s of items) {
				edits[s.setting_key] = s.setting_value;
			}
			editValues = edits;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			if (showLoader) loading = false;
		}
	}

	onMount(() => loadSettings(true));

	function isBooleanSetting(key: string): boolean {
		const s = settings.find(s => s.setting_key === key);
		return ['0', '1', 'true', 'false'].includes(s?.setting_value ?? '');
	}

	function toggleValue(current: string): string {
		if (current === '0' || current === 'false') return '1';
		return '0';
	}

	function isEnabled(val: string): boolean {
		return val === '1' || val === 'true';
	}

	function hasChanged(key: string): boolean {
		const setting = settings.find(s => s.setting_key === key);
		return setting ? editValues[key] !== setting.setting_value : false;
	}

	async function handleSave(key: string) {
		savingKeys = { ...savingKeys, [key]: true };
		try {
			await updateSetting(key, editValues[key]);
			toast.success('Setting updated');
			await loadSettings();
		} catch {
			toast.error('Failed to update setting');
		} finally {
			savingKeys = { ...savingKeys, [key]: false };
		}
	}

	async function handleAdd() {
		adding = true;
		try {
			await addSetting(addForm);
			toast.success('Setting added');
			showAddModal = false;
			addForm = { setting_key: '', setting_value: '', description: '' };
			await loadSettings();
		} catch {
			toast.error('Failed to add setting');
		} finally {
			adding = false;
		}
	}
</script>

{#if loading}
	<div class="loading-state">
		<span class="spinner"></span>
		<p>Loading settings…</p>
	</div>
{:else if error}
	<div class="error-state">
		<p class="error-text">{error}</p>
		<button class="btn" onclick={() => loadSettings(true)}>Retry</button>
	</div>
{:else}
	<div class="page">
		<div class="top-bar">
			<div class="title-row">
				<div>
					<SettingsIcon size={20} />
					<h1>System Settings</h1>
					<p class="title-subtitle">Configure system preferences and defaults</p>
				</div>
				<button class="btn btn-primary" onclick={() => showAddModal = true}>
					<Plus size={16} />
					Add Setting
				</button>
			</div>
		</div>

		{#if settings.length === 0}
			<div class="empty-state">
				<SettingsIcon size={32} />
				<p>No settings found.</p>
			</div>
		{:else}
			<div class="card-grid">
				{#each settings as setting (setting.setting_id)}
					<div class="setting-card">
						<div class="card-header">
							<span class="setting-key">{setting.setting_key}</span>
						</div>
						{#if setting.description}
							<p class="setting-desc">{setting.description}</p>
						{/if}
						<div class="card-body">
							{#if isBooleanSetting(setting.setting_key)}
								<label class="toggle-switch">
									<input
										type="checkbox"
										checked={isEnabled(editValues[setting.setting_key])}
										onchange={() => {
											editValues[setting.setting_key] = toggleValue(editValues[setting.setting_key]);
											handleSave(setting.setting_key);
										}}
									/>
									<span class="toggle-slider"></span>
								</label>
								<span class="toggle-label">{isEnabled(editValues[setting.setting_key]) ? 'Enabled' : 'Disabled'}</span>
							{:else}
								<input
									class="setting-input"
									type="text"
									bind:value={editValues[setting.setting_key]}
								/>
								{#if hasChanged(setting.setting_key)}
									<button
										class="btn btn-save"
										onclick={() => handleSave(setting.setting_key)}
										disabled={savingKeys[setting.setting_key]}
									>
										{#if savingKeys[setting.setting_key]}
											<span class="spinner-sm"></span>
										{:else}
											<Save size={14} />
										{/if}
										Save
									</button>
								{/if}
							{/if}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
{/if}

{#if showAddModal}
	<div class="modal-overlay" onclick={() => showAddModal = false} role="presentation">
		<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog">
			<div class="modal-header">
				<h2>Add Setting</h2>
				<button class="btn-icon" onclick={() => showAddModal = false}>
					<X size={18} />
				</button>
			</div>
			<div class="modal-body">
				<label>
					Key
					<input type="text" bind:value={addForm.setting_key} placeholder="setting_key" />
				</label>
				<label>
					Value
					<input type="text" bind:value={addForm.setting_value} placeholder="setting_value" />
				</label>
				<label>
					Description
					<input type="text" bind:value={addForm.description} placeholder="Optional description" />
				</label>
			</div>
			<div class="modal-footer">
				<button class="btn" onclick={() => showAddModal = false}>Cancel</button>
				<button
					class="btn btn-primary"
					onclick={handleAdd}
					disabled={adding || !addForm.setting_key || !addForm.setting_value}
				>
					{#if adding}
						<span class="spinner-sm"></span>
					{/if}
					Add Setting
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.page {
		font-family: var(--font-sans);
	}

	/* ---------- Loading / Error ---------- */
	.loading-state,
	.error-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 40vh;
		gap: 1rem;
		color: var(--text-light);
		font-family: var(--font-sans);
	}
	.spinner {
		width: 28px;
		height: 28px;
		border: 2.5px solid var(--border);
		border-top-color: var(--primary);
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
	}
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
	.spinner-sm {
		width: 14px;
		height: 14px;
		border: 2px solid currentColor;
		border-top-color: transparent;
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
		display: inline-block;
	}
	.error-text {
		color: var(--danger, #e74c3c);
		font-size: 14px;
	}

	/* ---------- Top Bar ---------- */
	.top-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 2rem;
	}
	.title-row {
		display: flex;
		align-items: center;
		gap: 10px;
		color: var(--text-primary);
	}
	.title-row :global(svg) {
		color: var(--text-muted);
	}
	.title-subtitle { font-size: 13px; color: #9ca3af; margin: 2px 0 0; font-weight: 400; }
	h1 {
		font-size: 20px;
		font-weight: 700;
		color: var(--text-primary);
		letter-spacing: -0.5px;
		margin: 0;
	}

	/* ---------- Buttons ---------- */
	.btn {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		padding: 8px 16px;
		border: none;
		border-radius: var(--radius-lg, 8px);
		font-family: var(--font-sans);
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		background: var(--bg-hover);
		color: var(--text-primary);
		transition: background 0.15s ease;
	}
	.btn:hover {
		background: var(--border);
	}
	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
	.btn-primary {
		background: #e8c97e;
		color: #1a1a2e;
	}
	.btn-primary:hover {
		background: #dbb96a;
	}
	.btn-save {
		background: transparent;
		border: 1px solid #e8c97e;
		color: #1a1a2e;
		padding: 6px 12px;
		font-size: 12px;
		border-radius: 6px;
		flex-shrink: 0;
	}
	.btn-save:hover {
		background: #e8c97e;
	}
	.btn-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		border: none;
		border-radius: 6px;
		background: transparent;
		color: var(--text-muted);
		cursor: pointer;
		transition: background 0.15s ease;
	}
	.btn-icon:hover {
		background: var(--bg-hover);
		color: var(--text-primary);
	}

	/* ---------- Card Grid ---------- */
	.card-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 16px;
	}
	@media (max-width: 1024px) {
		.card-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}
	@media (max-width: 640px) {
		.card-grid {
			grid-template-columns: 1fr;
		}
	}

	.setting-card {
		background: var(--bg-card);
		border: 0.5px solid var(--border);
		border-radius: var(--radius-lg, 10px);
		padding: 1.25rem;
		transition: transform 0.18s ease, box-shadow 0.18s ease;
	}
	.setting-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.07);
	}

	/* ---------- Card Content ---------- */
	.card-header {
		margin-bottom: 6px;
	}
	.setting-key {
		font-family: var(--font-mono);
		font-weight: 700;
		font-size: 14px;
		color: #1a1a2e;
		word-break: break-all;
	}
	.setting-desc {
		font-size: 12px;
		color: var(--text-muted);
		margin: 4px 0 12px;
		line-height: 1.4;
	}
	.card-body {
		display: flex;
		gap: 8px;
		align-items: center;
	}
	.setting-input {
		flex: 1;
		padding: 8px 10px;
		border: 0.5px solid var(--border);
		border-radius: 6px;
		font-family: var(--font-mono);
		font-size: 13px;
		color: var(--text-primary);
		background: var(--bg-canvas);
		outline: none;
		transition: border-color 0.15s ease;
		min-width: 0;
	}
	.setting-input:focus {
		border-color: #e8c97e;
	}

	/* ---------- Toggle Switch ---------- */
	.toggle-switch {
		position: relative;
		display: inline-block;
		width: 44px;
		height: 24px;
		flex-shrink: 0;
		cursor: pointer;
	}
	.toggle-switch input {
		opacity: 0;
		width: 0;
		height: 0;
	}
	.toggle-slider {
		position: absolute;
		inset: 0;
		background: var(--border);
		border-radius: 24px;
		transition: background 0.2s;
	}
	.toggle-slider::before {
		content: '';
		position: absolute;
		width: 18px;
		height: 18px;
		left: 3px;
		bottom: 3px;
		background: #fff;
		border-radius: 50%;
		transition: transform 0.2s;
	}
	.toggle-switch input:checked + .toggle-slider {
		background: #e8c97e;
	}
	.toggle-switch input:checked + .toggle-slider::before {
		transform: translateX(20px);
	}
	.toggle-label {
		font-size: 12px;
		font-weight: 600;
		color: var(--text-muted);
	}

	/* ---------- Empty State ---------- */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem 2rem;
		color: var(--text-muted);
		gap: 12px;
		font-size: 14px;
	}

	/* ---------- Modal ---------- */
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.4);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
	}
	.modal {
		background: var(--bg-card);
		border-radius: var(--radius-lg, 12px);
		width: 420px;
		max-width: 90vw;
		box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
	}
	.modal-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.25rem 1.5rem;
		border-bottom: 0.5px solid var(--border);
	}
	.modal-header h2 {
		font-size: 16px;
		font-weight: 600;
		margin: 0;
		color: var(--text-primary);
	}
	.modal-body {
		padding: 1.25rem 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 14px;
	}
	.modal-body label {
		display: flex;
		flex-direction: column;
		gap: 4px;
		font-size: 12px;
		font-weight: 500;
		color: var(--text-muted);
	}
	.modal-body input {
		padding: 8px 10px;
		border: 0.5px solid var(--border);
		border-radius: 6px;
		font-family: var(--font-sans);
		font-size: 13px;
		color: var(--text-primary);
		background: var(--bg-canvas);
		outline: none;
	}
	.modal-body input:focus {
		border-color: #e8c97e;
	}
	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 8px;
		padding: 1rem 1.5rem;
		border-top: 0.5px solid var(--border);
	}

	/* ---------- Responsive ---------- */
	@media (max-width: 720px) {
		.top-bar {
			flex-wrap: wrap;
			gap: 10px;
		}
	}
</style>
