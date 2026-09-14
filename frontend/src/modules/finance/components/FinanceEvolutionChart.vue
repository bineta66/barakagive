<template>
  <div class="self-stretch p-6 bg-white flex flex-col justify-start items-start gap-4">
    <!-- Header -->
    <div class="self-stretch pb-3 inline-flex justify-between items-center">
      <div class="self-stretch flex flex-col justify-start items-start gap-0.5">
        <div class="text-slate-900 text-base font-bold font-['Inter'] leading-6">
          Trajectoire budgÃ©taire et dÃ©penses (2026)
        </div>
        <div class="text-zinc-500 text-xs font-normal font-['Inter'] leading-4">
          Suivi cumulÃ© mensuel des dÃ©penses et du budget allouÃ©s (en millions FCFA)
        </div>
      </div>
      <div class="flex justify-start items-center gap-2">
        <div class="px-4 py-2 bg-bleu-nuit flex justify-start items-center gap-1 rounded-lg">
          <div class="w-3 h-3 bg-white"></div>
          <div class="text-center text-white text-sm font-semibold font-['Inter'] leading-5">
            Exporter arrÃªtÃ©
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
                TRAJECTOIRE BUDGÃ‰TAIRE ET DÃ‰PENSES
              </div>
              <div class="text-gray-500 text-xs font-normal font-['Inter'] leading-4">
                Progression mensuelle cumulÃ©e sur les 6 derniers mois (2025)
              </div>
            </div>
            <div class="flex justify-start items-center">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-bleu-nuit"></div>
                <span class="text-slate-600 text-xs font-['Inter']">Budget</span>
              </div>
              <div class="ml-4 flex items-center gap-2">
                <div class="w-3 h-3 bg-or"></div>
                <span class="text-slate-600 text-xs font-['Inter']">DÃ©penses</span>
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
                    :title="`${item.mois} - DÃ©penses: ${item.depensesMillions} M FCFA`"
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
          DÃ©tail analytique par projet
        </div>
        <div class="w-2 h-1.5 bg-bleu-nuit"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"

const dataMensuelle = ref([
  { mois: "Janvier", budget: 40, depenses: 33, budgetMillions: 30, depensesMillions: 25 },
  { mois: "FÃ©vrier", budget: 67, depenses: 51, budgetMillions: 50, depensesMillions: 38 },
  { mois: "Mars", budget: 73, depenses: 56, budgetMillions: 55, depensesMillions: 42 },
  { mois: "Avril", budget: 80, depenses: 69, budgetMillions: 60, depensesMillions: 52 },
  { mois: "Mai", budget: 100, depenses: 77, budgetMillions: 75, depensesMillions: 58 },
  { mois: "Juin", budget: 100, depenses: 12, budgetMillions: 75, depensesMillions: 9.25 },
])
</script>

