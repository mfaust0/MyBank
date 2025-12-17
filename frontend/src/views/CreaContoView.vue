<template>
  <BContainer class="mt-4">
    <h2>Ci siamo quasi..</h2>
    <p>Ho bisogno di sapere quale sarà il saldo iniziale del conto che stiamo aprendo</p>

    <BForm @submit.prevent="apriConto">
      <BFormGroup label="Saldo iniziale (>= 0):" label-for="saldoIniziale" class="mb-3">
        <BInputGroup>
          <BInputGroupText>€</BInputGroupText>
          <BFormInput
            id="saldoIniziale"
            type="number"
            v-model.number="saldoIniziale"
            min="0"
            step="0.01"
            required
          ></BFormInput>
        </BInputGroup>
      </BFormGroup>
      <BButton type="submit" variant="primary">
        Apri conto
      </BButton>
      <BAlert v-if="errorMessage" variant="danger" class="mt-3">
        {{ errorMessage }}
      </BAlert>
      <BAlert v-if="successMessage" variant="success" class="mt-3">
        {{ successMessage }}
      </BAlert>
    </BForm>
  </BContainer>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuth } from '@/stores/auth.js'
  import http from '@/services/http.js'
  import { BContainer, BForm, BFormGroup, BFormInput, BInputGroup, BInputGroupText, BButton, BAlert } from 'bootstrap-vue-next'
  
  const errorMessage = ref('')
  const auth = useAuth()
  const router = useRouter()
  const saldoIniziale = ref(0)
  const successMessage = ref('')

  const apriConto = async () => {
    errorMessage.value = ''
    successMessage.value = ''

    if (saldoIniziale.value < 0) {
      errorMessage.value = 'Il saldo iniziale non può essere negativo.'
      return
    }

    if (!auth.user || !auth.user.uuid_utente) {
      errorMessage.value = 'Impossibile creare il conto: utente non trovato.'
      return
    }

    const payload = {
      uuid_utente: auth.user.uuid_utente,
      saldo_iniziale: saldoIniziale.value
    }

    try {
      const response = await http.post('/conto/apri_conto', payload)
      console.log('Conto creato', response.data)
      successMessage.value = 'Conto aperto con successo!'
      setTimeout(() => {
        router.push({ name: 'dashboard' })
      }, 1000);
    } catch (error) {
        console.error('Errore durante la creazione del conto:', error.response || error.message);
        errorMessage.value = error.response?.data?.detail || 'Si è verificato un errore durante la creazione del conto.'
      }
  }

</script>

<style>
</style>
