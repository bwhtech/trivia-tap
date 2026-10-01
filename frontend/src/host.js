import { computed, ref } from "vue";
import { call } from "@/api";

// The navbar shows the host's face and name, and the profile page can change both.
export const firstName = ref(window.first_name || window.session_user);
export const userImage = ref(window.user_image || "");
export const initial = computed(() => firstName.value.charAt(0).toUpperCase());

export async function logout() {
	await call("logout");
	window.location.href = "/trivia-tap/join";
}
