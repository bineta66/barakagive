<template>
  <form @submit.prevent="submit" class="space-y-4">
    <!-- Région (remplie automatiquement par le clic sur la carte) -->
    <div>
      <label class="block text-xs font-bold tracking-wider uppercase text-gray-700 mb-1">
        Région
      </label>
      <input
        :value="form.region"
        type="text"
        readonly
        class="w-full rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-600"
      />
    </div>

    <!-- Département (rempli automatiquement par le clic sur la carte) -->
    <div>
      <label class="block text-xs font-bold tracking-wider uppercase text-gray-700 mb-1">
        Département
      </label>
      <input
        :value="form.departement"
        type="text"
        readonly
        class="w-full rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-600"
      />
    </div>

    <!-- Nom de la zone -->
    <div>
      <label class="block text-xs font-bold tracking-wider uppercase text-gray-700 mb-1">
        Nom de la zone *
      </label>
      <input
        v-model="form.nom"
        type="text"
        required
        placeholder="Ex : Zone Nord Pikine"
        class="w-full rounded-lg border border-gray-300 bg-slate-50 px-3 py-2 text-sm focus:ring-2 focus:ring-or/30 outline-none"
      />
    </div>

    <!-- Description -->
    <div>
      <label class="block text-xs font-bold tracking-wider uppercase text-gray-700 mb-1">
        Description
      </label>
      <textarea
        v-model="form.description"
        rows="3"
        placeholder="Ex : Zone d'intervention"
        class="w-full rounded-lg border border-gray-300 bg-slate-50 px-3 py-2 text-sm focus:ring-2 focus:ring-or/30 outline-none resize-y"
      ></textarea>
    </div>

    <!-- Rayon -->
    <div>
      <label class="block text-xs font-bold tracking-wider uppercase text-gray-700 mb-1">
        Rayon (mètres) *
      </label>
      <input
        v-model.number="form.rayon"
        type="number"
        required
        min="1"
        placeholder="Ex : 1000"
        class="w-full rounded-lg border border-gray-300 bg-slate-50 px-3 py-2 text-sm focus:ring-2 focus:ring-or/30 outline-none"
      />
    </div>

    <!-- Boutons -->
    <div class="flex gap-3 pt-2">
      <BoutonSecondary type="button" class="flex-1">
        Annuler
      </BoutonSecondary>

      <BoutonPrimary type="submit" class="flex-1">
        Enregistrer
      </BoutonPrimary>
    </div>
  </form>
</template>

<script setup>
import { reactive, watch } from "vue"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"

const props = defineProps({
  mode: {
    type: String,
    default: "creation",
  },
  initialData: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(["submit"])

const form = reactive({
  region: "",
  departement: "",
  nom: "",
  description: "",
  rayon: 1000,
  statut: true,
  latitude: null,
  longitude: null,
})

watch(
  () => props.initialData,
  (newData) => {
    if (newData && Object.keys(newData).length > 0) {
      Object.assign(form, newData)
    }
  },
  { immediate: true, deep: true }
)

const submit = () => {
  if (!form.latitude || !form.longitude) {
    alert("Veuillez sélectionner un point sur la carte.")
    return
  }
  if (!form.rayon || Number(form.rayon) <= 0) {
    alert("Veuillez renseigner un rayon valide.")
    return
  }
  emit("submit", { ...form })
}
</script>
