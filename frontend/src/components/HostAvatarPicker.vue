<template>
	<section class="flex flex-col gap-4 rounded-2xl border border-haze bg-dusk p-4 sm:p-5">
		<div class="flex items-center gap-4">
			<h2 class="font-display text-xl font-bold text-paper">Avatar</h2>
			<p v-if="error" class="text-sm text-alert">{{ error }}</p>
		</div>
		<div
			class="grid grid-cols-[repeat(auto-fill,minmax(2.75rem,1fr))] justify-items-center gap-y-2"
			role="group"
			aria-label="Avatar"
		>
			<button
				type="button"
				aria-label="Initial"
				:aria-pressed="!userImage"
				class="rounded-full p-0.5 transition"
				:class="ringClass(!userImage)"
				@click="pick('')"
			>
				<span
					class="flex size-10 items-center justify-center rounded-full bg-brand font-display text-lg font-extrabold text-sunk"
				>
					{{ initial }}
				</span>
			</button>
			<button
				v-for="option in avatars"
				:key="option.id"
				type="button"
				:aria-label="option.id"
				:aria-pressed="userImage === option.url"
				class="rounded-full p-0.5 transition"
				:class="ringClass(userImage === option.url)"
				@click="pick(option.url)"
			>
				<AvatarPic :id="option.id" :size="40" />
			</button>
		</div>
	</section>
</template>

<script setup>
import { ref } from "vue";
import { call, errorText } from "@/api";
import { avatars } from "@/avatars";
import { initial, userImage } from "@/host";
import AvatarPic from "@/components/AvatarPic.vue";

const error = ref("");

// Saves on click, like the join picker: one tap is the whole decision.
async function pick(url) {
	const previous = userImage.value;
	userImage.value = url;
	error.value = "";
	try {
		await call("frappe.client.set_value", {
			doctype: "User",
			name: window.session_user,
			fieldname: "user_image",
			value: url,
		});
	} catch (e) {
		userImage.value = previous;
		error.value = errorText(e);
	}
}

function ringClass(selected) {
	return selected ? "bg-mint ring-2 ring-mint" : "opacity-60 hover:opacity-100";
}
</script>
