<script lang="ts">
	let { onAnimationEnd }: { onAnimationEnd: () => void } = $props();

	let visible = $state(false);

	$effect(() => {
		requestAnimationFrame(() => visible = true);
		const timer = setTimeout(() => onAnimationEnd(), 2000);
		return () => clearTimeout(timer);
	});
</script>

<div class="overlay" class:visible>
	<div class="circle">
		<svg width="80" height="80" viewBox="0 0 80 80">
			<circle class="circle-bg" cx="40" cy="40" r="36" fill="none" stroke="#d1fae5" stroke-width="6" />
			<circle class="circle-fg" cx="40" cy="40" r="36" fill="none" stroke="#059669" stroke-width="6"
				stroke-linecap="round" stroke-dasharray="226" stroke-dashoffset="226" />
			<polyline class="check" points="24,42 36,54 56,30" fill="none" stroke="#059669" stroke-width="6"
				stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="50" stroke-dashoffset="50" />
		</svg>
	</div>
	<p class="text">Payment Successful!</p>
</div>

<style>
	.overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		z-index: 200;
		opacity: 0;
		transition: opacity 0.3s;
	}
	.overlay.visible {
		opacity: 1;
	}
	.circle {
		transform: scale(0);
		transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
	}
	.overlay.visible .circle {
		transform: scale(1);
	}
	.circle-bg {
		opacity: 0;
		animation: fadeIn 0.3s 0.1s forwards;
	}
	.circle-fg {
		animation: drawCircle 0.5s 0.3s ease-out forwards;
	}
	.check {
		animation: drawCheck 0.35s 0.7s ease-out forwards;
	}
	.text {
		color: #fff;
		font-size: 20px;
		font-weight: 600;
		margin-top: 24px;
		opacity: 0;
		animation: fadeIn 0.3s 1s forwards;
	}
	@keyframes drawCircle {
		to { stroke-dashoffset: 0; }
	}
	@keyframes drawCheck {
		to { stroke-dashoffset: 0; }
	}
	@keyframes fadeIn {
		to { opacity: 1; }
	}
</style>
