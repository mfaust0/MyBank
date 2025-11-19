<template>
  <div class="register-container">
    <h1>Conosciamoci meglio</h1>
    <!-- Selettore del tipo di utente (rimane invariato) -->
    <div class="form-group">
      <label for="userType">Sono un: </label>
      <select id="userType" v-model="userType" @change="resetForm">
        <option value="privato">Privato</option>
        <option value="azienda">Azienda</option>
      </select>
    </div>

    <form @submit.prevent="registrazione" class="register-form">

      <div class="form-group">
        <label for="email">Email:</label>
        <input type="email" id="email" v-model="formComune.mail" required>
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="formComune.password" required>
      </div>

      <!-- Campi per utente privato -->
      <div v-if="userType === 'privato'">
        <div class="form-group">
          <label for="nome">Nome:</label>
          <input type="text" id="nome" v-model="formPrivato.nome" required>
        </div>
        <div class="form-group">
          <label for="cognome">Cognome:</label>
          <input type="text" id="cognome" v-model="formPrivato.cognome" required>
        </div>
      </div>

      <!-- Campi per utente azienda -->
      <div v-else>
        <div class="form-group">
          <label for="ragioneSociale">Ragione Sociale:</label>
          <input type="text" id="ragioneSociale" v-model="formAzienda.ragione_sociale" required>
        </div>
        <div class="form-group">
          <label for="partitaIva">P. IVA:</label>
          <input type="text" id="partitaIva" v-model="formAzienda.partita_iva" required>
        </div>
      </div>
      <button type="submit">
        Registrati
      </button>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import http from '@/services/http.js'
  import { useAuth } from '@/stores/auth.js'

  const auth = useAuth()
  const router = useRouter()
  const userType = ref('privato')
  const errorMessage = ref('');

  //Dati comuni per Aziende e Privati
  const formComune = ref({
    mail: '',
    password: ''
  })

  // Dati specifici per il form Privato
  const formPrivato = ref({
    nome: '',
    cognome: ''
  })

  // Dati specifici per il form Azienda
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

      errorMessage.value = '';

    try {
      const response = await http.post(endpoint, payload);
      console.log('Successo:', response.data);

      await auth.loginUser(formComune.value.mail, formComune.value.password)
      router.push({ name: 'crea_conto' })

    } catch (error) {
        console.error('Errore:', error.response || error.message);
        errorMessage.value = error.response?.data?.detail || 'Si è verificato un errore.';
    }
  }

  const resetForm = () => {
    formPrivato.value = { nome: '', cognome: '' };
    formAzienda.value = { ragioneSociale: '', partitaIva: '' };
    errorMessage.value = '';
  }

</script>

<style scoped>
.register-container {
  max-width: 500px;
  margin: 40px auto;
  padding: 30px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-family: 'Arial', sans-serif;
}

h1 {
  color: #333;
  text-align: center;
  margin-bottom: 25px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: bold;
}

input, select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus, select:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}

button {
  width: 100%;
  padding: 12px;
  margin-top: 20px;
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

.error-message {
  color: #dc3545; /* Rosso vivo */
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 5px;
  margin-top: 15px;
  text-align: center;
}
</style>
