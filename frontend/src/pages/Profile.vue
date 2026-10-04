<template>
	<div class="flex h-full flex-col overflow-y-auto bg-night">
		<HostBar />
		<div
			class="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-10 p-5 pb-20 sm:p-8 sm:pb-20"
		>
			<header class="flex flex-col gap-8">
				<div class="flex items-center gap-5 sm:gap-6">
					<HostAvatarPicker />
					<div class="min-w-0">
						<p
							class="flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.28em] text-accent"
						>
							<svg class="h-3 w-3 fill-accent" viewBox="0 0 24 24">
								<path :d="SHAPES[1].path" />
							</svg>
							Host
						</p>
						<h1
							class="mt-2 truncate font-display text-3xl font-extrabold text-paper sm:text-5xl"
						>
							{{ fullName }}
						</h1>
						<p
							v-if="user !== fullName"
							class="mt-1 truncate font-mono text-sm text-paper/50"
						>
							{{ user }}
						</p>
					</div>
				</div>
				<dl class="grid grid-cols-3 gap-3 sm:gap-4">
					<div
						v-for="stat in STATS"
						:key="stat.key"
						class="flex flex-col-reverse justify-end gap-2 rounded-2xl border border-haze bg-dusk p-4 sm:p-5"
					>
						<dt
							class="font-mono text-[11px] uppercase tracking-[0.16em] text-paper/45"
						>
							{{ stat.label }}
						</dt>
						<dd
							class="font-display text-3xl font-extrabold tabular-nums text-paper sm:text-4xl"
						>
							{{ stats ? stats[stat.key].toLocaleString() : "–" }}
						</dd>
					</div>
				</dl>
			</header>

			<form
				class="flex flex-col gap-5 rounded-2xl border border-haze bg-dusk p-5 sm:p-6"
				@submit.prevent="saveName"
			>
				<h2 class="font-display text-xl font-bold text-paper">Your name</h2>
				<p class="-mt-2 text-sm text-paper/50">Shown in the menu and on your quizzes.</p>
				<div class="grid gap-4 sm:grid-cols-2">
					<label class="flex flex-col gap-2">
						<span
							class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
							>First name</span
						>
						<input
							v-model="firstName"
							class="field"
							autocomplete="given-name"
							required
						/>
					</label>
					<label class="flex flex-col gap-2">
						<span
							class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
							>Last name</span
						>
						<input v-model="lastName" class="field" autocomplete="family-name" />
					</label>
				</div>
				<div class="flex items-center justify-end gap-4">
					<p
						v-if="nameNote"
						class="text-sm"
						:class="nameFailed ? 'text-alert' : 'text-ok'"
						aria-live="polite"
					>
						{{ nameNote }}
					</p>
					<button
						class="ctl"
						:class="{ 'ctl-go': nameChanged }"
						:disabled="savingName || !nameChanged"
					>
						{{ savingName ? "Saving…" : "Save" }}
					</button>
				</div>
			</form>

			<form
				class="flex flex-col gap-5 rounded-2xl border border-haze bg-dusk p-5 sm:p-6"
				@submit.prevent="changePassword"
			>
				<div class="flex items-center justify-between gap-4">
					<div>
						<h2 class="font-display text-xl font-bold text-paper">Password</h2>
						<p class="mt-2 text-sm text-paper/50">
							{{
								editingPassword
									? "Pick something only you know."
									: "Log in with your email and this password."
							}}
						</p>
					</div>
					<button
						v-if="!editingPassword"
						type="button"
						class="ctl shrink-0"
						@click="editingPassword = true"
					>
						Change
					</button>
				</div>
				<p
					v-if="passwordNote && !editingPassword"
					class="-mt-2 text-sm"
					:class="passwordFailed ? 'text-alert' : 'text-ok'"
				>
					{{ passwordNote }}
				</p>
				<template v-if="editingPassword">
					<!-- lets password managers tie the new password to this account -->
					<input :value="user" autocomplete="username" hidden />
					<div class="flex flex-col gap-2">
						<span class="flex items-baseline justify-between">
							<label
								class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
								for="current-password"
								>Current password</label
							>
							<button
								type="button"
								class="text-sm text-paper/45 hover:text-paper disabled:opacity-50"
								:disabled="sendingLink"
								@click="sendResetLink"
							>
								{{ sendingLink ? "Sending…" : "Forgot?" }}
							</button>
						</span>
						<PasswordInput
							id="current-password"
							v-model="oldPassword"
							class="field"
							autocomplete="current-password"
							required
						/>
					</div>
					<div class="grid gap-4 sm:grid-cols-2">
						<div class="flex flex-col gap-2">
							<label
								class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
								for="new-password"
								>New password</label
							>
							<PasswordInput
								id="new-password"
								v-model="newPassword"
								class="field"
								autocomplete="new-password"
								required
							/>
						</div>
						<div class="flex flex-col gap-2">
							<label
								class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
								for="confirm-new-password"
								>Confirm new password</label
							>
							<PasswordInput
								id="confirm-new-password"
								v-model="confirmPassword"
								class="field"
								autocomplete="new-password"
								required
							/>
						</div>
					</div>
					<div class="flex items-center justify-end gap-3">
						<p
							v-if="passwordNote"
							class="mr-auto text-sm"
							:class="passwordFailed ? 'text-alert' : 'text-ok'"
							aria-live="polite"
						>
							{{ passwordNote }}
						</p>
						<button type="button" class="ctl" @click="cancelPassword">Cancel</button>
						<button
							class="ctl"
							:class="{ 'ctl-go': passwordFilled }"
							:disabled="savingPassword || !passwordFilled"
						>
							{{ savingPassword ? "Changing…" : "Change password" }}
						</button>
					</div>
				</template>
			</form>
		</div>
	</div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { call, errorText } from "@/api";
import { SHAPES } from "@/game";
import { firstName as greetedName } from "@/host";
import HostAvatarPicker from "@/components/HostAvatarPicker.vue";
import HostBar from "@/components/HostBar.vue";
import PasswordInput from "@/components/PasswordInput.vue";

const STATS = [
	{ key: "games_hosted", label: "Games hosted" },
	{ key: "players_reached", label: "Players joined" },
	{ key: "quizzes_written", label: "Quizzes created" },
];

const route = useRoute();
const router = useRouter();
const user = window.session_user;
const stats = ref(null);

const firstName = ref("");
const lastName = ref("");
const savedName = ref({ first: "", last: "" });
const fullName = computed(
	() => `${savedName.value.first} ${savedName.value.last}`.trim() || greetedName.value
);
const nameChanged = computed(
	() => firstName.value !== savedName.value.first || lastName.value !== savedName.value.last
);
const savingName = ref(false);
const nameNote = ref("");
const nameFailed = ref(false);

const oldPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const passwordFilled = computed(
	() => oldPassword.value && newPassword.value && confirmPassword.value
);
const savingPassword = ref(false);
const passwordChanged = route.query.password === "changed";
const passwordNote = ref(passwordChanged ? "Password changed." : "");
const passwordFailed = ref(false);
const editingPassword = ref(false);
const sendingLink = ref(false);

onMounted(async () => {
	if (passwordChanged) router.replace({ query: {} });
	call("trivia_tap.api.get_host_stats").then((result) => (stats.value = result));
	const profile = await call("frappe.client.get", { doctype: "User", name: user });
	firstName.value = profile.first_name || "";
	lastName.value = profile.last_name || "";
	savedName.value = { first: firstName.value, last: lastName.value };
});

async function saveName() {
	savingName.value = true;
	try {
		await call("frappe.client.set_value", {
			doctype: "User",
			name: user,
			fieldname: { first_name: firstName.value, last_name: lastName.value },
		});
		greetedName.value = firstName.value;
		savedName.value = { first: firstName.value, last: lastName.value };
		showNameNote("Saved.", false);
	} catch (e) {
		showNameNote(errorText(e), true);
	} finally {
		savingName.value = false;
	}
}

async function changePassword() {
	if (newPassword.value !== confirmPassword.value) {
		showPasswordNote("Passwords do not match.", true);
		return;
	}
	savingPassword.value = true;
	try {
		await call("trivia_tap.auth.change_password", {
			old_password: oldPassword.value,
			new_password: newPassword.value,
		});
		// frappe starts a new session, so the CSRF token in this page is stale now
		window.location.href = "/trivia-tap/host/profile?password=changed";
	} catch (e) {
		showPasswordNote(errorText(e), true);
		savingPassword.value = false;
	}
}

function cancelPassword() {
	editingPassword.value = false;
	oldPassword.value = newPassword.value = confirmPassword.value = "";
	passwordNote.value = "";
}

async function sendResetLink() {
	sendingLink.value = true;
	try {
		await call("trivia_tap.auth.send_reset_link");
		cancelPassword();
		showPasswordNote(`We emailed a reset link to ${user}.`, false);
	} catch (e) {
		showPasswordNote(errorText(e), true);
	} finally {
		sendingLink.value = false;
	}
}

function showNameNote(text, failed) {
	nameNote.value = text;
	nameFailed.value = failed;
}

function showPasswordNote(text, failed) {
	passwordNote.value = text;
	passwordFailed.value = failed;
}
</script>
