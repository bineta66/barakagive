<template>
  <div v-if="ouvert" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="fermer">
    <div class="bg-white border border-slate-200 rounded-2xl shadow-xs-sm max-w-md w-full">
      <div class="p-6">
        <h2 class="text-2xl font-bold" style="color: #744D03">Nouveau don</h2>
        <p class="text-sm text-gray-500 mt-1">Enregistrer un nouveau financement</p>
      </div>

      <form @submit.prevent="submit" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Bailleur / Donateur *</label>
          <input v-model="form.bailleur" type="text" class="w-full border rounded-lg px-3 py-2" required>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Projet *</label>
          <select v-model="form.projet" class="w-full border rounded-lg px-3 py-2" required>
            <option value="">Sélectionner</option>
            <option v-for="p in projets" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Budget *</label>
          <select v-model="form.budget" class="w-full border rounded-lg px-3 py-2" required>
            <option value="">Sélectionner</option>
            <option v-for="b in budgets" :key="b.id" :value="b.id">{{ b.source_financement }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Montant *</label>
          <input v-model.number="form.montant" type="number" class="w-full border rounded-lg px-3 py-2" required>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Moyen de paiement *</label>
          <select v-model="form.moyen_paiement" class="w-full border rounded-lg px-3 py-2" required>
            <option value="VIREMENT">Virement</option>
            <option value="ESPECE">Espèce</option>
            <option value="CHEQUE">Chèque</option>
            <option value="CARTE">Carte</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date *</label>
          <input v-model="form.date" type="date" class="w-full border rounded-lg px-3 py-2" required>
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
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'

const props = defineProps({
  ouvert: Boolean,
})

const emit = defineEmits(['fermer', 'save'])

const store = useFinanceStore()

const form = ref({
  bailleur: '',
  projet: '',
  budget: '',
  montant: 0,
  moyen_paiement: 'VIREMENT',
  date: '',
})

const projets = ref([])
const budgets = ref([])

onMounted(async () => {
  try {
    const [projectsRes, budgetsRes] = await Promise.all([
      api.get('/api/projects/'),
      api.get('/api/finance/budgets/'),
    ])
    projets.value = projectsRes.data
    budgets.value = budgetsRes.data
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