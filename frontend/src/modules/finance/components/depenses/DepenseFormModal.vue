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
            {{ depense ? 'Modifier la dÃ©pense' : 'Nouvelle dÃ©pense' }}
          </h2>
          <button
            @click="fermer"
            class="text-gray-400 hover:text-gray-600 transition"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        <p class="text-sm text-gray-500 mt-1">
          {{ depense ? 'Modifiez les informations de la dÃ©pense' : 'Enregistrez une nouvelle dÃ©pense' }}
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
          <label class="block text-xs font-medium text-gray-600 mb-1">Campagne (optionnel)</label>
          <select
            v-model="form.campagne"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
          >
            <option value="">Aucune campagne</option>
            <option v-for="c in campagnes" :key="c.id" :value="c.nom">{{ c.nom }}</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">CatÃ©gorie *</label>
          <select
            v-model="form.categorie"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">SÃ©lectionner</option>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
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
          <label class="block text-xs font-medium text-gray-600 mb-1">Fournisseur *</label>
          <input
            v-model="form.fournisseur"
            type="text"
            placeholder="Nom du fournisseur"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Mode de paiement *</label>
          <select
            v-model="form.modePaiement"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          >
            <option value="">SÃ©lectionner</option>
            <option v-for="m in modesPaiement" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">LibellÃ© *</label>
          <input
            v-model="form.libelle"
            type="text"
            placeholder="Description de la dÃ©pense"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
            required
          />
        </div>

        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Commentaire</label>
          <textarea
            v-model="form.commentaire"
            rows="3"
            placeholder="Commentaires..."
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30 resize-none"
          ></textarea>
        </div>
      </form>

      <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
        <BoutonTertiary @click="fermer">
          Annuler
        </BoutonTertiary>
        <BoutonPrimary @click="submit">
          {{ depense ? 'Mettre Ã  jour' : 'Enregistrer' }}
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
  campagnes: { type: Array, default: () => [] },
  categories: { type: Array, default: () => [] },
  modesPaiement: { type: Array, default: () => [] },
  depense: { type: Object, default: null },
})

const emit = defineEmits(['fermer', 'save'])

const form = ref({
  projetId: '',
  campagne: '',
  categorie: '',
  montant: 0,
  date: '',
  fournisseur: '',
  modePaiement: '',
  libelle: '',
  commentaire: '',
})

const campagnes = computed(() => {
  return Array.from({ length: 3 }, (_, i) => ({
    id: i + 1,
    nom: `Campagne ${i + 1}`
  }))
})

watch(
  () => props.ouvert,
  (val) => {
    if (val && props.depense) {
      form.value = { ...props.depense, campagne: props.depense.campagne || '' }
    }
    if (val && !props.depense) {
      form.value = {
        projetId: '',
        campagne: '',
        categorie: '',
        montant: 0,
        date: '',
        fournisseur: '',
        modePaiement: '',
        libelle: '',
        commentaire: '',
      }
    }
  },
  { immediate: true }
)

const submit = () => {
  const projet = props.projets.find(p => p.id === Number(form.value.projetId))
  const depenseData = {
    ...form.value,
    id: props.depense?.id || null,
    projetId: Number(form.value.projetId),
    projet: projet?.nom || '',
    montant: Number(form.value.montant) || 0,
    statut: props.depense?.statut || 'ValidÃ©',
    justificatif: props.depense?.justificatif || null,
  }
  emit('save', depenseData)
}
</script>





