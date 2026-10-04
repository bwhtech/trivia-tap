<!-- The quiz as the room will see it, played from the editor's own state:
     no session, no players, the same clocks the engine runs on. -->
<template>
	<dialog
		ref="dialog"
		class="qz-dialog h-full max-h-none w-full max-w-none rounded-none border-0 bg-night p-0"
		@cancel.prevent="emit('close')"
		@keydown.left="show(index - 1)"
		@keydown.right="show(index + 1)"
		@keydown.space.prevent="togglePlay"
	>
		<div class="flex h-full flex-col">
			<header
				class="flex shrink-0 items-center gap-4 border-b border-haze px-4 py-3 sm:px-6"
			>
				<p class="font-mono text-[11px] uppercase tracking-[0.28em] text-accent">
					Preview
				</p>
				<p class="ml-auto font-mono text-xs tabular-nums text-paper/40">
					{{ index + 1 }} / {{ beats.length }}
				</p>
				<button class="ctl" @click="emit('close')">Close</button>
			</header>

			<div v-if="beat" class="flex flex-1 flex-col overflow-y-auto p-4 sm:p-8">
				<!-- Read time: the question on its own, answers still held back -->
				<div
					v-if="beat.view === 'get_ready'"
					class="m-auto flex flex-col items-center gap-8 text-center sm:gap-10"
				>
					<p class="font-mono text-xs uppercase tracking-[0.28em] text-paper/40">
						Question {{ beat.number }} of {{ questions.length }}
					</p>
					<h1
						class="max-w-4xl font-display text-3xl font-extrabold leading-tight text-paper sm:text-6xl"
					>
						{{ beat.question.question_text || "Untitled question" }}
					</h1>
					<DrainRing
						:percent="percent"
						:seconds="Math.ceil(remaining)"
						:size="140"
						color="rgb(var(--accent))"
					/>
				</div>

				<div
					v-else-if="beat.view === 'explanation'"
					class="m-auto flex w-full max-w-5xl flex-col items-center gap-4 text-center sm:gap-8"
				>
					<p class="font-mono text-xs uppercase tracking-[0.28em] text-paper/40">
						Question {{ beat.number }} of {{ questions.length }}
					</p>
					<img
						v-if="beat.question.explanation_image"
						:src="beat.question.explanation_image"
						alt=""
						class="max-h-[28vh] w-full object-contain sm:max-h-[42vh]"
					/>
					<p
						v-if="beat.question.explanation"
						class="max-w-5xl text-balance font-display text-2xl font-bold leading-snug text-paper sm:text-4xl lg:text-5xl"
					>
						{{ beat.question.explanation }}
					</p>
					<DrainRing
						:percent="percent"
						:seconds="Math.ceil(remaining)"
						:size="88"
						color="rgb(var(--accent))"
					/>
				</div>

				<div v-else class="m-auto flex w-full max-w-6xl flex-col gap-5 sm:gap-7">
					<div class="flex flex-wrap items-center gap-4 sm:gap-6">
						<DrainRing
							v-if="beat.view === 'question'"
							:percent="percent"
							:seconds="Math.ceil(remaining)"
							:size="96"
							:color="remaining <= 5 ? 'rgb(var(--alert))' : 'rgb(var(--ok))'"
						/>
						<div class="order-last w-full min-w-0 sm:order-none sm:w-auto sm:flex-1">
							<p class="font-mono text-xs uppercase tracking-[0.28em] text-paper/40">
								Question {{ beat.number }} of {{ questions.length }}
							</p>
							<h1
								class="mt-2 font-display text-2xl font-extrabold leading-tight text-paper sm:text-4xl"
							>
								{{ beat.question.question_text || "Untitled question" }}
							</h1>
						</div>
					</div>

					<img
						v-if="beat.question.image"
						:src="beat.question.image"
						alt=""
						class="max-h-[22vh] w-full object-contain sm:max-h-[40vh]"
					/>

					<AnswerGrid
						:options="optionsOf(beat.question)"
						:correct-option="
							beat.view === 'answer' ? beat.question.correct_option : null
						"
					/>
				</div>
			</div>

			<p v-else class="m-auto text-paper/50">
				Nothing to preview yet. Write a question first.
			</p>

			<footer
				class="flex shrink-0 items-center justify-center gap-3 border-t border-haze px-4 py-3"
			>
				<button class="ctl" :disabled="index === 0" @click="show(index - 1)">
					← Back
				</button>
				<button class="ctl ctl-go" @click="togglePlay">
					{{ playing ? "Pause" : atEnd ? "Replay" : "Play" }}
				</button>
				<button class="ctl" :disabled="atEnd" @click="show(index + 1)">Next →</button>
			</footer>
		</div>
	</dialog>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useCountdown } from "@/game";
import AnswerGrid from "@/components/AnswerGrid.vue";
import DrainRing from "@/components/DrainRing.vue";

// Mirrors engine.py, so a preview runs on the clocks the real game runs on.
const GETREADY_SECONDS = 3;
const STATS_SECONDS = 5;

const props = defineProps({
	open: { type: Boolean, default: false },
	questions: { type: Array, default: () => [] },
	defaultSeconds: { type: Number, default: 20 },
	showExplanation: { type: Boolean, default: false },
	explanationPosition: { type: String, default: "Before Stats" },
	explanationSeconds: { type: Number, default: 10 },
});
const emit = defineEmits(["close"]);

const { remaining, start: startCountdown, stop: stopCountdown } = useCountdown();

const dialog = ref(null);
const index = ref(0);
const playing = ref(false);

const beats = computed(() =>
	props.questions.flatMap((question, position) => {
		const beat = (view, seconds) => ({ view, seconds, question, number: position + 1 });
		const screens = [
			beat("get_ready", GETREADY_SECONDS),
			beat("question", question.time_limit || props.defaultSeconds),
		];
		// same skip rule as the engine: nothing to explain, no screen
		const explains =
			props.showExplanation && (question.explanation || question.explanation_image);
		const explanation = beat("explanation", props.explanationSeconds);
		if (explains && props.explanationPosition === "Before Stats") screens.push(explanation);
		screens.push(beat("answer", STATS_SECONDS));
		if (explains && props.explanationPosition === "After Stats") screens.push(explanation);
		return screens;
	})
);

const beat = computed(() => beats.value[index.value]);
const atEnd = computed(() => index.value >= beats.value.length - 1);

// against the beat's own window, not the countdown's, so a resume after a pause
// picks the ring up where it stopped instead of refilling it
const percent = computed(() => (beat.value ? (remaining.value / beat.value.seconds) * 100 : 0));

watch(
	() => props.open,
	(open) => {
		if (!open) {
			stopCountdown();
			playing.value = false;
			return dialog.value.close();
		}
		dialog.value.showModal();
		playing.value = true;
		show(0);
	}
);

// The clock is what advances the game; the buttons only jump the queue.
watch(remaining, (left) => {
	if (left > 0 || !playing.value) return;
	if (atEnd.value) playing.value = false;
	else show(index.value + 1);
});

// An edit that shortens the quiz while the dialog is open must not strand the walk past its end.
watch(beats, (screens) => show(Math.min(index.value, screens.length - 1)));

function show(at) {
	index.value = Math.min(Math.max(at, 0), beats.value.length - 1);
	if (!beat.value) return;
	startCountdown(beat.value.seconds);
	if (!playing.value) stopCountdown();
}

function togglePlay() {
	if (playing.value) {
		playing.value = false;
		return stopCountdown();
	}
	playing.value = true;
	if (atEnd.value && remaining.value === 0) return show(0);
	startCountdown(remaining.value || beat.value.seconds);
}

const optionsOf = (question) => [1, 2, 3, 4].map((option) => question[`option_${option}`]);
</script>
