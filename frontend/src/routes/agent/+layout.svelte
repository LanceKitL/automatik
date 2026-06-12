<script lang="ts">
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Topbar from '$lib/components/Topbar.svelte';

	let { children } = $props();

	onMount(async () => {
		const ok = await auth.checkAuth();
		if (!ok || auth.role !== 'agent') {
			goto('/auth/login');
		}
	});
</script>
<head>
	<title>Sales Agent</title>
</head>
<div class="layout">
	<Sidebar />
	<div class="main-area">
		<Topbar />
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
		margin-left: 16rem;
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		background: var(--bg-main);
	}
	/* main {
		flex: 1;
		display: flex;
		flex-direction: column;
	} */
</style>
