<template>
  <div class="rounded-2xl bg-white border border-[#E5E7EB] shadow-sm overflow-hidden">
    <!-- Header bar -->
    <div v-if="title" class="p-5 border-b border-[#E5E7EB] flex items-center justify-between">
      <div>
        <h3 class="text-base font-bold text-[#021427]">{{ title }}</h3>
        <p v-if="subtitle" class="text-xs text-slate-500 mt-0.5">{{ subtitle }}</p>
      </div>
      <slot name="header-actions" />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="p-8 text-center text-slate-400">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#021427] border-t-transparent mb-2"></div>
      <p class="text-sm">Chargement des transactions...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!transactions || transactions.length === 0" class="p-8 text-center text-slate-400">
      <p class="text-sm font-medium">{{ emptyMessage }}</p>
    </div>

    <div v-else>
      <!-- Mobile View (Card List) -->
      <div class="block lg:hidden divide-y divide-[#E5E7EB]">
        <div
          v-for="tx in transactions"
          :key="tx.id || tx.reference"
          class="p-4 hover:bg-slate-50 transition-colors"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-mono font-bold text-[#021427]">
              {{ tx.reference || 'N/A' }}
            </span>
            <AlertBadge :status="tx.statut || 'APPROUVE'" />
          </div>

          <div class="text-sm font-semibold text-slate-900 mb-1">
            {{ tx.projet_nom || tx.projet?.nom || tx.projet || 'Projet non spécifié' }}
          </div>

          <div class="flex items-center justify-between text-xs text-slate-500 mt-2">
            <span class="inline-flex items-center gap-1 font-medium text-slate-600">
              <span class="w-2 h-2 rounded-full" :class="getTypeBadge(tx.type)"></span>
              {{ tx.type || (tx.bailleur ? 'Don' : 'Dépense') }}
            </span>
            <span>{{ formatDate(tx.date) }}</span>
          </div>

          <div class="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between">
            <span class="text-xs text-slate-500 font-medium">Montant</span>
            <span class="text-base font-bold" :class="tx.type === 'Don' || tx.bailleur ? 'text-emerald-700' : 'text-[#021427]'">
              {{ tx.type === 'Don' || tx.bailleur ? '+' : '-' }}{{ formatCurrency(tx.montant) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Desktop View (Full Table) -->
      <div class="hidden lg:block overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-[#F8FAFC] border-b border-[#E5E7EB] text-xs font-semibold uppercase tracking-wider text-slate-600">
              <th class="py-3.5 px-5">Référence</th>
              <th class="py-3.5 px-5">Projet</th>
              <th class="py-3.5 px-5">Type</th>
              <th class="py-3.5 px-5">Montant</th>
              <th class="py-3.5 px-5">Date</th>
              <th class="py-3.5 px-5">Statut</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#E5E7EB] text-sm">
            <tr
              v-for="tx in transactions"
              :key="tx.id || tx.reference"
              class="hover:bg-slate-50/80 transition-colors"
            >
              <td class="py-4 px-5 font-mono text-xs font-bold text-[#021427]">
                {{ tx.reference || 'N/A' }}
              </td>
              <td class="py-4 px-5 font-medium text-slate-800">
                {{ tx.projet_nom || tx.projet?.nom || tx.projet || 'N/A' }}
              </td>
              <td class="py-4 px-5">
                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                  <span class="w-1.5 h-1.5 rounded-full" :class="getTypeBadge(tx.type || (tx.bailleur ? 'Don' : 'Dépense'))"></span>
                  {{ tx.type || (tx.bailleur ? 'Don' : 'Dépense') }}
                </span>
              </td>
              <td class="py-4 px-5 font-bold" :class="tx.type === 'Don' || tx.bailleur ? 'text-emerald-700' : 'text-[#021427]'">
                {{ tx.type === 'Don' || tx.bailleur ? '+' : '-' }}{{ formatCurrency(tx.montant) }}
              </td>
              <td class="py-4 px-5 text-slate-600 text-xs">
                {{ formatDate(tx.date) }}
              </td>
              <td class="py-4 px-5">
                <AlertBadge :status="tx.statut || 'APPROUVE'" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import AlertBadge from "@/components/finance/AlertBadge.vue"

defineProps({
  title: {
    type: String,
    default: "",
  },
  subtitle: {
    type: String,
    default: "",
  },
  transactions: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  emptyMessage: {
    type: String,
    default: "Aucune transaction enregistrée pour le moment.",
  },
})

const formatCurrency = (val) => {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "XOF",
    maximumFractionDigits: 0,
  }).format(val || 0).replace("XOF", "FCFA")
}

const formatDate = (dateStr) => {
  if (!dateStr) return "N/A"
  try {
    const d = new Date(dateStr)
    return new Intl.DateTimeFormat("fr-FR", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }).format(d)
  } catch {
    return dateStr
  }
}

const getTypeBadge = (typeStr) => {
  const t = String(typeStr || "").toLowerCase()
  if (t.includes("don")) return "bg-emerald-500"
  if (t.includes("dépense") || t.includes("depense")) return "bg-rose-500"
  return "bg-blue-500"
}
</script>
