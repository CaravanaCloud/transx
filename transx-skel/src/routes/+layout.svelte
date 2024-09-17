<script lang="ts">
	import '../app.postcss';
	import { AppShell, AppBar } from '@skeletonlabs/skeleton';
	import { signOut } from '@auth/sveltekit/client';
	import { page } from '$app/stores';

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
		</svelte:fragment>
		<svelte:fragment slot="trail">
			<a
				class="btn btn-sm variant-ghost-surface"
				href="https://github.com/CaravanaCloud/transx"
				target="_blank"
				rel="noreferrer"
			>
				GitHub
			</a>
		</svelte:fragment>

		{#if $page.data.session}
			<a 
				class="btn btn-sm variant-ghost-surface"
				on:click|preventDefault={signOut}
			>
				Logout
			</a>
		{:else}
				<a href="/auth/login" class="btn btn-sm variant-ghost-surface" >Login</a>
		{/if}
			
	</AppBar>
	<!-- Page Route Content -->
	<slot />
</AppShell>
