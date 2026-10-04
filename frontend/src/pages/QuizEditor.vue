<template>
	<div class="flex h-full flex-col bg-night">
		<HostBar :show-new-quiz="false" />
		<header class="flex items-center gap-2 border-b border-haze px-3 py-2.5 sm:gap-3 sm:px-5">
			<input
				ref="titleInput"
				v-model="title"
				class="min-w-0 flex-1 rounded-lg border border-transparent bg-transparent px-2 py-1.5 font-display text-xl font-extrabold text-paper transition placeholder:text-paper/30 hover:border-haze focus:border-haze focus:outline-none sm:text-2xl"
				placeholder="Untitled quiz"
				aria-label="Quiz title"
			/>
			<span
				class="hidden shrink-0 font-mono text-xs sm:inline"
				:class="dirty ? 'text-paper/40' : 'text-ok'"
			>
				{{ dirty ? "Unsaved changes" : "Saved" }}
			</span>
			<button
				class="ctl shrink-0 gap-1.5 max-sm:size-10 max-sm:p-0"
				aria-label="Quiz settings"
				@click="showSettings = true"
			>
				<LucideSettings class="size-4" />
				<span class="hidden sm:inline">Settings</span>
			</button>
			<button
				class="ctl shrink-0 gap-1.5 max-sm:size-10 max-sm:p-0"
				aria-label="Preview"
				:disabled="!questions.length"
				@click="previewing = true"
			>
				<LucideEye class="size-4" />
				<span class="hidden sm:inline">Preview</span>
			</button>
			<button class="ctl ctl-go shrink-0" :disabled="saving" @click="save">
				{{ saving ? "Saving…" : "Save" }}
			</button>
		</header>
		<p
			v-if="error"
			class="border-b border-haze bg-dusk px-5 py-2 text-sm text-alert"
			role="alert"
		>
			{{ error }}
		</p>

		<div class="flex min-h-0 flex-1 flex-col md:flex-row">
			<QuestionRail
				:questions="questions"
				:selected="selected"
				@select="(question) => (selected = question)"
				@move="move"
				@duplicate="duplicate"
				@remove="remove"
				@add="add"
			/>
			<main
				v-if="selected"
				class="min-h-0 flex-1 overflow-y-auto lg:flex lg:overflow-hidden"
			>
				<div class="p-4 sm:p-8 lg:flex-1 lg:overflow-y-auto">
					<QuestionSlide ref="slide" :question="selected" />
				</div>
				<QuestionSettings
					class="border-t border-haze p-5 lg:w-72 lg:shrink-0 lg:overflow-y-auto lg:border-l lg:border-t-0"
					:question="selected"
					:default-seconds="settings.default_time_limit || DEFAULT_TIME_LIMIT"
					:show-explanation="settings.show_explanation"
					@duplicate="duplicate(selected)"
					@remove="remove(selected)"
				/>
			</main>
			<main v-else class="grid flex-1 place-items-center p-8 text-center">
				<div class="flex flex-col items-center gap-4">
					<p class="text-paper/50">A quiz with no questions is just a title.</p>
					<button class="ctl ctl-go gap-1.5" @click="add">
						<LucidePlus class="size-4" />
						Add question
					</button>
				</div>
			</main>
		</div>

		<QuizSettingsDialog
			:open="showSettings"
			:settings="settings"
			@close="showSettings = false"
		/>
		<QuizPreview
			:open="previewing"
			:questions="questions"
			:default-seconds="settings.default_time_limit"
			:show-explanation="settings.show_explanation"
			:explanation-position="settings.explanation_position"
			:explanation-seconds="settings.explanation_time_limit"
			@close="previewing = false"
		/>
	</div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { onBeforeRouteLeave, useRoute, useRouter } from "vue-router";
import { call, readError } from "@/api";
import { confirm } from "@/confirm";
import {
	QUESTION_FIELDS,
	blankQuestion,
	clampSeconds,
	copyQuestion,
	isBlank,
	questionProblem,
	withKey,
} from "@/quiz";
import HostBar from "@/components/HostBar.vue";
import QuestionRail from "@/components/QuestionRail.vue";
import QuestionSettings from "@/components/QuestionSettings.vue";
import QuestionSlide from "@/components/QuestionSlide.vue";
import QuizPreview from "@/components/QuizPreview.vue";
import QuizSettingsDialog from "@/components/QuizSettingsDialog.vue";

const DEFAULT_TIME_LIMIT = 20;
const DEFAULT_EXPLANATION_SECONDS = 10;

const route = useRoute();
const router = useRouter();

const loadedDoc = ref(null);
const title = ref("");
const settings = reactive({
	description: "",
	default_time_limit: DEFAULT_TIME_LIMIT,
	show_explanation: false,
	show_host_controls: false,
	explanation_time_limit: DEFAULT_EXPLANATION_SECONDS,
	explanation_position: "Before Stats",
});
const questions = ref([]);
const selected = ref(null);
const savedSnapshot = ref("");
const showSettings = ref(false);
const previewing = ref(false);
const saving = ref(false);
const error = ref("");
const titleInput = ref(null);
const slide = ref(null);

const dirty = computed(() => JSON.stringify(editedFields()) !== savedSnapshot.value);

onMounted(async () => {
	window.addEventListener("keydown", saveOnShortcut);
	window.addEventListener("beforeunload", warnBeforeUnload);
	if (route.params.name === "new") {
		questions.value = [blankQuestion()];
	} else {
		await load(route.params.name);
	}
	selected.value = questions.value[0] || null;
	markSaved();
});

onBeforeUnmount(() => {
	window.removeEventListener("keydown", saveOnShortcut);
	window.removeEventListener("beforeunload", warnBeforeUnload);
});

onBeforeRouteLeave(async () => {
	if (!dirty.value) return true;
	return await confirm("Leave without saving your changes?", {
		action: "Leave",
		danger: true,
	});
});

async function load(name) {
	try {
		const quiz = await call("frappe.client.get", { doctype: "TT Quiz", name });
		loadedDoc.value = quiz;
		title.value = quiz.title;
		Object.assign(settings, {
			description: quiz.description || "",
			default_time_limit: quiz.default_time_limit || DEFAULT_TIME_LIMIT,
			show_explanation: Boolean(quiz.show_explanation),
			show_host_controls: Boolean(quiz.show_host_controls),
			explanation_time_limit: quiz.explanation_time_limit || DEFAULT_EXPLANATION_SECONDS,
			explanation_position: quiz.explanation_position || settings.explanation_position,
		});
		// an unset Int comes back as 0; the field should read as empty, not as zero seconds
		questions.value = quiz.questions.map((question) =>
			withKey({
				...question,
				time_limit: question.time_limit || null,
				points_multiplier: question.points_multiplier || "1",
			})
		);
	} catch (e) {
		error.value = readError(e);
	}
}

async function save() {
	if (saving.value || !checkQuiz()) return;
	error.value = "";
	saving.value = true;
	try {
		const doc = { ...loadedDoc.value, doctype: "TT Quiz", ...editedFields() };
		const method = loadedDoc.value ? "frappe.client.save" : "frappe.client.insert";
		const isNew = !loadedDoc.value;
		loadedDoc.value = await call(method, { doc });
		markSaved();
		if (isNew) router.replace(`/host/quizzes/${loadedDoc.value.name}`);
	} catch (e) {
		error.value = readError(e);
	} finally {
		saving.value = false;
	}
}

function checkQuiz() {
	if (!title.value.trim()) {
		error.value = "Give the quiz a title.";
		titleInput.value.focus();
		return false;
	}
	if (!questions.value.length) {
		error.value = "A quiz needs at least one question.";
		return false;
	}
	const broken = questions.value.find(questionProblem);
	if (broken) {
		selected.value = broken;
		error.value = `Question ${questions.value.indexOf(broken) + 1} ${questionProblem(
			broken
		)}.`;
		return false;
	}
	return true;
}

function editedFields() {
	return {
		title: title.value,
		description: settings.description,
		default_time_limit: clampSeconds(settings.default_time_limit) || DEFAULT_TIME_LIMIT,
		show_explanation: Number(settings.show_explanation),
		show_host_controls: Number(settings.show_host_controls),
		explanation_time_limit:
			clampSeconds(settings.explanation_time_limit) || DEFAULT_EXPLANATION_SECONDS,
		explanation_position: settings.explanation_position,
		// no name or idx: frappe keeps an idx it is given, so the reorder would be ignored
		questions: questions.value.map((question) => ({
			doctype: "TT Question",
			...Object.fromEntries(QUESTION_FIELDS.map((field) => [field, question[field]])),
			time_limit: clampSeconds(question.time_limit),
		})),
	};
}

function markSaved() {
	savedSnapshot.value = JSON.stringify(editedFields());
}

function move(from, to) {
	const [question] = questions.value.splice(from, 1);
	questions.value.splice(to, 0, question);
}

function add() {
	insertAfterSelected(blankQuestion());
}

function duplicate(question) {
	selected.value = question;
	insertAfterSelected(copyQuestion(question));
}

async function insertAfterSelected(question) {
	const index = questions.value.indexOf(selected.value);
	questions.value.splice(index + 1, 0, question);
	selected.value = question;
	await nextTick();
	slide.value?.focus();
}

async function remove(question) {
	const index = questions.value.indexOf(question);
	if (!isBlank(question)) {
		const ok = await confirm(`Delete question ${index + 1}?`, {
			action: "Delete",
			danger: true,
		});
		if (!ok) return;
	}
	questions.value.splice(index, 1);
	if (selected.value === question) {
		selected.value = questions.value[Math.min(index, questions.value.length - 1)] || null;
	}
}

function saveOnShortcut(event) {
	if (event.key === "s" && (event.metaKey || event.ctrlKey)) {
		event.preventDefault();
		save();
	}
}

function warnBeforeUnload(event) {
	if (dirty.value) event.preventDefault();
}
</script>
