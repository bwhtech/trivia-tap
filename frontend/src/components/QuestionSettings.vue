<template>
	<aside class="flex flex-col gap-6">
		<label class="flex flex-col gap-2">
			<span class="label">Time limit</span>
			<span class="flex items-center gap-2">
				<input
					v-model.number="question.time_limit"
					type="number"
					:min="MIN_SECONDS"
					:max="MAX_SECONDS"
					class="field !w-24"
					:placeholder="String(defaultSeconds)"
				/>
				<span class="text-sm text-paper/50">seconds</span>
			</span>
		</label>

		<div class="flex flex-col gap-2">
			<span id="points-label" class="label">Points</span>
			<div class="grid grid-cols-3 gap-1.5" role="group" aria-labelledby="points-label">
				<button
					v-for="(label, value) in POINTS"
					:key="value"
					class="ctl !px-2"
					:data-on="question.points_multiplier === value"
					:aria-pressed="question.points_multiplier === value"
					@click="question.points_multiplier = value"
				>
					{{ label }}
				</button>
			</div>
		</div>

		<div v-if="showExplanation" class="flex flex-col gap-2">
			<span class="label">Explanation</span>
			<textarea
				v-model="question.explanation"
				rows="3"
				class="field"
				placeholder="Why is that the answer?"
				aria-label="Explanation"
			/>
			<ImageField
				v-model="question.explanation_image"
				label="explanation picture"
				class="h-32"
			/>
		</div>

		<div class="mt-auto flex flex-wrap gap-2">
			<button class="ctl gap-1.5" @click="emit('duplicate')">
				<LucideCopy class="size-4" />
				Duplicate
			</button>
			<button
				class="ctl gap-1.5 hover:!border-alert hover:!text-alert"
				@click="emit('remove')"
			>
				<LucideTrash2 class="size-4" />
				Delete
			</button>
		</div>
	</aside>
</template>

<script setup>
import { MAX_SECONDS, MIN_SECONDS } from "@/quiz";
import ImageField from "@/components/ImageField.vue";

const POINTS = { 0: "None", 1: "Normal", 2: "Double" };

defineProps({
	question: { type: Object, required: true },
	defaultSeconds: { type: Number, required: true },
	showExplanation: { type: Boolean, default: false },
});
const emit = defineEmits(["duplicate", "remove"]);
</script>

<style scoped>
.label {
	font-family: "Martian Mono", ui-monospace, monospace;
	font-size: 11px;
	text-transform: uppercase;
	letter-spacing: 0.2em;
	color: rgb(var(--paper) / 0.45);
}
</style>
