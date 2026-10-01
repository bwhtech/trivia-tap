<template>
	<img
		v-if="userImage"
		:src="userImage"
		alt=""
		class="shrink-0 rounded-full bg-card object-cover"
	/>
	<span
		v-else
		class="flex shrink-0 items-center justify-center rounded-full bg-brand font-display font-extrabold text-sunk"
	>
		{{ initial }}
	</span>
</template>

<script setup>
import { initial, userImage } from "@/host";
</script>
