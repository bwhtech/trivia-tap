<template>
	<div class="relative flex h-full flex-col overflow-y-auto bg-night px-5 py-10">
		<ThemeButton
			class="absolute right-4 top-4 text-lg leading-none opacity-60 transition hover:opacity-100"
		/>
		<div class="mx-auto mb-auto mt-[8vh] w-full max-w-sm">
			<p
				class="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.28em] text-accent"
			>
				<svg class="h-3 w-3 fill-accent" viewBox="0 0 24 24">
					<path :d="SHAPES[1].path" />
				</svg>
				Host
			</p>
			<h1
				class="flex items-center gap-3 font-display text-6xl font-extrabold leading-none text-paper"
			>
				<img alt="" class="size-14 rounded-2xl" :src="LOGO_URL" />
				TriviaTap
			</h1>
			<p class="mt-3 text-paper/50">
				{{ key ? "Pick a new password." : "This reset link is broken." }}
			</p>

			<form v-if="key" class="mt-9 flex flex-col gap-5" @submit.prevent="submit">
				<div class="flex flex-col gap-2">
					<label
						class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
						for="password"
					>
						New password
					</label>
					<PasswordInput
						id="password"
						v-model="password"
						class="w-full rounded-2xl border border-haze bg-dusk px-4 py-3.5 text-lg font-medium text-paper placeholder:text-paper/25 focus:border-accent focus:ring-0"
						autocomplete="new-password"
						required
					/>
				</div>
				<div class="flex flex-col gap-2">
					<label
						class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
						for="confirm-password"
					>
						Confirm password
					</label>
					<PasswordInput
						id="confirm-password"
						v-model="confirmPassword"
						class="w-full rounded-2xl border border-haze bg-dusk px-4 py-3.5 text-lg font-medium text-paper placeholder:text-paper/25 focus:border-accent focus:ring-0"
						autocomplete="new-password"
						required
					/>
				</div>
				<button
					type="submit"
					class="mt-1 rounded-2xl bg-brand py-4 font-display text-xl font-extrabold text-sunk transition hover:brightness-110 disabled:opacity-50"
					:disabled="busy"
				>
					{{ busy ? "One moment…" : "Set password and log in" }}
				</button>
				<p v-if="error" class="text-center text-sm text-alert">{{ error }}</p>
			</form>

			<RouterLink
				class="mt-8 block text-center text-sm text-paper/45 hover:text-paper"
				to="/login"
			>
				Back to log in
			</RouterLink>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue";
import { useRoute } from "vue-router";
import { call, errorText } from "@/api";
import { SHAPES } from "@/game";
import PasswordInput from "@/components/PasswordInput.vue";
import ThemeButton from "@/components/ThemeButton.vue";
import { LOGO_URL } from "@/theme";

const key = useRoute().query.key;
const password = ref("");
const confirmPassword = ref("");
const busy = ref(false);
const error = ref("");

async function submit() {
	error.value = "";
	if (password.value !== confirmPassword.value) {
		error.value = "Passwords do not match.";
		return;
	}
	busy.value = true;
	try {
		await call("trivia_tap.auth.reset_password_with_link", {
			key,
			new_password: password.value,
		});
		// the session user and CSRF token come from the server-rendered boot, so reload
		window.location.href = "/trivia-tap/host";
	} catch (e) {
		error.value = errorText(e);
		busy.value = false;
	}
}
</script>
