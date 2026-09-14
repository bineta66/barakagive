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
            {{ bailleur ? 'Modifier le bailleur' : 'Nouveau bailleur' }}
          </h2>
          <button
            @click="fermer"
            class="text-gray-400 hover:text-gray-600 transition"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        <p class="text-sm text-gray-500 mt-1">
          {{ bailleur ? 'Modifiez les informations du bailleur' : 'CrÃ©ez un nouveau bailleur' }}
        </p>
      </div>

      <form @submit.prevent="submit" class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Nom de l'organisation *</label>
          <input
            v-model="form.nom"
            type="text"
            placeholder="DG ECHO, USAID, AFD..."
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Contact institutionnel *</label>
          <input
            v-model="form.contact"
            type="email"
            placeholder="contact@organisation.org"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Type *</label>
          <select
            v-model="form.type"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">SÃ©lectionner</option>
            <option>International</option>
            <option>National</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Financement engagÃ©</label>
          <input
            v-model="form.finance"
            type="text"
            placeholder="4 500 000 Ã¢â€šÂ¬"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Projets associÃ©s</label>
          <input
            v-model="form.projets"
            type="number"
            placeholder="0"
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
            <option>ReÃ§u</option>
            <option>En attente</option>
          </select>
        </div>
      </form>

      <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
        <BoutonTertiary @click="fermer">
          Annuler
        </BoutonTertiary>
        <BoutonPrimary @click="submit">
          {{ bailleur ? 'Mettre Ã  jour' : 'Enregistrer' }}
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
  bailleur: { type: Object, default: null },
})

const emit = defineEmits(['fermer', 'save'])

const form = ref({
  nom: '',
  contact: '',
  type: '',
  finance: '',
  projets: 0,
  statut: 'ReÃ§u',
})

watch(
  () => props.ouvert,
  (val) => {
    if (val && props.bailleur) {
      form.value = { ...props.bailleur }
    }
    if (val && !props.bailleur) {
      form.value = {
        nom: '',
        contact: '',
        type: '',
        finance: '',
        projets: 0,
        statut: 'ReÃ§u',
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





