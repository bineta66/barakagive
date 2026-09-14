<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="fermer"
  >
    <div class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full">
      <div class="p-6">
        <div class="flex justify-between items-center">
          <h2 class="text-2xl font-bold" style="color: #744D03">
            {{ partenaire ? 'Modifier le partenaire' : 'Nouveau partenaire' }}
          </h2>
          <button
            @click="fermer"
            class="text-gray-400 hover:text-gray-600 transition"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        <p class="text-sm text-gray-500 mt-1">
          {{ partenaire ? 'Modifiez les informations du partenaire' : 'CrÃ©ez un nouveau partenaire' }}
        </p>
      </div>

      <form @submit.prevent="submit" class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Nom de l'organisation *</label>
          <input
            v-model="form.nom"
            type="text"
            placeholder="Croissant-Rouge SahÃ©lien, MSF..."
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Domaine d'intervention *</label>
          <input
            v-model="form.domaine"
            type="text"
            placeholder="Secours, SantÃ©, Eau..."
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Zone d'intervention *</label>
          <input
            v-model="form.zone"
            type="text"
            placeholder="Dakar, ThiÃ¨s, Kaolack..."
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Projet associÃ©</label>
          <input
            v-model="form.projet"
            type="text"
            placeholder="Nom du projet"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Statut *</label>
          <select
            v-model="form.statut"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option>ACTIF</option>
            <option>INACTIF</option>
          </select>
        </div>
      </form>

      <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
        <BoutonTertiary @click="fermer">
          Annuler
        </BoutonTertiary>
        <BoutonPrimary @click="submit">
          {{ partenaire ? 'Mettre Ã  jour' : 'Enregistrer' }}
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
  partenaire: { type: Object, default: null },
})

const emit = defineEmits(['fermer', 'save'])

const form = ref({
  nom: '',
  domaine: '',
  zone: '',
  projet: '',
  statut: 'ACTIF',
})

watch(
  () => props.ouvert,
  (val) => {
    if (val && props.partenaire) {
      form.value = { ...props.partenaire }
    }
    if (val && !props.partenaire) {
      form.value = {
        nom: '',
        domaine: '',
        zone: '',
        projet: '',
        statut: 'ACTIF',
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





