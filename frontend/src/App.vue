<template>
  <BNavbar toggleable="lg" type="dark" variant="primary" fixed="top">
    <BNavbarBrand :to="{ name: 'home'}">MyBank</BNavbarBrand>
    <BNavbarToggle target="nav-collapse"></BNavbarToggle>

    <BCollapse id="nav-collapse" is-nav>
      <BNavbarNav>
        <BNavItem :to="{ name: 'home'}" active-class="active">Home</BNavItem>
        <BNavItem :to="{ name: 'dashboard'}" active-class="active">Dashboard</BNavItem>
        <BNavItem v-if="!auth.isAuthenticated" :to="{ name: 'register'}" active-class="active">Apri conto</BNavItem>
        <template v-if="visualizzaMenuOperazioni">
          <BNavItem :to="{ name: 'nuovo_bonifico'}" active-class="active">
            Nuovo Bonifico SEPA
          </BNavItem>
          <BNavItem :to="{ name: 'nuovo_deposito'}" active-class="active">
            Nuovo Deposito
          </BNavItem>
          <BNavItem @click="chiudiConto(auth.dettagliConto.uuid_conto)" link-classes="text-warning" active-class="active">
            Chiudi Conto
          </BNavItem>
        </template>
      </BNavbarNav>

      <BNavbarNav class="ms-auto">
        <template v-if="auth.isAuthenticated && auth.user">
          <BNavText class="text-light me-3">
            {{ auth.user.fullName || auth.user.ragioneSociale }}
          </BNavText>
          <b-button variant="danger" @click="logout">Logout</b-button>
        </template>
        <template v-else>
          <b-button variant="success" :to="{ name: 'login'}">Login</b-button>
        </template>
      </BNavbarNav>
    </BCollapse>
  </BNavbar>

<div class="pt-5 mt-3">
    <BContainer fluid>
      <BRow>  
        <BCol md="12">
          <router-view/>
        </BCol>
      </BRow>
    </BContainer>
  </div>
</template>

<script setup lang="ts">
  import { useAuth } from '@/stores/auth.js'
  import { onMounted, computed } from 'vue'
  import http from '@/services/http.js'
  import { useRouter } from 'vue-router'
  import { BNavbar, BNavbarBrand, BNavbarToggle, BCollapse, BNavbarNav, BNavItem, BNavText, BButton, BContainer, BRow, BCol } from 'bootstrap-vue-next'
    
  const router = useRouter()
  const auth = useAuth()

  function logout() {
    auth.clear()
    router.push({ name: 'logout' })
  }

  const chiudiConto = async (uuidConto) => {
    if (confirm('Sei sicuro di voler chiudere il conto?')) {
      try {
        await http.patch(`/conto/chiudi_conto`, {
          uuid_conto: uuidConto
        })
        alert('Conto chiuso con successo.')
        await auth.checkContoUtente()
        if (router.currentRoute.value.name !== 'dashboard') {
          router.push({ name: 'dashboard' })
        }
      } catch (error) {
        console.error("Errore durante la chiusura del conto:", error)
        alert('Errore durante la chiusura del conto: ', error.response?.data?.detail || error.message)
      }
    }
  }

  onMounted(() => {
    if (auth.isAuthenticated && !auth.user) {
        auth.fetchUser()
    }
  })

  const visualizzaMenuOperazioni = computed(() => {
    const routeName = router.currentRoute.value.name
    return auth.isAuthenticated && (routeName === 'dashboard' || routeName === 'nuovo_bonifico' || routeName === 'nuovo_deposito')
  })

</script>

<style>

</style>

