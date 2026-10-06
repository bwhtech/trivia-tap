<template>
	<div class="relative shrink-0" :style="{ width: `${size}px`, height: `${size}px` }">
		<div
			class="drain-ring absolute inset-0 rounded-full"
			:style="{
				'--p': percent,
				'--drain-color': color,
				'--ring-w': `${Math.max(4, Math.round(size * 0.09))}px`,
			}"
			:data-urgent="seconds <= 5 && seconds > 0"
		/>
		<span
			class="absolute inset-0 grid place-items-center font-mono font-bold tabular-nums text-paper"
			:style="{ fontSize: `${Math.round(size * 0.34)}px` }"
		>
			{{ seconds }}
		</span>
	</div>
</template>

<script setup>
defineProps({
	percent: { type: Number, default: 0 },
	seconds: { type: Number, default: 0 },
	size: { type: Number, default: 64 },
	color: { type: String, default: "rgb(var(--alert))" },
});
</script>
