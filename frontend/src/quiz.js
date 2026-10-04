export const QUESTION_FIELDS = [
	"question_text",
	"image",
	"option_1",
	"option_2",
	"option_3",
	"option_4",
	"correct_option",
	"explanation",
	"explanation_image",
	"time_limit",
	"points_multiplier",
];
export const OPTIONS = ["1", "2", "3", "4"];
export const MIN_SECONDS = 5;
export const MAX_SECONDS = 120;

// rows only get a name once saved, and drag and selection need a stable key before that
let lastKey = 0;

export function withKey(question) {
	return { ...question, key: ++lastKey };
}

export function blankQuestion() {
	return withKey({
		question_text: "",
		image: null,
		option_1: "",
		option_2: "",
		option_3: "",
		option_4: "",
		correct_option: "1",
		explanation: "",
		explanation_image: null,
		time_limit: null,
		points_multiplier: "1",
	});
}

export function copyQuestion(question) {
	return withKey(Object.fromEntries(QUESTION_FIELDS.map((field) => [field, question[field]])));
}

export function isBlank(question) {
	const texts = [
		question.question_text,
		question.explanation,
		...OPTIONS.map((option) => question[`option_${option}`]),
	];
	return !question.image && !question.explanation_image && !texts.some((text) => text?.trim());
}

// Mirrors TTQuiz.validate so the host lands on the broken question without a round trip.
export function questionProblem(question) {
	if (!question.question_text?.trim()) return "has no text";
	const empty = OPTIONS.find((option) => !question[`option_${option}`]?.trim());
	if (empty) return `answer ${empty} is empty`;
	return null;
}

export function clampSeconds(seconds) {
	if (!seconds) return null;
	return Math.min(Math.max(seconds, MIN_SECONDS), MAX_SECONDS);
}
