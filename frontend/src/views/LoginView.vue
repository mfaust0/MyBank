<template>
  <BContainer class="mt-5">
    <BRow class="justify-content-center">
      <BCol md="6" lg="4">
        <h2>Login</h2>
        <BCard v-if="!auth.isAuthenticated" class="shadow-sm">
          <BForm @submit.prevent="login">
            <BFormInput
              v-model="user.username"
              type="text"
              placeholder="Mail"
              class="mb-3"
              required
            />
            <BFormInput
              v-model="user.password"
              type="password"
              placeholder="Password"
              class="mb-3"
              required
            />
            <BButton type="submit" variant="primary" class="w-100">Login</BButton>
          </BForm>
          <BAlert
            v-if="errorMsg"
            show variant="danger"
            class="mt-3"
          >
            {{ errorMsg }}
          </BAlert>
        </BCard>
        <p v-else>Hai già effettuato il login!</p>
      </BCol>
    </BRow>
  </BContainer>
</template>

<script setup>
  import {ref, reactive} from 'vue'
  import {useAuth} from '@/stores/auth.js'
  import { useRouter } from 'vue-router'
  import { BContainer, BRow, BCol, BCard, BForm, BFormInput, BButton, BAlert } from 'bootstrap-vue-next'

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

    const contoEsistente = await auth.checkContoUtente()
    if (!contoEsistente) {
      router.push({ name: 'crea_conto' })
      return
    } else {
    router.push({ name: 'dashboard' })
    }
  } catch (error) {
      console.log("Errore:", error?.response?.data || error.message);
      if (error.response && error.response.data && error.response.data.detail) {
        errorMsg.value = error.response.data.detail;
      }
    }
}
</script>

<style scoped>

</style>
