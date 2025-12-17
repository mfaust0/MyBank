 <template>
  <div>
    <h1 class="mb-4">Benvenuto, {{ auth.user?.fullName || auth.user?.ragioneSociale }}</h1>
    <BCard v-if="auth.dettagliConto" title="Dettagli Conto" class="mb-4 shadow-sm">
      <div v-if="dettagliContoInCaricamento" class="d-flex align-items-center">
        <BSpinner small type="grow"></BSpinner>
        <span class="ms-2">Caricamento dettagli conto...</span>
      </div>
      <p v-else-if="erroreConto" class="text-danger"> {{ erroreConto }}</p>
      <div v-else-if="auth.dettagliConto">
        <BRow>
          <BCol md="6">
            <p><strong>UUID Conto: </strong> {{ auth.dettagliConto.uuid_conto }}</p>
          </BCol>
        </BRow>
        <BRow>
          <BCol md="6">
            <p><strong>Data apertura: </strong> {{ formatDate(auth.dettagliConto.data_apertura) }}</p>
          </BCol>
        </BRow>
        <BRow>
          <BCol md="6">
            <p v-if="auth.dettagliConto.data_chiusura">
              Conto chiuso in data 
              <span class="text-danger">{{ formatDate(auth.dettagliConto.data_chiusura) }}</span>
            </p>
          </BCol>
        </BRow>
      </div>
      <p v-else class="text-muted">Dettagli conto non disponibili</p>
    </BCard>

    <BCard title="Saldo Attuale:" class="mb-4 shadow-sm">
      <div v-if="saldoInCaricamento" class="d-flex align-items-center">
        <BSpinner small type="grow"></BSpinner>
        <span class="ms-2">Caricamento saldo...</span>
      </div>
      <p v-else-if="erroreSaldo" class="text-danger">{{ erroreSaldo }}</p>
      <p v-else class="h2 text-success">{{ formatCurrency(saldo) }}</p>
    </BCard>

    <div class="movimenti-container">
      <h2 class="mb-3">Lista Movimenti:</h2>
      <p v-if="erroreMovimenti" class="text-danger">{{ erroreMovimenti }}</p>
      <div v-else-if="movimentiInCaricamento" class="d-flex align-items-center">
        <BSpinner small type="grow"></BSpinner>
        <span class="ms-2">Caricamento movimenti...</span>
      </div>
      <div v-else-if="movimenti.length">
        <BTable striped hover responsive :items="movimenti" :fields="tableFields" class="shadow-sm">
          <template #cell(data_transazione)="data">
            {{ formatDate(data.item.data_transazione) }}
          </template>
          <template #cell(importo_transazione)="data">
            <span :class="data.item.segno === '+' ? 'text-success' : 'text-danger'">
              {{ data.item.segno && formatCurrency(data.item.importo_transazione) }}
            </span> 
          </template>
          <template #cell(descrizione_movimento)="data">
            <span v-if="data.item.descrizione_movimento">
              {{ data.item.descrizione_movimento }}
            </span>
          </template>
          <template #cell(controparte)="data">
            <span v-if="data.item.controparte">
              {{ data.item.controparte }}
            </span>
          </template>
          <template #cell(nome_causale)="data">
            <span v-if="data.item.nome_causale">
              {{ data.item.nome_causale }}
            </span>
          </template>
          <template #cell(annulla)="data">
            <BButton
              v-if="data.item.nome_causale === 'BONIFICO IN USCITA'"
              variant="outline-danger"
              size="sm" 
              @click="annullaTransazione(data.item.uuid_transazione)"
              title="Annulla"
            >
              <span class="fw-bold">X</span>
          </BButton>
          </template>
        </BTable>
      </div>
      <p v-else class="text-muted">Nessun movimento trovato per questo conto.</p>
    </div>
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import http from '@/services/http.js'
  import { useAuth } from '@/stores/auth.js'
  import { BCard, BTable, BButton, BSpinner, BRow, BCol } from 'bootstrap-vue-next'

  const auth = useAuth()
  const router = useRouter()

  const saldo = ref(0)
  const movimenti = ref([])
  const erroreSaldo = ref(null)
  const erroreMovimenti = ref(null)
  const saldoInCaricamento = ref(false)
  const movimentiInCaricamento = ref(false)
  const dettagliContoInCaricamento = ref(false)

  const tableFields = [
    { key: 'data_transazione', label: 'Data', sortable: true },
    { key: 'descrizione_movimento', label: 'Descrizione', sortable: false },
    { key: 'controparte', label: 'Controparte', sortable: true },
    { key: 'importo_transazione', label: 'Importo', sortable: true, tdClass: 'text-end' },
    { key: 'nome_causale', label: 'Causale', sortable: true },
    { key: 'annulla', label: 'Annulla', sortable: false, thClass: 'text-center' }
  ]

  const formatCurrency = (importo) => {
    const numericValue = parseFloat(importo)
    if (isNaN(numericValue)) return ''
    return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(numericValue)
  }

  const formatDate = (stringaData) => {
    if (!stringaData) return ''
    return new Date(stringaData).toLocaleDateString('it-IT')
  }

  const annullaTransazione = async (uuidTransazione) => {
    if (!confirm('Sei sicuro di voler annullare la transazione ' + uuidTransazione + '?')) {
      return
    }
    try {
      await http.delete(`/transazione/annulla_bonifico/${uuidTransazione}`)
      await fetchSaldo()
      await fetchMovimenti()
      alert('Transazione ' + uuidTransazione + ' annullata con successo.')
    } catch (error) {
        console.error("Errore durante l'annullamento della transazione:", error)
        let errorMessage = "Errore generico durante l'annullamento"
        if (error.response && error.response.data && error.response.data.detail) {
          errorMessage = error.response.data.detail
        }
        else if (error.message) {
          errorMessage = "Errore durante l'annullamento della transazione."
        }
        alert(errorMessage)
      }
  }

  const fetchDettagliConto = async () => {
    dettagliContoInCaricamento.value = true
    try {
      auth.dettagliConto()
    } catch (error) {
        console.error("Errore nel recupero dei dettagli del conto:", error)
      } finally {
          dettagliContoInCaricamento.value = false
        }
  }

  const fetchSaldo = async () => {
    erroreSaldo.value = null
    saldoInCaricamento.value = true
    const userId = auth.user?.uuid_utente

    try {
      const response = await http.get('/conto/saldo')
      saldo.value = response.data.saldo
    } catch (error) {
        erroreSaldo.value = 'Errore nel recupero del saldo.'
        console.error(error)
      } finally {
          saldoInCaricamento.value = false
        }
  }

  const fetchMovimenti = async () => {
    erroreMovimenti.value = null
    movimentiInCaricamento.value = true
    const userId = auth.user?.uuid_utente

    try{
      const response = await http.get('/transazione/movimenti')
      movimenti.value = response.data
    } catch(error) {
        erroreMovimenti.value = 'Errore nel recupero dei movimenti'
        console.error(error)
      } finally {
          movimentiInCaricamento.value = false
        }
  }

  onMounted(() => {
    if (auth.isAuthenticated && auth.user) {
      fetchSaldo()
      fetchMovimenti()
    } else {
        router.push({ name: 'Login' })
      }

  })

</script>

<style scoped>
</style>
