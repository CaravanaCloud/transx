<script lang="ts">

  import { redirect } from '@sveltejs/kit';
    import { SignIn, SignOut } from "@auth/sveltekit/components"
  import { page } from "$app/stores"
    // import { signIn } from "@auth/sveltekit/client";
    // import { invalidateAll } from '$app/navigation';
    // const handleSubmit = async (event: any) => {
    //   const data = new FormData(event.target);
    //   try {
    //     await signIn('credentials', {
    //       email: data.get('email'),
    //       password: data.get('password')
    //     });
    //   } catch (error) {
    //     await invalidateAll();
    //   }
    // }
    function login() {
    // para ser utilizado com o backend se n funcionar o login front with cognito
    window.location.href = "https://your-cognito-domain.auth.YOUR_REGION.amazoncognito.com/login?client_id=YOUR_CLIENT_ID&response_type=token&scope=email+openid+profile&redirect_uri=http://localhost:5173/auth/callback";
  }
  </script>
<h1>SvelteKit Auth Example</h1>
<div>
  {#if $page.data.session}
    {#if $page.data.session.user?.image}
      <img
        src={$page.data.session.user.image}
        class="avatar"
        alt="User Avatar"
      />
    {/if}
    <span class="signedInText">
      <small>Signed in as</small><br />
      <strong>{$page.data.session.user?.name ?? "User"}</strong>
    </span>
    <SignOut>
      <div slot="submitButton" class="buttonPrimary">Sign out</div>
    </SignOut>
  {:else}
    <span class="notSignedInText">You are not signed in</span>
    <SignIn>
      <div slot="submitButton" class="buttonPrimary">Sign in</div>
    </SignIn>
    <SignIn provider="cognito"/>
  {/if}
</div>