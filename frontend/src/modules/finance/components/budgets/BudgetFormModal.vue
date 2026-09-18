<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="fermer"
  >
    <div class="bg-white border border-slate-200 rounded-2xl shadow-xs-sm max-w-3xl w-full">
      <div class="p-6">
        <div class="flex justify-between items-center">
          <h2 class="text-2xl font-bold" style="color: #744D03">
            {{ budget ? 'Modifier le budget' : 'Nouveau budget' }}
          </h2>
          <button
            @click="fermer"
            class="text-gray-400 hover:text-gray-600 transition"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        <p class="text-sm text-gray-500 mt-1">
          {{ budget ? 'Modifiez les informations du budget' : 'Créez un nouveau budget pour le projet' }}
        </p>
      </div>

      <form @submit.prevent="submit" class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Projet *</label>
          <select
            v-model="form.projetId"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">Sélectionner un projet</option>
            <option v-for="p in projets" :key="p.id" :value="p.id">{{ p.nom }} ({{ p.code }})</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Don *</label>
          <select
            v-model="form.donId"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            required
          >
            <option value="">Sélectionner un don</option>
            <option v-for="don in dons" :key="don.id" :value="don.id">
              {{ don.reference }} - {{ don.bailleur }} ({{ don.montant }} FCFA)
            </option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Exercice *</label>
          <input
            v-model="form.exercice"
            type="text"
            placeholder="2025"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Budget total *</label>
          <input
            v-model.number="form.budgetTotal"
            type="number"
            placeholder="0 FCFA"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Date début *</label>
          <input
            v-model="form.dateDebut"
            type="date"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Date fin *</label>
          <input
            v-model="form.dateFin"
            type="date"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Observation</label>
          <textarea
            v-model="form.observation"
            rows="3"
            placeholder="Observations sur le budget..."
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30 resize-none"
          ></textarea>
        </div>
      </form>

      <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
        <BoutonTertiary @click="fermer">
          Annuler
        </BoutonTertiary>
        <BoutonPrimary @click="submit">
          {{ budget ? 'Mettre à jour' : 'Enregistrer' }}
        </BoutonPrimary>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { X } from 'lucide-vue-next'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import BoutonTertiary from '@/components/ui/BoutonTertiary.vue'

const props = defineProps({
  ouvert: Boolean,
  projets: { type: Array, default: () => [] },
  dons: { type: Array, default: () => [] },
  budget: { type: Object, default: null },
})

const emit = defineEmits(['fermer', 'save'])

const form = ref({
  projetId: '',
  donId: '',
  exercice: '',
  budgetTotal: 0,
  dateDebut: '',
  dateFin: '',
  observation: '',
})

const projetSelectionne = computed(() => {
  return props.projets.find(p => p.id === Number(props.budget?.projetId)) || null
})

watch(
  () => props.ouvert,
  (val) => {
    if (val && props.budget) {
      form.value = { ...props.budget }
    }
    if (val && !props.budget) {
      form.value = {
        projetId: '',
        donId: '',
        exercice: '',
        budgetTotal: 0,
        dateDebut: '',
        dateFin: '',
        observation: '',
      }
    }
  },
  { immediate: true }
)

const submit = () => {
  const projet = props.projets.find(p => p.id === Number(form.value.projetId))
  const budgetData = {
    ...form.value,
    projetId: Number(form.value.projetId),
    donId: form.value.donId,
    projet: projet?.nom || '',
    chefProjet: projet?.chefProjet || '',
    budgetTotal: Number(form.value.budgetTotal) || 0,
    consomme: props.budget?.consomme || 0,
    solde: (Number(form.value.budgetTotal) || 0) - (props.budget?.consomme || 0),
    statut: props.budget?.statut || 'À budgétiser',
  }
  emit('save', budgetData)
}
</script>






