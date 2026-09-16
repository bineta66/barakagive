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
            {{ justificatif ? 'Modifier le justificatif' : 'Ajouter un justificatif' }}
          </h2>
          <button
            @click="fermer"
            class="text-gray-400 hover:text-gray-600 transition"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        <p class="text-sm text-gray-500 mt-1">
          {{ justificatif ? 'Modifiez les informations du justificatif' : 'Enregistrez un nouveau justificatif' }}
        </p>
      </div>

      <form @submit.prevent="submit" class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Dépense *</label>
          <select
            v-model="form.depenseId"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">Sélectionner une dépense</option>
            <option v-for="d in depenses" :key="d.id" :value="d.id">
              {{ d.libelle }} ({{ formatMontant(d.montant) }} FCFA)
            </option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Type de document *</label>
          <select
            v-model="form.typeDocument"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">Sélectionner</option>
            <option v-for="t in typesDocument" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Numéro du document *</label>
          <input
            v-model="form.numeroDocument"
            type="text"
            placeholder="FAC-2025-XXX"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Date du document *</label>
          <input
            v-model="form.dateDocument"
            type="date"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Montant</label>
          <input
            v-model.number="form.montant"
            type="number"
            placeholder="0 FCFA"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Pièce jointe</label>
          <div class="border-2 border-dashed border-gray-200 rounded-lg p-4 text-center hover:border-or/30 transition-colors cursor-pointer">
            <Upload :size="24" class="mx-auto text-gray-400 mb-2" />
            <p class="text-xs text-gray-500">PDF, JPG, PNG (max 5MB)</p>
            <input
              type="file"
              required
              accept=".pdf,.jpg,.jpeg,.png"
              @change="uploadFile"
            />
          </div>
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
          {{ justificatif ? 'Mettre à jour' : 'Enregistrer' }}
        </BoutonPrimary>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { X, Upload } from 'lucide-vue-next'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import BoutonTertiary from '@/components/ui/BoutonTertiary.vue'
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'

const store = useFinanceStore()
const { formatMontant } = store

const props = defineProps({
  ouvert: Boolean,
  depenses: { type: Array, default: () => [] },
  typesDocument: { type: Array, default: () => [] },
  justificatif: { type: Object, default: null },
  depenseInitiale: { type: Object, default: null },
})

const emit = defineEmits(['fermer', 'save'])

const form = ref({
  depenseId: '',
  typeDocument: '',
  numeroDocument: '',
  dateDocument: '',
  montant: 0,
  observation: '',
})

const uploadFile = (e) => {
  const file = e.target.files[0]
  if (file) {
    form.value.pieceJointe = file
    form.value.nomFichier = file.name
  }
}

watch(
  () => props.ouvert,
  (val) => {
    if (val && props.justificatif) {
      form.value = { ...props.justificatif }
    }
    if (val && !props.justificatif) {
      form.value = {
        depenseId: props.depenseInitiale?.id || '',
        typeDocument: '',
        numeroDocument: '',
        dateDocument: '',
        montant: 0,
        observation: '',
      }
    }
  },
  { immediate: true }
)

const submit = () => {
  const depense = props.depenses.find(d => d.id === Number(form.value.depenseId))
  const justificatifData = {
    id: props.justificatif?.id || null,
    depenseId: Number(form.value.depenseId),
    depense: depense?.libelle || '',
    projet: depense?.projet || '',
    typeDocument: form.value.typeDocument,
    numeroDocument: form.value.numeroDocument,
    dateDocument: form.value.dateDocument,
    montant: Number(form.value.montant) || 0,
    observation: form.value.observation,
    statut: props.justificatif?.statut || 'En attente',
    pieceJointe: form.value.pieceJointe,
  }
  emit('save', justificatifData)
}
</script>






