<template>
  <div class="min-h-screen space-y-6 bg-white p-6">
    <header class="flex items-center justify-between pb-4">
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Détail du projet</h1>
        <p class="mt-1 text-sm text-gray-600">Informations du projet et export du rapport.</p>
      </div>
      <div class="flex gap-3">
        <BoutonPrimary :disabled="!projet || exportLoading" @click="exporterPdf">
          <FileDown :size="18" />
          {{ exportLoading ? "Préparation…" : "Exporter PDF" }}
        </BoutonPrimary>
        <BoutonSecondary to="/chef-projet/finances">
          <List :size="18" />
          Retour aux finances
        </BoutonSecondary>
      </div>
    </header>

    <p v-if="loading" class="text-sm text-slate-600">Chargement du projet…</p>
    <p v-else-if="error" role="alert" class="rounded-lg bg-red-50 p-4 text-sm text-red-700">
      {{ error }}
    </p>

    <section v-else-if="projet" class="rounded-xl border border-slate-200 p-6">
      <dl class="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <dt class="mb-1 text-xs font-bold uppercase text-slate-900">Nom</dt>
          <dd class="text-gray-700">{{ projet.name }}</dd>
        </div>
        <div>
          <dt class="mb-1 text-xs font-bold uppercase text-slate-900">Code</dt>
          <dd class="text-gray-700">{{ projet.code || "—" }}</dd>
        </div>
        <div>
          <dt class="mb-1 text-xs font-bold uppercase text-slate-900">Région</dt>
          <dd class="text-gray-700">{{ projet.region || "—" }}</dd>
        </div>
        <div>
          <dt class="mb-1 text-xs font-bold uppercase text-slate-900">Budget</dt>
          <dd class="text-gray-700">{{ formatMontant(projet.budget) }} FCFA</dd>
        </div>
        <div>
          <dt class="mb-1 text-xs font-bold uppercase text-slate-900">Date de début</dt>
          <dd class="text-gray-700">{{ projet.start_date || "—" }}</dd>
        </div>
        <div>
          <dt class="mb-1 text-xs font-bold uppercase text-slate-900">Date de fin</dt>
          <dd class="text-gray-700">{{ projet.end_date || "—" }}</dd>
        </div>
        <div class="sm:col-span-2">
          <dt class="mb-1 text-xs font-bold uppercase text-slate-900">Description</dt>
          <dd class="whitespace-pre-wrap text-gray-700">{{ projet.description || "—" }}</dd>
        </div>
      </dl>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { useRoute } from "vue-router"
import { FileDown, List } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import api from "@/services/api.js"

const route = useRoute()
const projet = ref(null)
const loading = ref(true)
const exportLoading = ref(false)
const error = ref("")

onMounted(chargerProjet)

async function chargerProjet() {
  try {
    const response = await api.get(`/api/projects/${route.params.id}/`)
    projet.value = response.data
  } catch {
    error.value = "Impossible de charger ce projet."
  } finally {
    loading.value = false
  }
}

function formatMontant(montant) {
  const value = Number(montant)
  return Number.isFinite(value) ? value.toLocaleString("fr-FR") : "0"
}

async function exporterPdf() {
  if (!projet.value || exportLoading.value) return
  exportLoading.value = true
  try {
    const response = await api.get("/api/reports/export/pdf/", {
      params: { project_id: projet.value.id },
      responseType: "blob",
    })
    const url = URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }))
    const link = document.createElement("a")
    link.href = url
    link.download = `rapport_${projet.value.code || projet.value.id}.pdf`
    link.click()
    window.setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch {
    error.value = "L'export PDF du projet est indisponible pour le moment."
  } finally {
    exportLoading.value = false
  }
}
</script>
