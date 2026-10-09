<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-4xl font-bold text-bleu-nuit">Finances</h1>
        <p class="text-xs text-gray-500 mt-1">
          Consultation en lecture seule des indicateurs financiers.
        </p>
      </div>
    </div>

    <!-- Budgets en attente d'approbation -->
    <div
      v-if="budgetsEnAttente.length > 0"
      class="bg-orange-50 border border-orange-200 rounded-xl p-6"
    >
      <div class="flex justify-between items-center mb-4">
        <div>
          <h3 class="text-sm font-bold uppercase text-orange-800">
            Budgets en attente d'approbation
          </h3>
          <p class="text-xs text-orange-600 mt-1">
            {{ budgetsEnAttente.length }} budget(s) à valider
          </p>
        </div>
        <button
          @click="refreshBudgets"
          class="px-3 py-1.5 text-xs bg-orange-100 hover:bg-orange-200 text-orange-800 rounded-lg flex items-center gap-1"
        >
          <RefreshCw :size="14" /> Actualiser
        </button>
      </div>

      <div class="space-y-3">
        <div
          v-for="budget in budgetsEnAttente"
          :key="budget.id"
          class="bg-white border border-orange-200 rounded-lg p-4 flex justify-between items-center"
        >
          <div>
            <h4 class="font-semibold text-slate-800">
              {{ budget.projet_nom || "Projet #" + budget.projet }}
            </h4>
            <p class="text-sm text-slate-600">
              Montant:
              <span class="font-bold text-orange-600"
                >{{ formatMontant(budget.montant) }} FCFA</span
              >
            </p>
            <p class="text-xs text-slate-500">
              Ajouté par: {{ budget.responsable_nom || "Responsable Finance" }}
            </p>
            <p class="text-xs text-slate-500">
              Date: {{ formatDate(budget.date_creation) }}
            </p>
          </div>
          <div class="flex gap-2">
            <button
              @click="handleApprove(budget.id)"
              :disabled="approving === budget.id"
              class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg flex items-center gap-2 disabled:opacity-50"
            >
              <Check :size="16" />
              {{ approving === budget.id ? "..." : "Approuver" }}
            </button>
            <button
              @click="handleReject(budget.id)"
              :disabled="approving === budget.id"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg flex items-center gap-2 disabled:opacity-50"
            >
              <X :size="16" /> {{ approving === budget.id ? "..." : "Rejeter" }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">
            Budget total alloué
          </p>
          <h3 class="text-xl font-bold text-bleu-nuit mt-2">
            {{ formatMontant(statistiques.budgetTotal) }} FCFA
          </h3>
        </div>
        <PiggyBank class="text-bleu-nuit" :size="28" />
      </div>

      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">
            Dépenses réalisées
          </p>
          <h3 class="text-xl font-bold text-bleu-nuit mt-2">
            {{ formatMontant(statistiques.budgetEngage) }} FCFA
          </h3>
        </div>
        <Receipt class="text-bleu-nuit" :size="28" />
      </div>

      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">
            Solde disponible
          </p>
          <h3 class="text-xl font-bold text-bleu-nuit mt-2">
            {{ formatMontant(statistiques.soldeDisponible) }} FCFA
          </h3>
        </div>
        <Banknote class="text-bleu-nuit" :size="28" />
      </div>

      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">
            Taux d'exécution
          </p>
          <h3 class="text-xl font-bold text-bleu-nuit mt-2">
            {{ statistiques.tauxExecution }}%
          </h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Trajectoire budgétaire - read-only chart -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-6">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h3 class="text-sm font-bold uppercase text-slate-900">
            Trajectoire budgétaire et dépenses (2025)
          </h3>
          <p class="text-xs text-gray-500 mt-1">
            Progression mensuelle cumulée (en FCFA)
          </p>
        </div>
      </div>

      <div class="h-80">
        <svg
          :width="chartWidth"
          :height="chartHeight"
          class="w-full h-full"
          viewBox="0 0 800 320"
          preserveAspectRatio="xMidYMid meet"
        >
          <!-- Grid lines -->
          <g
            v-for="i in 6"
            :key="`grid-${i}`"
            stroke="#e2e8f0"
            stroke-width="1"
          >
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
              :class="
                i === dataMensuelle.length - 1
                  ? 'text-or'
                  : 'text-gray-500'
              "
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
          <div class="w-3 h-3 bg-bleu-nuit rounded-full"></div>
          <span class="text-slate-600 text-xs">Dépenses</span>
        </div>
      </div>
    </div>

    <!-- Répartition des projets par région -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
      <div class="px-6 py-4">
        <h3 class="text-sm font-bold uppercase text-slate-900">
          Répartition des projets par région
        </h3>
        <p class="text-xs text-gray-500 mt-1">
          {{ store.projets.length }} projet(s) géré(s)
        </p>
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
              <h3 class="font-semibold text-sm text-slate-800">
                {{ projet.nom }}
              </h3>
              <p class="text-xs text-gray-500">{{ projet.code }}</p>
            </td>
            <td class="px-4 py-3 text-sm text-slate-700">
              {{ projet.region }}
            </td>
            <td class="px-4 text-right text-sm font-semibold text-slate-900">
              {{ formatMontant(projet.budget) }} FCFA
            </td>
            <td class="px-4 py-3 text-sm text-slate-700">
              {{ projet.chefProjet }}
            </td>
            <td class="px-4 py-3">
              <StatusBadge :statut="projet.statut">{{
                projet.statut
              }}</StatusBadge>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  PiggyBank,
  Receipt,
  Banknote,
  Activity,
  RefreshCw,
  Check,
  X,
} from "lucide-vue-next";
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js";
import { useZoneStore } from "@/stores/zone.js";

const store = useGerantStore();
const zoneStore = useZoneStore();
const { formatMontant } = store;

// Budgets en attente d'approbation
const budgetsEnAttente = computed(() => store.budgetsEnAttente || []);
const approving = ref(null);

const refreshBudgets = async () => {
  await store.fetchBudgetsToApprove();
};

const handleApprove = async (budgetId) => {
  approving.value = budgetId;
  try {
    await store.approveBudget(budgetId, "approve");
    await refreshBudgets();
  } catch (e) {
    console.error("Erreur approbation:", e);
  } finally {
    approving.value = null;
  }
};

const handleReject = async (budgetId) => {
  approving.value = budgetId;
  try {
    await store.approveBudget(budgetId, "reject");
    await refreshBudgets();
  } catch (e) {
    console.error("Erreur rejet:", e);
  } finally {
    approving.value = null;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return "-";
  return new Date(dateStr).toLocaleDateString("fr-FR");
};

onMounted(async () => {
  await refreshBudgets();
});

const statistiques = computed(() => store.statistiques);

const firstGerantCampaignId = computed(() => store.campaigns?.[0]?.id || null);
const firstGerantProjetId = computed(() => {
  const first = store.campaigns?.[0];
  return (
    first?.projet?.id || first?.projet_id || store.projets?.[0]?.id || null
  );
});
const zonesForGerantIA = computed(() =>
  zoneStore.zones.map((z) => ({
    nom: z.nom,
    urgence: "Moyenne",
    score_total: z.score_total || 0,
    beneficiaires_prioritaires: z.nombre_beneficiaires || 0,
    top5: z.top5 || [],
  }))
);

const chartWidth = 800;
const chartHeight = 320;
const marginLeft = 60;
const marginRight = 24;
const marginTop = 24;
const marginBottom = 32;
const yAxisStep = (chartHeight - marginTop - marginBottom) / 5;

// Use finance store for real chart data
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js";
const financeStore = useFinanceStore();

onMounted(async () => {
  await financeStore.fetchExpenses();
  await financeStore.fetchBudgets();
});

const dataMensuelle = computed(() => {
  const moisNoms = ["Janv", "Févr", "Mars", "Avril", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"];
  const anneeEnCours = new Date().getFullYear();
  
  // Initialiser les données pour chaque mois
  let donnees = Array(12).fill(0).map((_, i) => ({
    mois: moisNoms[i],
    budget: 0,
    depenses: 0
  }));

  // Agréger les budgets
  const budgets = financeStore.budgets || [];
  budgets.forEach(b => {
    if (!b.date_creation) return;
    const date = new Date(b.date_creation);
    if (date.getFullYear() === anneeEnCours) {
      donnees[date.getMonth()].budget += parseFloat(b.montant) || 0;
    }
  });

  // Agréger les dépenses
  const depenses = financeStore.depenses || [];
  depenses.forEach(d => {
    if (!d.date) return;
    const date = new Date(d.date);
    if (date.getFullYear() === anneeEnCours) {
      donnees[date.getMonth()].depenses += parseFloat(d.montant) || 0;
    }
  });
  
  let maxVal = 0;
  donnees.forEach(d => {
    if (d.budget > maxVal) maxVal = d.budget;
    if (d.depenses > maxVal) maxVal = d.depenses;
  });
  
  if (maxVal > 0) {
    donnees = donnees.map(d => ({
      mois: d.mois,
      budget: (d.budget / maxVal) * 100,
      depenses: (d.depenses / maxVal) * 100,
      valeurReelleBudget: d.budget,
      valeurReelleDepenses: d.depenses
    }));
  }

  const moisActuel = new Date().getMonth();
  return donnees.slice(0, Math.min(moisActuel + 2, 12));
});

const chartAreaWidth = chartWidth - marginLeft - marginRight;
const chartAreaHeight = chartHeight - marginTop - marginBottom;

const pointX = (i) => {
  return marginLeft + (i / (dataMensuelle.value.length - 1)) * chartAreaWidth;
};

const pointY = (value) => {
  return marginTop + chartAreaHeight - (value / 100) * chartAreaHeight;
};

const budgetPoints = computed(() => {
  return dataMensuelle.value
    .map((item, i) => `${pointX(i)},${pointY(item.budget)}`)
    .join(" ");
});

const depensesPoints = computed(() => {
  return dataMensuelle.value
    .map((item, i) => `${pointX(i)},${pointY(item.depenses)}`)
    .join(" ");
});
</script>
