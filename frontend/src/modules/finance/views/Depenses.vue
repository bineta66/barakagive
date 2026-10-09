<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100"
    >
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Dépenses</h1>
        <p class="text-sm text-slate-500 mt-1">
          Gestion des dépenses et justificatifs.
        </p>
      </div>
      <BoutonPrimary @click="openCreateDepense">
        <Plus class="w-4 h-4" />
        Ajouter dépense
      </BoutonPrimary>
    </div>

    <!-- KPI -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Total dépenses
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
            Montant total engagé
          </p>
          <h3 class="text-2xl font-bold text-red-500 mt-1">
            {{ formatMontant(totalDepenses) }}
            <span class="text-sm font-normal text-slate-400">FCFA</span>
          </h3>
        </div>
        <TrendingDown class="text-bleu-nuit" :size="28" />
      </div>
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            En attente de validation
          </p>
          <h3 class="text-2xl font-bold text-amber-500 mt-1">
            {{ enAttente }}
          </h3>
        </div>
        <Clock class="text-bleu-nuit" :size="28" />
      </div>
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Avec justificatif
          </p>
          <h3 class="text-2xl font-bold text-emerald-500 mt-1">
            {{ avecJustificatif }}
          </h3>
        </div>
        <CheckCircle class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div
      class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 grid md:grid-cols-3 gap-3"
    >
      <div class="relative">
        <Search
          class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          :size="16"
        />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher par réf., projet, catégorie..."
          class="w-full border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
        />
      </div>
      <select
        v-model="filtreStatut"
        class="border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
      >
        <option value="">Tous les statuts</option>
        <option value="EN_ATTENTE">En attente</option>
        <option value="VERIFIE">Vérifié</option>
        <option value="APPROUVE">Approuvé</option>
        <option value="REJETE">Rejeté</option>
      </select>
      <BoutonTertiary
        @click="
          search = '';
          filtreStatut = '';
        "
        >Réinitialiser</BoutonTertiary
      >
    </div>

    <!-- Loading -->
    <LoadingSpinner v-if="store.loading" message="Chargement des dépenses..." />

    <!-- Tableau -->
    <div
      v-else
      class="bg-white border border-slate-200/60 shadow-xs rounded-xl overflow-hidden"
    >
      <div
        class="px-6 py-4 flex items-center justify-between border-b border-slate-100"
      >
        <h2 class="text-base font-bold text-slate-900">Liste des dépenses</h2>
        <span class="text-xs text-slate-400"
          >{{ filtered.length }} dépenses répertoriées</span
        >
      </div>

      <EmptyState
        v-if="filtered.length === 0"
        titre="Aucune dépense"
        description="Aucune dépense ne correspond aux filtres sélectionnés."
      />

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead
            class="bg-slate-50 text-xs font-semibold text-slate-600 uppercase"
          >
            <tr>
              <th class="text-left px-6 py-3">Référence</th>
              <th class="text-left px-6 py-3">Projet</th>
              <th class="text-left px-6 py-3">Catégorie</th>
              <th class="text-left px-6 py-3">Montant</th>
              <th class="text-left px-6 py-3">Date</th>
              <th class="text-center px-6 py-3">Statut</th>
              <th class="text-center px-6 py-3">Justif.</th>
              <th class="text-center px-6 py-3">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr
              v-for="depense in filtered"
              :key="depense.id"
              class="hover:bg-slate-50/50 cursor-pointer"
              @click="openDetail(depense)"
            >
              <td class="px-6 py-4 font-mono text-xs text-slate-700">
                {{ depense.reference }}
              </td>
              <td class="px-6 py-4 font-semibold text-slate-900">
                {{ depense.projet_nom }}
              </td>
              <td class="px-6 py-4 text-slate-600">{{ depense.categorie }}</td>
              <td class="px-6 py-4 font-bold text-red-500">
                -{{ formatMontant(depense.montant) }} FCFA
              </td>
              <td class="px-6 py-4 text-slate-500 text-xs">
                {{ depense.date }}
              </td>
              <td class="px-6 py-4 text-center">
                <StatusBadge :statut="statutLabel(depense.statut)">{{
                  depense.statut
                }}</StatusBadge>
              </td>
              <td class="px-6 py-4 text-center">
                <span
                  v-if="
                    depense.justifications && depense.justifications.length > 0
                  "
                  class="inline-flex items-center gap-1 text-xs font-medium text-emerald-600"
                >
                  <CheckCircle class="w-3.5 h-3.5" />
                  {{ depense.justifications.length }}
                </span>
                <span
                  v-else
                  class="inline-flex items-center gap-1 text-xs font-medium text-slate-400"
                >
                  <XCircle class="w-3.5 h-3.5" /> Non
                </span>
              </td>
              <td class="px-6 py-4 text-center" @click.stop>
                <div class="flex items-center justify-center gap-1">
                  <button
                    @click="openDetail(depense)"
                    class="p-1.5 rounded-lg hover:bg-bleu-nuit/10 text-bleu-nuit transition"
                    title="Voir détail"
                  >
                    <Eye :size="16" />
                  </button>
                  <button
                    @click="openEditDepense(depense)"
                    class="p-1.5 rounded-lg hover:bg-bleu-nuit/10 text-bleu-nuit transition"
                    title="Modifier la dépense"
                  >
                    <Pencil :size="16" />
                  </button>
                  <button
                    @click="openJustifUpload(depense)"
                    class="p-1.5 rounded-lg hover:bg-emerald-50 text-emerald-600 transition"
                    title="Ajouter justificatif"
                  >
                    <Upload :size="16" />
                  </button>
                  <button
                    @click="confirmDeleteDepense(depense)"
                    class="p-1.5 rounded-lg hover:bg-red-50 text-red-400 hover:text-red-600 transition"
                    title="Supprimer"
                  >
                    <Trash2 :size="16" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal ajout / modification dépense -->
    <DepenseFormModal
      v-if="modalOpen"
      :ouvert="modalOpen"
      :initial-budget-id="String(route.query.budget || '')"
      :depense="editingDepense"
      :erreur-backend="modalError"
      :saving="savingDepense"
      @fermer="
        modalOpen = false;
        editingDepense = null;
        modalError = '';
      "
      @save="saveDepense"
    />

    <!-- Modal détail dépense -->
    <DepenseDetailModal
      v-if="detailOpen && selectedDepense"
      :ouvert="detailOpen"
      :depense="selectedDepense"
      @fermer="detailOpen = false; selectedDepense = null;"
      @deleted="detailOpen = false; selectedDepense = null;"
    />

    <!-- Modal justification rapide -->
    <JustificationModal
      v-if="justifModalOpen && justifDepense"
      :ouvert="justifModalOpen"
      :depense="justifDepense"
      :erreur-backend="justifModalError"
      :chargement="uploadingJustification"
      @fermer="justifModalOpen = false; justifDepense = null;"
      @save="saveJustification"
    />

    <!-- Confirmation suppression -->
    <div
      v-if="deleteConfirm"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      @click.self="deleteConfirm = false"
    >
      <div class="bg-white rounded-xl shadow-lg p-6 max-w-sm w-full mx-4">
        <h3 class="text-lg font-bold text-slate-900 mb-2">Confirmer la suppression</h3>
        <p class="text-sm text-slate-600 mb-4">
          Voulez-vous vraiment supprimer la dépense
          <strong>{{ deleteTarget?.reference }}</strong> ?
        </p>
        <div class="flex justify-end gap-3">
          <button
            @click="deleteConfirm = false"
            class="px-4 py-2 text-sm border border-slate-200 rounded-lg text-slate-700 hover:bg-slate-100 transition"
          >
            Annuler
          </button>
          <button
            @click="handleDelete"
            :disabled="deleting"
            class="px-4 py-2 text-sm font-semibold text-white bg-red-600 rounded-lg hover:bg-red-700 transition disabled:opacity-60"
          >
            {{ deleting ? "Suppression..." : "Supprimer" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import {
  Plus,
  Receipt,
  TrendingDown,
  Clock,
  Search,
  CheckCircle,
  XCircle,
  Eye,
  Pencil,
  Upload,
  Trash2,
} from "lucide-vue-next";
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js";
import DepenseFormModal from "@/modules/finance/components/depenses/DepenseFormModal.vue";
import DepenseDetailModal from "@/modules/finance/components/depenses/DepenseDetailModal.vue";
import JustificationModal from "@/modules/finance/components/justifications/JustificationModal.vue";
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue";
import BoutonTertiary from "@/components/ui/BoutonTertiary.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { parseApiError } from "@/modules/finance/utils/parseApiError.js";

const store = useFinanceStore();
const route = useRoute();
const modalOpen = ref(false);
const editingDepense = ref(null);
const modalError = ref("");
const savingDepense = ref(false);
const search = ref("");
const filtreStatut = ref("");

const openCreateDepense = () => {
  editingDepense.value = null;
  modalOpen.value = true;
};

const openEditDepense = (depense) => {
  editingDepense.value = depense;
  modalOpen.value = true;
};

// Detail modal
const detailOpen = ref(false);
const selectedDepense = ref(null);

// Justification modal
const justifModalOpen = ref(false);
const justifDepense = ref(null);
const justifModalError = ref("");
const uploadingJustification = ref(false);

// Delete confirmation
const deleteConfirm = ref(false);
const deleteTarget = ref(null);
const deleting = ref(false);

const formatMontant = (v) => Number(v || 0).toLocaleString("fr-FR");

const totalDepenses = computed(() =>
  store.depenses.reduce((s, d) => s + parseFloat(d.montant || 0), 0)
);
const enAttente = computed(
  () => store.depenses.filter((d) => d.statut === "EN_ATTENTE").length
);
const avecJustificatif = computed(
  () =>
    store.depenses.filter(
      (d) => d.justifications && d.justifications.length > 0
    ).length
);

// Map backend statuts → StatusBadge keys
const statutLabel = (s) => {
  const map = {
    EN_ATTENTE: "En attente",
    VERIFIE: "En cours",
    APPROUVE: "ACTIF",
    REJETE: "Critique",
  };
  return map[s] || s;
};

const filtered = computed(() =>
  store.depenses.filter((d) => {
    const q = search.value.toLowerCase();
    const matchSearch =
      !q ||
      d.reference?.toLowerCase().includes(q) ||
      d.projet_nom?.toLowerCase().includes(q) ||
      d.categorie?.toLowerCase().includes(q) ||
      d.fournisseur?.toLowerCase().includes(q);
    const matchStatut = !filtreStatut.value || d.statut === filtreStatut.value;
    return matchSearch && matchStatut;
  })
);

// -- Actions
const openDetail = (depense) => {
  selectedDepense.value = depense;
  detailOpen.value = true;
};

const openJustifUpload = (depense) => {
  justifDepense.value = depense;
  justifModalOpen.value = true;
};

const confirmDeleteDepense = (depense) => {
  deleteTarget.value = depense;
  deleteConfirm.value = true;
};

const handleDelete = async () => {
  deleting.value = true;
  try {
    await store.deleteExpense(deleteTarget.value.id);
    deleteConfirm.value = false;
    deleteTarget.value = null;
  } catch (e) {
    // silent
  } finally {
    deleting.value = false;
  }
};

const saveDepense = async (data) => {
  if (savingDepense.value) return;
  modalError.value = "";
  savingDepense.value = true;
  try {
    if (data.id) {
      await store.updateExpense(data.id, data);
    } else {
      await store.createExpense(data);
    }
    modalOpen.value = false;
    editingDepense.value = null;
  } catch (e) {
    modalError.value = parseApiError(e);
  } finally {
    savingDepense.value = false;
  }
};

const saveJustification = async (data) => {
  if (uploadingJustification.value) return;
  justifModalError.value = "";
  uploadingJustification.value = true;
  try {
    await store.uploadJustification(
      data.depenseId,
      data.file,
      data.type_fichier
    );
    justifModalOpen.value = false;
    justifDepense.value = null;
  } catch (e) {
    justifModalError.value = parseApiError(e);
  } finally {
    uploadingJustification.value = false;
  }
};

onMounted(async () => {
  await store.fetchExpenses();
  if (route.query.budget) openCreateDepense();
});
</script>
