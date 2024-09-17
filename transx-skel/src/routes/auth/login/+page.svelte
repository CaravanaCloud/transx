<script lang="ts">
    import { signIn } from "@auth/sveltekit/client";
    import { invalidateAll } from '$app/navigation';
    const handleSubmit = async (event: any) => {
      const data = new FormData(event.target);
      try {
        await signIn('credentials', {
          email: data.get('email'),
          password: data.get('password')
        });
      } catch (error) {
        await invalidateAll();
      }
    }
  </script>
  <h1>Login</h1>
  <div>
    <form name="login" method="POST" on:submit|preventDefault={handleSubmit}>
      <input name="email" type="email" placeholder="Email Address" />
      <input name="password" placeholder="Password" type="password" />
      <button>Sign In</button>
    </form>
  </div>