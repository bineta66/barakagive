<template>
  <div class="bg-white rounded-2xl border border-slate-200/60 overflow-hidden">
    <div class="p-8 border-b border-gray-100">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-amber-800">
          1. Identification du projet
        </h2>

       
      </div>

      <div class="space-y-6">
        <!-- Nom -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Nom du projet *
          </label>

          <input
            v-model="form.nom"
            type="text"
            placeholder="Ex : Distribution Alimentaire d'Urgence Hivernage 2026"
            class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3 focus:ring-2 focus:ring-amber-700 outline-none"
          />

          <p class="text-xs text-gray-500 mt-2">
            Intitulé officiel utilisé par les bailleurs et les partenaires.
          </p>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Description
          </label>

          <textarea
            v-model="form.description"
            rows="4"
            placeholder="Décrivez le projet..."
            class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3 focus:ring-2 focus:ring-amber-700 outline-none"
          />
        </div>

        <!-- Code -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Code projet automatique
          </label>

          <div class="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 font-semibold text-blue-900">
            {{ codeProjet }}
          </div>

          <p class="text-xs text-gray-500 mt-2">
            Généré automatiquement par BarakaGive360.
          </p>
        </div>

        <!-- Critères projet -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-3">
            Critères projet
          </label>

          <div class="relative">
            <button
              type="button"
              @click="showCriteresDropdown = !showCriteresDropdown"
              class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3 text-left flex justify-between items-center focus:ring-2 focus:ring-amber-700 outline-none"
            >
              <span :class="form.criteres.length ? 'text-gray-800' : 'text-gray-400'">
                {{ form.criteres.length ? `${form.criteres.length} critère(s) sélectionné(s)` : 'Sélectionner des critères...' }}
              </span>
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </button>
            <div v-if="showCriteresDropdown" class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg">
              <div class="p-2 border-b border-gray-200">
                <input
                  v-model="critereSearch"
                  type="text"
                  placeholder="Rechercher..."
                  class="w-full rounded-lg border border-gray-300 bg-slate-50 px-3 py-2 text-sm focus:ring-2 focus:ring-amber-700 outline-none"
                  @click.stop
                />
              </div>
              <div class="max-h-48 overflow-y-auto">
                <div v-for="critere in filteredCriteres" :key="critere" class="px-4 py-2 hover:bg-gray-50 cursor-pointer flex items-center gap-2" @click="toggleCritere(critere)">
                  <div class="w-4 h-4 border rounded flex items-center justify-center" :class="form.criteres.includes(critere) ? 'bg-amber-800 border-amber-800' : 'border-gray-300'">
                    <svg v-if="form.criteres.includes(critere)" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                  <span class="text-sm text-gray-700">{{ critere }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2 mt-3">
            <input
              v-model="nouveauCritere"
              @keyup.enter="ajouterCritere"
              type="text"
              placeholder="Ajouter un critère..."
              class="flex-1 rounded-lg border border-gray-300 bg-slate-50 px-4 py-2 text-sm focus:ring-2 focus:ring-amber-700 outline-none"
            />
            <button
              @click="ajouterCritere"
              class="text-sm font-semibold text-sky-900 hover:underline"
            >
              + Ajouter
            </button>
          </div>
        </div>

        <!-- Objectif -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Objectif humanitaire *
          </label>

          <textarea
            v-model="form.objectif"
            rows="5"
            placeholder="Décrivez les bénéficiaires ciblés, les livrables et l'impact attendu..."
            class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3 focus:ring-2 focus:ring-amber-700 outline-none"
          />
        </div>
      </div>
    </div>

    <!-- Calendrier -->
    <div class="p-8 border-b border-gray-100">
      <div class="flex items-center gap-3 mb-6">
       

        <h2 class="text-2xl font-bold text-amber-800">
          2. Calendrier
        </h2>
      </div>

      <div class="grid md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Date de début *
          </label>

          <input
            v-model="form.dateDebut"
            type="date"
            class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Date de fin *
          </label>

          <input
            v-model="form.dateFin"
            type="date"
            class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-3"
          />
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="bg-gray-50 px-8 py-6 flex justify-between items-center">
      <div class="flex items-center gap-2 text-xs text-gray-600">
        <ShieldCheck class="text-slate-700" :size="18" />
        Vérification automatique des données conforme OCHA.
      </div>

      <div class="flex gap-4">
        <BoutonSecondary type="button">
          Annuler
        </BoutonSecondary>

        <BoutonPrimary @click="submit">
          <Plus :size="18" v-if="mode === 'creation'" />
          <Save :size="18" v-else />
          {{ buttonLabel }}
        </BoutonPrimary>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, ref, defineProps, defineEmits } from "vue"
import { ShieldCheck, Plus, Save } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"

const props = defineProps({
  mode: {
    type: String,
    default: "creation",
    validator: (value) => ["creation", "modification"].includes(value),
  },
})

const emit = defineEmits(["submit"])

const criteres = ["Urgence", "Vulnérabilité", "Saison agricole", "Population cible", "Zone rurale", "Urgence humanitaire"]

const showCriteresDropdown = ref(false)
const critereSearch = ref("")
const nouveauCritere = ref("")

const filteredCriteres = computed(() => {
  if (!critereSearch.value) return criteres
  const search = critereSearch.value.toLowerCase()
  return criteres.filter(critere => critere.toLowerCase().includes(search))
})

const form = reactive({
  nom: "",
  description: "",
  objectif: "",
  criteres: [],
  dateDebut: "",
  dateFin: "",
})

const toggleCritere = (critere) => {
  const index = form.criteres.indexOf(critere)
  if (index > -1) {
    form.criteres.splice(index, 1)
  } else {
    form.criteres.push(critere)
  }
}

const ajouterCritere = () => {
  const value = nouveauCritere.value.trim()
  if (value && !form.criteres.includes(value)) {
    form.criteres.push(value)
    criteres.push(value)
    nouveauCritere.value = ""
  }
}

const codeProjet = computed(() => {
  return "PRJ-2026-DKR-001"
})

const buttonLabel = computed(() => {
  return props.mode === "creation"
    ? "Créer et activer le projet"
    : "Enregistrer les modifications"
})

const submit = () => {
  emit("submit", { ...form })
}
</script>
