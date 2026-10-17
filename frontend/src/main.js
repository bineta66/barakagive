import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { installLiveFormValidation } from './services/liveFormValidation'

// PWA
import { registerSW } from 'virtual:pwa-register'

const updateSW = registerSW({
  onNeedRefresh() {
    if (confirm('Nouvelle version disponible. Voulez-vous mettre à jour?')) {
      updateSW(true)
    }
  },
  onOfflineReady() {
    console.log('Application prête pour le mode hors ligne')
  },
  onRegistered(registration) {
    console.log('Service Worker enregistré:', registration)
  },
  onRegisterError(error) {
    console.error('Erreur d\'enregistrement du Service Worker:', error)
  }
})

const app = createApp(App)
installLiveFormValidation()

app.use(createPinia())
app.use(router)

app.mount('#app')
