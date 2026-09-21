<template>
  <div class="p-4 sm:p-6 lg:p-8 space-y-6 bg-[#F8FAFC] min-h-screen">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-[#021427] tracking-tight">
          Gestion des Budgets
        </h1>
        <p class="text-xs sm:text-sm text-slate-600 mt-1">
          Planification, suivi de l'exécution budgétaire et allocation par projet.
        </p>
      </div>

      <button
        type="button"
        @click="openCreateModal"
        class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#744D03] text-white text-xs sm:text-sm font-semibold hover:bg-[#5c3c02] shadow-md transition cursor-pointer self-start sm:self-auto"
      >
        <Plus class="w-4 h-4" />
        <span>Créer un budget</span>
      </button>
    </div>

    <!-- Filters & Search Bar -->
    <div class="rounded-2xl bg-white p-4 border border-[#E5E7EB] shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
      <!-- Search Input -->
      <div class="relative w-full md:w-80">
        <Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Rechercher par source ou projet..."
          class="w-full pl-10 pr-4 py-2 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
        />
      </div>

      <!-- Project Filter -->
      <div class="flex items-center gap-3 w-full md:w-auto">
        <label class="text-xs font-semibold text-slate-600 whitespace-nowrap">Projet :</label>
        <select
          v-model="selectedProjet"
          class="w-full md:w-64 py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
        >
          <option value="">Tous les projets</option>
          <option
            v-for="p in projectsList"
            :key="p.id"
            :value="p.id"
          >
            {{ p.nom || p.name || p.code }}
          </option>
        </select>
      </div>
    </div>

    <!-- Table Container -->
    <div class="rounded-2xl bg-white border border-[#E5E7EB] shadow-sm overflow-hidden">
      <!-- Loading State -->
      <div v-if="financeStore.loading" class="p-12 text-center text-slate-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#021427] border-t-transparent mb-2"></div>
        <p class="text-sm">Chargement de la liste des budgets...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredBudgets.length === 0" class="p-12 text-center text-slate-400">
        <FolderKanban class="w-12 h-12 mx-auto mb-3 opacity-40 text-[#021427]" />
        <p class="text-base font-semibold text-[#021427]">Aucun budget trouvé</p>
        <p class="text-xs text-slate-500 mt-1">Essayez d'ajuster vos filtres de recherche ou créez un nouveau budget.</p>
      </div>

      <div v-else>
        <!-- Mobile Cards -->
        <div class="block lg:hidden divide-y divide-[#E5E7EB]">
          <div
            v-for="budget in filteredBudgets"
            :key="budget.id"
            class="p-4 space-y-3"
          >
            <div class="flex items-center justify-between">
              <span class="text-sm font-bold text-[#021427]">
                {{ budget.projet_nom || getProjectName(budget.projet) }}
              </span>
              <AlertBadge :status="budget.statut" />
            </div>

            <div class="grid grid-cols-2 gap-2 text-xs text-slate-600">
              <div>
                <span class="text-slate-400 block">Source</span>
                <span class="font-medium text-slate-800">{{ budget.source_financement }}</span>
              </div>
              <div>
                <span class="text-slate-400 block">Date</span>
                <span>{{ formatDate(budget.date) }}</span>
              </div>
              <div>
                <span class="text-slate-400 block">Montant</span>
                <span class="font-bold text-[#021427]">{{ formatCurrency(budget.montant) }}</span>
              </div>
              <div>
                <span class="text-slate-400 block">Solde</span>
                <span class="font-bold text-emerald-700">{{ formatCurrency(budget.solde) }}</span>
              </div>
            </div>

            <div class="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
              <button
                @click="viewBudget(budget)"
                class="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-semibold hover:bg-slate-200"
              >
                Consulter
              </button>
              <button
                @click="openEditModal(budget)"
                class="px-3 py-1.5 rounded-lg bg-amber-50 text-[#744D03] text-xs font-semibold hover:bg-amber-100"
              >
                Modifier
              </button>
              <button
                v-if="budget.statut !== 'CLOTURE'"
                @click="confirmCloseBudget(budget)"
                class="px-3 py-1.5 rounded-lg bg-rose-50 text-rose-700 text-xs font-semibold hover:bg-rose-100"
              >
                Clôturer
              </button>
            </div>
          </div>
        </div>

        <!-- Desktop Table -->
        <div class="hidden lg:block overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-[#F8FAFC] border-b border-[#E5E7EB] text-xs font-semibold uppercase tracking-wider text-slate-600">
                <th class="py-3.5 px-5">Projet</th>
                <th class="py-3.5 px-5">Source</th>
                <th class="py-3.5 px-5">Montant</th>
                <th class="py-3.5 px-5">Solde</th>
                <th class="py-3.5 px-5">Taux Exéc.</th>
                <th class="py-3.5 px-5">Statut</th>
                <th class="py-3.5 px-5">Date</th>
                <th class="py-3.5 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E5E7EB] text-sm">
              <tr
                v-for="budget in filteredBudgets"
                :key="budget.id"
                class="hover:bg-slate-50/80 transition-colors"
              >
                <td class="py-4 px-5 font-bold text-[#021427]">
                  {{ budget.projet_nom || getProjectName(budget.projet) }}
                </td>
                <td class="py-4 px-5 text-slate-700 font-medium">
                  {{ budget.source_financement }}
                </td>
                <td class="py-4 px-5 font-bold text-[#021427]">
                  {{ formatCurrency(budget.montant) }}
                </td>
                <td class="py-4 px-5 font-bold text-emerald-700">
                  {{ formatCurrency(budget.solde) }}
                </td>
                <td class="py-4 px-5">
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-800">
                    {{ budget.taux_execution || 0 }}%
                  </span>
                </td>
                <td class="py-4 px-5">
                  <AlertBadge :status="budget.statut" />
                </td>
                <td class="py-4 px-5 text-slate-600 text-xs">
                  {{ formatDate(budget.date) }}
                </td>
                <td class="py-4 px-5 text-right space-x-2">
                  <button
                    @click="viewBudget(budget)"
                    title="Consulter"
                    class="p-1.5 rounded-lg text-slate-600 hover:text-[#021427] hover:bg-slate-100"
                  >
                    <Eye class="w-4 h-4" />
                  </button>
                  <button
                    @click="openEditModal(budget)"
                    title="Modifier"
                    class="p-1.5 rounded-lg text-[#744D03] hover:bg-amber-50"
                  >
                    <Edit3 class="w-4 h-4" />
                  </button>
                  <button
                    v-if="budget.statut !== 'CLOTURE'"
                    @click="confirmCloseBudget(budget)"
                    title="Clôturer"
                    class="p-1.5 rounded-lg text-rose-600 hover:bg-rose-50"
                  >
                    <Lock class="w-4 h-4" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal: Créer / Modifier un Budget -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 bg-[#021427]/60 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 border border-[#E5E7EB]">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-lg font-bold text-[#021427]">
            {{ isEditing ? "Modifier le budget" : "Créer un nouveau budget" }}
          </h3>
          <button @click="showModal = false" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="submitForm" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Projet</label>
            <select
              v-model="form.projet"
              required
              class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
            >
              <option value="" disabled>Sélectionner un projet</option>
              <option
                v-for="p in projectsList"
                :key="p.id"
                :value="p.id"
              >
                {{ p.nom || p.name || p.code }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Source de financement</label>
            <input
              v-model="form.source_financement"
              type="text"
              placeholder="ex: Union Européenne / Banque Mondiale"
              required
              class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Montant (FCFA)</label>
              <input
                v-model.number="form.montant"
                type="number"
                min="1"
                required
                class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Date</label>
              <input
                v-model="form.date"
                type="date"
                required
                class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Statut</label>
            <select
              v-model="form.statut"
              class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
            >
              <option value="BROUILLON">Brouillon</option>
              <option value="EN_COURS">En cours</option>
              <option value="APPROUVE">Approuvé</option>
              <option value="CLOTURE">Clôturé</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Observation</label>
            <textarea
              v-model="form.observation"
              rows="3"
              placeholder="Remarques et détails complémentaires..."
              class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
            ></textarea>
          </div>

          <div class="pt-4 flex items-center justify-end gap-3 border-t">
            <button
              type="button"
              @click="showModal = false"
              class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 text-xs font-semibold"
            >
              Annuler
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="px-5 py-2 rounded-xl bg-[#744D03] text-white text-xs font-semibold hover:bg-[#5c3c02]"
            >
              {{ submitting ? "Enregistrement..." : (isEditing ? "Mettre à jour" : "Enregistrer") }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Detail Consultation -->
    <div
      v-if="selectedBudgetDetail"
      class="fixed inset-0 z-50 bg-[#021427]/60 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 border border-[#E5E7EB]">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-base font-bold text-[#021427]">Détails du Budget</h3>
          <button @click="selectedBudgetDetail = null" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="space-y-3 text-xs sm:text-sm">
          <div class="flex justify-between py-1 border-b">
            <span class="text-slate-500">Projet</span>
            <span class="font-bold text-[#021427]">{{ selectedBudgetDetail.projet_nom || getProjectName(selectedBudgetDetail.projet) }}</span>
          </div>
          <div class="flex justify-between py-1 border-b">
            <span class="text-slate-500">Source</span>
            <span class="font-medium text-slate-800">{{ selectedBudgetDetail.source_financement }}</span>
          </div>
          <div class="flex justify-between py-1 border-b">
            <span class="text-slate-500">Montant Initial</span>
            <span class="font-bold text-[#021427]">{{ formatCurrency(selectedBudgetDetail.montant) }}</span>
          </div>
          <div class="flex justify-between py-1 border-b">
            <span class="text-slate-500">Solde Disponible</span>
            <span class="font-bold text-emerald-700">{{ formatCurrency(selectedBudgetDetail.solde) }}</span>
          </div>
          <div class="flex justify-between py-1 border-b">
            <span class="text-slate-500">Taux d'exécution</span>
            <span class="font-bold text-purple-700">{{ selectedBudgetDetail.taux_execution || 0 }}%</span>
          </div>
          <div class="flex justify-between py-1 border-b">
            <span class="text-slate-500">Statut</span>
            <AlertBadge :status="selectedBudgetDetail.statut" />
          </div>
          <div class="flex justify-between py-1 border-b">
            <span class="text-slate-500">Date d'effet</span>
            <span>{{ formatDate(selectedBudgetDetail.date) }}</span>
          </div>
          <div v-if="selectedBudgetDetail.observation" class="pt-2">
            <span class="text-slate-500 block mb-1">Observation</span>
            <p class="p-2.5 bg-slate-50 rounded-xl text-slate-700 text-xs italic">{{ selectedBudgetDetail.observation }}</p>
          </div>
        </div>

        <div class="pt-3 text-right">
          <button
            @click="selectedBudgetDetail = null"
            class="px-5 py-2 rounded-xl bg-[#021427] text-white text-xs font-semibold"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { Plus, Search, FolderKanban, Eye, Edit3, Lock, X } from "lucide-vue-next"
import { useFinanceStore } from "@/stores/finance.js"
import AlertBadge from "@/components/finance/AlertBadge.vue"
import financeApi from "@/services/financeApi.js"

const financeStore = useFinanceStore()

const searchQuery = ref("")
const selectedProjet = ref("")
const projectsList = ref([])

const showModal = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const activeBudgetId = ref(null)
const selectedBudgetDetail = ref(null)

const form = ref({
  projet: "",
  source_financement: "",
  montant: 0,
  date: new Date().toISOString().substring(0, 10),
  statut: "EN_COURS",
  observation: "",
})

onMounted(async () => {
  await financeStore.fetchBudgets()
  try {
    const res = await financeApi.getProjects()
    projectsList.value = Array.isArray(res.data) ? res.data : res.data.results || []
  } catch {
    // fallback project options
  }
})

const filteredBudgets = computed(() => {
  return (financeStore.budgets || []).filter((b) => {
    const projName = String(b.projet_nom || getProjectName(b.projet) || "").toLowerCase()
    const source = String(b.source_financement || "").toLowerCase()
    const q = searchQuery.value.toLowerCase()

    const matchesSearch = !q || projName.includes(q) || source.includes(q)
    const matchesProjet = !selectedProjet.value || String(b.projet) === String(selectedProjet.value)

    return matchesSearch && matchesProjet
  })
})

const getProjectName = (projId) => {
  const found = projectsList.value.find((p) => String(p.id) === String(projId))
  return found ? (found.nom || found.name || found.code) : "Projet"
}

const formatCurrency = (val) => {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "XOF",
    maximumFractionDigits: 0,
  }).format(val || 0).replace("XOF", "FCFA")
}

const formatDate = (d) => {
  if (!d) return "N/A"
  return new Date(d).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" })
}

const openCreateModal = () => {
  isEditing.value = false
  activeBudgetId.value = null
  form.value = {
    projet: projectsList.value[0]?.id || "",
    source_financement: "",
    montant: 0,
    date: new Date().toISOString().substring(0, 10),
    statut: "EN_COURS",
    observation: "",
  }
  showModal.value = true
}

const openEditModal = (budget) => {
  isEditing.value = true
  activeBudgetId.value = budget.id
  form.value = {
    projet: budget.projet,
    source_financement: budget.source_financement,
    montant: Number(budget.montant) || 0,
    date: budget.date,
    statut: budget.statut || "EN_COURS",
    observation: budget.observation || "",
  }
  showModal.value = true
}

const viewBudget = (budget) => {
  selectedBudgetDetail.value = budget
}

const confirmCloseBudget = async (budget) => {
  if (confirm(`Voulez-vous vraiment clôturer le budget pour ${budget.projet_nom || 'ce projet'} ?`)) {
    await financeStore.cloturerBudget(budget.id)
  }
}

const submitForm = async () => {
  submitting.value = true
  try {
    if (isEditing.value && activeBudgetId.value) {
      await financeStore.updateBudget(activeBudgetId.value, form.value)
    } else {
      await financeStore.addBudget(form.value)
    }
    showModal.value = false
  } catch {
    alert("Une erreur s'est produite lors de l'enregistrement.")
  } finally {
    submitting.value = false
  }
}
</script>
