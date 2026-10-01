import { computed, ref } from "vue";
import { call } from "@/api";

// The navbar greets the host by name, and the profile page can rename them.
export const firstName = ref(window.first_name || window.session_user);
export const initial = computed(() => firstName.value.charAt(0).toUpperCase());

export async function logout() {
	await call("logout");
	window.location.href = "/trivia-tap/join";
}
