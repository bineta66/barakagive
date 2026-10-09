<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100"
    >
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Justifications</h1>
        <p class="text-sm text-slate-500 mt-1">
          Gestion des pièces justificatives des dépenses.
        </p>
      </div>
    </div>

    <!-- KPI -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Dépenses totales
          </p>
          <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
            {{ store.depenses.length }}
          </h3>
        </div>
        <Receipt class="text-bleu-nuit" :size="28" />
      </div>
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Avec justificatif
          </p>
          <h3 class="text-2xl font-bold text-emerald-600 mt-1">
            {{ avecJustificatif }}
          </h3>
        </div>
        <CheckCircle class="text-bleu-nuit" :size="28" />
      </div>
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Sans justificatif
          </p>
          <h3 class="text-2xl font-bold text-red-500 mt-1">
            {{ sansJustificatif }}
          </h3>
        </div>
        <AlertTriangle class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Loading -->
    <LoadingSpinner
      v-if="store.loading"
      message="Chargement des justifications..."
    />

    <!-- Tableau -->
    <div
      v-else
      class="bg-white border border-slate-200/60 shadow-xs rounded-xl overflow-hidden"
    >
      <div
        class="px-6 py-4 flex items-center justify-between border-b border-slate-100"
      >
        <h2 class="text-base font-bold text-slate-900">
          Pièces justificatives
        </h2>
        <span class="text-xs text-slate-400"
          >{{ store.depenses.length }} dépenses</span
        >
      </div>

      <EmptyState
        v-if="store.depenses.length === 0"
        titre="Aucune dépense"
        description="Aucune dépense n'a encore été enregistrée."
      />

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead
            class="bg-slate-50 text-xs font-semibold text-slate-600 uppercase"
          >
            <tr>
              <th class="text-left px-6 py-3">Dépense</th>
              <th class="text-left px-6 py-3">Catégorie</th>
              <th class="text-left px-6 py-3">Type fichier</th>
              <th class="text-center px-6 py-3">Statut justif.</th>
              <th class="text-left px-6 py-3">Date dépôt</th>
              <th class="text-center px-6 py-3">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr
              v-for="depense in store.depenses"
              :key="depense.id"
              class="hover:bg-slate-50/50"
            >
              <td class="px-6 py-4">
                <p class="font-mono text-xs text-slate-700">
                  {{ depense.reference }}
                </p>
                <p class="text-xs text-slate-400 mt-0.5">
                  {{ depense.projet_nom }}
                </p>
              </td>
              <td class="px-6 py-4 text-slate-600">{{ depense.categorie }}</td>
              <td class="px-6 py-4 text-slate-500">
                {{ depense.justifications?.[0]?.type_fichier || "—" }}
              </td>
              <td class="px-6 py-4 text-center">
                <template
                  v-if="
                    depense.justifications && depense.justifications.length > 0
                  "
                >
                  <StatusBadge
                    :statut="
                      justifStatutLabel(depense.justifications[0].statut)
                    "
                  >
                    {{ depense.justifications[0].statut }}
                  </StatusBadge>
                </template>
                <span v-else class="text-xs text-slate-400 italic">Aucun</span>
              </td>
              <td class="px-6 py-4 text-xs text-slate-500">
                {{
                  depense.justifications?.[0]?.created_at?.slice(0, 10) || "—"
                }}
              </td>
              <td class="px-6 py-4 text-center">
                <button
                  @click="uploadJustification(depense)"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors"
                  :class="
                    depense.justifications && depense.justifications.length > 0
                      ? 'bg-bleu-nuit/10 text-bleu-nuit hover:bg-bleu-nuit/20'
                      : 'bg-bleu-nuit/10 text-bleu-nuit hover:bg-bleu-nuit/20'
                  "
                >
                  <Upload class="w-3.5 h-3.5" />
                  {{
                    depense.justifications && depense.justifications.length > 0
                      ? "Remplacer"
                      : "Joindre"
                  }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <JustificationModal
      v-if="modalOpen"
      :ouvert="modalOpen"
      :depense="selectedDepense"
      :erreur-backend="modalError"
      :chargement="uploadingJustification"
      @fermer="
        modalOpen = false;
        modalError = '';
      "
      @save="saveJustification"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { Receipt, CheckCircle, AlertTriangle, Upload } from "lucide-vue-next";
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js";
import JustificationModal from "@/modules/finance/components/justifications/JustificationModal.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { parseApiError } from "@/modules/finance/utils/parseApiError.js";

const store = useFinanceStore();
const modalOpen = ref(false);
const modalError = ref("");
const uploadingJustification = ref(false);
const selectedDepense = ref(null);

const avecJustificatif = computed(
  () =>
    store.depenses.filter(
      (d) => d.justifications && d.justifications.length > 0
    ).length
);
const sansJustificatif = computed(
  () =>
    store.depenses.filter(
      (d) => !d.justifications || d.justifications.length === 0
    ).length
);

const justifStatutLabel = (s) => {
  const map = {
    CONFORME: "ACTIF",
    A_VERIFIER: "En attente",
    NON_CONFORME: "Critique",
  };
  return map[s] || "En attente";
};

const uploadJustification = (depense) => {
  selectedDepense.value = depense;
  modalOpen.value = true;
};

const saveJustification = async (data) => {
  if (uploadingJustification.value) return;
  modalError.value = "";
  uploadingJustification.value = true;
  try {
    // data = { depenseId, file, type_fichier }
    await store.uploadJustification(
      data.depenseId,
      data.file,
      data.type_fichier
    );
    modalOpen.value = false;
  } catch (e) {
    modalError.value = parseApiError(e);
  } finally {
    uploadingJustification.value = false;
  }
};

onMounted(() => store.fetchExpenses());
</script>
