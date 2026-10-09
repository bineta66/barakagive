<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100"
    >
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">
          Tableau de bord Financier
        </h1>
        <p class="text-sm text-slate-500 mt-1">
          Indicateurs financiers en temps réel pour vos projets assignés.
        </p>
      </div>
    </div>

    <!-- Loading -->
    <LoadingSpinner
      v-if="store.loading"
      message="Chargement des données financières..."
    />

    <div v-else class="space-y-6">
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
        <div
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
        >
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">
              Budget total
            </p>
            <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
              {{ formatMontant(store.dashboard?.budget_total) }}
            </h3>
            <span class="text-xs text-slate-400">FCFA</span>
          </div>
          <Wallet class="text-bleu-nuit" :size="32" />
        </div>

        <div
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
        >
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Financements reçus</p>
            <h3 class="text-2xl font-bold text-emerald-600 mt-1">
              {{ formatMontant(store.dashboard?.financements_recus) }}
            </h3>
            <span class="text-xs text-slate-400">FCFA</span>
          </div>
          <HandCoins class="text-bleu-nuit" :size="32" />
        </div>

        <div
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
        >
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">
              Dons reçus
            </p>
            <h3 class="text-2xl font-bold text-emerald-600 mt-1">
              {{ formatMontant(store.dashboard?.dons_recus) }}
            </h3>
            <span class="text-xs text-slate-400">FCFA</span>
          </div>
          <HandCoins class="text-bleu-nuit" :size="32" />
        </div>

        <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between items-center">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Dépenses validées</p>
            <h3 class="text-2xl font-bold text-red-500 mt-1">{{ formatMontant(store.dashboard?.depenses_validees) }}</h3>
            <span class="text-xs text-slate-400">FCFA</span>
          </div>
          <TrendingDown class="text-bleu-nuit" :size="32" />
        </div>

        <div
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
        >
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">
              Solde disponible
            </p>
            <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
              {{ formatMontant(store.dashboard?.solde_disponible ?? store.dashboard?.solde) }}
            </h3>
            <span class="text-xs text-slate-400">FCFA</span>
          </div>
          <PiggyBank class="text-bleu-nuit" :size="32" />
        </div>
      </div>

      <section class="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div class="xl:col-span-2 bg-white border border-slate-200/60 rounded-xl p-5">
          <div class="mb-4">
            <h2 class="text-base font-bold text-slate-900">Évolution financière</h2>
            <p class="text-xs text-slate-500">Flux reçus et dépenses validées, sur les 12 derniers mois.</p>
          </div>
          <DashboardChart v-if="evolutionChartData.labels.length" type="line" :data="evolutionChartData" value-format="currency" :height="260" />
          <p v-else class="py-12 text-center text-sm text-slate-400">Aucune donnée sur cette période.</p>
        </div>
        <div class="bg-white border border-slate-200/60 rounded-xl p-5">
          <h2 class="text-base font-bold text-slate-900">Alertes financières</h2>
          <div v-if="store.dashboard?.alerts?.length" class="mt-4 space-y-2">
            <div v-for="alert in store.dashboard.alerts" :key="alert.type" class="rounded-lg border p-3 text-sm" :class="alert.niveau === 'RED' ? 'border-red-200 bg-red-50 text-red-800' : alert.niveau === 'ORANGE' ? 'border-amber-200 bg-amber-50 text-amber-900' : 'border-slate-200 bg-slate-50 text-slate-700'">
              {{ alert.message }}
            </div>
          </div>
          <p v-else class="mt-4 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">Aucune alerte financière détectée.</p>
        </div>
      </section>

      <section class="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div class="bg-white border border-slate-200/60 rounded-xl p-5">
          <div class="flex items-start justify-between gap-3">
            <div><h2 class="text-base font-bold text-slate-900">Financements</h2><p class="text-xs text-slate-500">Seuls les montants reçus alimentent les KPI de trésorerie.</p></div>
            <span class="text-xs font-semibold text-slate-500">Reste à financer : {{ formatMontant(store.dashboard?.reste_a_financer) }} FCFA</span>
          </div>
          <div class="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div v-for="(value, key) in fundingStatusRows" :key="key" class="rounded-lg bg-slate-50 p-3"><p class="text-xs text-slate-500">{{ fundingStatusLabel(key) }}</p><p class="mt-1 font-semibold text-bleu-nuit">{{ formatMontant(value) }} FCFA</p></div>
          </div>
        </div>
        <div class="bg-white border border-slate-200/60 rounded-xl p-5">
          <div class="flex items-center justify-between"><div><h2 class="text-base font-bold text-slate-900">Exécution budgétaire</h2><p class="text-xs text-slate-500">Calculée à partir des budgets et dépenses validées.</p></div><span class="text-xl font-extrabold text-bleu-nuit">{{ store.dashboard?.execution_budgetaire?.taux_execution ?? 0 }}%</span></div>
          <div class="mt-4 h-2.5 overflow-hidden rounded-full bg-slate-100"><div class="h-full rounded-full bg-emerald-600 transition-all" :style="{ width: `${Math.min(100, store.dashboard?.execution_budgetaire?.taux_execution || 0)}%` }" /></div>
          <div class="mt-3 flex flex-wrap justify-between gap-2 text-xs text-slate-600"><span>Prévu : {{ formatMontant(store.dashboard?.execution_budgetaire?.budget_prevu) }} FCFA</span><span>Validé : {{ formatMontant(store.dashboard?.execution_budgetaire?.depenses_validees) }} FCFA</span><span>Disponible : {{ formatMontant(store.dashboard?.execution_budgetaire?.disponible) }} FCFA</span></div>
          <p v-if="store.dashboard?.execution_budgetaire?.budget_revise == null" class="mt-2 text-[11px] text-slate-400">Aucun budget révisé enregistré.</p>
        </div>
      </section>

      <section class="bg-white border border-slate-200/60 rounded-xl p-5">
        <div class="mb-3"><h2 class="text-base font-bold text-slate-900">Analyse financière</h2><p class="text-xs text-slate-500">Synthèse issue des données Django de votre organisation.</p></div>
        <p v-if="assistantStore.homeData?.observation" class="text-sm text-slate-700">{{ assistantStore.homeData.observation }}</p>
        <div v-if="assistantStore.homeData?.risques?.length" class="mt-3">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">À surveiller</p>
          <ul class="mt-1 space-y-1 text-sm text-slate-700"><li v-for="risk in assistantStore.homeData.risques.slice(0, 3)" :key="risk">{{ risk }}</li></ul>
        </div>
        <p v-if="assistantStore.homeData?.recommandation" class="mt-3 text-sm text-slate-700"><span class="font-semibold text-bleu-nuit">Priorité :</span> {{ assistantStore.homeData.recommandation }}</p>
        <p v-if="!assistantStore.homeData?.observation && !assistantStore.loadingHome" class="text-sm text-slate-500">L’analyse est indisponible pour le moment.</p>
      </section>

      <!-- Graphiques : Donut répartition + Barres dépenses par catégorie -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Donut : Budget / Dépenses / Solde -->
        <div
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5"
        >
          <h2 class="text-sm font-bold text-slate-900 mb-4">
            Répartition financière
          </h2>
          <ChartDonut
            v-if="donutFinanceItems.some((i) => i.value > 0)"
            :items="donutFinanceItems"
            :size="128"
            :thickness="22"
            :center-value="formatMontant(store.dashboard?.dons_recus ?? 0)"
            center-label="dons reçus"
            :center-font-size="13"
          />
          <div
            v-else
            class="flex items-center justify-center h-32 text-slate-400 text-sm"
          >
            Aucune donnée financière
          </div>
        </div>

        <!-- Barres horizontales : Dépenses par catégorie -->
        <div
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5"
        >
          <h2 class="text-sm font-bold text-slate-900 mb-4">
            Dépenses par catégorie
          </h2>
          <ChartBarsH
            :items="depensesCatItems"
            :max-items="6"
            default-color="#021427"
            :bar-height="8"
            :label-width="120"
            format="fcfa"
          />
          <p
            v-if="!depensesCatItems.length"
            class="text-xs text-slate-400 text-center py-4"
          >
            Aucune dépense enregistrée
          </p>
        </div>
      </div>

      <!-- Dernières transactions -->
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl overflow-hidden"
      >
        <div
          class="px-6 py-4 flex items-center justify-between border-b border-slate-100"
        >
          <h2 class="text-base font-bold text-slate-900">
            Dernières transactions
          </h2>
          <span class="text-xs text-slate-400"
            >{{ recentTransactions.length }} entrées</span
          >
        </div>

        <EmptyState
          v-if="recentTransactions.length === 0"
          titre="Aucune transaction"
          description="Aucun don ou dépense enregistré pour le moment."
        />

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead
              class="bg-slate-50 text-xs font-semibold text-slate-600 uppercase"
            >
              <tr>
                <th class="text-left px-6 py-3">Type</th>
                <th class="text-left px-6 py-3">Référence</th>
                <th class="text-left px-6 py-3">Description</th>
                <th class="text-left px-6 py-3">Montant</th>
                <th class="text-left px-6 py-3">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              <tr
                v-for="item in recentTransactions"
                :key="item.id"
                class="hover:bg-slate-50/50"
              >
                <td class="px-6 py-3.5">
                  <StatusBadge
                    :statut="item.type === 'Don' ? 'ACTIF' : 'Critique'"
                    >{{ item.type }}</StatusBadge
                  >
                </td>
                <td class="px-6 py-3.5 font-mono text-xs text-slate-700">
                  {{ item.reference }}
                </td>
                <td class="px-6 py-3.5 text-slate-600">
                  {{ item.description }}
                </td>
                <td
                  class="px-6 py-3.5 font-semibold"
                  :class="
                    item.type === 'Don' ? 'text-emerald-600' : 'text-red-500'
                  "
                >
                  {{ item.type === "Don" ? "+" : "-"
                  }}{{ formatMontant(item.montant) }} FCFA
                </td>
                <td class="px-6 py-3.5 text-slate-500 text-xs">
                  {{ item.date }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { Wallet, HandCoins, TrendingDown, PiggyBank } from "lucide-vue-next";
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js";
import { useAutoRefresh } from "@/composables/useAutoRefresh.js";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import ChartDonut from "@/components/ui/ChartDonut.vue";
import ChartBarsH from "@/components/ui/ChartBarsH.vue";
import DashboardChart from "@/components/ui/DashboardChart.vue";
import { useFinanceAssistantStore } from "@/stores/financeAssistant.js";

const store = useFinanceStore();
const assistantStore = useFinanceAssistantStore();

const formatMontant = (value) => Number(value || 0).toLocaleString("fr-FR");

const evolutionChartData = computed(() => {
  const rows = store.dashboard?.evolution || [];
  return {
    labels: rows.map((row) => row.label),
    datasets: [
      { label: "Financements reçus", data: rows.map((row) => row.financements_recus), borderColor: "#021427", backgroundColor: "rgba(2,20,39,.08)", fill: false },
      { label: "Dons reçus", data: rows.map((row) => row.dons_recus), borderColor: "#16a34a", backgroundColor: "rgba(22,163,74,.08)", fill: false },
      { label: "Dépenses validées", data: rows.map((row) => row.depenses_validees), borderColor: "#d20c4f", backgroundColor: "rgba(210,12,79,.08)", fill: false },
    ],
  };
});

const fundingStatusRows = computed(() => store.dashboard?.financements?.par_statut || {});
const fundingStatusLabel = (key) => ({ PREVU: "Prévus", CONFIRME: "Confirmés", RECU: "Reçus", ANNULE: "Annulés" }[key] || key);

const tauxColor = computed(() => {
  const t = store.dashboard?.taux_execution ?? 0;
  if (t >= 90) return "bg-red-500";
  if (t >= 70) return "bg-bleu-nuit";
  return "bg-emerald-500";
});

// ── Donut répartition financière ─────────────────────────────────
const donutFinanceItems = computed(() => [
  {
    label: "Dépenses réalisées",
    value: Number(store.dashboard?.depenses_totales ?? 0),
    color: "#021427",
    displayValue:
      formatMontant(store.dashboard?.depenses_totales ?? 0) + " FCFA",
  },
  {
    label: "Solde disponible",
    value: Math.max(0, Number(store.dashboard?.solde ?? 0)),
    color: "#94a3b8",
    displayValue:
      formatMontant(Math.max(0, store.dashboard?.solde ?? 0)) + " FCFA",
  },
]);

// ── Barres dépenses par catégorie ────────────────────────────────
const COLORS_CAT = [
  "#021427",
  "#94a3b8",
  "#0369A8",
  "#16a34a",
  "#dc2626",
  "#7c3aed",
  "#0891b2",
  "#d97706",
];
const depensesCatItems = computed(() =>
  (store.dashboard?.depenses?.par_categorie || []).map((row, i) => ({
    label: row.categorie || "Sans catégorie",
    value: Number(row.montant || 0),
    color: COLORS_CAT[i % COLORS_CAT.length],
  }))
);

const recentTransactions = computed(() => {
  const list = [];
  store.dons.slice(0, 5).forEach((d) =>
    list.push({
      id: "don-" + d.id,
      type: "Don",
      reference: d.reference,
      description: d.donateur || d.donateur_nom || "Donateur anonyme",
      montant: d.montant,
      date: d.date,
    })
  );
  store.depenses.slice(0, 5).forEach((d) =>
    list.push({
      id: "dep-" + d.id,
      type: "Dépense",
      reference: d.reference,
      description: d.categorie,
      montant: d.montant,
      date: d.date,
    })
  );
  return list.sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 10);
});

useAutoRefresh(() => store.refreshAll());
onMounted(() => assistantStore.fetchHomeData());
</script>
