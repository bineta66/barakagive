<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="fermer"
  >
    <div class="bg-white border border-slate-200 rounded-2xl shadow-xs-sm max-w-3xl w-full">
      <div class="p-6">
        <div class="flex justify-between items-center">
          <h2 class="text-2xl font-bold text-or">
            {{ projet ? 'Modifier le projet' : 'Nouveau projet' }}
          </h2>
          <button
            @click="fermer"
            class="text-gray-400 hover:text-gray-600 transition"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        <p class="text-sm text-gray-500 mt-1">
          {{ projet ? 'Modifiez les informations du projet' : 'Créez un nouveau projet' }}
        </p>
      </div>

      <form @submit.prevent="submit" class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Nom du projet *</label>
          <input
            v-model="form.nom"
            type="text"
            placeholder="Ex: Distribution alimentaire hivernage"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Code *</label>
          <input
            v-model="form.code"
            type="text"
            placeholder="PRJ-2025-XXX"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Chef de projet *</label>
          <select
            v-model="form.chefProjet"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">Sélectionner</option>
            <option v-for="c in chefsProjet" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Responsable Finance *</label>
          <select
            v-model="form.responsableFinance"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">Sélectionner</option>
            <option v-for="r in responsablesFinance" :key="r" :value="r">{{ r }}</option>
          </select>
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
          <label class="block text-xs font-medium text-gray-600 mb-1">Statut</label>
          <select
            v-model="form.statut"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
          >
            <option>En cours</option>
            <option>Planifié</option>
            <option>Terminé</option>
          </select>
        </div>

        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Observation</label>
          <textarea
            v-model="form.observation"
            rows="3"
            placeholder="Observations..."
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30 resize-none"
          ></textarea>
        </div>
      </form>

      <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
        <BoutonTertiary @click="fermer">
          Annuler
        </BoutonTertiary>
        <BoutonPrimary @click="submit">
          {{ projet ? 'Mettre à jour' : 'Enregistrer' }}
        </BoutonPrimary>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { X } from 'lucide-vue-next'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import BoutonTertiary from '@/components/ui/BoutonTertiary.vue'

const props = defineProps({
  ouvert: Boolean,
  projet: { type: Object, default: null },
  chefsProjet: { type: Array, default: () => [] },
  responsablesFinance: { type: Array, default: () => [] },
})

const emit = defineEmits(['fermer', 'save'])

const form = ref({
  nom: '',
  code: '',
  chefProjet: '',
  responsableFinance: '',
  dateDebut: '',
  dateFin: '',
  statut: 'En cours',
  observation: '',
})

watch(
  () => props.ouvert,
  (val) => {
    if (val && props.projet) {
      form.value = { ...props.projet }
    }
    if (val && !props.projet) {
      form.value = {
        nom: '',
        code: '',
        chefProjet: '',
        responsableFinance: '',
        dateDebut: '',
        dateFin: '',
        statut: 'En cours',
        observation: '',
      }
    }
  },
  { immediate: true }
)

const fermer = () => {
  emit('fermer')
}

const submit = () => {
  emit('save', { ...form.value })
}
</script>






