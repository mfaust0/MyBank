  import axios from 'axios'
  import { ref, onMounted } from 'vue'

  const saldo = ref(0.00)
  const error = ref(null)

  const fetchSaldo = async () => {
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
