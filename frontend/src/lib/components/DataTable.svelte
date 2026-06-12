<script lang="ts">
	import type { Snippet } from 'svelte';

	type Column =
		| string
		| { key: string; label: string };

	let {
		columns,
		children
	}: {
		columns: Column[];
		children: Snippet;
	} = $props();

	function colLabel(col: Column): string {
		return typeof col === 'string' ? col : col.label;
	}
</script>

<div class="wrapper">
	<table>
		<thead>
			<tr>
				{#each columns as col}
					<th>{colLabel(col)}</th>
				{/each}
			</tr>
		</thead>
		<tbody>
			{@render children()}
		</tbody>
	</table>
</div>

<style>
	.wrapper {
		overflow-x: auto;
	}
	.wrapper :global(table) {
		width: 100%;
		border-collapse: collapse;
	}
	.wrapper :global(th),
	.wrapper :global(td) {
		text-align: left;
		padding: 0.5rem;
		border-bottom: 1px solid var(--border);
	}
</style>
