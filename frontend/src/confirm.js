import { ref } from "vue";

// Not window.confirm: it draws the browser's own chrome over the projector.
export const pendingConfirm = ref(null);

export function confirm(message, { action = "Confirm", danger = false } = {}) {
	return new Promise((resolve) => {
		pendingConfirm.value = {
			message,
			action,
			danger,
			settle(answer) {
				pendingConfirm.value = null;
				resolve(answer);
			},
		};
	});
}
