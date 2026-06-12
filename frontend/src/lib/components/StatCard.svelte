<script lang="ts">
	let { value, label }: { value: string | number; label: string } = $props();
</script>

<div class="card">
	<strong>{value}</strong>
	<span>{label}</span>
</div>

<style>
	.card {
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		padding: 1.5rem;
		text-align: center;
		background: var(--bg-muted);
	}
	strong {
		display: block;
		font-size: 2rem;
	}
</style>
