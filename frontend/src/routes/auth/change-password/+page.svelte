<script lang="ts">
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import { changePassword } from '$lib/services/api';
	import { toast } from 'svelte-sonner';
	import { Eye, EyeClosed, Lock, KeyRound, ShieldCheck } from '@lucide/svelte';

	let currentPassword = $state('');
	let newPassword = $state('');
	let confirmPassword = $state('');
	let loading = $state(false);

	let showCurrent = $state(false);
	let showNew = $state(false);
	let showConfirm = $state(false);

	let passwordStrength = $derived.by(() => {
		const p = newPassword;
		if (!p) return { label: '', pct: 0, color: '' };
		let score = 0;
		if (p.length >= 6) score += 20;
		if (p.length >= 10) score += 10;
		if (/[a-z]/.test(p)) score += 15;
		if (/[A-Z]/.test(p)) score += 15;
		if (/[0-9]/.test(p)) score += 20;
		if (/[^a-zA-Z0-9]/.test(p)) score += 20;
		if (score < 40) return { label: 'Weak', pct: score, color: '#ef4444' };
		if (score < 70) return { label: 'Medium', pct: score, color: '#f59e0b' };
		return { label: 'Strong', pct: score, color: '#10b981' };
	});

	let isFirstLogin = $derived(auth.mustResetPassword);
	let mismatch = $derived(confirmPassword && newPassword !== confirmPassword);

	onMount(() => {
		if (!auth.isAuthenticated) goto('/auth/login');
	});

	async function handleSubmit(e: Event) {
		e.preventDefault();
		if (!currentPassword || !newPassword || !confirmPassword) {
			toast.error('Please fill in all fields.');
			return;
		}
		if (newPassword.length < 6) {
			toast.error('New password must be at least 6 characters.');
			return;
		}
		if (newPassword !== confirmPassword) {
			toast.error('Passwords do not match.');
			return;
		}
		if (newPassword === currentPassword) {
			toast.error('New password cannot be the same as your current password.');
			return;
		}
		loading = true;
		try {
			await changePassword(currentPassword, newPassword, confirmPassword);
			toast.success('Password changed successfully!');
			auth.clearPendingReset();

			// Redirect to the appropriate dashboard
			const role = auth.role;
			const routes: Record<string, string> = {
				admin: '/admin',
				agent: '/agent',
				customer: '/portal',
				finance_staff: '/finance_staff',
				service_staff: '/service_staff',
				service_advisor: '/service_staff'
			};
			goto(role ? routes[role] || '/' : '/');
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Failed to change password.');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>{isFirstLogin ? 'Set Your Password' : 'Change Password'}</title>
</svelte:head>

<div class="page">
	<div class="card">
		<div class="card-icon">
			{#if isFirstLogin}
				<ShieldCheck size={32} />
			{:else}
				<Lock size={32} />
			{/if}
		</div>

		<h1>{isFirstLogin ? 'Set Your Password' : 'Change Password'}</h1>

		{#if isFirstLogin}
			<p class="subtitle">Welcome! For security, please set a new password to continue.</p>
		{:else}
			<p class="subtitle">Enter your current password and choose a new one.</p>
		{/if}

		<form onsubmit={handleSubmit}>
			<div class="field">
				<label for="current">Current Password</label>
				<div class="input-wrap">
					<input
						id="current"
						type={showCurrent ? 'text' : 'password'}
						bind:value={currentPassword}
						placeholder="Enter current password"
						autocomplete="current-password"
						disabled={loading}
					/>
					<button type="button" class="toggle" onclick={() => showCurrent = !showCurrent} tabindex="-1">
						{#if showCurrent}<EyeClosed size={18} />{:else}<Eye size={18} />{/if}
					</button>
				</div>
			</div>

			<div class="field">
				<label for="new-pw">New Password</label>
				<div class="input-wrap">
					<input
						id="new-pw"
						type={showNew ? 'text' : 'password'}
						bind:value={newPassword}
						placeholder="Min. 6 characters"
						autocomplete="new-password"
						disabled={loading}
					/>
					<button type="button" class="toggle" onclick={() => showNew = !showNew} tabindex="-1">
						{#if showNew}<EyeClosed size={18} />{:else}<Eye size={18} />{/if}
					</button>
				</div>
				{#if newPassword}
					<div class="strength-bar">
						<div class="strength-fill" style="width:{passwordStrength.pct}%;background:{passwordStrength.color};"></div>
					</div>
					<span class="strength-label" style="color:{passwordStrength.color}">{passwordStrength.label}</span>
				{/if}
			</div>

			<div class="field">
				<label for="confirm-pw">Confirm New Password</label>
				<div class="input-wrap">
					<input
						id="confirm-pw"
						type={showConfirm ? 'text' : 'password'}
						bind:value={confirmPassword}
						placeholder="Re-enter new password"
						autocomplete="new-password"
						disabled={loading}
						class:error={mismatch}
					/>
					<button type="button" class="toggle" onclick={() => showConfirm = !showConfirm} tabindex="-1">
						{#if showConfirm}<EyeClosed size={18} />{:else}<Eye size={18} />{/if}
					</button>
				</div>
				{#if mismatch}
					<span class="field-error">Passwords do not match</span>
				{/if}
			</div>

			<button type="submit" class="btn-submit" disabled={loading || !!mismatch}>
				<KeyRound size={18} />
				{loading ? 'Updating…' : isFirstLogin ? 'Set Password & Continue' : 'Update Password'}
			</button>

			{#if !isFirstLogin}
				<a href="/" class="back-link">Back to Dashboard</a>
			{/if}
		</form>
	</div>
</div>

<style>
	.page {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		padding: 2rem;
		background: #f5f7fb;
		font-family: 'Syne', sans-serif;
	}
	.card {
		background: #fff;
		border-radius: 16px;
		padding: 2.5rem;
		width: 100%;
		max-width: 420px;
		box-shadow: 0 4px 24px rgba(0,0,0,0.06);
		text-align: center;
	}
	.card-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 56px;
		height: 56px;
		border-radius: 50%;
		background: #1a1a2e;
		color: #e8c97e;
		margin: 0 auto 1rem;
	}
	h1 {
		font-size: 20px;
		font-weight: 700;
		color: #1a1a2e;
		margin: 0 0 0.35rem;
	}
	.subtitle {
		font-size: 13px;
		color: #9ca3af;
		margin: 0 0 1.5rem;
		line-height: 1.5;
	}
	form {
		text-align: left;
		display: flex;
		flex-direction: column;
		gap: 1.15rem;
	}
	.field {
		display: flex;
		flex-direction: column;
		gap: 5px;
	}
	.field label {
		font-size: 12px;
		font-weight: 600;
		color: #374151;
		letter-spacing: 0.3px;
		text-transform: uppercase;
	}
	.input-wrap {
		position: relative;
	}
	.input-wrap input {
		width: 100%;
		padding: 10px 40px 10px 12px;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		font-family: 'Syne', sans-serif;
		font-size: 13px;
		color: #1a1a2e;
		background: #f9fafb;
		outline: none;
		box-sizing: border-box;
		transition: border-color 0.15s;
	}
	.input-wrap input:focus {
		border-color: #7c9df7;
		background: #fff;
	}
	.input-wrap input.error {
		border-color: #ef4444;
	}
	.toggle {
		position: absolute;
		right: 10px;
		top: 50%;
		transform: translateY(-50%);
		background: none;
		border: none;
		color: #9ca3af;
		cursor: pointer;
		display: flex;
		align-items: center;
		padding: 4px;
		border-radius: 4px;
	}
	.toggle:hover { color: #374151; }
	.strength-bar {
		height: 4px;
		background: #e5e7eb;
		border-radius: 2px;
		overflow: hidden;
	}
	.strength-fill {
		height: 100%;
		border-radius: 2px;
		transition: width 0.2s, background 0.2s;
	}
	.strength-label {
		font-size: 11px;
		font-weight: 600;
	}
	.field-error {
		font-size: 11px;
		color: #ef4444;
		font-weight: 500;
	}
	.btn-submit {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		width: 100%;
		padding: 11px;
		background: #1a1a2e;
		color: #e8c97e;
		border: none;
		border-radius: 8px;
		font-family: 'Syne', sans-serif;
		font-size: 14px;
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.15s;
		margin-top: 0.25rem;
	}
	.btn-submit:hover:not(:disabled) { opacity: 0.85; }
	.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
	.back-link {
		display: block;
		text-align: center;
		font-size: 13px;
		color: #7c9df7;
		text-decoration: none;
		margin-top: 0.25rem;
	}
	.back-link:hover { text-decoration: underline; }
</style>
