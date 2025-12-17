<template>
  <BContainer class="mt-4">
    <h1>Nuovo Bonifico SEPA</h1>
    <template v-if="auth.isAuthenticated">
      <BForm @submit.prevent="nuovoBonifico">
        <BFormGroup label="Mail beneficiario:" label-for="mailBeneficiario" class="mb-3">
          <BFormInput
            id="mailBeneficiario"
            type="email"
            v-model="mailBeneficiario"
            placeholder="Inserisci la mail del beneficiario"
            required
          />
        </BFormGroup>
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
        <BFormGroup label="Data esecuzione:" label-for="dataEsecuzione" class="mb-3">
          <BFormInput
            id="dataEsecuzione"
            type="date"
            v-model="dataEsecuzione"
            required
          />
        </BFormGroup>
        <BFormGroup label="Causale:" label-for="descrizione" class="mb-3">
          <BFormInput
            id="descrizione"
            type="text"
            v-model="descrizione"
            placeholder="Causale"
          />
        </BFormGroup>
        <BButton type="submit" variant="primary">Esegui</BButton>
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
  import type { AxiosError } from 'axios'
  const auth = useAuth()
  const router = useRouter()

  const userId = auth.user?.uuid_utente
  const errorMessage = ref('')
  const mailBeneficiario = ref('')
  const importo = ref(0)
  const dataEsecuzione = ref('')
  const descrizione = ref('')
  const successMessage = ref('')

  const nuovoBonifico = async () => {

    errorMessage.value = ''
    successMessage.value = ''

    if (!userId) {
      errorMessage.value = "Impossibile recuperare uuid utente"
      return
    }

    let endpoint = '/transazione/nuovo_bonifico'
    let payload = {
      beneficiario: mailBeneficiario.value,
      importo: importo.value,
      data_esecuzione: dataEsecuzione.value,
      data: dataEsecuzione.value,
      descrizione: descrizione.value
    }

    try {
      const response = await http.post(endpoint, payload)
      console.log('Bonifico inviato:', response.data)
      successMessage.value = 'Bonifico inviato!'

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
