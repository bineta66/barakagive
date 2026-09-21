<template>
  <div v-if="ouvert" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="fermer">
    <div class="bg-white border border-slate-200 rounded-2xl shadow-xs-sm max-w-md w-full">
      <div class="p-6">
        <h2 class="text-2xl font-bold" style="color: #744D03">Nouvelle dépense</h2>
        <p class="text-sm text-gray-500 mt-1">Enregistrer une nouvelle dépense</p>
      </div>

      <form @submit.prevent="submit" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Projet *</label>
          <select v-model="form.projet" class="w-full border rounded-lg px-3 py-2" required>
            <option value="">Sélectionner</option>
            <option v-for="p in projets" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Catégorie *</label>
          <input v-model="form.categorie" type="text" class="w-full border rounded-lg px-3 py-2" required>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Montant *</label>
          <input v-model.number="form.montant" type="number" class="w-full border rounded-lg px-3 py-2" required>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fournisseur</label>
          <input v-model="form.fournisseur" type="text" class="w-full border rounded-lg px-3 py-2">
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Région</label>
          <input v-model="form.region" type="text" class="w-full border rounded-lg px-3 py-2">
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date *</label>
          <input v-model="form.date" type="date" class="w-full border rounded-lg px-3 py-2" required>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea v-model="form.description" rows="2" class="w-full border rounded-lg px-3 py-2"></textarea>
        </div>
      </form>

      <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
        <button @click="fermer" class="px-4 py-2 border rounded-lg">Annuler</button>
        <button @click="submit" class="px-4 py-2 bg-orange-600 text-white rounded-lg">Enregistrer</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api.js'

const props = defineProps({
  ouvert: Boolean,
})

const emit = defineEmits(['fermer', 'save'])

const form = ref({
  projet: '',
  categorie: '',
  montant: 0,
  fournisseur: '',
  region: '',
  date: '',
  description: '',
})

const projets = ref([])

onMounted(async () => {
  try {
    const response = await api.get('/api/projects/')
    projets.value = response.data
  } catch (error) {
    console.error('Erreur:', error)
  }
})

const submit = () => {
  emit('save', form.value)
  fermer()
}

const fermer = () => emit('fermer')
</script>