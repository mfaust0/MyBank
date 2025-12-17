import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.css'
/*import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'*/
import * as BootstrapVueNext from 'bootstrap-vue-next'
/*import 'bootstrap/dist/js/bootstrap.bundle.min.js'*/
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'


const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(BootstrapVueNext.createBootstrap())

app.mount('#app')
