<template>
  <div class="p-4 sm:p-6 lg:p-8 space-y-6 bg-[#F8FAFC] min-h-screen">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-[#021427] tracking-tight">
          Gestion des Dépenses
        </h1>
        <p class="text-xs sm:text-sm text-slate-600 mt-1">
          Enregistrement des charges, contrôle des pièces et circuit d'approbation.
        </p>
      </div>

      <button
        type="button"
        @click="openAddModal"
        class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#744D03] text-white text-xs sm:text-sm font-semibold hover:bg-[#5c3c02] shadow-md transition cursor-pointer self-start sm:self-auto"
      >
        <Plus class="w-4 h-4" />
        <span>Nouvelle dépense</span>
      </button>
    </div>

    <!-- Filters & Search Bar -->
    <div class="rounded-2xl bg-white p-4 border border-[#E5E7EB] shadow-sm grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 items-center">
      <!-- Search Input -->
      <div class="relative">
        <Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Référence, fournisseur ou libellé..."
          class="w-full pl-10 pr-4 py-2 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
        />
      </div>

      <!-- Category Filter -->
      <div>
        <select
          v-model="selectedCategory"
          class="w-full py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
        >
          <option value="">Toutes les catégories</option>
          <option
            v-for="cat in uniqueCategories"
            :key="cat"
            :value="cat"
          >
            {{ cat }}
          </option>
        </select>
      </div>

      <!-- Region Filter -->
      <div>
        <select
          v-model="selectedRegion"
          class="w-full py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
        >
          <option value="">Toutes les régions</option>
          <option
            v-for="reg in regionsList"
            :key="reg.id || reg"
            :value="reg.id || reg"
          >
            {{ reg.nom || reg.name || reg }}
          </option>
        </select>
      </div>

      <!-- Status Filter -->
      <div>
        <select
          v-model="selectedStatus"
          class="w-full py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
        >
          <option value="">Tous les statuts</option>
          <option value="APPROUVE">Approuvée (Vert)</option>
          <option value="EN_ATTENTE">En attente (Jaune)</option>
          <option value="REJETE">Rejetée (Rouge)</option>
        </select>
      </div>
    </div>

    <!-- Table Container -->
    <div class="rounded-2xl bg-white border border-[#E5E7EB] shadow-sm overflow-hidden">
      <!-- Loading State -->
      <div v-if="financeStore.loading" class="p-12 text-center text-slate-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#021427] border-t-transparent mb-2"></div>
        <p class="text-sm">Chargement des dépenses...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredDepenses.length === 0" class="p-12 text-center text-slate-400">
        <Receipt class="w-12 h-12 mx-auto mb-3 opacity-40 text-[#021427]" />
        <p class="text-base font-semibold text-[#021427]">Aucune dépense trouvée</p>
        <p class="text-xs text-slate-500 mt-1">Ajustez vos filtres ou enregistrez une nouvelle dépense.</p>
      </div>

      <div v-else>
        <!-- Mobile Cards -->
        <div class="block lg:hidden divide-y divide-[#E5E7EB]">
          <div
            v-for="dep in filteredDepenses"
            :key="dep.id || dep.reference"
            class="p-4 space-y-3"
          >
            <div class="flex items-center justify-between">
              <span class="text-xs font-mono font-bold text-[#021427]">{{ dep.reference || 'DEP-REF' }}</span>
              <AlertBadge :status="dep.statut" />
            </div>

            <div class="text-sm font-bold text-slate-900">
              {{ dep.categorie }} - {{ dep.fournisseur || 'Fournisseur N/A' }}
            </div>

            <div class="grid grid-cols-2 gap-2 text-xs text-slate-600">
              <div>
                <span class="text-slate-400 block">Projet</span>
                <span class="font-medium text-slate-800">{{ dep.projet_nom || 'Projet ONG' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block">Région</span>
                <span>{{ dep.region_nom || dep.region || 'N/A' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block">Date</span>
                <span>{{ formatDate(dep.date) }}</span>
              </div>
              <div>
                <span class="text-slate-400 block">Montant</span>
                <span class="font-bold text-rose-600">-{{ formatCurrency(dep.montant) }}</span>
              </div>
            </div>

            <div class="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
              <button
                @click="openUploadModal(dep)"
                class="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-semibold hover:bg-slate-200"
              >
                + Pièce justificative
              </button>
            </div>
          </div>
        </div>

        <!-- Desktop Table -->
        <div class="hidden lg:block overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-[#F8FAFC] border-b border-[#E5E7EB] text-xs font-semibold uppercase tracking-wider text-slate-600">
                <th class="py-3.5 px-5">Référence</th>
                <th class="py-3.5 px-5">Région</th>
                <th class="py-3.5 px-5">Catégorie</th>
                <th class="py-3.5 px-5">Projet</th>
                <th class="py-3.5 px-5">Montant</th>
                <th class="py-3.5 px-5">Fournisseur</th>
                <th class="py-3.5 px-5">Date</th>
                <th class="py-3.5 px-5">Statut</th>
                <th class="py-3.5 px-5 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E5E7EB] text-sm">
              <tr
                v-for="dep in filteredDepenses"
                :key="dep.id || dep.reference"
                class="hover:bg-slate-50/80 transition-colors"
              >
                <td class="py-4 px-5 font-mono text-xs font-bold text-[#021427]">
                  {{ dep.reference || 'N/A' }}
                </td>
                <td class="py-4 px-5 font-medium text-slate-800">
                  {{ dep.region_nom || dep.region || 'N/A' }}
                </td>
                <td class="py-4 px-5 font-semibold text-slate-900">
                  {{ dep.categorie }}
                </td>
                <td class="py-4 px-5 text-slate-700">
                  {{ dep.projet_nom || 'Projet ONG' }}
                </td>
                <td class="py-4 px-5 font-bold text-rose-600">
                  -{{ formatCurrency(dep.montant) }}
                </td>
                <td class="py-4 px-5 text-slate-600">
                  {{ dep.fournisseur || 'N/A' }}
                </td>
                <td class="py-4 px-5 text-slate-600 text-xs">
                  {{ formatDate(dep.date) }}
                </td>
                <td class="py-4 px-5">
                  <AlertBadge :status="dep.statut" />
                </td>
                <td class="py-4 px-5 text-right">
                  <button
                    @click="openUploadModal(dep)"
                    title="Ajouter un justificatif"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-semibold hover:bg-[#021427] hover:text-white transition"
                  >
                    <Paperclip class="w-3.5 h-3.5" />
                    <span>Justificatif</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal: Nouvelle dépense -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 z-50 bg-[#021427]/60 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 border border-[#E5E7EB]">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-lg font-bold text-[#021427]">Enregistrer une nouvelle dépense</h3>
          <button @click="showAddModal = false" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="submitExpense" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Budget / Projet</label>
            <select
              v-model="form.budget"
              required
              class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
            >
              <option value="" disabled>Sélectionner un budget</option>
              <option
                v-for="b in financeStore.budgets"
                :key="b.id"
                :value="b.id"
              >
                {{ b.projet_nom || b.source_financement }} (Solde: {{ formatCurrency(b.solde) }})
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Catégorie</label>
              <input
                v-model="form.categorie"
                type="text"
                placeholder="ex: Achats Vivres, Logistique"
                required
                class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Fournisseur</label>
              <input
                v-model="form.fournisseur"
                type="text"
                placeholder="ex: SENELEC / TotalEnergies"
                class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Région</label>
              <select
                v-model="form.region"
                required
                class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
              >
                <option value="" disabled>Sélectionner une région</option>
                <option
                  v-for="reg in regionsList"
                  :key="reg.id || reg"
                  :value="reg.id || reg"
                >
                  {{ reg.nom || reg.name || reg }}
                </option>
              </select>
            </div>

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
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Date</label>
              <input
                v-model="form.date"
                type="date"
                required
                class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Statut initial</label>
              <select
                v-model="form.statut"
                class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
              >
                <option value="EN_ATTENTE">En attente (Jaune)</option>
                <option value="APPROUVE">Approuvée (Vert)</option>
                <option value="REJETE">Rejetée (Rouge)</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Description / Motif</label>
            <textarea
              v-model="form.description"
              rows="2"
              placeholder="Description détaillée du besoin..."
              class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
            ></textarea>
          </div>

          <div class="pt-4 flex items-center justify-end gap-3 border-t">
            <button
              type="button"
              @click="showAddModal = false"
              class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 text-xs font-semibold"
            >
              Annuler
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="px-5 py-2 rounded-xl bg-[#744D03] text-white text-xs font-semibold hover:bg-[#5c3c02]"
            >
              {{ submitting ? "Enregistrement..." : "Enregistrer la dépense" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Upload Justificatif -->
    <div
      v-if="uploadTargetDepense"
      class="fixed inset-0 z-50 bg-[#021427]/60 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 border border-[#E5E7EB]">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-base font-bold text-[#021427]">Ajouter un justificatif</h3>
          <button @click="uploadTargetDepense = null" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="text-xs text-slate-600 space-y-1">
          <p>Dépense : <strong class="text-[#021427]">{{ uploadTargetDepense.reference }}</strong></p>
          <p>Catégorie : {{ uploadTargetDepense.categorie }} | Montant : {{ formatCurrency(uploadTargetDepense.montant) }}</p>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Fichier (PDF ou Image, Max 10Mo)</label>
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            @change="handleFileChange"
            class="w-full text-xs text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-[#021427] file:text-white hover:file:bg-slate-800"
          />
        </div>

        <div class="pt-4 flex items-center justify-end gap-3 border-t">
          <button
            type="button"
            @click="uploadTargetDepense = null"
            class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 text-xs font-semibold"
          >
            Annuler
          </button>
          <button
            type="button"
            @click="submitUpload"
            :disabled="!selectedFile || uploadingJustif"
            class="px-5 py-2 rounded-xl bg-[#744D03] text-white text-xs font-semibold hover:bg-[#5c3c02] disabled:opacity-50"
          >
            {{ uploadingJustif ? "Téléversement..." : "Téléverser" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { Plus, Search, Receipt, Paperclip, X } from "lucide-vue-next"
import { useFinanceStore } from "@/stores/finance.js"
import AlertBadge from "@/components/finance/AlertBadge.vue"
import financeApi from "@/services/financeApi.js"

const financeStore = useFinanceStore()

const searchQuery = ref("")
const selectedCategory = ref("")
const selectedRegion = ref("")
const selectedStatus = ref("")

const regionsList = ref([
  "Dakar", "Thiès", "Saint-Louis", "Ziguinchor", "Kaolack", "Kolda", "Tambacounda"
])
const showAddModal = ref(false)
const submitting = ref(false)
const uploadTargetDepense = ref(null)
const selectedFile = ref(null)
const uploadingJustif = ref(false)

const form = ref({
  budget: "",
  categorie: "",
  fournisseur: "",
  region: "Dakar",
  montant: 0,
  date: new Date().toISOString().substring(0, 10),
  statut: "EN_ATTENTE",
  description: "",
})

onMounted(async () => {
  await Promise.all([
    financeStore.fetchExpenses(),
    financeStore.fetchBudgets(),
  ])
  try {
    const filtersRes = await financeApi.getReportFilters()
    if (filtersRes.data?.regions) {
      regionsList.value = filtersRes.data.regions
    }
  } catch {
    // optional fallback
  }
})

const uniqueCategories = computed(() => {
  const set = new Set()
  ;(financeStore.depenses || []).forEach((d) => {
    if (d.categorie) set.add(d.categorie)
  })
  return Array.from(set).sort()
})

const filteredDepenses = computed(() => {
  return (financeStore.depenses || []).filter((d) => {
    const ref = String(d.reference || "").toLowerCase()
    const four = String(d.fournisseur || "").toLowerCase()
    const cat = String(d.categorie || "").toLowerCase()
    const q = searchQuery.value.toLowerCase()

    const matchesSearch = !q || ref.includes(q) || four.includes(q) || cat.includes(q)
    const matchesCat = !selectedCategory.value || d.categorie === selectedCategory.value
    const matchesReg = !selectedRegion.value || String(d.region) === String(selectedRegion.value)
    const matchesStat = !selectedStatus.value || String(d.statut).toUpperCase() === String(selectedStatus.value).toUpperCase()

    return matchesSearch && matchesCat && matchesReg && matchesStat
  })
})

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

const openAddModal = () => {
  form.value = {
    budget: financeStore.budgets[0]?.id || "",
    categorie: "",
    fournisseur: "",
    region: regionsList.value[0]?.id || regionsList.value[0] || "Dakar",
    montant: 0,
    date: new Date().toISOString().substring(0, 10),
    statut: "EN_ATTENTE",
    description: "",
  }
  showAddModal.value = true
}

const submitExpense = async () => {
  submitting.value = true
  try {
    await financeStore.addExpense(form.value)
    showAddModal.value = false
  } catch {
    alert("Erreur lors de l'enregistrement de la dépense.")
  } finally {
    submitting.value = false
  }
}

const openUploadModal = (dep) => {
  uploadTargetDepense.value = dep
  selectedFile.value = null
}

const handleFileChange = (e) => {
  if (e.target.files?.length > 0) {
    selectedFile.value = e.target.files[0]
  }
}

const submitUpload = async () => {
  if (!selectedFile.value || !uploadTargetDepense.value) return
  uploadingJustif.value = true
  try {
    await financeStore.addJustification(uploadTargetDepense.value.id, selectedFile.value)
    alert("Pièce justificative ajoutée avec succès.")
    uploadTargetDepense.value = null
  } catch {
    alert("Erreur lors de l'envoi du fichier.")
  } finally {
    uploadingJustif.value = false
  }
}
</script>
