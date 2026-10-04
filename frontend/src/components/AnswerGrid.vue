<template>
	<div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
		<div
			v-for="shape in visibleShapes"
			:key="shape.id"
			class="flex items-center gap-3 rounded-2xl px-4 py-4 transition sm:gap-5 sm:px-6 sm:py-7"
			:class="[shape.fill, dimmed(shape.id) ? 'opacity-25' : '']"
		>
			<svg class="size-7 shrink-0 fill-sunk/55 sm:size-9" viewBox="0 0 24 24">
				<path :d="shape.path" />
			</svg>
			<span class="flex-1 font-display text-lg font-extrabold text-sunk sm:text-2xl">
				{{ options[Number(shape.id) - 1] }}
			</span>
			<span v-if="revealed(shape.id)" class="text-3xl text-sunk">✓</span>
		</div>
	</div>
</template>

<script setup>
import { computed } from "vue";
import { SHAPES } from "@/game";

const props = defineProps({
	options: { type: Array, default: () => [] },
	// null until the answer is out: nothing is ticked and nothing is dimmed
	correctOption: { type: [String, Number], default: null },
});

const visibleShapes = computed(() =>
	SHAPES.filter((shape) => props.options[Number(shape.id) - 1])
);

const revealed = (optionId) => optionId === String(props.correctOption);
const dimmed = (optionId) => props.correctOption != null && !revealed(optionId);
</script>
