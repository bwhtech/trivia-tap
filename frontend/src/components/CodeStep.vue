<template>
	<div class="flex flex-col gap-2">
		<label
			class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
			for="email-code"
		>
			Code from your email
		</label>
		<input
			id="email-code"
			v-model="code"
			class="w-full rounded-2xl border border-haze bg-dusk py-4 text-center font-mono text-4xl font-bold tracking-[0.18em] text-paper placeholder:text-paper/20 focus:border-accent focus:ring-0"
			placeholder="000000"
			inputmode="numeric"
			autocomplete="one-time-code"
			maxlength="6"
			pattern="\d{6}"
			title="The 6-digit code from your email"
			required
			autofocus
		/>
		<p class="text-sm text-paper/50">
			Sent to <span class="font-medium text-paper">{{ email }}</span
			>.
			<button type="button" class="text-accent hover:underline" @click="emit('back')">
				Change
			</button>
		</p>
		<button
			type="button"
			class="self-start text-sm text-paper/45 transition hover:text-paper disabled:hover:text-paper/45"
			:disabled="wait > 0"
			@click="resend"
		>
			{{ wait > 0 ? `Send a new code in ${wait}s` : "Send a new code" }}
		</button>
	</div>
</template>

<script setup>
import { onBeforeUnmount, ref } from "vue";

// matches RESEND_AFTER_SECONDS on the server
const RESEND_AFTER = 30;

defineProps({ email: { type: String, required: true } });
const emit = defineEmits(["back", "resend"]);
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
