const { adjectives = [], nouns = [] } = window.nickname_words || {};

function pick(list) {
	return list[Math.floor(Math.random() * list.length)];
}

export function suggestNicknames(count = 3) {
	// distinct nouns: three "…Narwhal" options read as one option with a typo
	const used = new Set();
	while (used.size < count && adjectives.length && nouns.length >= count) {
		used.add(pick(nouns));
	}
	return [...used].map((noun) => `${pick(adjectives)}${noun}`);
}
