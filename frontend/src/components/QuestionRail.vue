<template>
	<nav
		class="flex shrink-0 gap-3 overflow-x-auto border-b border-haze p-3 md:w-60 md:flex-col md:overflow-y-auto md:overflow-x-hidden md:border-b-0 md:border-r md:p-4"
		aria-label="Questions"
	>
		<TransitionGroup
			tag="ol"
			name="rail"
			class="flex gap-3 md:flex-col"
			@dragover.prevent
			@drop.prevent
		>
			<li
				v-for="(question, index) in questions"
				:key="question.key"
				class="group relative w-40 shrink-0 md:w-auto"
				:class="{ 'opacity-40': question === dragged }"
				draggable="true"
				@dragstart="startDrag($event, question)"
				@dragenter="dragOver(index)"
				@dragend="dragged = null"
			>
				<p
					class="mb-1 flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-[0.2em]"
					:class="question === selected ? 'text-accent' : 'text-paper/40'"
				>
					{{ index + 1 }}
					<span
						v-if="questionProblem(question)"
						class="size-1.5 rounded-full bg-alert"
						:title="`Question ${index + 1} ${questionProblem(question)}`"
					/>
				</p>
				<button
					class="card flex h-24 w-full cursor-grab flex-col gap-1.5 rounded-xl border-2 bg-dusk p-2 text-left transition active:cursor-grabbing"
					:class="
						question === selected
							? 'border-accent'
							: 'border-transparent hover:border-haze'
					"
					:aria-current="question === selected"
					:aria-label="`Question ${index + 1}: ${question.question_text || 'empty'}`"
					@click="emit('select', question)"
					@keydown.alt.up.prevent="moveBy(index, -1)"
					@keydown.alt.down.prevent="moveBy(index, 1)"
				>
					<span
						class="line-clamp-2 w-full text-center text-[11px] font-bold leading-tight text-paper"
						:class="{ 'text-paper/30': !question.question_text }"
					>
						{{ question.question_text || "Question" }}
					</span>
					<span class="flex min-h-0 flex-1 justify-center">
						<img
							v-if="question.image"
							:src="question.image"
							alt=""
							class="h-full rounded object-contain"
						/>
					</span>
					<span class="grid grid-cols-2 gap-1">
						<span
							v-for="shape in SHAPES"
							:key="shape.id"
							class="h-2 rounded-sm"
							:class="[
								shape.fill,
								question.correct_option === shape.id ? '' : 'opacity-30',
							]"
						/>
					</span>
				</button>
				<div
					class="absolute -top-1 right-0 flex gap-0.5 opacity-0 transition focus-within:opacity-100 group-hover:opacity-100"
				>
					<button
						class="rail-action"
						:aria-label="`Duplicate question ${index + 1}`"
						@click="emit('duplicate', question)"
					>
						<LucideCopy class="size-3.5" />
					</button>
					<button
						class="rail-action hover:!text-alert"
						:aria-label="`Delete question ${index + 1}`"
						@click="emit('remove', question)"
					>
						<LucideTrash2 class="size-3.5" />
					</button>
				</div>
			</li>
		</TransitionGroup>
		<button
			class="ctl shrink-0 gap-1.5 self-center md:mt-1 md:self-stretch"
			@click="emit('add')"
		>
			<LucidePlus class="size-4" />
			Add question
		</button>
	</nav>
</template>

<script setup>
import { ref } from "vue";
import { SHAPES } from "@/game";
import { questionProblem } from "@/quiz";

const props = defineProps({
	questions: { type: Array, required: true },
	selected: { type: Object, default: null },
});
const emit = defineEmits(["select", "move", "duplicate", "remove", "add"]);

const dragged = ref(null);

function startDrag(event, question) {
	dragged.value = question;
	event.dataTransfer.effectAllowed = "move";
}

// Reorder live as the card passes over others, so the drop spot is always visible.
function dragOver(index) {
	if (!dragged.value) return;
	const from = props.questions.indexOf(dragged.value);
	if (from !== index) emit("move", from, index);
}

function moveBy(index, step) {
	const to = index + step;
	if (to < 0 || to >= props.questions.length) return;
	emit("move", index, to);
}
</script>

<style scoped>
.rail-action {
	display: grid;
	place-items: center;
	width: 1.5rem;
	height: 1.5rem;
	border-radius: 999px;
	color: rgb(var(--paper) / 0.5);
	transition: 0.15s ease;
}

.rail-action:hover {
	color: rgb(var(--paper));
}

.rail-move {
	transition: transform 0.2s ease;
}
</style>
