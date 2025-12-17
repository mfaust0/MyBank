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
  auth.clear();
});
</script>

<style scoped>

</style>
