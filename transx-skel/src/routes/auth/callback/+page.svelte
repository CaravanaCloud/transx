<script>
    import { onMount } from "svelte";
  
    onMount(() => {
      const hash = window.location.hash;
      const params = new URLSearchParams(hash.substring(1));
      const token = params.get("id_token");
      
      if (token) {
        // Armazene o token localmente
        localStorage.setItem("token", token);
        window.location.href = "/";
      } else {
        console.error("Token não encontrado");
      }
    });
  </script>
  
  <p>Autenticando...</p>
  