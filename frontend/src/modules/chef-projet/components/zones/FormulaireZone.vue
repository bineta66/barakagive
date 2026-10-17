<template>
  <form @submit.prevent="submit" class="space-y-4">
    <!-- Région (auto-remplie par clic sur la carte ou modifiable manuellement) -->
    <div>
      <div class="flex items-center justify-between mb-1">
        <label class="block text-xs font-bold tracking-wider uppercase text-gray-700">
          Région *
        </label>
        <span class="text-[11px] text-gray-500 font-normal">
          {{ form.region ? form.region : 'Cliquer sur la carte' }}
        </span>
      </div>
      <select
        v-model="form.region"
        @change="onRegionChange"
        class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
      >
        <option value="" disabled>Sélectionnez une région ou cliquez sur la carte</option>
        <option v-for="r in senegalRegions" :key="r" :value="r">{{ r }}</option>
      </select>
      <p v-if="errors.region" class="mt-1 text-xs text-red-600">{{ errors.region }}</p>
    </div>

    <!-- Département (éditable, filtré selon la région sélectionnée) -->
    <div>
      <div class="flex items-center justify-between mb-1">
        <label class="block text-xs font-bold tracking-wider uppercase text-gray-700">
          Département *
        </label>
        <span v-if="availableDepartements.length > 1" class="text-[11px] text-gray-500 font-normal">
          {{ availableDepartements.length }} départements disponibles
        </span>
      </div>

      <select
        v-if="availableDepartements.length > 0"
        v-model="form.departement"
        class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
      >
        <option value="" disabled>Sélectionnez un département</option>
        <option v-for="d in availableDepartements" :key="d" :value="d">{{ d }}</option>
      </select>
      <input
        v-else
        v-model="form.departement"
        type="text"
        :placeholder="form.region ? 'Nom du département' : 'Sélectionnez d’abord une région'"
        class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:ring-2 focus:ring-bleu-nuit/30 outline-none"
      />
      <p v-if="errors.departement" class="mt-1 text-xs text-red-600">{{ errors.departement }}</p>
    </div>

    <!-- Coordonnées (indicateur visuel) -->
    <div class="rounded-lg bg-slate-50 border border-slate-200 p-2.5 text-xs text-gray-600 space-y-1">
      <div class="flex justify-between items-center">
        <span class="font-medium text-gray-700">Position :</span>
        <span v-if="form.latitude && form.longitude" class="font-mono text-bleu-nuit font-semibold">
          {{ Number(form.latitude).toFixed(4) }}, {{ Number(form.longitude).toFixed(4) }}
        </span>
        <span v-else class="text-gray-400 italic">Cliquez sur la carte</span>
      </div>
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
        placeholder="Ex : Zone d'intervention humanitaire"
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
      <BoutonSecondary type="button" class="flex-1" @click="onCancel">
        Annuler
      </BoutonSecondary>

      <BoutonPrimary type="submit" class="flex-1" :disabled="saving">
        {{ saving ? "Enregistrement..." : "Enregistrer" }}
      </BoutonPrimary>
    </div>
  </form>
</template>

<script setup>
import { reactive, computed, watch } from "vue"
import { useRouter } from "vue-router"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"

const router = useRouter()

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

const senegalRegions = [
  "Dakar",
  "Diourbel",
  "Fatick",
  "Kaffrine",
  "Kaolack",
  "Kédougou",
  "Kolda",
  "Louga",
  "Matam",
  "Saint-Louis",
  "Sédhiou",
  "Tambacounda",
  "Thiès",
  "Ziguinchor",
]

const departementsByRegion = {
  "Dakar": ["Dakar", "Guédiawaye", "Keur Massar", "Pikine", "Rufisque"],
  "Diourbel": ["Bambey", "Diourbel", "Mbacké"],
  "Fatick": ["Fatick", "Foundiougne", "Gossas"],
  "Kaffrine": ["Birkelane", "Kaffrine", "Koungheul", "Malem Hodar"],
  "Kaolack": ["Guinguinéo", "Kaolack", "Nioro du Rip"],
  "Kédougou": ["Kédougou", "Salémata", "Saraya"],
  "Kolda": ["Kolda", "Médina Yoro Foulah", "Vélingara"],
  "Louga": ["Kébémer", "Linguère", "Louga"],
  "Matam": ["Kanel", "Matam", "Ranérou"],
  "Saint-Louis": ["Dagana", "Podor", "Saint-Louis"],
  "Sédhiou": ["Bounkiling", "Goudomp", "Sédhiou"],
  "Tambacounda": ["Bakel", "Goudiry", "Koumpentoum", "Tambacounda"],
  "Thiès": ["Mbour", "Thiès", "Tivaouane"],
  "Ziguinchor": ["Bignona", "Oussouye", "Ziguinchor"],
}

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

const errors = reactive({
  region: "",
  departement: "",
  nom: "",
  rayon: "",
  position: "",
})

const availableDepartements = computed(() => {
  if (!form.region) return []
  // Normalize match
  const key = Object.keys(departementsByRegion).find(
    (k) => k.toLowerCase() === form.region.trim().toLowerCase()
  )
  if (key && departementsByRegion[key]) {
    const list = [...departementsByRegion[key]]
    // If form.departement is currently set to a valid custom value not in list, include it
    if (form.departement && !list.includes(form.departement)) {
      list.unshift(form.departement)
    }
    return list
  }
  return form.departement ? [form.departement] : [form.region]
})

const onRegionChange = () => {
  errors.region = ""
  const depts = availableDepartements.value
  if (depts.length > 0) {
    // If current departement is not in new region's departments, switch to first one
    if (!form.departement || !depts.includes(form.departement)) {
      form.departement = depts[0]
    }
  } else {
    form.departement = form.region
  }
}

watch(
  () => props.initialData,
  (newData) => {
    if (newData && Object.keys(newData).length > 0) {
      const prevRegion = form.region
      Object.assign(form, newData)
      // If region was updated and departement not set or mismatch, ensure valid departement
      if (form.region) {
        const depts = availableDepartements.value
        if (depts.length > 0 && (!form.departement || !depts.includes(form.departement))) {
          form.departement = depts[0]
        }
      }
    }
  },
  { immediate: true, deep: true }
)

const onCancel = () => {
  router.back()
}

const submit = () => {
  if (props.saving) return
  validateRegion()
  validateDepartement()
  validateNom()
  validateRayon()

  const latitude = Number(form.latitude)
  const longitude = Number(form.longitude)
  errors.position =
    Number.isFinite(latitude) &&
    latitude >= -90 &&
    latitude <= 90 &&
    Number.isFinite(longitude) &&
    longitude >= -180 &&
    longitude <= 180
      ? ""
      : "Veuillez sélectionner un point valide sur la carte."

  if (errors.region || errors.departement || errors.nom || errors.rayon || errors.position) {
    return
  }
  emit("submit", { ...form })
}

const validateRegion = () => {
  errors.region = !String(form.region || "").trim()
    ? "Veuillez sélectionner une région."
    : ""
}

const validateDepartement = () => {
  errors.departement = !String(form.departement || "").trim()
    ? "Veuillez sélectionner un département."
    : ""
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
