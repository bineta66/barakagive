<template>
  <div class="self-stretch flex flex-col justify-start items-start gap-4">
    <!-- En-tête -->
    <div class="self-stretch inline-flex justify-between items-center">
      <div class="inline-flex flex-col justify-start items-start gap-0.5">
        <div class="text-slate-700 text-sm font-bold uppercase leading-5 tracking-wide">
          EVOLUTION DES PROJETS ET BENEFICIAIRES
        </div>
        <div class="text-gray-500 text-xs font-normal leading-4">
          Progression mensuelle cumulée sur les 6 derniers mois (2025)
        </div>
      </div>

      <!-- Légende -->
      <div class="inline-flex justify-start items-center gap-6">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-bleu-nuit rounded"></div>
          <span class="text-slate-600 text-xs">Projets</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-or rounded"></div>
          <span class="text-slate-600 text-xs">Bénéficiaires (x100)</span>
        </div>
      </div>
    </div>

    <!-- Graphique -->
    <div class="self-stretch h-64 relative">
      <!-- Grille horizontale -->
      <div
        v-for="i in 5"
        :key="`grid-${i}`"
        class="absolute left-0 right-0 border-t border-slate-100"
        :style="{ top: `${i * 20}%` }"
      ></div>

      <!-- Barres -->
      <div class="absolute bottom-0 left-0 right-0 h-full flex items-end justify-between pl-2">
        <div
          v-for="item in dataMensuelle"
          :key="item.mois"
          class="flex items-end gap-1 h-full justify-center flex-1"
        >
          <!-- Barre Projet -->
          <div
            class="w-4 bg-bleu-nuit rounded-t transition-all"
            :style="{ height: `${item.projets}%` }"
            :title="`${item.mois} - Projets: ${item.projetsValue}`"
          ></div>
          <!-- Barre Bénéficiaires -->
          <div
            class="w-4 bg-or opacity-90 rounded-t transition-all"
            :style="{ height: `${item.beneficiaires}%` }"
            :title="`${item.mois} - Bénéficiaires: ${item.beneficiairesValue}`"
          ></div>
        </div>
      </div>
    </div>

    <!-- Labels mensuels -->
    <div class="self-stretch pt-3 inline-flex justify-between items-start">
      <div
        v-for="item in dataMensuelle"
        :key="item.mois"
        class="flex-1 flex justify-center"
      >
        <div class="text-center">
          <div
            class="text-xs font-semibold"
            :class="item.mois === 'Juin' ? 'text-bleu-nuit font-bold' : 'text-gray-500'"
          >
            {{ item.mois }}
          </div>
          <span v-if="item.mois === 'Juin'" class="text-xs text-gray-500">(en cours)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  projects: { type: Array, default: () => [] },
  beneficiaries: { type: Array, default: () => [] },
  fallback: { type: Array, default: null },
})

const MONTHS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin"]

const asNumber = (value) => Number(value || 0)

const monthIndex = (value) => {
  if (!value) return -1
  const d = new Date(value)
  if (isNaN(d.getTime())) return -1
  return d.getMonth()
}

const dataMensuelle = computed(() => {
  const hasReal = props.projects.length || props.beneficiaries.length
  if (!hasReal && props.fallback) {
    return props.fallback.map((item, i) => ({
      ...item,
      isCurrent: i === MONTHS.length - 1,
    }))
  }

  const byMonth = {}
  MONTHS.forEach((m) => { byMonth[m] = { projets: 0, beneficiaires: 0 } })

  props.projects.forEach((p) => {
    const idx = monthIndex(p.created_at || p.date_debut)
    if (idx >= 0 && idx < MONTHS.length) {
      byMonth[MONTHS[idx]].projets += 1
    }
  })

  props.beneficiaries.forEach((b) => {
    const idx = monthIndex(b.created_at)
    if (idx >= 0 && idx < MONTHS.length) {
      byMonth[MONTHS[idx]].beneficiaires += 1
    }
  })

  const maxProjet = Math.max(...MONTHS.map((m) => byMonth[m].projets), 1)
  const maxBen = Math.max(...MONTHS.map((m) => byMonth[m].beneficiaires), 1)

  return MONTHS.map((m, i) => {
    const projets = byMonth[m].projets
    const beneficiaires = byMonth[m].beneficiaires
    return {
      mois: m,
      projets: maxProjet ? Math.round((projets / maxProjet) * 100) : 0,
      beneficiaires: maxBen ? Math.round((beneficiaires / maxBen) * 100) : 0,
      projetsValue: projets,
      beneficiairesValue: beneficiaires,
      isCurrent: i === MONTHS.length - 1,
    }
  })
})
</script>