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
			<p v-if="codeSent" class="mt-3 text-paper/50">
				Enter the code we sent to <span class="text-paper">{{ email }}</span
				>.
			</p>
			<p v-else class="mt-3 text-paper/50">{{ current.blurb }}</p>

			<div class="mt-9 grid grid-cols-2 gap-1 rounded-2xl border border-haze bg-dusk p-1">
				<button
					v-for="tab in TABS"
					:key="tab.flow"
					type="button"
					class="rounded-xl py-2.5 font-medium transition"
					:class="
						current.tab === tab.flow
							? 'bg-haze text-paper'
							: 'text-paper/50 hover:text-paper'
					"
					@click="switchTo(tab.flow)"
				>
					{{ tab.label }}
				</button>
			</div>

			<form class="mt-6 flex flex-col gap-5" @submit.prevent="submit">
				<label v-if="flow === 'signup' && !codeSent" class="flex flex-col gap-2">
					<span class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
						>Your name</span
					>
					<input
						v-model="fullName"
						class="w-full rounded-2xl border border-haze bg-dusk px-4 py-3.5 text-lg font-medium text-paper placeholder:text-paper/25 focus:border-accent focus:ring-0"
						autocomplete="name"
						placeholder="Ada Lovelace"
						required
					/>
				</label>
				<label v-if="!codeSent" class="flex flex-col gap-2">
					<span class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
						>Email</span
					>
					<input
						v-model="email"
						class="w-full rounded-2xl border border-haze bg-dusk px-4 py-3.5 text-lg font-medium text-paper placeholder:text-paper/25 focus:border-accent focus:ring-0"
						type="email"
						autocomplete="email"
						placeholder="you@school.org"
						required
					/>
				</label>
				<CodeStep v-else v-model="code" @resend="sendCode" @complete="codeComplete" />
				<div v-if="asksPassword" class="flex flex-col gap-2">
					<span class="flex items-baseline justify-between">
						<label
							class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
							for="password"
						>
							{{ flow === "forgot" ? "New password" : "Password" }}
						</label>
						<button
							v-if="flow === 'login'"
							type="button"
							class="text-sm text-paper/45 hover:text-paper"
							@click="switchTo('forgot')"
						>
							Forgot?
						</button>
					</span>
					<PasswordInput
						id="password"
						class="w-full rounded-2xl border border-haze bg-dusk px-4 py-3.5 text-lg font-medium text-paper placeholder:text-paper/25 focus:border-accent focus:ring-0"
						v-model="password"
						:autocomplete="flow === 'login' ? 'current-password' : 'new-password'"
						required
					/>
				</div>
				<div v-if="asksPassword && flow !== 'login'" class="flex flex-col gap-2">
					<label
						class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
						for="confirm-password"
					>
						Confirm password
					</label>
					<PasswordInput
						id="confirm-password"
						class="w-full rounded-2xl border border-haze bg-dusk px-4 py-3.5 text-lg font-medium text-paper placeholder:text-paper/25 focus:border-accent focus:ring-0"
						v-model="confirmPassword"
						autocomplete="new-password"
						required
					/>
				</div>

				<button
					type="submit"
					class="mt-1 rounded-2xl bg-brand py-4 font-display text-xl font-extrabold text-sunk transition hover:brightness-110 disabled:opacity-50"
					:disabled="busy"
				>
					{{
						busy
							? "One moment…"
							: codeSent || flow === "login"
							? current.finish
							: "Email me a code"
					}}
				</button>
				<p v-if="error" class="text-center text-sm text-alert">{{ error }}</p>
				<button
					v-if="secondary"
					type="button"
					class="text-sm text-paper/45 hover:text-paper"
					@click="secondary.go"
				>
					{{ secondary.label }}
				</button>
			</form>

			<RouterLink
				class="mt-8 block text-center text-sm text-paper/45 hover:text-paper"
				to="/join"
			>
				Joining a game? Enter the PIN instead
			</RouterLink>
		</div>
	</div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import { call, errorText } from "@/api";
import { SHAPES } from "@/game";
import CodeStep from "@/components/CodeStep.vue";
import PasswordInput from "@/components/PasswordInput.vue";
import ThemeButton from "@/components/ThemeButton.vue";
import { LOGO_URL } from "@/theme";

const TABS = [
	{ flow: "login", label: "Log in" },
	{ flow: "signup", label: "Sign up" },
];

const FLOWS = {
	login: {
		tab: "login",
		blurb: "Welcome back! Make a quiz and start a game.",
		finish: "Log in",
	},
	signup: {
		tab: "signup",
		purpose: "sign_up",
		blurb: "Write the questions, then watch a room full of phones race to answer them.",
		finish: "Create account",
	},
	forgot: {
		tab: "login",
		purpose: "reset_password",
		blurb: "Happens to the best of us. We'll email you a code to set a new one.",
		finish: "Set password and log in",
	},
	code_login: {
		tab: "login",
		purpose: "log_in",
		blurb: "Skip the password. We'll email you a code.",
		finish: "Log in",
	},
};

const route = useRoute();

const flow = ref(route.query.mode === "signup" ? "signup" : "login");
const fullName = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const code = ref("");
const codeSent = ref(false);
const busy = ref(false);
const error = ref("");

const current = computed(() => FLOWS[flow.value]);
// sign up takes the password before the code, reset takes it after
const asksPassword = computed(
	() =>
		flow.value === "login" ||
		(flow.value === "signup" && !codeSent.value) ||
		(flow.value === "forgot" && codeSent.value)
);

const FINISH = {
	login: () => call("login", { usr: email.value, pwd: password.value }),
	signup: () =>
		call("trivia_tap.auth.sign_up", {
			full_name: fullName.value,
			email: email.value,
			password: password.value,
			code: code.value,
		}),
	forgot: () =>
		call("trivia_tap.auth.reset_password", {
			email: email.value,
			code: code.value,
			new_password: password.value,
		}),
	code_login: () =>
		call("trivia_tap.auth.login_with_code", { email: email.value, code: code.value }),
};

// one way out of every screen, under the main button
const secondary = computed(() => {
	if (codeSent.value)
		return { label: "Use a different email", go: () => (codeSent.value = false) };
	return {
		login: { label: "Log in with an email code instead", go: () => switchTo("code_login") },
		code_login: { label: "Log in with your password", go: () => switchTo("login") },
		forgot: { label: "Back to log in", go: () => switchTo("login") },
	}[flow.value];
});

function switchTo(next) {
	flow.value = next;
	codeSent.value = false;
	code.value = "";
	error.value = "";
}

async function submit() {
	if (busy.value) return;
	error.value = "";
	if (asksPassword.value && flow.value !== "login" && password.value !== confirmPassword.value) {
		error.value = "Passwords do not match.";
		return;
	}
	busy.value = true;
	try {
		if (flow.value === "login" || codeSent.value) {
			await FINISH[flow.value]();
			// the session user and CSRF token come from the server-rendered boot, so reload
			window.location.href = `/trivia-tap${redirectPath()}`;
			return;
		}
		if (flow.value === "signup") await checkPasswordStrength();
		await sendCode();
		codeSent.value = true;
	} catch (e) {
		error.value = errorText(e);
	}
	busy.value = false;
}

// reset still needs the new password, every other flow is done once the code is in
function codeComplete() {
	if (asksPassword.value) document.getElementById("password").focus();
	else submit();
}

async function sendCode() {
	error.value = "";
	try {
		await call("trivia_tap.auth.send_code", {
			email: email.value,
			purpose: current.value.purpose,
		});
	} catch (e) {
		if (!codeSent.value) throw e;
		error.value = errorText(e);
	}
}

// fail before mailing a code, not after the host has typed it in
async function checkPasswordStrength() {
	const result = await call("frappe.core.doctype.user.user.test_password_strength", {
		new_password: password.value,
	});
	const feedback = result?.feedback;
	if (feedback && !feedback.password_policy_validation_passed) {
		throw new Error(
			feedback.warning || feedback.suggestions?.join(" ") || "Pick a stronger password."
		);
	}
}

// only paths inside the SPA, so the link cannot bounce a fresh login off-site
function redirectPath() {
	const path = route.query.redirect;
	return typeof path === "string" && path.startsWith("/") && !path.startsWith("//")
		? path
		: "/host";
}
</script>
