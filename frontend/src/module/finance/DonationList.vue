<template>
  <div class="p-4 sm:p-6 lg:p-8 space-y-6 bg-[#F8FAFC] min-h-screen">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-[#021427] tracking-tight">
          Gestion des Dons & Financements
        </h1>
        <p class="text-xs sm:text-sm text-slate-600 mt-1">
          Suivi des subventions, dons institutionnels, privés et des modes de paiement.
        </p>
      </div>

      <button
        type="button"
        @click="openAddModal"
        class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#744D03] text-white text-xs sm:text-sm font-semibold hover:bg-[#5c3c02] shadow-md transition cursor-pointer self-start sm:self-auto"
      >
        <Plus class="w-4 h-4" />
        <span>Ajouter un don</span>
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
          placeholder="Référence, bailleur ou projet..."
          class="w-full pl-10 pr-4 py-2 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
        />
      </div>

      <!-- Bailleur Filter -->
      <div>
        <select
          v-model="selectedBailleur"
          class="w-full py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
        >
          <option value="">Tous les bailleurs</option>
          <option
            v-for="b in uniqueBailleurs"
            :key="b"
            :value="b"
          >
            {{ b }}
          </option>
        </select>
      </div>

      <!-- Start Date Filter -->
      <div>
        <input
          v-model="startDate"
          type="date"
          class="w-full py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
          title="Date de début"
        />
      </div>

      <!-- End Date Filter -->
      <div>
        <input
          v-model="endDate"
          type="date"
          class="w-full py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
          title="Date de fin"
        />
      </div>
    </div>

    <!-- Table Container -->
    <div class="rounded-2xl bg-white border border-[#E5E7EB] shadow-sm overflow-hidden">
      <!-- Loading State -->
      <div v-if="financeStore.loading" class="p-12 text-center text-slate-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#021427] border-t-transparent mb-2"></div>
        <p class="text-sm">Chargement des dons...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredDons.length === 0" class="p-12 text-center text-slate-400">
        <Banknote class="w-12 h-12 mx-auto mb-3 opacity-40 text-[#021427]" />
        <p class="text-base font-semibold text-[#021427]">Aucun don enregistré</p>
        <p class="text-xs text-slate-500 mt-1">Ajustez les filtres ou enregistrez un don pour cette période.</p>
      </div>

      <div v-else>
        <!-- Mobile Cards -->
        <div class="block lg:hidden divide-y divide-[#E5E7EB]">
          <div
            v-for="don in filteredDons"
            :key="don.id || don.reference"
            class="p-4 space-y-3"
          >
            <div class="flex items-center justify-between">
              <span class="text-xs font-mono font-bold text-[#021427]">{{ don.reference || 'DON-REF' }}</span>
              <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
                {{ formatPaymentMethod(don.moyen_paiement) }}
              </span>
            </div>

            <div class="text-sm font-bold text-slate-900">
              {{ don.bailleur }}
            </div>

            <div class="grid grid-cols-2 gap-2 text-xs text-slate-600">
              <div>
                <span class="text-slate-400 block">Projet</span>
                <span class="font-medium text-slate-800">{{ don.projet_nom || don.budget_source || 'N/A' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block">Campagne</span>
                <span>{{ don.campagne_nom || 'N/A' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block">Date</span>
                <span>{{ formatDate(don.date) }}</span>
              </div>
              <div>
                <span class="text-slate-400 block">Montant</span>
                <span class="font-bold text-emerald-700">+{{ formatCurrency(don.montant) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Desktop Table -->
        <div class="hidden lg:block overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-[#F8FAFC] border-b border-[#E5E7EB] text-xs font-semibold uppercase tracking-wider text-slate-600">
                <th class="py-3.5 px-5">Référence</th>
                <th class="py-3.5 px-5">Bailleur</th>
                <th class="py-3.5 px-5">Projet</th>
                <th class="py-3.5 px-5">Campagne</th>
                <th class="py-3.5 px-5">Montant</th>
                <th class="py-3.5 px-5">Paiement</th>
                <th class="py-3.5 px-5">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E5E7EB] text-sm">
              <tr
                v-for="don in filteredDons"
                :key="don.id || don.reference"
                class="hover:bg-slate-50/80 transition-colors"
              >
                <td class="py-4 px-5 font-mono text-xs font-bold text-[#021427]">
                  {{ don.reference || 'N/A' }}
                </td>
                <td class="py-4 px-5 font-bold text-slate-800">
                  {{ don.bailleur }}
                </td>
                <td class="py-4 px-5 font-medium text-slate-700">
                  {{ don.projet_nom || don.budget_source || 'N/A' }}
                </td>
                <td class="py-4 px-5 text-slate-600">
                  {{ don.campagne_nom || 'N/A' }}
                </td>
                <td class="py-4 px-5 font-bold text-emerald-700">
                  +{{ formatCurrency(don.montant) }}
                </td>
                <td class="py-4 px-5">
                  <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
                    <CreditCard class="w-3.5 h-3.5" />
                    {{ formatPaymentMethod(don.moyen_paiement) }}
                  </span>
                </td>
                <td class="py-4 px-5 text-slate-600 text-xs">
                  {{ formatDate(don.date) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal: Ajouter un don -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 bg-[#021427]/60 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 border border-[#E5E7EB]">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-lg font-bold text-[#021427]">Ajouter un nouveau don</h3>
          <button @click="showModal = false" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="submitForm" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Nom du bailleur / Donateur</label>
            <input
              v-model="form.bailleur"
              type="text"
              placeholder="ex: Fondation Bill & Melinda Gates"
              required
              class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Budget / Projet lié</label>
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

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Campagne (Optionnel)</label>
            <select
              v-model="form.campagne"
              class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
            >
              <option value="">Aucune campagne spécifique</option>
              <option
                v-for="c in campaignsList"
                :key="c.id"
                :value="c.id"
              >
                {{ c.nom || c.name || c.code_campagne }}
              </option>
            </select>
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
              <label class="block text-xs font-semibold text-slate-700 mb-1">Mode de paiement</label>
              <select
                v-model="form.moyen_paiement"
                required
                class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
              >
                <option value="VIREMENT">Virement bancaire</option>
                <option value="ESPECE">Espèce</option>
                <option value="CHEQUE">Chèque</option>
                <option value="CARTE">Carte bancaire</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Date de réception</label>
            <input
              v-model="form.date"
              type="date"
              required
              class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Observation</label>
            <textarea
              v-model="form.observation"
              rows="2"
              placeholder="Détails du don..."
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
              {{ submitting ? "Enregistrement..." : "Enregistrer le don" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { Plus, Search, Banknote, CreditCard, X } from "lucide-vue-next"
import { useFinanceStore } from "@/stores/finance.js"
import financeApi from "@/services/financeApi.js"

const financeStore = useFinanceStore()

const searchQuery = ref("")
const selectedBailleur = ref("")
const startDate = ref("")
const endDate = ref("")

const campaignsList = ref([])
const showModal = ref(false)
const submitting = ref(false)

const form = ref({
  bailleur: "",
  budget: "",
  campagne: "",
  montant: 0,
  moyen_paiement: "VIREMENT",
  date: new Date().toISOString().substring(0, 10),
  observation: "",
})

onMounted(async () => {
  await Promise.all([
    financeStore.fetchDonations(),
    financeStore.fetchBudgets(),
  ])
  try {
    const res = await financeApi.getCampaigns()
    campaignsList.value = Array.isArray(res.data) ? res.data : res.data.results || []
  } catch {
    // optional fallback
  }
})

const uniqueBailleurs = computed(() => {
  const set = new Set()
  ;(financeStore.dons || []).forEach((d) => {
    if (d.bailleur) set.add(d.bailleur)
  })
  return Array.from(set).sort()
})

const filteredDons = computed(() => {
  return (financeStore.dons || []).filter((d) => {
    const ref = String(d.reference || "").toLowerCase()
    const bailleur = String(d.bailleur || "").toLowerCase()
    const proj = String(d.projet_nom || d.budget_source || "").toLowerCase()
    const q = searchQuery.value.toLowerCase()

    const matchesSearch = !q || ref.includes(q) || bailleur.includes(q) || proj.includes(q)
    const matchesBailleur = !selectedBailleur.value || d.bailleur === selectedBailleur.value

    let matchesDate = true
    if (startDate.value) {
      matchesDate = matchesDate && new Date(d.date) >= new Date(startDate.value)
    }
    if (endDate.value) {
      matchesDate = matchesDate && new Date(d.date) <= new Date(endDate.value)
    }

    return matchesSearch && matchesBailleur && matchesDate
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

const formatPaymentMethod = (m) => {
  const map = {
    VIREMENT: "Virement",
    ESPECE: "Espèce",
    CHEQUE: "Chèque",
    CARTE: "Carte bancaire",
  }
  return map[m] || m || "Virement"
}

const openAddModal = () => {
  form.value = {
    bailleur: "",
    budget: financeStore.budgets[0]?.id || "",
    campagne: "",
    montant: 0,
    moyen_paiement: "VIREMENT",
    date: new Date().toISOString().substring(0, 10),
    observation: "",
  }
  showModal.value = true
}

const submitForm = async () => {
  submitting.value = true
  try {
    const payload = { ...form.value }
    if (!payload.campagne) delete payload.campagne
    await financeStore.addDonation(payload)
    showModal.value = false
  } catch {
    alert("Une erreur s'est produite lors de l'enregistrement du don.")
  } finally {
    submitting.value = false
  }
}
</script>
