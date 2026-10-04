<template>
	<div class="relative flex h-full flex-col overflow-y-auto bg-night px-5 py-10">
		<ThemeButton
			class="absolute right-4 top-4 text-lg leading-none opacity-60 transition hover:opacity-100"
		/>
		<div class="m-auto w-full max-w-sm">
			<p
				class="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.28em] text-accent"
			>
				<svg class="h-3 w-3 fill-accent" viewBox="0 0 24 24">
					<path :d="SHAPES[1].path" />
				</svg>
				Live quiz
			</p>
			<h1
				class="flex items-center gap-3 font-display text-6xl font-extrabold leading-none text-paper"
			>
				<img alt="" class="size-14 rounded-2xl" :src="LOGO_URL" />
				TriviaTap
			</h1>
			<p class="mt-3 text-paper/50">
				Type the PIN from the big screen, pick a nickname and a face, and you're in.
			</p>

			<form class="mt-9 flex flex-col gap-7" @submit.prevent="join">
				<div class="flex flex-col gap-2">
					<label
						class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45"
						for="game-pin"
					>
						Game PIN
					</label>
					<PinInputRoot
						v-model="pinDigits"
						class="grid grid-cols-6 gap-2"
						type="number"
						placeholder="·"
						@complete="nicknameInput?.focus()"
					>
						<PinInputInput
							v-for="(digit, index) in PIN_LENGTH"
							:key="digit"
							:index="index"
							:id="index === 0 ? 'game-pin' : undefined"
							:aria-label="`PIN digit ${digit} of ${PIN_LENGTH}`"
							:autofocus="index === 0 && !pin"
							class="h-16 w-full rounded-2xl border border-haze bg-dusk p-0 text-center font-mono text-3xl font-bold text-paper caret-accent placeholder:text-paper/20 focus:border-accent focus:ring-0"
						/>
					</PinInputRoot>
				</div>

				<div class="flex flex-col gap-2">
					<span class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45">
						You
					</span>
					<div class="flex items-center gap-3">
						<AvatarPic
							:id="avatar"
							:size="56"
							class="ring-2 ring-mint ring-offset-2 ring-offset-night"
						/>
						<div class="relative min-w-0 flex-1">
							<input
								aria-label="Nickname"
								ref="nicknameInput"
								v-model="nickname"
								class="w-full rounded-2xl border border-haze bg-dusk py-3.5 pl-4 pr-12 text-lg font-medium text-paper placeholder:text-paper/25 focus:border-accent focus:ring-0"
								placeholder="Your nickname"
								maxlength="20"
								autocomplete="off"
							/>
							<button
								type="button"
								class="absolute inset-y-0 right-1.5 my-auto grid size-9 place-items-center rounded-xl text-paper/45 transition hover:bg-haze/60 hover:text-paper"
								aria-label="More nickname ideas"
								title="More nickname ideas"
								@click="suggestions = suggestNicknames()"
							>
								<LucideShuffle class="size-4" />
							</button>
						</div>
					</div>
					<span class="flex flex-wrap items-center gap-2 pt-1">
						<button
							v-for="suggestion in suggestions"
							:key="suggestion"
							type="button"
							class="rounded-full border px-3 py-1 text-sm transition"
							:class="
								nickname === suggestion
									? 'border-accent text-accent'
									: 'border-haze text-paper/70 hover:border-accent hover:text-accent'
							"
							@click="nickname = suggestion"
						>
							{{ suggestion }}
						</button>
					</span>
				</div>

				<div class="flex flex-col gap-2">
					<span class="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/45">
						Swipe for a face
					</span>
					<!-- The bleed lives on the wrapper so the scroller's 50% end padding,
					     which is what lets the first and last face reach the centre line,
					     measures against the full-bleed width. -->
					<div
						class="-mx-5 [mask-image:linear-gradient(to_right,transparent,#000_18%,#000_82%,transparent)]"
					>
						<div
							ref="scroller"
							class="no-scrollbar flex snap-x snap-mandatory gap-1 overflow-x-auto px-[calc(50%-26px)] py-1.5 motion-safe:scroll-smooth"
							@scroll="queuePick"
						>
							<!-- Only the face inside scales, so picking never reflows the row. -->
							<button
								v-for="option in avatars"
								:key="option.id"
								:data-avatar="option.id"
								type="button"
								class="shrink-0 snap-center"
								:aria-label="option.id"
								:aria-pressed="avatar === option.id"
								@click="select(option.id)"
							>
								<span
									class="block rounded-full p-0.5 transition duration-200"
									:class="
										avatar === option.id
											? 'bg-mint ring-2 ring-mint'
											: 'scale-75 opacity-60 hover:opacity-100'
									"
								>
									<AvatarPic :id="option.id" :size="48" />
								</span>
							</button>
						</div>
					</div>
				</div>

				<button
					type="submit"
					class="rounded-2xl bg-brand py-4 font-display text-xl font-extrabold text-sunk transition hover:brightness-110 disabled:opacity-50"
					:disabled="joining || !ready"
				>
					{{ joining ? "Joining…" : "Join game" }}
				</button>
				<p v-if="error" class="text-center text-sm text-alert" role="alert">
					{{ error }}
				</p>
			</form>

			<RouterLink
				class="mt-8 block text-center text-sm text-paper/45 hover:text-paper"
				to="/login"
			>
				Want to host a quiz? Log in or sign up
			</RouterLink>
		</div>
	</div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from "vue";
import { PinInputInput, PinInputRoot } from "reka-ui";
import { useRoute, useRouter } from "vue-router";
import { call, errorText } from "@/api";
import { savePlayer } from "@/player";
import { avatars, randomAvatar } from "@/avatars";
import { suggestNicknames } from "@/nicknames";
import { SHAPES } from "@/game";
import AvatarPic from "@/components/AvatarPic.vue";
import ThemeButton from "@/components/ThemeButton.vue";
import { LOGO_URL } from "@/theme";

const route = useRoute();
const router = useRouter();

const PIN_LENGTH = 6;

const pin = ref(String(route.query.pin || "").slice(0, PIN_LENGTH));
const pinDigits = computed({
	get: () => [...pin.value],
	set: (value) => (pin.value = value.join("")),
});
const nickname = ref("");
const avatar = ref(randomAvatar());
const suggestions = ref(suggestNicknames());
const joining = ref(false);
const error = ref("");
const scroller = ref(null);
const nicknameInput = ref(null);
const ready = computed(() => pin.value.length === PIN_LENGTH && nickname.value.trim());

const centerSelected = (behavior) =>
	scroller.value
		?.querySelector(`[data-avatar="${avatar.value}"]`)
		?.scrollIntoView({ inline: "center", block: "nearest", behavior });

function select(id) {
	avatar.value = id;
	nextTick(() => centerSelected("smooth"));
}

// The highlight stays put and the faces move under it, so the pick is whatever
// the scroll parks in the centre. Snapping keeps it off the gaps between faces.
function pickCentered() {
	const row = scroller.value;
	if (!row) return;
	const center = row.getBoundingClientRect().left + row.clientWidth / 2;
	let closest = null;
	let smallest = Infinity;
	for (const slot of row.children) {
		const box = slot.getBoundingClientRect();
		const distance = Math.abs(box.left + box.width / 2 - center);
		if (distance < smallest) {
			smallest = distance;
			closest = slot;
		}
	}
	if (closest) avatar.value = closest.dataset.avatar;
}

let pickPending = false;
function queuePick() {
	if (pickPending) return;
	pickPending = true;
	requestAnimationFrame(() => {
		pickPending = false;
		pickCentered();
	});
}

// The opening pick is random, so it lands anywhere in the roster.
onMounted(() => {
	centerSelected("instant");
	if (pin.value.length === PIN_LENGTH) nicknameInput.value?.focus();
});

async function join() {
	error.value = "";
	joining.value = true;
	try {
		const result = await call("trivia_tap.api.join_session", {
			pin: pin.value.trim(),
			nickname: nickname.value.trim(),
			avatar: avatar.value,
		});
		savePlayer(result);
		router.push("/play");
	} catch (e) {
		error.value = errorText(e);
	} finally {
		joining.value = false;
	}
}
</script>
