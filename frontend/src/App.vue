<template>
  <nav class="navbar">
    <ul class="navbar-links">
      <li>
        <router-link :to="{name:'home'}">Home</router-link>
      </li>
      <li>
        <router-link :to="{name:'dashboard'}">Dashboard</router-link>
      </li>
        <li v-if="!auth.isAuthenticated">
            <router-link  :to="{name:'register'}">Apri conto</router-link>
        </li>
    </ul>

    <div class="navbar-auth">
      <template v-if="auth.isAuthenticated && auth.user">
        <span> {{ auth.user.fullName || auth.user.ragioneSociale }} </span>
        <button @click="logout" class="logout-btn">Logout</button>
      </template>
      <template v-else>
        <router-link :to="{name:'login'}">Login</router-link>
      </template>
    </div>
  </nav>

  <!-- Qui verranno visualizzate le view delle rotte -->
  <router-view/>
</template>

<script setup lang="ts">
  import {useAuth} from '@/stores/auth.js'
  import { onMounted } from 'vue'
  import http from '@/services/http.js'
  import { useRouter } from 'vue-router'

  const router = useRouter()
  const auth = useAuth()

  function logout() {
    auth.clear()
    router.push({ name: 'logout' })
  }

  onMounted(() => {
    // Carica i dati all'avvio dell'app, SE un token è già presente in localStorage
    if (auth.isAuthenticated && !auth.user) {
        auth.fetchUser()
    }
  })
</script>

<style>
body {
  margin: 0;
  padding-top: 60px;
  background-color: #f4f7f9;
  font-family: 'Arial', Helvetica, Arial, sans-serif;
}


.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #0056b3;
  color: white;
  padding: 0 20px;
  height: 60px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  font-family: 'Arial', Helvetica, Arial, sans-serif;
}

.navbar-links {
  list-style: none;
  display: flex;
  margin: 0;
  padding: 0;
}

.navbar-links li {
  margin-right: 20px;
}

.navbar-links a, .navbar-auth a {
  color: white;
  text-decoration: none;
  padding: 10px 0;
  transition: color 0.3s, border-bottom 0.3s;
}

.navbar-links a:hover, .navbar-auth a:hover {
  color: #a0c4ff;
  border-bottom: 2px solid #a0c4ff;
}

.navbar-links a.router-link-exact-active {
    border-bottom: 2px solid #ffc107;
    color: #ffc107;
}

.navbar-auth {
  display: flex;
  align-items: center;
}

.navbar-auth span {
  margin-right: 15px;
  font-size: 0.9em;
  opacity: 0.9;
}

.logout-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #c82333;
}
</style>

