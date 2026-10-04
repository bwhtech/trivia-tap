<template>
	<p v-if="error" class="text-alert">{{ error }}</p>
	<div v-if="quizzes.length" class="flex flex-col gap-2">
		<div
			v-for="quiz in quizzes"
			:key="quiz.name"
			class="quiz relative flex items-center gap-3 rounded-2xl border border-haze bg-dusk py-3 pl-5 pr-3 transition hover:border-accent sm:gap-4"
		>
			<!-- the link covers the row so the whole card opens the editor, and the buttons
			     sit above it -->
			<RouterLink
				class="min-w-0 flex-1 after:absolute after:inset-0 after:rounded-2xl"
				:to="`/host/quizzes/${quiz.name}`"
			>
				<p class="truncate font-display text-xl font-bold text-paper">
					{{ quiz.title }}
				</p>
				<p class="font-mono text-xs text-paper/40">
					{{ quiz.question_count }}
					{{ quiz.question_count === 1 ? "question" : "questions" }}
				</p>
			</RouterLink>
			<button
				class="relative grid size-9 shrink-0 place-items-center rounded-full text-paper/30 transition hover:bg-night hover:text-alert focus-visible:text-alert"
				:aria-label="`Delete ${quiz.title}`"
				@click="remove(quiz)"
			>
				<LucideTrash2 class="size-4" />
			</button>
			<button
				class="ctl play relative shrink-0 gap-1.5"
				:aria-label="`Play ${quiz.title}`"
				@click="$emit('play', quiz.name)"
			>
				<LucidePlay class="size-4" />
				Play
			</button>
		</div>
	</div>
	<template v-else-if="loaded">
		<p class="text-paper/50">No quizzes yet. Every game night starts with one question.</p>
		<RouterLink class="ctl self-start" to="/host/quizzes/new">New quiz</RouterLink>
	</template>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { call, readError } from "@/api";
import { confirm } from "@/confirm";

defineEmits(["play"]);

const quizzes = ref([]);
const loaded = ref(false);
const error = ref("");

onMounted(load);

async function load() {
	try {
		quizzes.value = await call("trivia_tap.api.list_quizzes");
		loaded.value = true;
	} catch (e) {
		error.value = readError(e);
	}
}

async function remove(quiz) {
	if (!(await confirm(`Delete "${quiz.title}"?`, { action: "Delete", danger: true }))) return;
	error.value = "";
	try {
		// a played quiz is refused by the TT Session link, which is the rule we want anyway
		await call("frappe.client.delete", { doctype: "TT Quiz", name: quiz.name });
		await load();
	} catch (e) {
		// the framework's own link error names doctypes and links into Desk, which means
		// nothing to a host who never opens it
		error.value =
			e.exc_type === "LinkExistsError"
				? `"${quiz.title}" has been played, so it cannot be deleted.`
				: readError(e);
	}
}
</script>

<style scoped>
/* one lit Play at a time: a column of brand buttons drowns out New quiz */
.quiz:hover .play,
.quiz:focus-within .play {
	background: var(--brand);
	border-color: transparent;
	color: #0a100e;
	font-weight: 800;
}
</style>
