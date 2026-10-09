<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100"
    >
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Budgets</h1>
        <p class="text-sm text-slate-500 mt-1">
          Gestion des budgets par projet.
        </p>
      </div>
      <BoutonPrimary @click="modalOpen = true">
        <Plus class="w-4 h-4" />
        Ajouter budget
      </BoutonPrimary>
    </div>

    <!-- KPI -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Total budgets
          </p>
          <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
            {{ store.budgets.length }}
          </h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Montant total alloué
          </p>
          <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
            {{ formatMontant(totalMontant) }}
            <span class="text-sm font-normal text-slate-400">FCFA</span>
          </h3>
        </div>
        <TrendingUp class="text-bleu-nuit" :size="28" />
      </div>
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Solde disponible
          </p>
          <h3 class="text-2xl font-bold text-emerald-600 mt-1">
            {{ formatMontant(totalSolde) }}
            <span class="text-sm font-normal text-slate-400">FCFA</span>
          </h3>
        </div>
        <PiggyBank class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Loading -->
    <LoadingSpinner v-if="store.loading" message="Chargement des budgets..." />

    <!-- Tableau -->
    <div
      v-else
      class="bg-white border border-slate-200/60 shadow-xs rounded-xl overflow-hidden"
    >
      <div
        class="px-6 py-4 flex items-center justify-between border-b border-slate-100"
      >
        <h2 class="text-base font-bold text-slate-900">Liste des budgets</h2>
        <span class="text-xs text-slate-400"
          >{{ store.budgets.length }} budgets répertoriés</span
        >
      </div>

      <EmptyState
        v-if="store.budgets.length === 0"
        titre="Aucun budget"
        description="Aucun budget n'a encore été créé pour vos projets."
      />

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead
            class="bg-slate-50 text-xs font-semibold text-slate-600 uppercase"
          >
            <tr>
              <th class="text-left px-6 py-3">Projet</th>
              <th class="text-left px-6 py-3">Montant</th>
              <th class="text-left px-6 py-3">Source</th>
              <th class="text-left px-6 py-3">Solde</th>
              <th class="text-left px-6 py-3">Taux</th>
              <th class="text-center px-6 py-3">Statut</th>
              <th class="text-center px-6 py-3">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr
              v-for="budget in store.budgets"
              :key="budget.id"
              class="hover:bg-slate-50/50"
            >
              <td class="px-6 py-4">
                <RouterLink :to="{ name: 'finance-budget-detail', params: { id: budget.id } }" class="font-semibold text-bleu-nuit hover:underline focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 rounded">
                  {{ budget.projet_nom }}
                </RouterLink>
              </td>
              <td class="px-6 py-4 font-semibold text-slate-900">
                {{ formatMontant(budget.montant) }} FCFA
              </td>
              <td class="px-6 py-4 text-slate-600">
                {{ budget.source_financement }}
              </td>
              <td
                class="px-6 py-4 font-bold"
                :class="budget.solde >= 0 ? 'text-emerald-600' : 'text-red-500'"
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
                    class="text-xs text-slate-600 font-medium whitespace-nowrap"
                    >{{ budget.taux_execution }}%</span
                  >
                </div>
              </td>
              <td class="px-6 py-4 text-center">
                <StatusBadge :statut="budget.statut">{{
                  budget.statut
                }}</StatusBadge>
              </td>
              <td class="px-6 py-4 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button
                    @click="openEdit(budget)"
                    class="p-1.5 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition-colors"
                    title="Modifier"
                  >
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button
                    @click="confirmDelete(budget)"
                    class="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Supprimer"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <BudgetFormModal
      v-if="modalOpen"
      :ouvert="modalOpen"
      :erreur-backend="modalError"
      :budget="editingBudget"
      :saving="savingBudget"
      @fermer="
        modalOpen = false;
        modalError = '';
        editingBudget = null;
      "
      @save="saveBudget"
    />

    <!-- Confirmation suppression -->
    <Teleport to="body">
      <div
        v-if="deleteConfirm"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
        @click.self="deleteConfirm = false"
      >
        <div class="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full">
          <div
            class="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center mx-auto mb-4"
          >
            <Trash2 :size="22" class="text-red-600" />
          </div>
          <h3 class="text-center font-bold text-slate-900 mb-2">
            Supprimer le budget
          </h3>
          <p class="text-center text-sm text-slate-500 mb-6">
            Voulez-vous vraiment supprimer le budget du projet
            <strong>{{ budgetToDelete?.projet_nom }}</strong> ? Cette action est
            irréversible.
          </p>
          <div class="flex gap-3">
            <button
              @click="deleteConfirm = false"
              class="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              Annuler
            </button>
            <button
              @click="handleDelete"
              :disabled="deleting"
              class="flex-1 px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm font-semibold transition disabled:opacity-60"
            >
              {{ deleting ? "Suppression..." : "Supprimer" }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { Plus, Wallet, TrendingUp, PiggyBank, Pencil, Trash2 } from "lucide-vue-next";
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js";
import BudgetFormModal from "@/modules/finance/components/budgets/BudgetFormModal.vue";
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { parseApiError } from "@/modules/finance/utils/parseApiError.js";

const store = useFinanceStore();
const modalOpen = ref(false);
const modalError = ref("");
const editingBudget = ref(null);
const savingBudget = ref(false);
const deleteConfirm = ref(false);
const budgetToDelete = ref(null);
const deleting = ref(false);

const formatMontant = (v) => Number(v || 0).toLocaleString("fr-FR");

const totalMontant = computed(() =>
  store.budgets.reduce((s, b) => s + parseFloat(b.montant || 0), 0)
);
const totalSolde = computed(() =>
  store.budgets.reduce((s, b) => s + parseFloat(b.solde || 0), 0)
);

const openEdit = (budget) => {
  editingBudget.value = budget;
  modalOpen.value = true;
};

const confirmDelete = (budget) => {
  budgetToDelete.value = budget;
  deleteConfirm.value = true;
};

const handleDelete = async () => {
  if (!budgetToDelete.value) return;
  deleting.value = true;
  try {
    await store.deleteBudget(budgetToDelete.value.id);
    deleteConfirm.value = false;
    budgetToDelete.value = null;
  } catch (e) {
    // silent
  } finally {
    deleting.value = false;
  }
};

const saveBudget = async (data) => {
  if (savingBudget.value) return;
  modalError.value = "";
  savingBudget.value = true;
  try {
    if (data.id) {
      // Mode édition
      await store.updateBudget(data.id, data);
    } else {
      // Mode création
      await store.createBudget(data);
    }
    modalOpen.value = false;
    editingBudget.value = null;
  } catch (e) {
    modalError.value = parseApiError(e);
  } finally {
    savingBudget.value = false;
  }
};

onMounted(() => store.fetchBudgets());
</script>
