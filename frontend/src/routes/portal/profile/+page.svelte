<script lang="ts">
	import { onMount } from 'svelte';
	import { getPortalProfile, updatePortalProfile, changePassword } from '$lib/services/api';
	import { toast } from 'svelte-sonner';
	import { User, Mail, Phone, MapPin, Lock, Save, Camera } from '@lucide/svelte';
	import Loader from '$lib/components/Loader.svelte';

	let loading = $state(true);
	let saving = $state(false);
	let form = $state({ name: '', email: '', phone: '', address: '' });
	let passwords = $state({ current: '', new: '', confirm: '' });
	let changingPwd = $state(false);

	onMount(async () => {
		try {
			const res = await getPortalProfile();
			const p = res.profile ?? {};
			const u = res.user ?? {};
			form.name = (p.full_name as string) ?? '';
			form.email = (u.email as string) ?? '';
			form.phone = (p.phone_number as string) ?? '';
			form.address = (p.address as string) ?? '';
		} catch {
			// ignore
		} finally {
			loading = false;
		}
	});

	async function saveProfile() {
		saving = true;
		try {
			await updatePortalProfile({
				full_name: form.name,
				phone_number: form.phone,
				address: form.address,
			});
			toast.success('Profile saved');
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to save profile');
		} finally {
			saving = false;
		}
	}

	async function handleChangePassword() {
		if (!passwords.current || !passwords.new) { toast.error('Fill in all fields.'); return; }
		if (passwords.new.length < 6) { toast.error('New password must be at least 6 characters.'); return; }
		if (passwords.new !== passwords.confirm) { toast.error('Passwords do not match.'); return; }
		changingPwd = true;
		try {
			await changePassword(passwords.current, passwords.new, passwords.confirm);
			toast.success('Password changed successfully.');
			passwords = { current: '', new: '', confirm: '' };
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to change password.');
		} finally {
			changingPwd = false;
		}
	}
</script>

<div class="page-header">
	<h1>My Profile</h1>
	<p class="subtitle">Manage your personal information and security settings.</p>
</div>

{#if loading}
	<div class="loader"><Loader /></div>
{:else}
	<div class="profile-grid">
		<div class="card profile-card">
			<div class="avatar-section">
				<div class="avatar">
					<User size={36} />
					<button class="avatar-edit"><Camera size={16} /></button>
				</div>
				<div class="avatar-name">{form.name || 'User'}</div>
				<div class="avatar-role">Customer</div>
			</div>
			<div class="profile-stats">
				<div class="stat"><span class="stat-value">{form.email || '—'}</span><span class="stat-label">Email</span></div>
			</div>
		</div>

		<div class="card form-card">
			<div class="card-header"><h2><User size={16} /> Personal Information</h2></div>
			<div class="card-body">
				<div class="form-row">
					<div class="form-group">
						<label><User size={14} /> Full Name</label>
						<input type="text" bind:value={form.name} placeholder="Your name" />
					</div>
					<div class="form-group">
						<label><Mail size={14} /> Email</label>
						<input type="email" bind:value={form.email} placeholder="email@example.com" disabled />
					</div>
				</div>
				<div class="form-row">
					<div class="form-group">
						<label><Phone size={14} /> Phone</label>
						<input type="tel" bind:value={form.phone} placeholder="+63 9XX XXX XXXX" />
					</div>
					<div class="form-group">
						<label><MapPin size={14} /> Address</label>
						<input type="text" bind:value={form.address} placeholder="Your address" />
					</div>
				</div>
				<div class="form-actions">
					<button class="btn-primary" onclick={saveProfile} disabled={saving}>
						<Save size={16} /> {saving ? 'Saving…' : 'Save Changes'}
					</button>
				</div>
			</div>
		</div>

		<div class="card form-card">
			<div class="card-header"><h2><Lock size={16} /> Change Password</h2></div>
			<div class="card-body">
				<div class="form-row">
					<div class="form-group">
						<label>Current Password</label>
						<input type="password" bind:value={passwords.current} placeholder="••••••••" />
					</div>
				</div>
				<div class="form-row">
					<div class="form-group">
						<label>New Password</label>
						<input type="password" bind:value={passwords.new} placeholder="Min. 6 characters" />
					</div>
					<div class="form-group">
						<label>Confirm New Password</label>
						<input type="password" bind:value={passwords.confirm} placeholder="Re-enter new password" />
					</div>
				</div>
				<div class="form-actions">
					<button class="btn-primary" onclick={handleChangePassword} disabled={changingPwd}>
						<Lock size={16} /> {changingPwd ? 'Changing…' : 'Change Password'}
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	.page-header { margin-bottom:24px; }
	h1 { font-size:24px; font-weight:700; color:var(--text-dark); margin:0; }
	.subtitle { font-size:14px; color:var(--text-muted); margin-top:4px; }
	.loader { display:grid; place-items:center; height:50vh; }
	.profile-grid { display:flex; flex-direction:column; gap:16px; }
	.card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); overflow:hidden; box-shadow:var(--shadow-sm); }
	.profile-card { text-align:center; padding:32px 20px; }
	.avatar-section { margin-bottom:16px; }
	.avatar { width:80px; height:80px; border-radius:50%; background:var(--primary-bg); color:var(--primary); display:flex; align-items:center; justify-content:center; margin:0 auto 12px; position:relative; }
	.avatar-edit { position:absolute; bottom:0; right:0; width:28px; height:28px; border-radius:50%; background:var(--primary); color:var(--text-white); border:2px solid var(--bg-card); display:flex; align-items:center; justify-content:center; cursor:pointer; }
	.avatar-name { font-size:18px; font-weight:700; color:var(--text-dark); }
	.avatar-role { font-size:12px; color:var(--text-muted); margin-top:4px; }
	.profile-stats { margin-top:12px; }
	.stat { display:flex; flex-direction:column; gap:2px; }
	.stat-value { font-size:13px; color:var(--text-dark); }
	.stat-label { font-size:11px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; }
	.card-header { display:flex; align-items:center; gap:8px; padding:14px 20px; background:var(--bg-muted); border-bottom:1px solid var(--border); }
	.card-header h2 { font-size:14px; font-weight:700; margin:0; display:flex; align-items:center; gap:6px; color:var(--text-dark); }
	.card-body { padding:20px; }
	.form-row { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px; }
	.form-group { display:flex; flex-direction:column; gap:6px; }
	.form-group label { font-size:12px; font-weight:600; color:var(--text-dark); display:flex; align-items:center; gap:4px; }
	.form-group input { padding:9px 12px; border:1px solid var(--border); border-radius:var(--radius-sm); font-size:13px; background:var(--bg-card); color:var(--text-dark); }
	.form-group input:focus { outline:none; border-color:var(--primary); }
	.form-group input:disabled { opacity:0.6; }
	.form-actions { display:flex; align-items:center; gap:12px; margin-top:4px; }
	.btn-primary { display:inline-flex; align-items:center; gap:6px; padding:9px 18px; background:var(--primary); color:var(--text-white); border:none; border-radius:var(--radius-sm); font-size:13px; font-weight:600; cursor:pointer; }
	.btn-primary:disabled { opacity:0.6; cursor:not-allowed; }
	.btn-primary:hover:not(:disabled) { opacity:0.9; }
	.saved-msg { font-size:12px; color:#059669; font-weight:600; }
	.alert-error { background:#fef2f2; color:#dc2626; padding:8px 12px; border-radius:var(--radius-sm); font-size:12px; margin-bottom:12px; }
	.alert-success { background:#d1fae5; color:#065f46; padding:8px 12px; border-radius:var(--radius-sm); font-size:12px; margin-bottom:12px; }
</style>
