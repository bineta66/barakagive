<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="fermer"
  >
    <div class="bg-white border border-slate-200 rounded-2xl shadow-xs-sm max-w-lg w-full">
      <div class="p-6">
        <div class="flex justify-between items-center">
          <h2 class="text-2xl font-bold text-or">Ajouter un critère</h2>
          <button
            @click="fermer"
            class="text-gray-400 hover:text-gray-600 transition"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        <p class="text-sm text-gray-500 mt-1">
          Créez un nouveau critère de vulnérabilité pour ce projet.
        </p>
      </div>

      <div class="px-6 py-4 space-y-4">
        <AlertMessage
          v-if="submitError"
          type="error"
          :message="submitError"
          :dismissible="true"
          @dismiss="submitError = null"
          class="mb-4"
        />

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">
            Nom du critère *
          </label>
          <input
            v-model="nom"
            type="text"
            placeholder="Ex: Femme enceinte"
            class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
            :disabled="submitting"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">
            Poids (%) *
          </label>
          <input
            v-model="poids"
            type="number"
            min="1"
            max="100"
            placeholder="Ex: 25"
            class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
            :disabled="submitting"
            required
          />
          <p class="text-xs text-gray-500 mt-1">
            Valeur comprise entre 1 et 100.
          </p>
        </div>
      </div>

      <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
        <BoutonTertiary :disabled="submitting" @click="fermer" class="disabled:opacity-50 disabled:cursor-not-allowed">
          Annuler
        </BoutonTertiary>
        <BoutonPrimary
          :disabled="submitting"
          @click="creer"
          class="disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus v-if="!submitting" :size="16" />
          <span v-if="submitting">Création...</span>
          <span v-else>Créer le critère</span>
        </BoutonPrimary>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { X, Plus } from "lucide-vue-next"
import { useProjectStore } from "@/stores/project.js"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonTertiary from "@/components/ui/BoutonTertiary.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"

const props = defineProps({
  ouvert: { type: Boolean, default: false },
})

const emit = defineEmits(["fermer", "cree"])

const store = useProjectStore()
const nom = ref("")
const poids = ref("")
const submitting = ref(false)
const submitError = ref(null)

const fermer = () => {
  nom.value = ""
  poids.value = ""
  submitError.value = null
  emit("fermer")
}

const creer = async () => {
  if (submitting.value) return
  const nomValue = nom.value.trim()
  const poidsValue = parseInt(poids.value, 10)
  if (!nomValue || !poidsValue) return
  if (poidsValue < 1 || poidsValue > 100) {
    submitError.value = "Le poids doit être compris entre 1 et 100."
    return
  }
  submitting.value = true
  submitError.value = null
  try {
    emit("cree", { nom: nomValue, poids: poidsValue })
    fermer()
  } catch (err) {
    submitError.value = "Erreur lors de la création du critère."
  } finally {
    submitting.value = false
  }
}
</script>

