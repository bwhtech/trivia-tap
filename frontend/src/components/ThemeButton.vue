<template>
	<!-- Unstyled: the host wears this as a `ctl` pill and the players as a bare header icon. -->
	<button
		type="button"
		:aria-label="`Theme: ${theme}`"
		:title="`Theme: ${theme}`"
		@click="cycleTheme"
	>
		{{ ICON[theme] }}
	</button>
</template>

<script setup>
import { cycleTheme, theme } from "@/theme";

const ICON = { auto: "🌗", light: "☀️", dark: "🌙" };
</script>
