<script lang="ts">
	import '../app.postcss';
	import { AppShell, AppBar } from '@skeletonlabs/skeleton';

	import type { PageData } from './$types';

	export let data: PageData;

	// Floating UI for Popups
	import { computePosition, autoUpdate, flip, shift, offset, arrow } from '@floating-ui/dom';
	import { storePopup } from '@skeletonlabs/skeleton';

	storePopup.set({ computePosition, autoUpdate, flip, shift, offset, arrow });
</script>

<!-- App Shell -->
<AppShell>
	<!-- App Bar -->
	<AppBar>
		<svelte:fragment slot="lead">
			<a href="/" target="_blank" rel="noreferrer">
				<strong class="text-xl uppercase">TransX</strong>
			</a>
			<a
				class="btn btn-sm variant-ghost-surface"
				href="https://github.com/CaravanaCloud/transx"
				target="_blank"
				rel="noreferrer"
			>
				GitHub
			</a>
		</svelte:fragment>
		<!-- <svelte:fragment>
			<a
				class="btn btn-sm variant-ghost-surface"
				href="https://github.com/CaravanaCloud/transx"
				target="_blank"
				rel="noreferrer"
			>
				GitHub
			</a>
		</svelte:fragment> -->
		<!-- { lead: {}; default: {}; trail: {}; headline: {} -->

		<svelte:fragment slot="trail">
			{#if data.email}
				<a
					class="btn btn-sm variant-ghost-surface"
					href={data.signOutUrl}
					target="_blank"
					rel="noreferrer"
				>
					logout
				</a>
			{:else}
				<a
					class="btn btn-sm variant-ghost-surface"
					href={data.signInUrl}
					target="_blank"
					rel="noreferrer"
				>
					login
				</a>
			{/if}
	
		</svelte:fragment>
	</AppBar>
	<!-- Page Route Content -->
	<slot />
</AppShell>
