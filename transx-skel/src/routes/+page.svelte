<script lang="ts">
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<div class="container h-full mx-auto flex justify-center items-center">
	<div class="space-y-10 text-center flex flex-col items-center">
		<h2 class="h2">Welcome to Transx</h2>
		<h3 class="h3">Automated transcription and translation</h3>
		<a class="btn variant-filled" href="/protected/file_upload" rel="noreferrer"> Submit files </a>

		<h1>Auth demo</h1>
		<a href={data.signInUrl}>Sign in (or sign up)</a>
		{#if data.email}
			<p>Logged in as {data.email}</p>
		{:else}
			<p>Not logged in</p>
		{/if}
	</div>
</div>

<style lang="postcss">
	figure {
		@apply flex relative flex-col;
	}
	figure svg,
	.img-bg {
		@apply w-64 h-64 md:w-80 md:h-80;
	}
	.img-bg {
		@apply absolute z-[-1] rounded-full blur-[50px] transition-all;
		animation:
			pulse 5s cubic-bezier(0, 0, 0, 0.5) infinite,
			glow 5s linear infinite;
	}
	@keyframes glow {
		0% {
			@apply bg-primary-400/50;
		}
		33% {
			@apply bg-secondary-400/50;
		}
		66% {
			@apply bg-tertiary-400/50;
		}
		100% {
			@apply bg-primary-400/50;
		}
	}
	@keyframes pulse {
		50% {
			transform: scale(1.5);
		}
	}
</style>
