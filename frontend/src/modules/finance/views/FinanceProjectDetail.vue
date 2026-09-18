<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-or">Détail du projet assigné</h1>
        <p class="text-sm text-gray-500 mt-1">Consultation en lecture seule.</p>
      </div>
      <BoutonSecondary to="/finance/projets">
        <List :size="18" />
        Retour aux projets
      </BoutonSecondary>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement du projet..." />
    <AlertMessage v-if="error" type="error" :message="error" />

    <div v-if="project && !loading" class="bg-white border border-slate-200 rounded-xl p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
      <div><p class="label">Nom</p><p>{{ project.name }}</p></div>
      <div><p class="label">Code</p><p>{{ project.code }}</p></div>
      <div><p class="label">Région</p><p>{{ project.region }}</p></div>
      <div><p class="label">Budget</p><p>{{ formatMontant(project.budget) }} FCFA</p></div>
      <div><p class="label">Chef de projet</p><p>{{ project.chef_projet || "-" }}</p></div>
      <div><p class="label">Responsable finance</p><p>{{ project.responsable_finance || "-" }}</p></div>
      <div><p class="label">Début</p><p>{{ project.start_date }}</p></div>
      <div><p class="label">Fin</p><p>{{ project.end_date }}</p></div>
      <div class="md:col-span-2"><p class="label">Objectif</p><p>{{ project.objectif }}</p></div>
      <div class="md:col-span-2"><p class="label">Description</p><p class="whitespace-pre-line">{{ project.description }}</p></div>
    </div>
  </div>

  <FinancialOrbital />
</template>

<script setup>
import { onMounted, ref } from "vue"
import { useRoute } from "vue-router"
import { List } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { financeService } from "@/modules/finance/services/financeService.js"
import FinancialOrbital from "@/components/ia/FinancialOrbital.vue"

const route = useRoute()
const project = ref(null)
const loading = ref(true)
const error = ref(null)
const formatMontant = (value) => Number(value || 0).toLocaleString("fr-FR")

onMounted(async () => {
  try {
    project.value = await financeService.fetchProject(route.params.id)
  } catch (err) {
    error.value = err.response?.data?.detail || "Impossible de charger les détails du projet."
  } finally {
    loading.value = false
  }
})
</script>

<FinancialOrbital />

<style scoped>
.label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #0f172a; margin-bottom: 0.25rem; }
</style>
