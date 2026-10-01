<template>
	<div class="flex flex-col gap-2">
		<span class="flex items-baseline justify-between">
			<label
				class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
				for="email-code"
			>
				Code
			</label>
			<button
				type="button"
				class="text-sm text-paper/45 transition hover:text-paper disabled:hover:text-paper/45"
				:disabled="wait > 0"
				@click="resend"
			>
				{{ wait > 0 ? `Resend in ${wait}s` : "Resend" }}
			</button>
		</span>
		<input
			id="email-code"
			v-model="code"
			class="w-full rounded-2xl border border-haze bg-dusk px-4 py-3.5 font-mono text-lg font-medium tracking-[0.3em] text-paper placeholder:text-paper/25 focus:border-accent focus:ring-0"
			placeholder="000000"
			inputmode="numeric"
			autocomplete="one-time-code"
			maxlength="6"
			pattern="\d{6}"
			title="The 6-digit code from your email"
			required
			autofocus
		/>
	</div>
</template>

<script setup>
import { onBeforeUnmount, ref } from "vue";

// matches RESEND_AFTER_SECONDS on the server
const RESEND_AFTER = 30;

const emit = defineEmits(["resend"]);
const code = defineModel({ type: String });

const wait = ref(RESEND_AFTER);
let timer;

function countDown() {
	wait.value = RESEND_AFTER;
	clearInterval(timer);
	timer = setInterval(() => {
		wait.value -= 1;
		if (wait.value <= 0) clearInterval(timer);
	}, 1000);
}

function resend() {
	code.value = "";
	countDown();
	emit("resend");
}

countDown();
onBeforeUnmount(() => clearInterval(timer));
</script>
