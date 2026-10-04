<template>
	<header
		class="flex h-16 shrink-0 items-center gap-x-4 border-b border-haze px-4 sm:gap-x-6 sm:px-6"
	>
		<RouterLink
			class="flex shrink-0 items-center gap-2 font-display text-lg font-extrabold text-paper"
			to="/host"
			aria-label="TriviaTap"
		>
			<img alt="" class="size-7 rounded-md" :src="LOGO_URL" />
			<span class="hidden sm:inline">TriviaTap</span>
		</RouterLink>
		<RouterLink
			class="ctl ctl-go ml-auto shrink-0 gap-1.5 max-sm:size-10 max-sm:p-0"
			to="/host/quizzes/new"
			aria-label="New quiz"
		>
			<LucidePlus class="size-4" />
			<span class="hidden sm:inline">New quiz</span>
		</RouterLink>
		<button
			class="shrink-0 rounded-full transition hover:brightness-110"
			popovertarget="account-menu"
			:aria-label="`Account: ${firstName}`"
		>
			<HostAvatar class="size-10 text-lg" />
		</button>
		<div
			id="account-menu"
			popover
			class="account-menu fixed m-0 w-64 rounded-2xl border border-haze bg-dusk p-2 text-paper shadow-2xl"
		>
			<div class="flex items-center gap-3 px-3 pb-3 pt-2">
				<HostAvatar class="size-10 text-lg" />
				<div class="min-w-0">
					<p class="truncate font-display text-lg font-bold">{{ firstName }}</p>
					<p class="mt-0.5 truncate font-mono text-xs text-paper/50">{{ user }}</p>
				</div>
			</div>
			<RouterLink class="menu-item" to="/host/profile" @click="closeMenu">
				<LucideUser class="size-4" />
				Profile
			</RouterLink>
			<div class="flex items-center justify-between gap-2 px-3 py-2">
				<span class="text-sm">Theme</span>
				<div
					class="flex rounded-full border border-haze p-0.5"
					role="group"
					aria-label="Theme"
				>
					<button
						v-for="option in THEMES"
						:key="option"
						class="rounded-full px-2.5 py-1 text-xs capitalize text-paper/60 transition hover:text-paper aria-pressed:bg-paper aria-pressed:font-semibold aria-pressed:text-night"
						:aria-pressed="theme === option"
						@click="theme = option"
					>
						{{ option }}
					</button>
				</div>
			</div>
			<hr class="my-1 border-haze" />
			<button class="menu-item w-full" @click="logout">
				<LucideLogOut class="size-4" />
				Log out
			</button>
		</div>
	</header>
</template>

<script setup>
import { firstName, logout } from "@/host";
import HostAvatar from "@/components/HostAvatar.vue";
import { LOGO_URL, theme } from "@/theme";

const THEMES = ["auto", "light", "dark"];

const user = window.session_user;

function closeMenu() {
	document.getElementById("account-menu").hidePopover();
}
</script>

<style scoped>
/* Popovers open centred in the top layer; pin this one under the avatar. */
.account-menu {
	inset: 4.25rem 1rem auto auto;
}

@media (min-width: 640px) {
	.account-menu {
		right: 1.5rem;
	}
}

.menu-item {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	border-radius: 0.75rem;
	padding: 0.6rem 0.75rem;
	font-size: 0.875rem;
	text-align: left;
}

.menu-item:hover {
	background: rgb(var(--paper) / 0.08);
}
</style>
