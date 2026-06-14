<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { resetPassword } from '$lib/services/api';

	let token_id = $derived($page.url.searchParams.get('token_id') ?? '');
	let raw_token = $derived($page.url.searchParams.get('raw_token') ?? '');

	let new_password = $state('');
	let confirm_password = $state('');
	let error = $state('');
	let message = $state('');
	let loading = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		message = '';
		loading = true;

		try {
			const res = await resetPassword({
				token_id,
				raw_token,
				new_password,
				confirm_password
			});
			message = res.message;
			setTimeout(() => goto('/auth/login'), 2000);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Something went wrong';
		} finally {
			loading = false;
		}
	}
</script>

<form onsubmit={handleSubmit}>
	<h1>Reset Password</h1>

	{#if !token_id || !raw_token}
		<p class="error">Invalid or missing reset link. Please request a new password reset.</p>
		<p><a href="/auth/forgot-password">Request new reset link</a></p>
	{:else if message}
		<p class="success">{message}</p>
		<p>Redirecting to sign in…</p>
	{:else}
		{#if error}
			<p class="error">{error}</p>
		{/if}

		<label>
			New Password
			<input
				type="password"
				bind:value={new_password}
				placeholder="new password"
				required
				disabled={loading}
			/>
		</label>

		<label>
			Confirm Password
			<input
				type="password"
				bind:value={confirm_password}
				placeholder="confirm password"
				required
				disabled={loading}
			/>
		</label>

		<button type="submit" disabled={loading}>
			{loading ? 'Resetting…' : 'Reset Password'}
		</button>
	{/if}
</form>

<style>
	form {
		max-width: 24rem;
		margin: 4rem auto;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	label {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}
	input {
		padding: 0.5rem;
		font-size: 1rem;
	}
	button {
		padding: 0.5rem;
		font-size: 1rem;
		cursor: pointer;
	}
	.error {
		color: #c00;
		background: #fee;
		padding: 0.5rem;
		border-radius: 4px;
	}
	.success {
		color: #080;
		background: #efe;
		padding: 0.5rem;
		border-radius: 4px;
	}
	h1 {
		text-align: center;
	}
</style>
