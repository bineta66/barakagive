<template>
  <div class="self-stretch flex flex-col justify-start items-start gap-4">
    <!-- En-tête -->
    <div class="self-stretch inline-flex justify-between items-center">
      <div class="inline-flex flex-col justify-start items-start gap-0.5">
        <div
          class="text-slate-700 text-sm font-bold uppercase leading-5 tracking-wide"
        >
          EVOLUTION DES PROJETS ET BÉNÉFICIAIRES
        </div>
        <div class="text-gray-500 text-xs font-normal leading-4">
          Progression mensuelle cumulée sur les 6 derniers mois ({{
            currentYear
          }})
        </div>
      </div>

      <!-- Légende -->
      <div class="inline-flex justify-start items-center gap-6">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-green-600 rounded"></div>
          <span class="text-slate-600 text-xs">Projets</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-orange-500 rounded"></div>
          <span class="text-slate-600 text-xs">Bénéficiaires</span>
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
      <div
        class="absolute bottom-0 left-0 right-0 h-full flex items-end justify-between pl-2"
      >
        <div
          v-for="item in dataMensuelle"
          :key="item.mois"
          class="flex items-end gap-1 h-full justify-center flex-1"
        >
          <!-- Barre Projet -->
          <div
            class="w-4 bg-green-600 rounded-t transition-all"
            :style="{ height: `${item.projets}%` }"
            :title="`${item.mois} ${currentYear} - Projets: ${item.projetsValue}`"
          ></div>
          <!-- Barre Bénéficiaires -->
          <div
            class="w-4 bg-orange-500/90 rounded-t transition-all"
            :style="{ height: `${item.beneficiaires}%` }"
            :title="`${item.mois} ${currentYear} - Bénéficiaires: ${item.beneficiairesValue}`"
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
            :class="
              item.isCurrent ? 'text-bleu-nuit font-bold' : 'text-gray-500'
            "
          >
            {{ item.mois }}
          </div>
          <span v-if="item.isCurrent" class="text-xs text-gray-500"
            >(en cours)</span
          >
        </div>
      </div>
    </div>

    <!-- Message si pas de données -->
    <div v-if="!hasData" class="text-center py-8 text-gray-400 text-sm">
      Aucune donnée disponible pour les 6 derniers mois
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  projects: { type: Array, default: () => [] },
  beneficiaries: { type: Array, default: () => [] },
  fallback: { type: Array, default: null },
});

const MONTHS = [
  "Janvier",
  "Février",
  "Mars",
  "Avril",
  "Mai",
  "Juin",
  "Juillet",
  "Août",
  "Septembre",
  "Octobre",
  "Novembre",
  "Décembre",
];

// Année dynamique basée sur la date actuelle
const currentYear = new Date().getFullYear();

// Obtenir les 6 derniers mois dynamiquement
const getLast6Months = () => {
  const now = new Date();
  const months = [];
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    months.push({
      index: d.getMonth(),
      name: MONTHS[d.getMonth()],
      year: d.getFullYear(),
      date: d,
    });
  }
  return months;
};

const last6Months = getLast6Months();

const currentMonthIndex = computed(() => {
  return new Date().getMonth();
});

const asNumber = (value) => Number(value || 0);

// Parser la date de manière robuste
const parseDate = (value) => {
  if (!value) return null;
  const d = new Date(value);
  if (isNaN(d.getTime())) return null;
  return d;
};

const monthIndex = (value) => {
  const d = parseDate(value);
  if (!d) return -1;
  return d.getMonth();
};

const getYear = (value) => {
  const d = parseDate(value);
  if (!d) return -1;
  return d.getFullYear();
};

const hasData = computed(() => {
  return props.projects.length > 0 || props.beneficiaries.length > 0;
});

const dataMensuelle = computed(() => {
  // Si pas de données réelles et fallback disponible
  const hasReal = props.projects.length || props.beneficiaries.length;
  if (!hasReal && props.fallback) {
    return props.fallback.map((item, i) => ({
      ...item,
      isCurrent: i === last6Months.length - 1,
    }));
  }

  // Initialiser le compteur par mois
  const byMonth = {};
  last6Months.forEach((m) => {
    const key = `${m.name}`;
    byMonth[key] = { projets: 0, beneficiaires: 0 };
  });

  // Compter les projets par mois
  props.projects.forEach((p) => {
    const idx = monthIndex(p.created_at || p.date_debut);
    const year = getYear(p.created_at || p.date_debut);

    // Trouver le mois correspondant dans les 6 derniers mois
    const matchingMonth = last6Months.find(
      (m) => m.index === idx && m.year === year
    );
    if (matchingMonth) {
      byMonth[matchingMonth.name].projets += 1;
    }
  });

  // Compter les bénéficiaires par mois
  props.beneficiaries.forEach((b) => {
    const idx = monthIndex(b.created_at);
    const year = getYear(b.created_at);

    const matchingMonth = last6Months.find(
      (m) => m.index === idx && m.year === year
    );
    if (matchingMonth) {
      byMonth[matchingMonth.name].beneficiaires += 1;
    }
  });

  // Calculer les pourcentages pour l'affichage
  const projetCounts = last6Months.map((m) => byMonth[m.name].projets);
  const benCounts = last6Months.map((m) => byMonth[m.name].beneficiaires);

  const maxProjet = Math.max(...projetCounts, 1);
  const maxBen = Math.max(...benCounts, 1);

  return last6Months.map((m, i) => {
    const projets = byMonth[m.name].projets;
    const beneficiaires = byMonth[m.name].beneficiaires;
    return {
      mois: m.name,
      projets: maxProjet ? Math.round((projets / maxProjet) * 100) : 0,
      beneficiaires: maxBen ? Math.round((beneficiaires / maxBen) * 100) : 0,
      projetsValue: projets,
      beneficiairesValue: beneficiaires,
      isCurrent: i === last6Months.length - 1,
    };
  });
});
</script>
