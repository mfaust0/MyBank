<script setup lang="ts">
  import axios from 'axios'
  import { ref, onMounted } from 'vue'

  const conti = ref([])
  const error = ref(null)

  const fetchConti = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/conti_aperti')
      conti.value = response.data
    } catch ( err ) {
      error.value = err
    }
  }

  onMounted(() => {
    fetchConti()
  })

</script>

<template>
  <div>
    <h2>Lista conti:</h2>
    <p v-if="error">Errore nel caricamento dei conti: {{ error.message }}</p>
    <ul v-else-if="conti.length">
      <li v-for="conto in conti" :key="conto.numero_conto">
        <a href="www.google.com"> Conto nr: {{ conto.numero_conto }} Titolare: {{ conto.intestatario }}</a>
      </li>
    </ul>
    <p v-else>Nessun conto trovato! Creane uno ora!</p>
  </div>
</template>
