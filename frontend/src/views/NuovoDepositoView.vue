<template>
  <BContainer class="mt-4">
    <h1>Nuovo Deposito</h1>
    <template v-if="auth.isAuthenticated">
      <BForm @submit.prevent="nuovoDeposito">
        <BFormGroup label="Importo:" label-for="importo" class="mb-3">
          <BInputGroup>
            <BInputGroupText>€</BInputGroupText>
            <BFormInput
              id="importo"
              type="number"
              v-model.number="importo"
              min="1"
              step="0.01"
              placeholder="Inserisci importo"
              required
            />
          </BInputGroup>
        </BFormGroup>
        <BFormGroup label="Causale:" label-for="descrizione" class="mb-3">
          <BFormInput
            id="descrizione"
            type="text"
            v-model="descrizione"
            placeholder="Causale"
          />
        </BFormGroup>
        <BButton type="submit" variant="primary">Deposita</BButton>
      </BForm>

      <BAlert v-if="errorMessage" show variant="danger" class="mt-3">
        {{ errorMessage }}
      </BAlert>
      <BAlert v-if="successMessage" show variant="success" class="mt-3">
        {{ successMessage }}
      </BAlert>
    </template>
  </BContainer>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import http from '@/services/http.js'
  import { useAuth } from '@/stores/auth.js'
  import { BContainer, BForm, BFormGroup, BFormInput, BInputGroup, BInputGroupText, BButton, BAlert } from 'bootstrap-vue-next'

  const auth = useAuth()
  const router = useRouter()

  const userId = auth.user?.uuid_utente
  const importo = ref(0)
  const descrizione = ref('')
  const successMessage = ref('')
  const errorMessage = ref('')

  const nuovoDeposito = async () => {

    errorMessage.value = ''
    successMessage.value = ''

    if (!userId) {
      errorMessage.value = "Impossibile recuperare uuid utente"
      return
    }

    let endpoint = '/transazione/nuovo_deposito'
    let payload = {
      importo: importo.value,
      descrizione: descrizione.value
    }

    try {
      const response = await http.post(endpoint, payload)
      console.log('Deposito effettuato:', response.data)
      successMessage.value = 'Deposito effettuato!'

      setTimeout(() => {
        router.push({ name: 'dashboard' })
      }, 1000);


    } catch (error) {
        console.error('Errore:', error.response || error.message);
        errorMessage.value = error.response?.data?.detail || 'Si è verificato un errore.'
      }
  }

</script>

<style>

</style>
