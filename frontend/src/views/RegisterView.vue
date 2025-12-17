<template>
  <BContainer class="mt-5">
    <BRow class="justify-content-center">
      <BCol md="8" lg="6">
        <BCard title="Conosciamoci meglio" class="shadow-sm">
          <BFormGroup label="Sono un:" label-for="userType" class="mb-3">
            <BFormSelect
              id="userType"
              v-model="userType"
              @change="resetForm"
              :options="[
                { value: 'privato', text: 'Privato' },
                { value: 'azienda', text: 'Azienda' }
              ]"
              required
            />
          </BFormGroup>
          <BForm @submit.prevent="registrazione" class="register-form">
            <BFormGroup label="Mail:" label-for="email" class="mb-3">
              <BFormInput
                type="email"
                id="email"
                v-model="formComune.mail"
                required
              />
            </BFormGroup>
            <BFormGroup label="Password:" label-for="password" class="mb-3">
              <BFormInput
                type="password"
                id="password"
                v-model="formComune.password"
                required
              />
            </BFormGroup>
            <div v-if="userType === 'privato'">
              <BFormGroup label="Nome:" label-for="nome" class="mb-3">
                <BFormInput
                  type="text"
                  id="nome"
                  v-model="formPrivato.nome"
                  required
                />
              </BFormGroup>
              <BFormGroup label="Cognome:" label-for="cognome" class="mb-3">
                <BFormInput
                  type="text"
                  id="cognome"
                  v-model="formPrivato.cognome"
                  required
                />
              </BFormGroup>
            </div>
            <div v-else>
              <BFormGroup label="Ragione Sociale:" label-for="ragioneSociale" class="mb-3">
                <BFormInput
                  type="text"
                  id="ragioneSociale"
                  v-model="formAzienda.ragione_sociale"
                  required
                />
              </BFormGroup>
              <BFormGroup label="P. IVA:" label-for="partitaIva" class="mb-3">
                <BFormInput
                  type="text"
                  id="partitaIva"
                  v-model="formAzienda.partita_iva"
                  required
                />
              </BFormGroup>
            </div>
            <BButton type="submit" variant="primary" class="w-100">
              Registrati
            </BButton>
            <BAlert v-if="errorMessage" show variant="danger" class="mt-3">
              {{ errorMessage }}
            </BAlert>
            <BAlert v-if="successMessage" show variant="success" class="mt-3">
              {{ successMessage }}
            </BAlert>
          </BForm>

        </BCard>
      </BCol>
    </BRow>
  </BContainer>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import http from '@/services/http.js'
  import { useAuth } from '@/stores/auth.js'
  import { BContainer, BRow, BCol, BCard, BForm, BFormGroup, BFormInput, BFormSelect, BButton, BAlert } from 'bootstrap-vue-next'

  const auth = useAuth()
  const router = useRouter()
  const userType = ref('privato')
  const errorMessage = ref('');
  const successMessage = ref('')

  const formComune = ref({
    mail: '',
    password: ''
  })

  const formPrivato = ref({
    nome: '',
    cognome: ''
  })

  const formAzienda = ref({
    ragione_sociale: '',
    partita_iva: ''
  })

  const registrazione = async () => {
    let endpoint = ''
    let payload = {}

    if (userType.value === 'privato'){
      endpoint = '/utente/crea_utente_privato'
      payload = {
        ...formComune.value,
        ...formPrivato.value
      }
    } else { //caso azienda
        endpoint = '/utente/crea_utente_azienda'
        payload = {
          ...formComune.value,
          ...formAzienda.value
        }
      }

      errorMessage.value = ''
      successMessage.value = ''

    try {
      const response = await http.post(endpoint, payload)
      console.log('Successo:', response.data)

      await auth.loginUser(formComune.value.mail, formComune.value.password)

      successMessage.value = 'Registrazione completata!'
      setTimeout(() => {
        router.push({ name: 'crea_conto' })
      }, 1000);
    } catch (error) {
        console.error('Errore:', error.response || error.message);
        errorMessage.value = error.response?.data?.detail || 'Si è verificato un errore.'
    }
  }

  const resetForm = () => {
    formPrivato.value = { nome: '', cognome: '' }
    formAzienda.value = { ragione_sociale: '', partita_iva: '' }
    errorMessage.value = ''
    successMessage.value = ''
  }

</script>

<style scoped>

</style>
