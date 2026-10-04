<!-- Not frappe-ui's Avatar: it caps at 3xl and the host screen renders these far larger. -->
<template>
	<img
		v-if="url"
		:src="url"
		:alt="nickname || id"
		class="shrink-0 rounded-full bg-surface-gray-2 object-cover"
		:style="{ width: `${size}px`, height: `${size}px` }"
	/>
</template>

<script setup>
import { computed } from "vue";
import { avatarUrl } from "@/avatars";

const props = defineProps({
	id: String,
	nickname: String,
	size: { type: Number, default: 40 },
});

const url = computed(() => avatarUrl(props.id));
</script>
