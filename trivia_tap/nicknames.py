"""Server-side so the profanity test can prove every adjective and noun pair is clean."""

ADJECTIVES = (
	"Swift",
	"Brave",
	"Clever",
	"Sunny",
	"Lucky",
	"Bold",
	"Cosmic",
	"Neon",
	"Turbo",
	"Mighty",
	"Quiet",
	"Jolly",
	"Rapid",
	"Golden",
	"Silver",
	"Wild",
	"Nimble",
	"Bright",
	"Fuzzy",
	"Zesty",
)

NOUNS = (
	"Falcon",
	"Otter",
	"Comet",
	"Panda",
	"Tiger",
	"Maple",
	"Rocket",
	"Puffin",
	"Cactus",
	"Dragon",
	"Walrus",
	"Marble",
	"Pixel",
	"Mango",
	"Badger",
	"Meteor",
	"Quokka",
	"Lantern",
	"Narwhal",
	"Pepper",
)


def get_boot_words() -> dict:
	return {"adjectives": list(ADJECTIVES), "nouns": list(NOUNS)}
