<script lang="ts">
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Topbar from '$lib/components/Topbar.svelte';
	import { connectSocket } from '$lib/stores/socket.svelte';

	let { children } = $props();

	onMount(async () => {
		connectSocket();
		const ok = await auth.checkAuth();
		if (!ok || auth.role !== 'agent') {
			goto('/auth/login');
		}
	});
</script>
<svelte:head>
	<title>Agent Portal</title>
</svelte:head>
<div class="layout">
	<Sidebar />
	<div class="main-area">
	<Topbar/>
		<main>
			{@render children()}
		</main>
	</div>
</div>

<style>
	.layout {
		display: flex;
	}	
	
	.main-area {
		flex: 1;
		display: flex;
		flex-direction: column;
		background: var(--bg-main);
		min-height: 100vh;
		margin-left: 16rem;
	}
	main {
		flex: 1;
		padding: 2rem;
		background: #f5f7fb;
	}
</style>
