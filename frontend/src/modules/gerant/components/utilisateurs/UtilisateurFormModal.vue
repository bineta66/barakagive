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
            {{ utilisateur ? "Modifier l'utilisateur" : "Nouvel utilisateur" }}
          </h2>
          <button
            @click="fermer"
            class="text-gray-400 hover:text-gray-600 transition"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        <p class="text-sm text-gray-500 mt-1">
          {{ utilisateur ? "Modifiez les informations de l'utilisateur" : "CrÃ©ez un nouvel utilisateur" }}
        </p>
      </div>

      <form @submit.prevent="submit" class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Nom complet *</label>
          <input
            v-model="form.nom"
            type="text"
            placeholder="Nom prÃ©nom"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Email *</label>
          <input
            v-model="form.email"
            type="email"
            placeholder="nom@barakagive.org"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">RÃ´le *</label>
          <select
            v-model="form.role"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">SÃ©lectionner</option>
            <option>Chef de projet</option>
            <option>Responsable Finance</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">TÃ©lÃ©phone</label>
          <input
            v-model="form.telephone"
            type="tel"
            placeholder="+221 XX XXX XX XX"
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
            <option>Actif</option>
            <option>Inactif</option>
          </select>
        </div>
      </form>

      <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
        <BoutonTertiary @click="fermer">
          Annuler
        </BoutonTertiary>
        <BoutonPrimary @click="submit">
          {{ utilisateur ? 'Mettre Ã  jour' : 'Enregistrer' }}
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
  utilisateur: { type: Object, default: null },
})

const emit = defineEmits(['fermer', 'save'])

const form = ref({
  nom: '',
  email: '',
  role: '',
  telephone: '',
  statut: 'Actif',
})

watch(
  () => props.ouvert,
  (val) => {
    if (val && props.utilisateur) {
      form.value = { ...props.utilisateur }
    }
    if (val && !props.utilisateur) {
      form.value = {
        nom: '',
        email: '',
        role: '',
        telephone: '',
        statut: 'Actif',
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





