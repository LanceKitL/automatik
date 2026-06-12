<script lang="ts">
    import {auth} from '$lib/stores/auth.svelte'

    let {title}: {title: string} = $props();
</script>


<header>
    <h1>{title}</h1>

    <span>{auth.user?.email}</span>
    <button onclick={() => auth.logout()}>Sign out</button>
</header>

<style>
    header { display: flex; align-items: center; gap: 1rem; padding: 1rem; border-bottom: 1px solid var(--border); }
	header h1 { margin: 0; flex: 1; }
</style>