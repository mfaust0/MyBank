<!-- src/views/LogoutView.vue -->
<template>
  <div class="logout-container">
    <h1>Disconnessione Effettuata</h1>
    <p>Arrivederci</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuth } from '@/stores/auth.js';

const auth = useAuth();

onMounted(() => {
  // Ci assicuriamo che lo store sia pulito quando la pagina viene visitata
  auth.clear();
});
</script>

<style scoped>

</style>
