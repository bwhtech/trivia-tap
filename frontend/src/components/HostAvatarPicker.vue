<template>
	<button
		type="button"
		class="group relative shrink-0 rounded-full"
		aria-label="Change profile picture"
		@click="open"
	>
		<HostAvatar class="size-16 text-3xl" />
		<span
			class="absolute inset-0 flex items-center justify-center rounded-full bg-sunk/55 text-card opacity-0 transition group-hover:opacity-100 group-focus-visible:opacity-100"
		>
			<LucidePencil class="size-5" />
		</span>
		<span
			role="tooltip"
			class="pointer-events-none absolute left-1/2 top-full z-10 mt-2 -translate-x-1/2 whitespace-nowrap rounded-lg bg-paper px-2.5 py-1 text-xs font-medium text-night opacity-0 transition group-hover:opacity-100 group-focus-visible:opacity-100"
		>
			Change profile picture
		</span>
	</button>

	<!-- Native <dialog>: focus trap, Esc, and backdrop come free. -->
	<dialog
		ref="dialog"
		class="qz-dialog w-[min(24rem,calc(100vw-2rem))] rounded-2xl border border-haze bg-dusk p-6 text-paper"
		@click.self="dialog.close()"
		@keydown.left.prevent="step(-1)"
		@keydown.right.prevent="step(1)"
	>
		<h2 class="font-display text-xl font-bold">Profile picture</h2>
		<div class="mt-6 flex items-center justify-between gap-4">
			<button type="button" class="arrow" aria-label="Previous" @click="step(-1)">
				<LucideChevronLeft class="size-5" />
			</button>
			<img
				v-if="choice.url"
				:src="choice.url"
				alt=""
				class="size-32 rounded-full bg-card object-cover"
			/>
			<span
				v-else
				class="flex size-32 items-center justify-center rounded-full bg-brand font-display text-6xl font-extrabold text-sunk"
			>
				{{ initial }}
			</span>
			<button type="button" class="arrow" aria-label="Next" @click="step(1)">
				<LucideChevronRight class="size-5" />
			</button>
		</div>
		<p class="mt-4 text-center font-mono text-xs capitalize text-paper/50" aria-live="polite">
			{{ choice.label }} · {{ index + 1 }} / {{ choices.length }}
		</p>
		<p v-if="error" class="mt-4 text-center text-sm text-alert">{{ error }}</p>
		<div class="mt-6 flex justify-end gap-3">
			<button type="button" class="ctl" @click="dialog.close()">Cancel</button>
			<button type="button" class="ctl ctl-go" :disabled="saving" @click="save">
				{{ saving ? "Saving…" : "Save" }}
			</button>
		</div>
	</dialog>
</template>

<script setup>
import { computed, ref } from "vue";
import { call, errorText } from "@/api";
import { avatars } from "@/avatars";
import { initial, userImage } from "@/host";
import HostAvatar from "@/components/HostAvatar.vue";

// The initial stores as an empty image, which is "no picture".
const PACK_CHOICES = [
	{ url: "", label: "Initial" },
	...avatars.map((avatar) => ({ url: avatar.url, label: avatar.id })),
];

const dialog = ref(null);
const choices = ref(PACK_CHOICES);
const index = ref(0);
const saving = ref(false);
const error = ref("");
const choice = computed(() => choices.value[index.value]);

function open() {
	const current = PACK_CHOICES.findIndex((option) => option.url === userImage.value);
	// A photo uploaded in Desk is not in the pack; keep it on offer so Save cannot drop it.
	choices.value =
		current === -1
			? [{ url: userImage.value, label: "Your photo" }, ...PACK_CHOICES]
			: PACK_CHOICES;
	index.value = Math.max(current, 0);
	error.value = "";
	dialog.value.showModal();
}

function step(direction) {
	const count = choices.value.length;
	index.value = (index.value + direction + count) % count;
}

async function save() {
	saving.value = true;
	error.value = "";
	try {
		await call("frappe.client.set_value", {
			doctype: "User",
			name: window.session_user,
			fieldname: "user_image",
			value: choice.value.url,
		});
		userImage.value = choice.value.url;
		dialog.value.close();
	} catch (e) {
		error.value = errorText(e);
	} finally {
		saving.value = false;
	}
}
</script>

<style scoped>
.arrow {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 2.75rem;
	height: 2.75rem;
	flex-shrink: 0;
	border: 1px solid rgb(var(--haze));
	border-radius: 999px;
	color: rgb(var(--paper) / 0.7);
	transition: 0.15s ease;
}

.arrow:hover {
	border-color: rgb(var(--paper));
	color: rgb(var(--paper));
}
</style>
