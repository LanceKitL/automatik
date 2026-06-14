<script>
	import favicon from '$lib/assets/favicon.svg';
	import '../app.css';
	import { Toaster } from 'svelte-sonner';

	let { children } = $props();
</script>
<header>
	<title>Homepage</title>
</header>
<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
<Toaster richColors closeButton />
