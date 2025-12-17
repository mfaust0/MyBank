import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import http from '@/services/http.js'

export const useAuth = defineStore('auth', () => {

  const token = ref(localStorage.getItem('token'))
  const user = ref(null)
  const contoPresente = ref(null)
  const dettagliConto = ref(null)

  const isAuthenticated = computed(() => {
    return token.value
  })

  function setToken(tokenValue) {
    localStorage.setItem('token', tokenValue)
    token.value = tokenValue
  }

  function clear() {
    localStorage.removeItem('token')
    token.value = ''
    user.value = null
    contoPresente.value = null
    dettagliConto.value = null
  }

  async function checkContoUtente() {
    if ( !token.value) {
      clear()
      return false
    }

    try {
      const response = await http.get('/conto/conto')
      dettagliConto.value = response.data
      contoPresente.value = true

      return true

    } catch (error) {
      if (error.response && error.response.status === 400) {
        contoPresente.value = false
        dettagliConto.value = null
        return false
      } else {
        console.error("Errore nel recupero dati conto: ", error)
        contoPresente.value = false
        dettagliConto.value = null
        throw error
      }
    }
  }

  async function fetchUser() {

    try {
      const response = await http.get('/utente/me')
      const { uuid_utente, nome, cognome, ragione_sociale, partita_iva } = response.data;
      user.value = {}
      if (nome && cognome) {
        user.value.fullName = `${nome} ${cognome}`;
      }
      if (ragione_sociale) {
        user.value.ragioneSociale = `${ragione_sociale}`
      }
      if( uuid_utente ) {
        user.value.uuid_utente = `${uuid_utente}`
      }
      if( partita_iva ) {
        user.value.partita_iva = `${partita_iva}`
      }

    } catch ( err ) {
      console.error("Errore nel recupero dei dati dell'utente (probabile token scaduto)", err)
      clear()
      }
  }

  async function loginUser(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const { data } = await http.post('/utente/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })

    setToken(data.access_token)
    await fetchUser()
    return data
  }

  return {
    token,
    user,
    setToken,
    isAuthenticated,
    clear,
    fetchUser,
    loginUser,
    contoPresente,
    dettagliConto,
    checkContoUtente
  }
})
