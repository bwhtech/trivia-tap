<template>
	<dialog
		ref="dialog"
		class="qz-dialog w-[min(32rem,calc(100vw-2rem))] rounded-2xl border border-haze bg-dusk p-6 text-paper"
		@close="emit('close')"
		@click.self="dialog.close()"
	>
		<div class="flex items-center justify-between gap-4">
			<h2 class="font-display text-2xl font-extrabold">Quiz settings</h2>
			<button class="ctl" @click="dialog.close()">Done</button>
		</div>

		<div class="mt-6 flex flex-col gap-5">
			<textarea
				v-model="settings.description"
				rows="2"
				class="field"
				placeholder="Description (optional)"
				aria-label="Description"
			/>

			<label class="flex items-center justify-between gap-4">
				<span>Seconds per question</span>
				<input
					v-model.number="settings.default_time_limit"
					type="number"
					:min="MIN_SECONDS"
					:max="MAX_SECONDS"
					class="field !w-20"
				/>
			</label>

			<div class="flex items-center justify-between gap-4">
				<span>
					Host controls
					<span class="block text-sm text-paper/50"
						>Skip, auto-advance and end game during play</span
					>
				</span>
				<button
					class="ctl shrink-0"
					aria-label="Host controls"
					:data-on="settings.show_host_controls"
					:aria-pressed="settings.show_host_controls"
					@click="settings.show_host_controls = !settings.show_host_controls"
				>
					{{ settings.show_host_controls ? "On" : "Off" }}
				</button>
			</div>

			<div class="flex items-center justify-between gap-4">
				<span>
					Explanations
					<span class="block text-sm text-paper/50">Say why an answer is right</span>
				</span>
				<button
					class="ctl shrink-0"
					aria-label="Explanations"
					:data-on="settings.show_explanation"
					:aria-pressed="settings.show_explanation"
					@click="settings.show_explanation = !settings.show_explanation"
				>
					{{ settings.show_explanation ? "On" : "Off" }}
				</button>
			</div>

			<template v-if="settings.show_explanation">
				<div class="flex items-center justify-between gap-4">
					<span>Show them</span>
					<div class="flex gap-2">
						<button
							v-for="(label, position) in POSITIONS"
							:key="position"
							class="ctl"
							:data-on="settings.explanation_position === position"
							:aria-pressed="settings.explanation_position === position"
							@click="settings.explanation_position = position"
						>
							{{ label }}
						</button>
					</div>
				</div>
				<label class="flex items-center justify-between gap-4">
					<span>Seconds per explanation</span>
					<input
						v-model.number="settings.explanation_time_limit"
						type="number"
						:min="MIN_SECONDS"
						:max="MAX_SECONDS"
						class="field !w-20"
					/>
				</label>
			</template>
		</div>
	</dialog>
</template>

<script setup>
import { ref, watch } from "vue";
import { MAX_SECONDS, MIN_SECONDS } from "@/quiz";

const POSITIONS = { "Before Stats": "Before results", "After Stats": "After results" };

const props = defineProps({
	open: { type: Boolean, default: false },
	settings: { type: Object, required: true },
});
const emit = defineEmits(["close"]);

const dialog = ref(null);

watch(
	() => props.open,
	(open) => (open ? dialog.value.showModal() : dialog.value.close())
);
</script>
