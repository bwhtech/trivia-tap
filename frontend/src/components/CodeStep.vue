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
		<PinInputRoot
			v-model="digits"
			class="grid grid-cols-6 gap-2"
			type="number"
			otp
			required
			@complete="emit('complete')"
		>
			<PinInputInput
				v-for="(digit, index) in CODE_LENGTH"
				:key="digit"
				:index="index"
				:id="index === 0 ? 'email-code' : undefined"
				:aria-label="`Digit ${digit} of ${CODE_LENGTH}`"
				:autofocus="index === 0"
				class="h-14 w-full rounded-2xl border border-haze bg-dusk p-0 text-center font-mono text-2xl font-bold text-paper caret-accent focus:border-accent focus:ring-0"
			/>
		</PinInputRoot>
	</div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import { PinInputInput, PinInputRoot } from "reka-ui";

const CODE_LENGTH = 6;
// matches RESEND_AFTER_SECONDS on the server
const RESEND_AFTER = 30;

const emit = defineEmits(["resend", "complete"]);
const code = defineModel({ type: String });
const digits = computed({
	get: () => [...code.value],
	set: (value) => (code.value = value.join("")),
});

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
