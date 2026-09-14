<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-or">CrÃ©er un projet</h1>
        <p class="text-sm text-gray-500 mt-1">
          Configurez les paramÃ¨tres opÃ©rationnels, la cible de bÃ©nÃ©ficiaires et les zones de dÃ©ploiement.
        </p>
      </div>
      <BoutonSecondary to="/gerant/projets">
        <ArrowLeft :size="16" />
        Retour
      </BoutonSecondary>
    </div>

    <form @submit.prevent="submit" class="space-y-6">
      <!-- Section 1: Identification du projet -->
      <div class="bg-white rounded-xl border border-slate-200/60 overflow-hidden">
        <div class="px-6 py-4  bg-slate-50 flex items-center gap-2">
          <div class="w-2 h-5 bg-or rounded"></div>
          <h2 class="text-or text-base font-semibold uppercase tracking-wide">
            1. Identification du projet
          </h2>
        </div>

        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Nom du projet -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Nom du projet *
            </label>
            <input
              v-model="form.nom"
              type="text"
              placeholder="Ex: Distribution Alimentaire d'Urgence Hivernage 2026"
              class="w-full px-3 py-2 bg-slate-50 rounded-lg border border-gray-300 text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            />
            <p class="text-xs text-gray-500 mt-1">
              IntitulÃ© officiel utilisÃ© par les bailleurs et les partenaires.
            </p>
          </div>

          <!-- Description -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Description
            </label>
            <textarea
              v-model="form.description"
              rows="4"
              placeholder="DÃ©crivez le projet..."
              class="w-full px-3 py-2 bg-slate-50 rounded-lg border border-gray-300 text-gray-800 placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-or/30"
            ></textarea>
          </div>

          <!-- Code projet automatique -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Code projet automatique
            </label>
            <div class="px-4 py-3 bg-sky-50 rounded-lg border border-sky-200">
              <span class="text-bleu-nuit font-semibold">{{ form.code }}</span>
            </div>
            <p class="text-xs text-gray-500 mt-1">
              GÃ©nÃ©rÃ© automatiquement par BarakaGive360.
            </p>
          </div>

          <!-- Chef de projet -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Chef de projet *
            </label>
            <select
              v-model="form.chefProjet"
              class="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-800 focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            >
              <option value="">SÃ©lectionner un chef de projet</option>
              <option
                v-for="c in chefsProjet"
                :key="c"
                :value="c"
              >{{ c }}</option>
            </select>
          </div>

          <!-- Responsable Finance -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Responsable Finance *
            </label>
            <select
              v-model="form.responsableFinance"
              class="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-800 focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            >
              <option value="">SÃ©lectionner un responsable finance</option>
              <option
                v-for="r in responsablesFinance"
                :key="r"
                :value="r"
              >{{ r }}</option>
            </select>
          </div>

          <!-- RÃ©gion -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              RÃ©gion *
            </label>
            <input
              v-model="form.region"
              type="text"
              placeholder="Dakar"
              class="w-full px-3 py-2 bg-slate-50 rounded-lg border border-gray-300 text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            />
          </div>

          <!-- Budget -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Budget (FCFA) *
            </label>
            <input
              v-model.number="form.budget"
              type="number"
              placeholder="0 FCFA"
              class="w-full px-3 py-2 bg-slate-50 rounded-lg border border-gray-300 text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            />
          </div>

          <!-- CritÃ¨res projet -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              CritÃ¨res projet
            </label>
            <div class="flex gap-2">
              <select
                v-model="form.critere"
                class="flex-1 px-3 py-2 bg-slate-50 border border-gray-300 rounded-lg text-gray-800 focus:outline-none focus:ring-2 focus:ring-or/30"
              >
                <option value="">SÃ©lectionner des critÃ¨res...</option>
                <option value="urgence">Urgence</option>
                <option value="nutrition">Nutrition</option>
                <option value="education">Ã‰ducation</option>
              </select>
              <button
                type="button"
                @click="ajouterCritere"
                class="px-4 py-2 text-or font-semibold hover:bg-bleu-nuit/10 rounded-lg transition"
              >
                + Ajouter
              </button>
            </div>
          </div>

          <!-- Objectif humanitaire -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Objectif humanitaire *
            </label>
            <textarea
              v-model="form.objectif"
              rows="4"
              placeholder="DÃ©crivez les bÃ©nÃ©ficiaires ciblÃ©s, les livrables et l'impact attendu..."
              class="w-full px-3 py-2 bg-slate-50 rounded-lg border border-gray-300 text-gray-800 placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Section 2: Calendrier -->
      <div class="bg-white rounded-xl border border-slate-200/60 overflow-hidden">
        <div class="px-6 py-4  bg-slate-50 flex items-center gap-2">
          <div class="w-2 h-5 bg-or rounded"></div>
          <h2 class="text-or text-base font-semibold uppercase tracking-wide">
            2. Calendrier
          </h2>
        </div>

        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Date de dÃ©but -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Date de dÃ©but *
            </label>
            <input
              v-model="form.dateDebut"
              type="date"
              class="w-full px-3 py-2 bg-slate-50 rounded-lg border border-gray-300 text-gray-800 focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            />
          </div>

          <!-- Date de fin -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">
              Date de fin *
            </label>
            <input
              v-model="form.dateFin"
              type="date"
              class="w-full px-3 py-2 bg-slate-50 rounded-lg border border-gray-300 text-gray-800 focus:outline-none focus:ring-2 focus:ring-or/30"
              required
            />
          </div>
        </div>
      </div>

      <!-- CHS Notice -->
      <div class="bg-white rounded-xl border border-slate-200/60 p-6 flex items-start gap-4">
        <div class="w-12 h-12 bg-or rounded-full flex items-center justify-center flex-shrink-0">
          <Check :size="24" class="text-white" />
        </div>
        <div>
          <p class="text-or text-sm font-bold uppercase tracking-wide mb-1">
            STANDARD DE RESPONSABILITÃ‰ HUMANITAIRE (CHS)
          </p>
          <p class="text-gray-600 text-xs">
            Toutes les campagnes crÃ©Ã©es sont soumises Ã  l'audit de transparence
            des bÃ©nÃ©ficiaires et aux protocoles de sÃ©curitÃ© des donnÃ©es
            sensibles de BarakaGive360.
          </p>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="flex justify-end gap-3 pt-4">
        <BoutonSecondary @click="annuler">
          Annuler
        </BoutonSecondary>
        <button
          type="submit"
          class="h-10 px-5 bg-bleu-nuit rounded-lg flex items-center justify-center gap-2 text-white text-sm font-semibold"
        >
          <Plus :size="16" />
          CrÃ©er et activer le projet
        </button>
      </div>

      <!-- OCHA Note -->
      <div class="flex items-center gap-2 text-xs text-gray-500">
        <div class="w-4 h-4 border-2 border-gray-500 rounded-sm flex items-center justify-center">
          <Check :size="10" class="text-gray-700" />
        </div>
        <span>VÃ©rification automatique des donnÃ©es conforme OCHA.</span>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useRouter } from "vue-router"
import { ArrowLeft, Plus, Check } from "lucide-vue-next"
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"

const router = useRouter()
const store = useGerantStore()

const chefsProjet = store.chefsProjet
const responsablesFinance = store.responsablesFinance

const form = ref({
  nom: "",
  description: "",
  code: "PRJ-2026-DKR-" + String(Math.floor(Math.random() * 999) + 1).padStart(3, "0"),
  chefProjet: "",
  responsableFinance: "",
  region: "",
  budget: 0,
  critere: "",
  criteres: [],
  objectif: "",
  dateDebut: "",
  dateFin: "",
})

const ajouterCritere = () => {
  if (form.value.critere && !form.value.criteres.includes(form.value.critere)) {
    form.value.criteres.push(form.value.critere)
  }
}

const annuler = () => {
  router.push("/gerant/projets")
}

const submit = () => {
  console.log("Nouveau projet:", form.value)
  router.push("/gerant/projets")
}
</script>





