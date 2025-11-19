<template>
  <div class="create-account-container">
    <h2>Ci siamo quasi..</h2>
    <p>Ho bisogno di sapere quale sarà il saldo iniziale del conto che stiamo aprendo</p>

    <form @submit.prevent="apriConto">
      <div class="form-group">
        <label for="saldoIniziale">Saldo iniziale (>= 0):</label>
        <div class="input-container">
          <span class="currency-symbol">€</span>
          <input
            type="number"
            id="saldoIniziale"
            v-model.number="saldoIniziale"
            min="0"
            step="0.01"
            required
          >
        </div>
      </div>
      <button type="submit">
        Apri conto
      </button>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
    </form>
  </div>
</template>


<script setup lang="ts">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuth } from '@/stores/auth.js'
  import http from '@/services/http.js'

  const errorMessage = ref('')
  const auth = useAuth()
  const router = useRouter()
  const saldoIniziale = ref(0)
  const successMessage = ref('');

  const apriConto = async () => {
    errorMessage.value = '';
    successMessage.value = '';

    if (saldoIniziale.value < 0) {
      errorMessage.value = 'Il saldo iniziale non può essere negativo.'
      isLoading.value = false
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

      router.push({ name: 'dashboard' })
    } catch (error) {
        console.error('Errore durante la creazione del conto:', error.response || error.message);
        errorMessage.value = error.response?.data?.detail || 'Si è verificato un errore durante la creazione del conto.';
      }


  }

  const resetForm = () => {

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
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 5px;
  margin-top: 15px;
  text-align: center;
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.currency-symbol {
  position: absolute;
  left: 10px;
  color: #888;
}

.input-container input {
  padding-left: 25px;
}
</style>
