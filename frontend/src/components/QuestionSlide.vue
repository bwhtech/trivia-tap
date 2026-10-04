<template>
	<div class="mx-auto flex w-full max-w-4xl flex-col gap-4 sm:gap-6">
		<textarea
			ref="questionInput"
			v-model="question.question_text"
			rows="1"
			class="question-text field !bg-dusk text-center font-display text-2xl font-extrabold leading-tight sm:text-4xl"
			placeholder="Type your question"
			aria-label="Question"
		/>

		<ImageField
			v-model="question.image"
			label="picture"
			class="mx-auto h-40 w-full max-w-lg sm:h-60"
		/>

		<div class="grid gap-3 sm:grid-cols-2">
			<div
				v-for="shape in SHAPES"
				:key="shape.id"
				class="flex items-center gap-3 rounded-2xl px-4 py-4 ring-offset-4 ring-offset-night transition sm:gap-4 sm:py-6"
				:class="[shape.fill, isCorrect(shape.id) ? 'ring-4 ring-paper' : '']"
			>
				<svg class="size-7 shrink-0 fill-sunk/55" viewBox="0 0 24 24" aria-hidden="true">
					<path :d="shape.path" />
				</svg>
				<input
					v-model="question[`option_${shape.id}`]"
					class="min-w-0 flex-1 border-0 bg-transparent font-display text-lg font-extrabold text-sunk placeholder:text-sunk/45 focus:outline-none focus:ring-0 sm:text-xl"
					:placeholder="`Answer ${shape.id}`"
					:aria-label="`Answer ${shape.id}`"
				/>
				<button
					class="grid size-9 shrink-0 place-items-center rounded-full border-[3px] transition"
					:class="
						isCorrect(shape.id)
							? 'border-sunk bg-sunk text-card'
							: 'border-sunk/40 text-transparent hover:border-sunk hover:text-sunk/50'
					"
					:aria-pressed="isCorrect(shape.id)"
					:aria-label="`Answer ${shape.id} is correct`"
					@click="question.correct_option = shape.id"
				>
					<LucideCheck class="size-5" :stroke-width="3" />
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue";
import { SHAPES } from "@/game";
import ImageField from "@/components/ImageField.vue";

const props = defineProps({
	question: { type: Object, required: true },
});

const questionInput = ref(null);

const isCorrect = (optionId) => props.question.correct_option === optionId;

defineExpose({ focus: () => questionInput.value?.focus() });
</script>

<style scoped>
/* grows with the text instead of scrolling inside a two-line box */
.question-text {
	field-sizing: content;
	padding-block: 1.5rem;
	resize: none;
}

.question-text:not(:hover, :focus) {
	border-color: transparent;
}
</style>
