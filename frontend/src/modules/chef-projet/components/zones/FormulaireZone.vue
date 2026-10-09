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
        maxlength="200"
        placeholder="Ex : Zone Nord Pikine"
        @input="validateNom"
        class="w-full rounded-lg border border-gray-300 bg-slate-50 px-3 py-2 text-sm focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
      />
      <p v-if="errors.nom" class="mt-1 text-xs text-red-600">{{ errors.nom }}</p>
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
        class="w-full rounded-lg border border-gray-300 bg-slate-50 px-3 py-2 text-sm focus:ring-2 focus:ring-bleu-nuit/30 outline-none resize-y"
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
        step="1"
        placeholder="Ex : 1000"
        @input="validateRayon"
        class="w-full rounded-lg border border-gray-300 bg-slate-50 px-3 py-2 text-sm focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
      />
      <p v-if="errors.rayon" class="mt-1 text-xs text-red-600">{{ errors.rayon }}</p>
    </div>

    <p v-if="errors.position" role="alert" class="text-xs text-red-600">{{ errors.position }}</p>

    <!-- Boutons -->
    <div class="flex gap-3 pt-2">
      <BoutonSecondary type="button" class="flex-1">
        Annuler
      </BoutonSecondary>

      <BoutonPrimary type="submit" class="flex-1" :disabled="saving">
        {{ saving ? "Enregistrement..." : "Enregistrer" }}
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
  saving: { type: Boolean, default: false },
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
const errors = reactive({ nom: "", rayon: "", position: "" })

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
  if (props.saving) return
  validateNom()
  validateRayon()
  const latitude = Number(form.latitude)
  const longitude = Number(form.longitude)
  errors.position = Number.isFinite(latitude) && latitude >= -90 && latitude <= 90 &&
    Number.isFinite(longitude) && longitude >= -180 && longitude <= 180
    ? ""
    : "Veuillez sélectionner un point valide sur la carte."
  if (errors.nom || errors.rayon || errors.position) return
  emit("submit", { ...form })
}

const validateNom = () => {
  const value = String(form.nom || "").trim()
  errors.nom = !value
    ? "Ce champ est obligatoire."
    : value.length > 200
      ? "Le nom ne peut pas dépasser 200 caractères."
      : ""
}

const validateRayon = () => {
  const rayon = Number(form.rayon)
  errors.rayon = !Number.isInteger(rayon) || rayon <= 0
    ? "Le rayon doit être un nombre entier supérieur à 0."
    : ""
}
</script>
