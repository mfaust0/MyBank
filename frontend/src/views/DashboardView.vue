 <template>
  <div class="dashboard-container">
    <h1>Benvenuto, {{ auth.user?.fullName || auth.user?.ragioneSociale }}</h1>
    <div class="saldo-card">
      <h2>Saldo Attuale:</h2>
      <p v-if="erroreSaldo" class="error-message">{{ erroreSaldo }}</p>
      <p v-else class="importo-saldo">{{ formatCurrency(saldo) }}</p>
    </div>

    <div class="operazioni-container">
      <button @click="effettuaBonifico" class="action-button primary">
          Effettua Bonifico
      </button>
      <button @click="effettuaDeposito" class="action-button secondary">
          Effettua Deposito
      </button>
    </div>

    <div class="movimenti-container">
      <h2>Lista Movimenti</h2>
      <p v-if="erroreMovimenti" class="error-message">{{ erroreMovimenti }}</p>
      <div v-else-if="movimenti.length" class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Data</th>
              <th>Causale</th>
              <th>Descrizione</th>
              <th>UUID Transazione</th>
              <th>Importo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="movimento in movimenti" :key="movimento.uuid_movimento" class="movement-item">
              <!-- Data Esecuzione -->
              <td>{{ formatDate(movimento.transazione?.data_esecuzione) }}</td>

              <!-- Causale -->
              <td>{{ movimento.causale?.descrizione }}</td>

              <!-- Descrizione (campo 'ciao') -->
              <td>{{ movimento.descrizione }}</td>

              <td class="uuid-colonna">{{ movimento.transazione?.uuid_transazione }}</td>
              <!-- Importo con colore e segno -->
              <td :class="movimento.segno === '+' ? 'amount-plus' : 'amount-minus'">
                {{ formatCurrency(movimento.transazione?.importo) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else>Nessun movimento trovato per questo conto.</p>
    </div>
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import http from '@/services/http.js'
  import { useAuth } from '@/stores/auth.js'

  const auth = useAuth()
  const router = useRouter()

  const saldo = ref(0)
  const movimenti = ref([])
  const erroreSaldo = ref(null)
  const erroreMovimenti = ref(null)

  const formatCurrency = (value) => {
    const numericValue = parseFloat(value);
    if (isNaN(numericValue)) return '';
    return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(numericValue);
  }

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('it-IT');
  }

  const fetchSaldo = async () => {
    erroreSaldo.value = null
    const userId = auth.user?.uuid_utente

    if (!userId) {
      erroreSaldo.value = "Impossibile recuperare uuid utente"
      return
    }

    try {
      const response = await http.get('/conto/saldo')
      saldo.value = response.data.saldo
    } catch (error) {
        erroreSaldo.value = 'Errore nel recupero del saldo.'
        console.error(error)
      }
  }

  const fetchMovimenti = async () => {
    erroreMovimenti.value = null
    const userId = auth.user?.uuid_utente

    try{
      const response = await http.get('/transazione/movimenti')
      movimenti.value = response.data
    } catch(error) {
        erroreMovimenti.value = 'Errore nel recupero dei movimenti'
        console.error(error)
      }
  }

  const effettuaBonifico = () => {
    router.push({ name: 'NuovoBonifico' });
  }

  const effettuaDeposito = () => {
    router.push({ name: 'NuovoDeposito' });
  }

  onMounted(() => {
    if (auth.isAuthenticated && auth.user) {
      fetchSaldo()
      fetchMovimenti()
    } else {
        router.push({ name: 'Login' });
      }

  })

</script>

<style scoped>

.dashboard-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
  color: #333;
}

h1 {
  color: #333;
  margin-bottom: 25px;
  text-align: center;
}

h2 {
  color: #0056b3;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}


.saldo-card {
  background-color: #007bff;
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.importo-saldo {
  font-size: 2.5em;
  font-weight: bold;
  margin: 0;
}


.operazioni-container {
  display: flex;
  gap: 15px;
  margin-bottom: 40px;
  justify-content: center;
}

.action-button {
  padding: 12px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  font-weight: bold;
  transition: background-color 0.3s;
  min-width: 150px;
}

.primary {
  background-color: #f75e25;
  color: white;
}

.primary:hover { background-color: #218838; }

.secondary {
  background-color: #28a745;
  color: black;
}

.secondary:hover { background-color: #e0a800; }


.movimenti-container {
    margin-top: 40px;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  table-layout: fixed;
  font-size: 0.9em;
}

th, td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

thead th {
  background-color: #f4f4f4;
  color: #333;
  font-weight: bold;
  text-transform: capitalize;
}

th:nth-child(1), td:nth-child(1) { width: 10%; }
th:nth-child(2), td:nth-child(2) { width: 18%; }
th:nth-child(3), td:nth-child(3) { width: 22%; }

th:nth-child(4), td:nth-child(4) {
    width: 35%;
}

th:nth-child(5), td:nth-child(5) {
    width: 15%;
    text-align: right;
}


tbody tr:hover { background-color: #f9f9f9; }

.amount-plus { color: #28a745; font-weight: bold; }
.amount-minus { color: #dc3545; font-weight: bold; }


.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 5px;
  margin-top: 15px;
  text-align: center;
}

p {
  margin-top: 10px;
}
</style>
