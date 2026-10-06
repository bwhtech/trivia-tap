<template>
	<FileUploader
		file-types="image/*"
		:upload-args="{ private: 0, optimize: true }"
		@success="(file) => emit('update:modelValue', file.file_url)"
	>
		<template #default="{ openFileSelector, uploading, progress }">
			<div
				v-if="modelValue"
				class="group relative grid size-full place-items-center overflow-hidden rounded-xl bg-night/60"
			>
				<img :src="modelValue" alt="" class="max-h-full max-w-full object-contain" />
				<div
					class="absolute right-2 top-2 flex gap-1.5 opacity-0 transition focus-within:opacity-100 group-hover:opacity-100 [@media(hover:none)]:opacity-100"
				>
					<button
						class="image-action"
						:aria-label="`Replace ${label}`"
						@click="openFileSelector"
					>
						<LucideImageUp class="size-4" />
					</button>
					<button
						class="image-action hover:!text-alert"
						:aria-label="`Remove ${label}`"
						@click="emit('update:modelValue', null)"
					>
						<LucideTrash2 class="size-4" />
					</button>
				</div>
			</div>
			<button
				v-else
				class="flex size-full flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-haze text-sm text-paper/50 transition hover:border-paper/40 hover:text-paper"
				@click="openFileSelector"
			>
				<LucideImagePlus class="size-6" />
				{{ uploading ? `Uploading ${progress}%` : `Add ${label}` }}
			</button>
		</template>
	</FileUploader>
</template>

<script setup>
import { FileUploader } from "frappe-ui";

defineProps({
	modelValue: { type: String, default: null },
	label: { type: String, default: "image" },
});
const emit = defineEmits(["update:modelValue"]);
</script>

<style scoped>
.image-action {
	display: grid;
	place-items: center;
	width: 2.25rem;
	height: 2.25rem;
	border-radius: 999px;
	background: rgb(var(--night) / 0.85);
	color: rgb(var(--paper));
	transition: color 150ms ease;
}
</style>
