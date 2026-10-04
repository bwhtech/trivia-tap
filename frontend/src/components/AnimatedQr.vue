<template>
	<canvas ref="canvas" role="img" :aria-label="label" />
</template>

<script setup>
import QRCode from "qrcode";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { LOGO_URL } from "@/theme";

const props = defineProps({
	url: { type: String, required: true },
	label: { type: String, default: "Join QR code" },
});

const INK = [10, 16, 14];
const PAPER = "#F2FBF6";
const MINT = [62, 230, 160];
const LEAF = [24, 160, 104];
const POP_MS = 500;
const HOLD_MS = 900;
const STAGGER_MS = 600;
const FLY_MS = 1100;
const BADGE_MS = 350;
const BADGE_SHARE = 0.2;

const canvas = ref(null);
let frame = 0;

onMounted(play);
onBeforeUnmount(() => cancelAnimationFrame(frame));
watch(() => props.url, play);

async function play() {
	cancelAnimationFrame(frame);
	const element = canvas.value;
	const padding = parseFloat(getComputedStyle(element).paddingLeft) * 2;
	const size = Math.round((element.clientWidth - padding) * window.devicePixelRatio);
	element.width = element.height = size;
	const logo = await loadImage(LOGO_URL);
	const dots = planDots(props.url, size, logo);
	const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
	const start = performance.now() - (reduced ? 1e9 : 0);
	const step = (now) => {
		const done = draw(element.getContext("2d"), size, dots, logo, now - start);
		if (!done) frame = requestAnimationFrame(step);
	};
	frame = requestAnimationFrame(step);
}

function planDots(url, size, logo) {
	const { modules } = QRCode.create(url, { errorCorrectionLevel: "H" });
	const cell = size / (modules.size + 2);
	const centre = size / 2;
	const badgeHalf = (size * BADGE_SHARE * 1.24) / 2;
	const targets = [];
	for (let row = 0; row < modules.size; row++) {
		for (let column = 0; column < modules.size; column++) {
			const x = (column + 1.5) * cell;
			const y = (row + 1.5) * cell;
			const underBadge =
				logo && Math.abs(x - centre) < badgeHalf && Math.abs(y - centre) < badgeHalf;
			if (modules.get(row, column) && !underBadge) targets.push({ x, y });
		}
	}
	const sources = logo ? mascotOutline(logo, size) : targets;
	const byAngle = (point) => Math.atan2(point.y - centre, point.x - centre);
	targets.sort((a, b) => byAngle(a) - byAngle(b));
	sources.sort((a, b) => byAngle(a) - byAngle(b));
	const farthest = Math.hypot(centre, centre);
	return targets.map((target, index) => {
		const source = sources[Math.floor((index * sources.length) / targets.length)];
		return {
			from: source,
			to: target,
			cell,
			popDelay: (index / targets.length) * POP_MS * 0.6,
			flyDelay: (Math.hypot(target.x - centre, target.y - centre) / farthest) * STAGGER_MS,
			tint: mix(MINT, LEAF, source.y / size),
		};
	});
}

// The mascot is the black ink of the logo, so its dark pixels are the outline the dots draw.
function mascotOutline(logo, size) {
	const grid = 110;
	const sampler = document.createElement("canvas");
	sampler.width = sampler.height = grid;
	const context = sampler.getContext("2d", { willReadFrequently: true });
	context.drawImage(logo, 0, 0, grid, grid);
	const { data } = context.getImageData(0, 0, grid, grid);
	const inset = size * 0.08;
	const scale = (size - inset * 2) / grid;
	const points = [];
	for (let index = 0; index < data.length; index += 4) {
		const lightness = data[index] + data[index + 1] + data[index + 2];
		if (data[index + 3] > 128 && lightness < 150) {
			const pixel = index / 4;
			points.push({
				x: inset + (pixel % grid) * scale,
				y: inset + Math.floor(pixel / grid) * scale,
			});
		}
	}
	return points;
}

function draw(context, size, dots, logo, elapsed) {
	context.fillStyle = PAPER;
	context.fillRect(0, 0, size, size);
	const flyStart = POP_MS + HOLD_MS;
	for (const dot of dots) {
		const grown = easeOutBack(progress(elapsed - dot.popDelay, POP_MS * 0.5));
		const flown = easeInOutCubic(progress(elapsed - flyStart - dot.flyDelay, FLY_MS));
		const dx = dot.to.x - dot.from.x;
		const dy = dot.to.y - dot.from.y;
		const arc = Math.sin(Math.PI * flown) * 0.18;
		const bob = (1 - flown) * Math.sin(elapsed / 160 + dot.from.x / 40) * dot.cell * 0.15;
		const x = dot.from.x + dx * flown - dy * arc;
		const y = dot.from.y + dy * flown + dx * arc + bob;
		const side = grown * (dot.cell * (0.7 + 0.3 * flown) + flown);
		const [red, green, blue] = mix(dot.tint, INK, flown);
		context.fillStyle = `rgb(${red} ${green} ${blue})`;
		context.beginPath();
		context.roundRect(x - side / 2, y - side / 2, side, side, (side / 2) * (1 - flown));
		context.fill();
	}
	const landed = flyStart + STAGGER_MS + FLY_MS;
	const shown = progress(elapsed - landed, BADGE_MS);
	if (logo && shown > 0) drawBadge(context, size, logo, easeOutBack(shown));
	return shown >= 1;
}

function drawBadge(context, size, logo, scale) {
	const badge = size * BADGE_SHARE * scale;
	const pad = badge * 0.12;
	const at = (size - badge) / 2;
	context.globalAlpha = Math.min(1, scale);
	context.fillStyle = PAPER;
	context.fillRect(at - pad, at - pad, badge + pad * 2, badge + pad * 2);
	context.drawImage(logo, at, at, badge, badge);
	context.globalAlpha = 1;
}

async function loadImage(src) {
	const image = new Image();
	image.src = src;
	try {
		await image.decode();
		return image;
	} catch {
		return null; // a missing logo is not worth losing the code over
	}
}

const progress = (elapsed, duration) => Math.min(1, Math.max(0, elapsed / duration));
const easeInOutCubic = (t) => (t < 0.5 ? 4 * t ** 3 : 1 - (-2 * t + 2) ** 3 / 2);
const easeOutBack = (t) => 1 + 2.70158 * (t - 1) ** 3 + 1.70158 * (t - 1) ** 2;
const mix = (from, to, amount) =>
	from.map((value, index) => Math.round(value + (to[index] - value) * amount));
</script>
