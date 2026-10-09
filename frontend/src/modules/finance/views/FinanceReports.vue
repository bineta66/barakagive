<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100"
    >
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Rapports Financiers</h1>
        <p class="text-sm text-slate-500 mt-1">
          Génération de rapports financiers exportables.
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="generateIAReport"
          :disabled="isGeneratingIA"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-bleu-nuit hover:bg-[#0a2540] text-white text-sm font-semibold rounded-lg transition disabled:opacity-50"
        >
          <Sparkles class="w-4 h-4" />
          {{ isGeneratingIA ? "Génération..." : "Rapport IA" }}
        </button>
        <button
          @click="generatePDF"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-bleu-nuit hover:bg-[#0a2540] text-white text-sm font-semibold rounded-lg transition"
        >
          <FileText class="w-4 h-4" />
          Exporter PDF
        </button>
        <button
          @click="generateExcel"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-or hover:bg-[#5c3c02] text-white text-sm font-semibold rounded-lg transition"
        >
          <FileSpreadsheet class="w-4 h-4" />
          Exporter Excel
        </button>
      </div>
    </div>

    <!-- Loading -->
    <LoadingSpinner v-if="store.loading" message="Chargement des données..." />

    <div v-else class="space-y-6">
      <!-- Récapitulatif financier -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5"
        >
          <div class="flex items-center gap-3 mb-3">
            <div
              class="w-9 h-9 rounded-lg bg-bleu-nuit/10 flex items-center justify-center"
            >
              <Wallet class="w-5 h-5 text-bleu-nuit" />
            </div>
            <p class="text-xs font-bold uppercase text-slate-500">
              Budget initial
            </p>
          </div>
          <p class="text-2xl font-extrabold text-slate-900">
            {{ formatMontant(store.dashboard?.budget_total) }}
          </p>
          <p class="text-xs text-slate-400 mt-1">FCFA</p>
        </div>

        <div
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5"
        >
          <div class="flex items-center gap-3 mb-3">
            <div
              class="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center"
            >
              <HandCoins class="w-5 h-5 text-emerald-600" />
            </div>
            <p class="text-xs font-bold uppercase text-slate-500">Dons reçus</p>
          </div>
          <p class="text-2xl font-extrabold text-emerald-600">
            {{ formatMontant(store.dashboard?.dons_recus) }}
          </p>
          <p class="text-xs text-slate-400 mt-1">FCFA</p>
        </div>

        <div
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5"
        >
          <div class="flex items-center gap-3 mb-3">
            <div
              class="w-9 h-9 rounded-lg bg-red-50 flex items-center justify-center"
            >
              <TrendingDown class="w-5 h-5 text-red-500" />
            </div>
            <p class="text-xs font-bold uppercase text-slate-500">
              Dépenses totales
            </p>
          </div>
          <p class="text-2xl font-extrabold text-red-500">
            {{ formatMontant(store.dashboard?.depenses_totales) }}
          </p>
          <p class="text-xs text-slate-400 mt-1">FCFA</p>
        </div>

        <div
          class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-5"
        >
          <div class="flex items-center gap-3 mb-3">
            <div
              class="w-9 h-9 rounded-lg bg-bleu-accent/10 flex items-center justify-center"
            >
              <PiggyBank class="w-5 h-5 text-bleu-accent" />
            </div>
            <p class="text-xs font-bold uppercase text-slate-500">
              Solde disponible
            </p>
          </div>
          <p class="text-2xl font-extrabold text-bleu-nuit">
            {{ formatMontant(store.dashboard?.solde) }}
          </p>
          <p class="text-xs text-slate-400 mt-1">FCFA</p>
        </div>
      </div>

      <!-- Taux d'exécution -->
      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-base font-bold text-slate-900">
            Taux d'exécution budgétaire
          </h2>
          <span class="text-3xl font-extrabold text-bleu-nuit"
            >{{ store.dashboard?.taux_execution ?? 0 }}%</span
          >
        </div>
        <div class="w-full bg-slate-100 rounded-full h-4">
          <div
            class="h-4 rounded-full transition-all duration-700"
            :class="tauxColor"
            :style="{
              width: Math.min(store.dashboard?.taux_execution ?? 0, 100) + '%',
            }"
          />
        </div>
        <div class="flex justify-between text-xs text-slate-400 mt-2">
          <span>0% — Aucune exécution</span>
          <span>100% — Budget épuisé</span>
        </div>
      </div>

      <!-- Synthèse par budget -->
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl overflow-hidden"
      >
        <div class="px-6 py-4 border-b border-slate-100">
          <h2 class="text-base font-bold text-slate-900">
            Synthèse par budget projet
          </h2>
        </div>

        <EmptyState
          v-if="store.budgets.length === 0"
          titre="Aucun budget"
          description="Aucun budget disponible pour générer un rapport."
        />

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead
              class="bg-slate-50 text-xs font-semibold text-slate-600 uppercase"
            >
              <tr>
                <th class="text-left px-6 py-3">Projet</th>
                <th class="text-left px-6 py-3">Budget alloué</th>
                <th class="text-left px-6 py-3">Solde</th>
                <th class="text-left px-6 py-3">Taux</th>
                <th class="text-center px-6 py-3">Statut</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              <tr
                v-for="budget in store.budgets"
                :key="budget.id"
                class="hover:bg-slate-50/50"
              >
                <td class="px-6 py-4 font-semibold text-slate-900">
                  {{ budget.projet_nom }}
                </td>
                <td class="px-6 py-4 text-slate-700">
                  {{ formatMontant(budget.montant) }} FCFA
                </td>
                <td
                  class="px-6 py-4 font-bold"
                  :class="
                    budget.solde >= 0 ? 'text-emerald-600' : 'text-red-500'
                  "
                >
                  {{ formatMontant(budget.solde) }} FCFA
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <div
                      class="flex-1 bg-slate-100 rounded-full h-1.5 min-w-[60px]"
                    >
                      <div
                        class="h-1.5 rounded-full"
                        :class="
                          budget.taux_execution >= 90
                            ? 'bg-red-500'
                            : budget.taux_execution >= 70
                            ? 'bg-bleu-nuit'
                            : 'bg-emerald-500'
                        "
                        :style="{
                          width: Math.min(budget.taux_execution, 100) + '%',
                        }"
                      />
                    </div>
                    <span
                      class="text-xs font-medium text-slate-600 whitespace-nowrap"
                      >{{ budget.taux_execution }}%</span
                    >
                  </div>
                </td>
                <td class="px-6 py-4 text-center">
                  <StatusBadge :statut="budget.statut">{{
                    budget.statut
                  }}</StatusBadge>
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
import { ref, computed, onMounted } from "vue";
import {
  Wallet,
  HandCoins,
  TrendingDown,
  PiggyBank,
  FileText,
  FileSpreadsheet,
  Sparkles,
  X,
} from "lucide-vue-next";
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import api from "@/services/api.js";
import financeApi from "@/services/financeApi.js";

const store = useFinanceStore();

const isGeneratingIA = ref(false);
const showIAReport = ref(false);
const iaReportContent = ref("");

const formatMontant = (v) => Number(v || 0).toLocaleString("fr-FR");

const tauxColor = computed(() => {
  const t = store.dashboard?.taux_execution ?? 0;
  if (t >= 90) return "bg-red-500";
  if (t >= 70) return "bg-bleu-nuit";
  return "bg-emerald-500";
});

const downloadReport = (blob, filename) => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
};

const generatePDF = async () => {
  try {
    const response = await financeApi.exportPDF();
    downloadReport(response.data, `rapport_barakagive_${new Date().toISOString().slice(0, 10)}.pdf`);
  } catch {
    alert("L'export PDF est indisponible pour le moment.");
  }
};

const generateExcel = async () => {
  try {
    const response = await financeApi.exportExcel();
    downloadReport(response.data, `rapport_barakagive_${new Date().toISOString().slice(0, 10)}.xlsx`);
  } catch {
    alert("L'export Excel est indisponible pour le moment.");
  }
};

const generateIAReport = async () => {
  if (isGeneratingIA.value) return;
  isGeneratingIA.value = true;
  try {
    const response = await api.post("/api/ia/rapport/generate");
    iaReportContent.value = response.data.report || "Aucun rapport généré.";
    showIAReport.value = true;
  } catch (error) {
    console.error("Erreur génération IA:", error);
    alert("Erreur lors de la génération du rapport.");
  } finally {
    isGeneratingIA.value = false;
  }
};

const downloadIAReport = () => {
  const content = document.getElementById("ia-report-content").innerHTML;
  const printWindow = window.open("", "", "height=600,width=800");
  printWindow.document.write("<html><head><title>Rapport IA</title>");
  printWindow.document.write(
    "<style>body{font-family:sans-serif;padding:20px;white-space:pre-wrap;}</style>"
  );
  printWindow.document.write("</head><body>");
  printWindow.document.write(content);
  printWindow.document.write("</body></html>");
  printWindow.document.close();
  printWindow.focus();
  setTimeout(() => {
    printWindow.print();
    printWindow.close();
  }, 250);
};

onMounted(() => store.refreshAll());
</script>
