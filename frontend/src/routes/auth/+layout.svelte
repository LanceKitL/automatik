<script>
	let { children } = $props();
</script>

<a href="/" class="back-home">← Back to Home</a>
{@render children()}

<style>
	.back-home {
		position: fixed;
		top: 1rem;
		left: 1rem;
		z-index: 10;
		font-family: var(--font-sans);
		font-size: 14px;
		color: var(--primary);
		text-decoration: none;
		font-weight: 600;
	}
	.back-home:hover {
		text-decoration: underline;
	}
</style>
