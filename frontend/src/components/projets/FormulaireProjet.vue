<template>
  <div class="bg-white rounded-2xl border border-slate-200/60 overflow-hidden">
    <div class="p-8 border-b border-gray-100">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-amber-800">
          1. Identification du projet
        </h2>

        <span class="bg-gray-100 text-xs font-bold px-3 py-1 rounded uppercase">
          Section obligatoire
        </span>
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

        <!-- Urgence -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-3">
            Niveau d'urgence
          </label>

          <div class="grid grid-cols-3 gap-3">
            <button
              v-for="niveau in urgences"
              :key="niveau"
              type="button"
              @click="form.urgence = niveau"
              :class="
                form.urgence === niveau
                  ? 'bg-amber-800 text-white'
                  : 'bg-slate-100 text-gray-700'
              "
              class="rounded-lg py-3 font-medium transition"
            >
              {{ niveau }}
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
        <div class="w-1.5 h-6 bg-sky-900 rounded-full"></div>

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
        <button
          type="button"
          class="border border-sky-900 text-sky-900 px-6 py-2.5 rounded-lg font-semibold"
        >
          Annuler
        </button>

        <button
          @click="submit"
          class="bg-slate-900 hover:bg-slate-800 text-white px-6 py-2.5 rounded-lg font-semibold flex items-center gap-2"
        >
          <Plus :size="18" v-if="mode === 'creation'" />
          <Save :size="18" v-else />
          {{ buttonLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from "vue"
import { ShieldCheck, Plus, Save } from "lucide-vue-next"

const props = defineProps({
  mode: {
    type: String,
    default: "creation",
    validator: (value) => ["creation", "modification"].includes(value),
  },
})

const emit = defineEmits(["submit"])

const urgences = ["Faible", "Moyenne", "Élevée"]

const form = reactive({
  nom: "",
  description: "",
  urgence: "Moyenne",
  objectif: "",
  dateDebut: "",
  dateFin: "",
})

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
