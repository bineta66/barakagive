<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Finances</h1>
        <p class="text-xs text-gray-500 mt-1">
          Consultation en lecture seule des indicateurs financiers.
        </p>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Budget total alloué</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(statistiques.budgetTotal) }} FCFA</h3>
        </div>
        <PiggyBank class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Dépenses réalisées</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(statistiques.budgetEngage) }} FCFA</h3>
        </div>
        <Receipt class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Solde disponible</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(statistiques.soldeDisponible) }} FCFA</h3>
        </div>
        <Banknote class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Taux d'exécution</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.tauxExecution }}%</h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Trajectoire budgétaire - read-only chart -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-6">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h3 class="text-sm font-bold uppercase text-slate-900">Trajectoire budgétaire et dépenses (2025)</h3>
          <p class="text-xs text-gray-500 mt-1">Progression mensuelle cumulée (en FCFA)</p>
        </div>
      </div>

      <div class="h-80">
        <svg :width="chartWidth" :height="chartHeight" class="w-full h-full" viewBox="0 0 800 320" preserveAspectRatio="xMidYMid meet">
          <!-- Grid lines -->
          <g v-for="i in 6" :key="`grid-${i}`" stroke="#e2e8f0" stroke-width="1">
            <line
              :x1="marginLeft"
              :y1="marginTop + (i - 1) * yAxisStep"
              :x2="chartWidth - marginRight"
              :y2="marginTop + (i - 1) * yAxisStep"
            />
          </g>

          <!-- Budget curve -->
          <polyline
            :points="budgetPoints"
            fill="none"
            stroke="#0369A8"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
          />

          <!-- Dépenses curve -->
          <polyline
            :points="depensesPoints"
            fill="none"
            stroke="#744D03"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
          />

          <!-- Budget data points -->
          <g v-for="(item, i) in dataMensuelle" :key="`budget-${i}`">
            <circle
              :cx="pointX(i)"
              :cy="pointY(item.budget)"
              r="5"
              fill="#0369A8"
              stroke="white"
              stroke-width="2"
            />
          </g>

          <!-- Dépenses data points -->
          <g v-for="(item, i) in dataMensuelle" :key="`depenses-${i}`">
            <circle
              :cx="pointX(i)"
              :cy="pointY(item.depenses)"
              r="5"
              fill="#744D03"
              stroke="white"
              stroke-width="2"
            />
          </g>

          <!-- Month labels -->
          <g v-for="(item, i) in dataMensuelle" :key="`label-${i}`">
            <text
              :x="pointX(i)"
              :y="chartHeight - 8"
              class="text-xs font-semibold"
              :class="i === dataMensuelle.length - 1 ? 'text-sky-700' : 'text-gray-500'"
              text-anchor="middle"
            >
              {{ item.mois }}
            </text>
          </g>
        </svg>
      </div>

      <div class="flex justify-start items-center gap-4 mt-4">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-bleu-nuit rounded-full"></div>
          <span class="text-slate-600 text-xs">Budget</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-or rounded-full"></div>
          <span class="text-slate-600 text-xs">Dépenses</span>
        </div>
      </div>
    </div>

    <!-- Répartition des projets par région -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
      <div class="px-6 py-4 ">
        <h3 class="text-sm font-bold uppercase text-slate-900">Répartition des projets par région</h3>
        <p class="text-xs text-gray-500 mt-1">{{ store.projets.length }} projet(s) géré(s)</p>
      </div>

      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
          <tr>
            <th class="text-left px-4 py-3">Projet</th>
            <th class="text-left px-4 py-3">Région</th>
            <th class="text-right px-4 py-3">Budget</th>
            <th class="text-left px-4 py-3">Chef de projet</th>
            <th class="text-left px-4 py-3">Statut</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="projet in store.projets"
            :key="projet.id"
            class="border-t hover:bg-slate-50"
          >
            <td class="px-4 py-3">
              <h3 class="font-semibold text-sm text-slate-800">{{ projet.nom }}</h3>
              <p class="text-xs text-gray-500">{{ projet.code }}</p>
            </td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ projet.region }}</td>
            <td class="px-4 text-right text-sm font-semibold text-slate-900">{{ formatMontant(projet.budget) }} FCFA</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ projet.chefProjet }}</td>
            <td class="px-4 py-3">
              <StatusBadge :statut="projet.statut">{{ projet.statut }}</StatusBadge>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { PiggyBank, Receipt, Banknote, Activity } from "lucide-vue-next"
import { useGerantStore } from '@/modules/gerant/stores/gerantStore.js'
import { useZoneStore } from "@/stores/zone.js"

const store = useGerantStore()
const zoneStore = useZoneStore()
const { formatMontant } = store

const statistiques = computed(() => store.statistiques)

const firstGerantCampaignId = computed(() => store.campaigns?.[0]?.id || null)
const firstGerantProjetId = computed(() => {
  const first = store.campaigns?.[0]
  return first?.projet?.id || first?.projet_id || store.projets?.[0]?.id || null
})
const zonesForGerantIA = computed(() =>
  zoneStore.zones.map((z) => ({
    nom: z.nom,
    urgence: "Moyenne",
    score_total: z.score_total || 0,
    beneficiaires_prioritaires: z.nombre_beneficiaires || 0,
    top5: z.top5 || [],
  }))
)

const chartWidth = 800
const chartHeight = 320
const marginLeft = 60
const marginRight = 24
const marginTop = 24
const marginBottom = 32
const yAxisStep = (chartHeight - marginTop - marginBottom) / 5
const dataMensuelle = ref([
  { mois: "Janv", budget: 20, depenses: 15 },
  { mois: "Févr", budget: 40, depenses: 33 },
  { mois: "Mars", budget: 60, depenses: 45 },
  { mois: "Avril", budget: 75, depenses: 55 },
  { mois: "Mai", budget: 90, depenses: 70 },
  { mois: "Juin", budget: 100, depenses: 77 },
])

const chartAreaWidth = chartWidth - marginLeft - marginRight
const chartAreaHeight = chartHeight - marginTop - marginBottom

const pointX = (i) => {
  return marginLeft + (i / (dataMensuelle.value.length - 1)) * chartAreaWidth
}

const pointY = (value) => {
  return marginTop + chartAreaHeight - (value / 100) * chartAreaHeight
}

const budgetPoints = computed(() => {
  return dataMensuelle.value
    .map((item, i) => `${pointX(i)},${pointY(item.budget)}`)
    .join(" ")
})

const depensesPoints = computed(() => {
  return dataMensuelle.value
    .map((item, i) => `${pointX(i)},${pointY(item.depenses)}`)
    .join(" ")
})

const badgeClass = (statut) => {
  switch (statut) {
    case "En cours":
      return "bg-or/10 text-or"
    case "Planifié":
      return "bg-or/10 text-bleu-nuit"
    case "Terminé":
      return "bg-bleu-nuit/10 text-bleu-nuit"
    default:
      return "bg-gray-100 text-gray-600"
  }
}
</script>
