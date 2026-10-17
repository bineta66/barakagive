<template>
  <div class="min-w-0 space-y-6 bg-white p-4 sm:p-6 min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit sm:text-4xl">Finances</h1>
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
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">
            Budget total alloué
          </p>
          <h3 class="text-xl font-bold text-bleu-nuit mt-2">
            {{ formatMontant(financeStore.dashboard?.budget_total ?? statistiques.budgetTotal) }} FCFA
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
            {{ formatMontant(financeStore.dashboard?.depenses_validees ?? 0) }} FCFA
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
            {{ formatMontant(financeStore.dashboard?.solde_tresorerie ?? 0) }} FCFA
          </h3>
        </div>
        <Banknote class="text-bleu-nuit" :size="28" />
      </div>

    </div>

    <div v-if="financeStore.loading && !financeStore.dashboard" class="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-500">Chargement des données financières…</div>
    <section v-if="financeStore.dashboard" class="grid min-w-0 gap-4 xl:grid-cols-2" aria-label="Analyses financières">
      <article class="min-w-0 rounded-xl border border-slate-200/60 bg-white p-4 sm:p-6 xl:col-span-2">
        <h2 class="text-sm font-bold uppercase text-slate-900">Évolution mensuelle des flux financiers</h2>
        <p class="mt-1 text-xs text-gray-500">Comparez les financements et dons reçus aux dépenses validées. Survolez un point pour voir le montant exact.</p>
        <DashboardChart v-if="evolutionChart.labels.length" class="mt-4" type="line" :data="evolutionChart" :height="300" value-format="currency" />
        <p v-else class="py-10 text-center text-sm text-slate-500">Aucun mouvement financier sur cette période.</p>
      </article>

      <article class="min-w-0 rounded-xl border border-slate-200/60 bg-white p-4 sm:p-6">
        <h2 class="text-sm font-bold uppercase text-slate-900">Dépenses validées par catégorie</h2>
        <p class="mt-1 text-xs text-gray-500">Répartition basée sur les dépenses approuvées enregistrées.</p>
        <DashboardChart v-if="categoryChart.labels.length" class="mt-4" type="bar" :data="categoryChart" :height="280" horizontal value-format="currency" />
        <p v-else class="py-10 text-center text-sm text-slate-500">Aucune dépense validée enregistrée.</p>
      </article>

      <article class="min-w-0 rounded-xl border border-slate-200/60 bg-white p-4 sm:p-6">
        <h2 class="text-sm font-bold uppercase text-slate-900">Financements reçus par bailleur</h2>
        <p class="mt-1 text-xs text-gray-500">Montants confirmés comme reçus dans la base.</p>
        <DashboardChart v-if="bailleurChart.labels.length" class="mt-4" type="bar" :data="bailleurChart" :height="280" horizontal value-format="currency" />
        <p v-else class="py-10 text-center text-sm text-slate-500">Aucun financement reçu par bailleur.</p>
      </article>

      <article class="min-w-0 rounded-xl border border-slate-200/60 bg-white p-4 sm:p-6 xl:col-span-2">
        <h2 class="text-sm font-bold uppercase text-slate-900">Budget et dépenses par budget de projet</h2>
        <p class="mt-1 text-xs text-gray-500">Comparaison des montants alloués, dépensés et encore disponibles.</p>
        <DashboardChart v-if="budgetChart.labels.length" class="mt-4" type="bar" :data="budgetChart" :height="Math.max(260, Math.min(460, budgetChart.labels.length * 52))" horizontal value-format="currency" />
        <p v-else class="py-10 text-center text-sm text-slate-500">Aucun budget enregistré.</p>
      </article>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  PiggyBank,
  Receipt,
  Banknote,
  Activity,
  HandCoins,
  RefreshCw,
  Check,
  X,
} from "lucide-vue-next";
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js";
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js";
import DashboardChart from "@/components/ui/DashboardChart.vue";

const store = useGerantStore();
const financeStore = useFinanceStore();
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

const statistiques = computed(() => store.statistiques);
const evolutionChart = computed(() => {
  const rows = financeStore.dashboard?.evolution || [];
  return {
    labels: rows.map((row) => {
      const [year, month] = (row.key || '').split('-').map(Number);
      if (!year || !month) return row.label;
      const label = new Date(year, month - 1, 1).toLocaleDateString('fr-FR', { month: 'short' });
      return month === 1 ? `${label} ${year}` : label;
    }),
    datasets: [
      { label: "Financements reçus", data: rows.map((row) => Number(row.financements_recus || 0)), borderColor: "#0369A8", backgroundColor: "rgba(3,105,168,.08)", fill: false },
      { label: "Dons reçus", data: rows.map((row) => Number(row.dons_recus || 0)), borderColor: "#16a34a", backgroundColor: "rgba(22,163,74,.08)", fill: false },
      { label: "Dépenses validées", data: rows.map((row) => Number(row.depenses_validees || 0)), borderColor: "#D20C4F", backgroundColor: "rgba(210,12,79,.08)", fill: false },
    ],
  };
});

const categoryChart = computed(() => {
  const rows = (financeStore.dashboard?.depenses?.par_categorie || []).slice(0, 8);
  return {
    labels: rows.map((row) => row.categorie || "Sans catégorie"),
    datasets: [{ label: "Dépenses validées", data: rows.map((row) => Number(row.montant || 0)), backgroundColor: "#D20C4F" }],
  };
});

const bailleurChart = computed(() => {
  const rows = (financeStore.dashboard?.financements?.par_bailleur || []).slice(0, 8);
  return {
    labels: rows.map((row) => row.bailleur__nom || "Bailleur inconnu"),
    datasets: [{ label: "Financements reçus", data: rows.map((row) => Number(row.montant || 0)), backgroundColor: "#0369A8" }],
  };
});

const budgetChart = computed(() => {
  const byProject = new Map();
  for (const budget of financeStore.dashboard?.execution_budgetaire?.par_budget || []) {
    const row = byProject.get(budget.projet) || { projet: budget.projet, budget_prevu: 0, depenses_validees: 0, disponible: 0 };
    row.budget_prevu += Number(budget.budget_prevu || 0);
    row.depenses_validees += Number(budget.depenses_validees || 0);
    row.disponible += Number(budget.disponible || 0);
    byProject.set(budget.projet, row);
  }
  const rows = [...byProject.values()].sort((a, b) => b.budget_prevu - a.budget_prevu).slice(0, 8);
  return {
    labels: rows.map((row) => row.projet),
    datasets: [
      { label: "Budget alloué", data: rows.map((row) => Number(row.budget_prevu || 0)), backgroundColor: "#0369A8" },
      { label: "Dépenses validées", data: rows.map((row) => Number(row.depenses_validees || 0)), backgroundColor: "#D20C4F" },
      { label: "Disponible après engagements", data: rows.map((row) => Number(row.disponible || 0)), backgroundColor: "#94a3b8" },
    ],
  };
});

onMounted(async () => {
  await Promise.allSettled([refreshBudgets(), financeStore.fetchDashboard()]);
});
</script>
