<template>
  <div class="self-stretch p-6 bg-white flex flex-col justify-start items-start gap-4">
    <!-- Header -->
    <div class="self-stretch pb-3 inline-flex justify-between items-center">
      <div class="self-stretch flex flex-col justify-start items-start gap-0.5">
        <div class="text-slate-900 text-base font-bold font-['Inter'] leading-6">
          Trajectoire budgétaire et dépenses (2026)
        </div>
        <div class="text-zinc-500 text-xs font-normal font-['Inter'] leading-4">
          Suivi cumulé mensuel des dépenses et du budget alloués (en millions FCFA)
        </div>
      </div>
      <div class="flex justify-start items-center gap-2">
        <div class="px-4 py-2 bg-bleu-nuit flex justify-start items-center gap-1 rounded-lg">
          <div class="w-3 h-3 bg-white"></div>
          <div class="text-center text-white text-sm font-semibold font-['Inter'] leading-5">
            Exporter arrêté
          </div>
        </div>
      </div>
    </div>

    <!-- Chart -->
    <div class="self-stretch h-96 relative">
      <div class="w-[880px] p-6 left-0 top-0 absolute bg-white inline-flex flex-col justify-start items-start gap-14">
        <div class="self-stretch flex flex-col justify-start items-start gap-4">
          <!-- Chart header -->
          <div class="self-stretch inline-flex justify-between items-center">
            <div class="self-stretch flex flex-col justify-start items-start gap-0.5">
              <div class="text-slate-700 text-sm font-bold font-['Inter'] uppercase leading-5 tracking-wide">
                TRAJECTOIRE BUDGETAIRE ET DEPENSES
              </div>
              <div class="text-gray-500 text-xs font-normal font-['Inter'] leading-4">
                Progression mensuelle cumulée sur les 6 derniers mois (2025)
              </div>
            </div>
            <div class="flex justify-start items-center">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-bleu-nuit"></div>
                <span class="text-slate-600 text-xs font-['Inter']">Budget</span>
              </div>
              <div class="ml-4 flex items-center gap-2">
                <div class="w-3 h-3 bg-or"></div>
                <span class="text-slate-600 text-xs font-['Inter']">Dépenses</span>
              </div>
            </div>
          </div>

          <!-- Chart bars -->
          <div class="self-stretch h-64 flex flex-col justify-center items-start">
            <div class="self-stretch flex-1 relative overflow-hidden">
              <!-- Grid lines -->
              <div
                v-for="i in 5"
                :key="`grid-${i}`"
                class="absolute left-0 right-0 outline outline-1 outline-offset-[-0.51px] outline-slate-100"
                :style="{ top: `${i * 20}%` }"
              ></div>

              <!-- Bars -->
              <div class="absolute bottom-0 left-0 right-0 h-full flex items-end justify-between pl-2">
                <div
                  v-for="item in dataMensuelle"
                  :key="item.mois"
                  class="flex items-end gap-1 h-full justify-center flex-1"
                >
                  <div
                    class="w-4 bg-bleu-nuit rounded-t transition-all"
                    :style="{ height: `${item.budget}%` }"
                    :title="`${item.mois} - Budget: ${item.budgetMillions} M FCFA`"
                  ></div>
                  <div
                    class="w-4 bg-or opacity-90 rounded-t transition-all"
                    :style="{ height: `${item.depenses}%` }"
                    :title="`${item.mois} - Dépenses: ${item.depensesMillions} M FCFA`"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Month labels -->
        <div class="self-stretch pt-3 inline-flex justify-center items-start">
          <div
            v-for="item in dataMensuelle"
            :key="item.mois"
            class="w-24 inline-flex flex-col justify-start items-center"
          >
            <div
              class="text-center text-xs font-semibold font-['Inter'] leading-4"
              :class="item.mois === 'Juin' ? 'text-bleu-nuit font-bold' : 'text-gray-500'"
            >
              {{ item.mois }}
            </div>
            <span v-if="item.mois === 'Juin'" class="text-xs text-gray-500 font-['Inter']">(en cours)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="self-stretch pt-3 inline-flex justify-between items-center">
      <div class="text-zinc-500 text-xs font-normal font-['Inter'] leading-4">
        Source : Rapprochements comptables analytiques au 24/10/2026
      </div>
      <div class="flex items-center gap-0.5">
        <div class="text-bleu-nuit text-xs font-semibold font-['Inter'] leading-4 tracking-tight">
          Détail analytique par projet
        </div>
        <div class="w-2 h-1.5 bg-bleu-nuit"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js"

const store = useFinanceStore()

const MONTHS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin"]

const asNumber = (value) => Number(value || 0)

const dataMensuelle = computed(() => {
  const budgets = store.budgets || []
  const depenses = store.depenses || []

  const budgetTotal = budgets.reduce((sum, b) => sum + asNumber(b.budgetTotal), 0)
  const depensesTotal = depenses.reduce((sum, d) => sum + asNumber(d.montant), 0)
  const maxVal = Math.max(budgetTotal, depensesTotal, 1)

  // Aggregate budgets and expenses by month (based on date fields)
  const byMonth = {}
  MONTHS.forEach((m) => {
    byMonth[m] = { budget: 0, depenses: 0 }
  })

  const monthIndex = (value) => {
    if (!value) return -1
    const d = new Date(value)
    if (isNaN(d.getTime())) return -1
    return d.getMonth() // 0-based
  }

  budgets.forEach((b) => {
    const idx = monthIndex(b.date || b.created_at)
    if (idx >= 0 && idx < MONTHS.length) {
      byMonth[MONTHS[idx]].budget += asNumber(b.budgetTotal)
    }
  })

  depenses.forEach((d) => {
    const idx = monthIndex(d.date || d.date_depense || d.created_at)
    if (idx >= 0 && idx < MONTHS.length) {
      byMonth[MONTHS[idx]].depenses += asNumber(d.montant)
    }
  })

  return MONTHS.map((m, i) => {
    const budget = byMonth[m].budget
    const depenses = byMonth[m].depenses
    return {
      mois: m,
      budget: maxVal ? Math.round((budget / maxVal) * 100) : 0,
      depenses: maxVal ? Math.round((depenses / maxVal) * 100) : 0,
      budgetMillions: (budget / 1_000_000).toFixed(1),
      depensesMillions: (depenses / 1_000_000).toFixed(1),
      isCurrent: i === MONTHS.length - 1,
    }
  })
})
</script>