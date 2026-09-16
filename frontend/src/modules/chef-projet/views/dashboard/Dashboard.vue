<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Titre -->
    <div class="pb-4">
      <h1 class="text-4xl font-bold text-or">Tableau de bord</h1>
      <p class="text-xs text-gray-500 mt-1">
        Vue d'ensemble de l'activité humanitaire de l'organisation.
      </p>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement des indicateurs..." />
    <AlertMessage v-if="error" type="error" :message="error" class="mb-4" />

    <!-- Cartes statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Projets actifs</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ activeProjectsCount }}</h3>
        </div>
        <FolderKanban class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Campagnes en cours</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ activeCampaignsCount }}</h3>
        </div>
        <ClipboardList class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Bénéficiaires</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ totalBeneficiariesCount }}</h3>
        </div>
        <Users class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Budget alloué</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatBudget(totalBudget) }}</h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Graphique + Activité récente -->
    <div class="flex flex-col lg:flex-row gap-6">
      <div class="flex-[2] min-w-0">
        <div class="bg-white border border-slate-200/60 rounded-xl p-6 h-full">
          <EvolutionChart
            :projects="projectStore.projects"
            :beneficiaries="beneficiaryStore.beneficiaries"
          />
        </div>
      </div>

      <div class="flex-[1] min-w-0">
        <div class="bg-white border border-slate-200/60 rounded-xl h-full">
          <ActiviteRecent />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { FolderKanban, ClipboardList, Users, Wallet } from "lucide-vue-next"
import EvolutionChart from "@/components/ui/EvolutionChart.vue"
import ActiviteRecent from "@/components/ui/ActiviteRecent.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useProjectStore } from "@/stores/project.js"
import { useCampaignStore } from "@/stores/campaign.js"
import { useBeneficiaryStore } from "@/stores/beneficiary.js"

const projectStore = useProjectStore()
const campaignStore = useCampaignStore()
const beneficiaryStore = useBeneficiaryStore()

const loading = ref(false)
const error = ref(null)

const activeProjectsCount = computed(() => {
  return projectStore.projects.filter((p) => !p.archived).length
})

const activeCampaignsCount = computed(() => {
  return campaignStore.activeCampaigns.length || campaignStore.campaigns.length
})

const totalBeneficiariesCount = computed(() => {
  return beneficiaryStore.beneficiaries.length
})

const totalBudget = computed(() => {
  return projectStore.projects.reduce((acc, p) => acc + (parseFloat(p.budget) || 0), 0)
})

const formatBudget = (val) => {
  return new Intl.NumberFormat("fr-FR").format(val) + " FCFA"
}

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    await Promise.allSettled([
      projectStore.fetchProjects(),
      campaignStore.fetchCampaigns(),
      beneficiaryStore.fetchBeneficiaries(),
    ])
  } catch (err) {
    error.value = "Erreur lors de la récupération des données du tableau de bord."
  } finally {
    loading.value = false
  }
})
</script>


