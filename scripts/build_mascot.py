# Cuts the logo PNG into layers (background, head, eyes, sparks) and writes an
# SVG that animates them with CSS, so the mascot blinks and fidgets anywhere an
# <img> can show it. Re-run after the logo changes:
#
#   uv run --with numpy --with scipy --with pillow python scripts/build_mascot.py

import base64
import io
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

IMAGES = Path(__file__).resolve().parent.parent / "trivia_tap/public/images"
SOURCE = IMAGES / "trivia-tap-logo.png"
# bundled by Vite, so the URL carries a content hash and a new mascot is never served stale
TARGET = Path(__file__).resolve().parent.parent / "frontend/src/assets/trivia-tap-mascot.svg"

STYLE = """
.part { transform-box: fill-box; transform-origin: center; }
.head { transform-origin: 50% 100%; animation: bob 2.8s ease-in-out infinite; }
.eyes { animation: glance 5s ease-in-out infinite; }
.eye { animation: blink 5s infinite; }
.spark { animation: flash 2.2s ease-out infinite; }
@keyframes bob {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-5px) rotate(-3deg); }
}
@keyframes glance {
  0%, 30%, 100% { transform: translate(0, 0); }
  36%, 58% { transform: translate(-5px, 1px); }
  64%, 86% { transform: translate(4px, -1px); }
}
@keyframes blink {
  0%, 18%, 23%, 100% { transform: scaleY(1); }
  20.5% { transform: scaleY(0.1); }
}
@keyframes flash {
  0%, 55%, 100% { transform: scale(1); opacity: 1; }
  68% { transform: scale(0.55); opacity: 0.35; }
  80% { transform: scale(1.18); opacity: 1; }
}
@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
"""


def main():
	pixels = np.asarray(Image.open(SOURCE).convert("RGBA")).astype(float)
	rgb, alpha = pixels[..., :3], pixels[..., 3]
	brightest, darkest = rgb.max(-1), rgb.min(-1)
	saturation = (brightest - darkest) / np.maximum(brightest, 1)
	# the background is saturated green, the mascot is black and white
	pale = np.clip((0.5 - saturation) / 0.35, 0, 1)
	dark = np.clip((150 - brightest) / 60, 0, 1)
	ink = np.maximum(pale, dark) * (alpha / 255)
	grey = darkest

	labels, _ = ndimage.label((brightest < 90) & (alpha > 0))
	sizes = {index: (labels == index).sum() for index in np.unique(labels)[1:]}
	parts = [index for index, size in sizes.items() if size > 200]
	outline = max(parts, key=sizes.get)
	eyes = [index for index in parts if index != outline and is_inside_face(labels, index)]
	sparks = [index for index in parts if index not in eyes and index != outline]

	def grow(index):
		return ndimage.binary_dilation(labels == index, iterations=2)

	eye_mask = np.any([grow(index) for index in eyes], axis=0)
	spark_mask = np.any([grow(index) for index in sparks], axis=0)

	head = layer(grey, ink * ~spark_mask)
	head[eye_mask] = [255, 255, 255, 255]

	images = [
		image_tag(background(rgb, alpha, ink), "part"),
		'<g class="part head">',
		image_tag(head, "part"),
		'<g class="part eyes">',
		*[image_tag(layer(grey, ink * grow(index)), "part eye") for index in eyes],
		"</g>",
		*[
			image_tag(layer(grey, ink * grow(index)), "part spark", f"animation-delay: {order * 0.14}s")
			for order, index in enumerate(sparks)
		],
		"</g>",
	]
	TARGET.write_text(
		'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">'
		f"<style>{STYLE}</style>{''.join(images)}</svg>\n"
	)


def is_inside_face(labels, index):
	rows, columns = np.where(labels == index)
	return rows.mean() > 75 and columns.mean() < 165


def layer(grey, ink):
	return np.dstack([grey, grey, grey, ink * 255]).astype(np.uint8)


# Fit the gradient behind the mascot, so the head can move without leaving a hole.
def background(rgb, alpha, ink):
	rows, columns = np.mgrid[: rgb.shape[0], : rgb.shape[1]] / rgb.shape[0]
	terms = np.stack([np.ones_like(rows), rows, columns, rows * columns, rows**2, columns**2], -1)
	known = (ink == 0) & (alpha == 255)
	coefficients, *_ = np.linalg.lstsq(terms[known], rgb[known], rcond=None)
	filled = np.clip(terms @ coefficients, 0, 255)
	return np.dstack([filled, alpha]).astype(np.uint8)


def image_tag(pixels, css_class, style=""):
	rows, columns = np.where(pixels[..., 3] > 0)
	top, bottom, left, right = rows.min(), rows.max() + 1, columns.min(), columns.max() + 1
	buffer = io.BytesIO()
	Image.fromarray(pixels[top:bottom, left:right]).save(buffer, "PNG", optimize=True)
	data = base64.b64encode(buffer.getvalue()).decode()
	return (
		f'<image class="{css_class}" style="{style}" x="{left}" y="{top}" width="{right - left}" '
		f'height="{bottom - top}" href="data:image/png;base64,{data}"/>'
	)


if __name__ == "__main__":
	main()
