<template>
  <h2>Login</h2>
  <template v-if="!auth.isAuthenticated">
    <form @submit.prevent="login">
      <input type="text" placeholder="mail" v-model="user.username">
      <input type="password" placeholder="password" v-model="user.password">
      <button type="submit">Login</button>
    </form>
    <template v-if="errorMsg">
      <div>
        {{ errorMsg }}
      </div>
    </template>
  </template>
  <template v-else>
    <p>Hai già effettuato il login</p>
  </template>
</template>

<script setup>
  import {ref, reactive} from 'vue'
  import {useAuth} from '@/stores/auth.js'
  import { useRouter } from 'vue-router'
  const auth = useAuth()
  const router = useRouter()
  const errorMsg = ref(null)

  const user = reactive({
    username:'',
    password:''
  })

async function login() {
  errorMsg.value = null
  try {
    await auth.loginUser(user.username, user.password)
    console.log("Login Successo:", auth.token)
    router.push({ name: 'dashboard' })
  } catch (error) {
      console.log("Errore:", error?.response?.data || error.message);
      if (error.response && error.response.data && error.response.data.detail) {
        // Cattura il messaggio specifico dall'API FastAPI
        errorMsg.value = error.response.data.detail;
      }
    }
}
</script>

<style scoped>
form {
  max-width: 400px;
  margin: 50px auto;
  padding: 30px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-family: 'Arial', sans-serif;
}

h2 {
  color: #333;
  text-align: center;
  margin-top: 50px;
  margin-bottom: 25px;
  font-family: 'Arial', sans-serif;
}

input {
  width: 100%;
  padding: 12px;
  margin-bottom: 15px; /* Spazio tra gli input */
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}

/* Stile per il pulsante di Login */
button {
  width: 100%;
  padding: 12px;
  margin-top: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #0056b3;
}

div {
  color: #dc3545; /* Rosso vivo */
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 5px;
  margin-top: 15px;
  text-align: center;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

p {
    text-align: center;
    margin-top: 20px;
    color: #28a745;
    font-size: 1.1em;
}
</style>
