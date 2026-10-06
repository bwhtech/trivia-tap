import frappeUIPreset from "frappe-ui/tailwind";

export default {
	// touch screens keep :hover after a tap, which leaves the last-tapped answer lit
	future: { hoverOnlyWhenSupported: true },
	presets: [frappeUIPreset],
	content: [
		"./index.html",
		"./src/**/*.{vue,js,ts,jsx,tsx}",
		"./node_modules/frappe-ui/src/**/*.{vue,js,ts,jsx,tsx}",
	],
	theme: {
		extend: {
			colors: {
				// values live in index.css so light mode can re-derive them
				night: "rgb(var(--night) / <alpha-value>)",
				dusk: "rgb(var(--dusk) / <alpha-value>)",
				haze: "rgb(var(--haze) / <alpha-value>)",
				paper: "rgb(var(--paper) / <alpha-value>)",
				// accent text has to carry 4.5:1 against the ground, so it darkens where the fills below cannot
				alert: "rgb(var(--alert) / <alpha-value>)",
				accent: "rgb(var(--accent) / <alpha-value>)",
				ok: "rgb(var(--ok) / <alpha-value>)",
				// never themed: a player learns "red is top-left" once
				ember: "#FF5A36",
				lagoon: "#17B0BE",
				gold: "#FFC43D",
				orchid: "#9B6BFF",
				mint: "#20EEA0",
				sunk: "#0A100E",
				card: "#F2FBF6",
			},
			backgroundImage: {
				brand: "var(--brand)",
			},
			fontFamily: {
				display: ['"Bricolage Grotesque"', "system-ui", "sans-serif"],
				sans: ['"Instrument Sans"', "system-ui", "sans-serif"],
				mono: ['"Martian Mono"', "ui-monospace", "monospace"],
			},
			// frappe-ui's preset caps fontSize at 3xl (24px); add display sizes for the big screen
			fontSize: {
				"4xl": ["2.25rem", "1.05"],
				"5xl": ["3rem", "1.02"],
				"6xl": ["3.75rem", "1"],
				"7xl": ["4.5rem", "0.95"],
				"8xl": ["6rem", "0.9"],
				"9xl": ["8rem", "0.88"],
			},
		},
	},
	plugins: [],
};
