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
            {{ don ? 'Modifier le financement' : 'Nouveau financement' }}
          </h2>
          <button
            @click="fermer"
            class="text-gray-400 hover:text-gray-600 transition"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        <p class="text-sm text-gray-500 mt-1">
          {{ don ? 'Modifiez les informations du financement' : 'Enregistrez un nouveau financement reÃ§u' }}
        </p>
      </div>

      <form @submit.prevent="submit" class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Projet *</label>
          <select
            v-model="form.projetId"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">SÃ©lectionner un projet</option>
            <option v-for="p in projets" :key="p.id" :value="p.id">{{ p.nom }}</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Bailleur *</label>
          <select
            v-model="form.bailleur"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">SÃ©lectionner un bailleur</option>
            <option v-for="b in bailleurs" :key="b" :value="b">{{ b }}</option>
            <option value="__new__">Autre...</option>
          </select>
        </div>

        <div v-if="form.bailleur === '__new__'">
          <label class="block text-xs font-medium text-gray-600 mb-1">Nouveau bailleur</label>
          <input
            v-model="form.nouveauBailleur"
            type="text"
            placeholder="Nom du bailleur"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Type de financement *</label>
          <select
            v-model="form.typeFinancement"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">SÃ©lectionner</option>
            <option v-for="t in typesFinancement" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Montant *</label>
          <input
            v-model.number="form.montant"
            type="number"
            placeholder="0 FCFA"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Date *</label>
          <input
            v-model="form.date"
            type="date"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">RÃ©fÃ©rence</label>
          <input
            v-model="form.reference"
            type="text"
            placeholder="REF-2025-XXX"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
          />
        </div>

        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Commentaire</label>
          <textarea
            v-model="form.commentaire"
            rows="3"
            placeholder="Commentaires sur le financement..."
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30 resize-none"
          ></textarea>
        </div>
      </form>

      <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
        <BoutonTertiary @click="fermer">
          Annuler
        </BoutonTertiary>
        <BoutonPrimary @click="submit">
          {{ don ? 'Mettre Ã  jour' : 'Enregistrer' }}
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
  bailleurs: { type: Array, default: () => [] },
  typesFinancement: { type: Array, default: () => [] },
  don: { type: Object, default: null },
})

const emit = defineEmits(['fermer', 'save'])

const form = ref({
  projetId: '',
  bailleur: '',
  nouveauBailleur: '',
  typeFinancement: '',
  montant: 0,
  date: '',
  reference: '',
  commentaire: '',
})

watch(
  () => props.ouvert,
  (val) => {
    if (val && props.don) {
      form.value = { ...props.don }
    }
    if (val && !props.don) {
      form.value = {
        projetId: '',
        bailleur: '',
        nouveauBailleur: '',
        typeFinancement: '',
        montant: 0,
        date: '',
        reference: '',
        commentaire: '',
      }
    }
  },
  { immediate: true }
)

const submit = () => {
  let bailleurFinal = form.value.bailleur
  if (bailleurFinal === '__new__') {
    bailleurFinal = form.value.nouveauBailleur
  }
  const projet = props.projets.find(p => p.id === Number(form.value.projetId))
  const donData = {
    ...form.value,
    bailleur: bailleurFinal,
    projetId: Number(form.value.projetId),
    projet: projet?.nom || '',
    montant: Number(form.value.montant) || 0,
  }
  emit('save', donData)
}
</script>





