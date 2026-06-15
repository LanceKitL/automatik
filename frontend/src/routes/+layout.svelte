<script>
	import favicon from '$lib/assets/favicon.svg';
	import '../app.css';
	import { Toaster } from 'svelte-sonner';

	let { children } = $props();
</script>
<svelte:head>
	<title>AutoMatik</title>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
<Toaster richColors closeButton />
