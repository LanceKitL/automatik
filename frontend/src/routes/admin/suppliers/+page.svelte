<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	onMount(() => {
		goto('/admin/vehicles?tab=suppliers', { replaceState: true });
	});
</script>

<p>Redirecting to Inventory…</p>
