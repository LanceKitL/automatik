<script lang="ts">
	import { toast } from 'svelte-sonner';
	import type { CreateUserPayload } from '$lib/services/api';

	let {
		show,
		user,
		onClose,
		onSaved
	}: {
		show: boolean;
		user: Record<string, unknown> | null;
		onClose: () => void;
		onSaved: () => void;
	} = $props();

	let saving = $state(false);

	let form = $state<CreateUserPayload>({
		username: '',
		email: '',
		password: '',
		role: 'customer',
		full_name: '',
		phone_number: '',
		address: '',
		city: '',
		province: '',
		zip_code: '',
	});

	$effect(() => {
		if (user) {
			form.username = (user.username as string) ?? '';
			form.email = (user.email as string) ?? '';
			form.password = '';
			form.role = (user.role as string) ?? 'customer';
			form.full_name = (user.full_name as string) ?? '';
			form.phone_number = (user.phone_number as string) ?? '';
			form.address = (user.address as string) ?? '';
			form.city = (user.city as string) ?? '';
			form.province = (user.province as string) ?? '';
			form.zip_code = (user.zip_code as string) ?? '';
		} else {
			form.username = '';
			form.email = '';
			form.password = '';
			form.role = 'customer';
			form.full_name = '';
			form.phone_number = '';
			form.address = '';
			form.city = '';
			form.province = '';
			form.zip_code = '';
		}
	});

	async function handleSubmit(e: Event) {
		e.preventDefault();
		saving = true;

		try {
			const { createUser, updateUser, updateUserProfile } = await import('$lib/services/api');

			if (user) {
				// Edit mode
				const payload: Record<string, unknown> = {};
				if (form.username !== user.username) payload.username = form.username;
				if (form.email !== user.email) payload.email = form.email;
				if (form.role !== user.role) payload.role = form.role;
				if (Object.keys(payload).length > 0) {
					await updateUser(user.user_id as number, payload);
				}

				const profilePayload: Record<string, unknown> = {};
				if (form.full_name !== user.full_name) profilePayload.full_name = form.full_name;
				if (form.phone_number !== (user.phone_number ?? '')) profilePayload.phone_number = form.phone_number || null;
				if (form.address !== (user.address ?? '')) profilePayload.address = form.address || null;
				if (form.city !== (user.city ?? '')) profilePayload.city = form.city || null;
				if (form.province !== (user.province ?? '')) profilePayload.province = form.province || null;
				if (form.zip_code !== (user.zip_code ?? '')) profilePayload.zip_code = form.zip_code || null;
				if (Object.keys(profilePayload).length > 0) {
					await updateUserProfile(user.user_id as number, profilePayload);
				}

				toast.success('User updated.');
				onSaved();
				onClose();
			} else {
				// Create mode — password is optional (auto-generated, user sets via email link)
				await createUser({
					username: form.username,
					email: form.email,
					password: form.password || undefined,
					role: form.role,
					full_name: form.full_name,
				});
				toast.success('User created. An email has been sent with instructions to set their password.');
				onSaved();
				onClose();
			}
		} catch (e) {
			toast.error((e as Error).message || 'Failed to save user.');
		} finally {
			saving = false;
		}
	}
</script>

{#if show}
	<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
	<div class="overlay" onclick={onClose}>
		<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<h2>{user ? 'Edit User' : 'Create User'}</h2>

			<form onsubmit={handleSubmit}>
				<div class="grid">
					<label>
						Username *
						<input type="text" bind:value={form.username} required disabled={!!user} />
					</label>
					<label>
						Email *
						<input type="email" bind:value={form.email} required />
					</label>
					<label>
						Password {#if user}(leave blank to keep){/if} *
						<input type="password" bind:value={form.password} required={!user} />
					</label>
					<label>
						Role *
						<select bind:value={form.role} required>
							<option value="admin">Admin</option>
							<option value="agent">Sales Agent</option>
							<option value="customer">Customer</option>
							<option value="finance_staff">Finance Staff</option>
							<option value="service_staff">Service Staff</option>
						</select>
					</label>
				</div>

				<fieldset>
					<legend>Profile</legend>
					<div class="grid">
						<label>
							Full Name
							<input type="text" bind:value={form.full_name} />
						</label>
						<label>
							Phone
							<input type="text" bind:value={form.phone_number} />
						</label>
						<label>
							Address
							<input type="text" bind:value={form.address} />
						</label>
						<label>
							City
							<input type="text" bind:value={form.city} />
						</label>
						<label>
							Province
							<input type="text" bind:value={form.province} />
						</label>
						<label>
							Zip Code
							<input type="text" bind:value={form.zip_code} />
						</label>
					</div>
				</fieldset>

				<div class="actions">
					<button type="button" onclick={onClose} disabled={saving}>Cancel</button>
					<button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save'}</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<style>
	.overlay {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.4);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}
	.modal {
		background: var(--bg-card);
		border-radius: var(--radius-md);
		padding: 24px;
		max-width: 600px;
		width: 90%;
		max-height: 90vh;
		overflow-y: auto;
	}
	h2 { margin: 0 0 16px; }
	.grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 12px;
		margin-bottom: 16px;
	}
	label {
		display: flex;
		flex-direction: column;
		font-size: 0.875rem;
		gap: 4px;
	}
	input, select {
		padding: 8px;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		font-size: 0.875rem;
	}
	fieldset {
		border: 1px solid var(--border-light);
		border-radius: var(--radius-sm);
		padding: 12px;
		margin-bottom: 16px;
	}
	legend { font-weight: 600; font-size: 0.875rem; }
	.actions {
		display: flex;
		gap: 8px;
		justify-content: flex-end;
	}
	button {
		padding: 8px 16px;
		border: none;
		border-radius: var(--radius-sm);
		cursor: pointer;
		font-size: 0.875rem;
	}
	button[type="submit"] { background: var(--primary); color: var(--text-white); }
	button[type="submit"]:disabled { opacity: 0.6; }
	button[type="button"] { background: var(--bg-hover); }
</style>
