<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">Détail de la campagne</h1>
        <p class="text-sm text-gray-600 mt-1">
          Informations complètes de la campagne et gestion du formulaire de collecte.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonPrimary :to="`/chef-projet/campagnes/${route.params.id}/formulaire`">
          <FileText :size="18" />
          Formulaire dynamique
        </BoutonPrimary>

        <BoutonSecondary to="/chef-projet/campagnes">
          <List :size="18" />
          Liste des campagnes
        </BoutonSecondary>
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement de la campagne..." />
    <AlertMessage v-if="error" type="error" :message="error" class="mb-4" />

    <!-- Détails -->
    <div class="max-w-3xl bg-white border border-slate-200/60 rounded-xl p-6 shadow-xs-sm" v-if="campagne">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Nom de la campagne</p>
          <p class="text-gray-800 font-semibold text-lg">{{ campagne.nom }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Code Campagne</p>
          <p class="text-gray-700 font-mono">{{ campagne.code_campagne }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Projet rattaché</p>
          <p class="text-gray-700 font-medium">{{ campagne.projet?.name || "-" }}</p>
          <p class="text-xs text-gray-500">{{ campagne.projet?.code }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Statut</p>
          <span
            class="px-2.5 py-1 text-xs font-semibold rounded-full inline-block"
            :class="badgeStatut(campagne.statut)"
          >
            {{ labelStatut(campagne.statut) }}
          </span>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de début</p>
          <p class="text-gray-700">{{ campagne.date_debut || "Non définie" }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de fin</p>
          <p class="text-gray-700">{{ campagne.date_fin || "Non définie" }}</p>
        </div>

        <div class="col-span-1 md:col-span-2">
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Zones d'intervention</p>
          <div v-if="campagne.zones?.length" class="flex flex-wrap gap-2 mt-1">
            <span
              v-for="z in campagne.zones"
              :key="z.id"
              class="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs rounded-md border"
            >
              {{ z.nom }} ({{ z.region }})
            </span>
          </div>
          <p v-else class="text-gray-500 text-sm">Aucune zone assignée.</p>
        </div>

        <div class="col-span-1 md:col-span-2">
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Description</p>
          <p class="text-gray-700 whitespace-pre-line">{{ campagne.description || "Aucune description fournie." }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import { List, FileText } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useCampaignStore } from "@/stores/campaign.js"

const route = useRoute()
const campaignStore = useCampaignStore()

const campagne = ref(null)
const loading = ref(false)
const error = ref(null)

const statutCampagne = computed(() => labelStatut(campagne.value?.statut))

const labelStatut = (statut) => {
  switch (statut) {
    case "BROUILLON":
      return "Brouillon"
    case "PLANIFIER":
      return "Planifiée"
    case "EN_COURS":
      return "En cours"
    case "TERMINE":
      return "Terminée"
    case "ANNULEE":
      return "Annulée"
    default:
      return statut || "-"
  }
}

const badgeStatut = (statut) => {
  switch (statut) {
    case "EN_COURS":
      return "bg-emerald-50 text-emerald-700"
    case "PLANIFIER":
      return "bg-bleu-nuit text-white"
    case "TERMINE":
      return "bg-gray-500 text-white"
    case "ANNULEE":
      return "bg-red-100 text-red-800"
    case "BROUILLON":
      return "bg-amber-100 text-amber-800"
    default:
      return "bg-slate-100 text-slate-600"
  }
}

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    campagne.value = await campaignStore.fetchCampaign(route.params.id)
  } catch (err) {
    error.value = "Impossible de charger les détails de cette campagne."
  } finally {
    loading.value = false
  }
})
</script>

