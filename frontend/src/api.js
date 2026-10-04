import { frappeRequest } from "frappe-ui";

const HOST_ACCESS_ERROR = "Log in with a Quiz Host account to write and host quizzes.";

// the framework's permission message names doctypes, which means nothing to a teacher
export function readError(e) {
	return e.exc_type === "PermissionError" ? HOST_ACCESS_ERROR : errorText(e);
}

// server messages are HTML (the password policy sends a <ul> of hints) and the screens show text
export function errorText(e) {
	const html = e.messages?.[0] || e.message;
	const body = new DOMParser().parseFromString(html, "text/html").body;
	const items = [...body.querySelectorAll("li")].map((item) => item.textContent);
	return items.length ? items.join(" ") : body.textContent;
}

export function call(method, params = {}) {
	return frappeRequest({
		url: `/api/method/${method}`,
		method: "POST",
		params,
		headers: { "X-Frappe-Site-Name": window.site_name },
	});
}
