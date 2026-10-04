# Phase 20: Animated join QR

## Goal

The lobby QR comes alive. Its dots first draw the TriviaTap mascot, then fly
into place as the real, scannable join code with the logo in the middle.
Inspired by tree.icqr.com, where voxels of a tree fold into a QR.

## Behaviour

- Each dark QR module is one dot. On first show the dots pop in as the mascot
  outline, sampled from the dark pixels of `trivia-tap-logo.png`, tinted with
  the logo's mint-to-green gradient.
- After a short hold the dots travel on a slight arc to their module, staggered
  from the centre outwards, and settle to the QR ink colour.
- The logo badge fades in over the middle once every dot has landed.
- The fullscreen code is the same component, so opening it plays the
  animation again at projector size.
- `prefers-reduced-motion: reduce` draws the finished QR at once.
- The final frame matches `renderQr`: error level H, margin 1, same colours, a
  20% logo badge. It must scan.

## Out of scope

- 3D voxels or WebGL. A 2D canvas carries the idea with no new dependency.
