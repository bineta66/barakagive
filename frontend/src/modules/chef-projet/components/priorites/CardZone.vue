<template>
  <div
    class="rounded-xl border transition-all duration-200"
    :class="[
      expanded ? 'border-slate-300 shadow-md' : 'border-slate-200 hover:border-slate-300 hover:shadow-sm',
      cardBgClass,
    ]"
  >
    <!-- En-tête de la zone -->
    <div class="p-4">
      <div class="flex items-start justify-between gap-3">
        <!-- Rang + Infos zone -->
        <div class="flex items-center gap-3 min-w-0">
          <!-- Numéro de rang -->
          <div
            class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-black text-white flex-shrink-0"
            :class="rangBgClass"
          >
            {{ rang }}
          </div>
          <div class="min-w-0">
            <h4 class="text-sm font-bold text-slate-800 leading-tight truncate">{{ zone.nom }}</h4>
            <p class="text-xs text-slate-500 mt-0.5">
              {{ zone.total_beneficiaires }} bénéficiaire{{ zone.total_beneficiaires > 1 ? "s" : "" }}
            </p>
          </div>
        </div>

        <!-- Score + badge -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <span
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold"
            :class="niveauBadgeClass"
          >
            <span class="w-1.5 h-1.5 rounded-full" :class="niveauDotClass"></span>
            {{ zone.niveau }}
          </span>
          <span class="text-xl font-black" :class="scoreTextClass">
            {{ zone.score_moyen }}
            <span class="text-xs font-semibold text-slate-400">/100</span>
          </span>
        </div>
      </div>

      <!-- Barre de progression -->
      <div class="mt-3 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-700"
          :class="progressBarClass"
          :style="{ width: zone.score_moyen + '%' }"
        />
      </div>

      <!-- Actions : Voir les bénéficiaires (redirection tableau) + toggle aperçu -->
      <div class="mt-3 flex items-center gap-2">
        <button
          @click="goToTableau"
          class="flex-1 flex items-center justify-center gap-2 text-xs font-semibold py-2 px-3 rounded-lg transition-all bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md group"
        >
          <Users :size="13" />
          <span>Voir les bénéficiaires ({{ zone.total_beneficiaires }})</span>
          <ArrowRight :size="13" class="group-hover:translate-x-0.5 transition-transform" />
        </button>
        <button
          @click="expanded = !expanded"
          class="p-2 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition-colors flex-shrink-0"
          :title="expanded ? 'Masquer aperçu' : 'Aperçu rapide'"
        >
          <ChevronDown
            :size="14"
            class="transition-transform duration-200"
            :class="expanded ? 'rotate-180' : ''"
          />
        </button>
      </div>
    </div>

    <!-- Liste des bénéficiaires (expandable) -->
    <Transition name="expand">
      <div v-if="expanded" class="border-t border-slate-200 divide-y divide-slate-100">
        <button
          v-for="b in zone.beneficiaires"
          :key="b.id"
          class="w-full text-left px-4 py-3 hover:bg-slate-50 transition-colors flex items-center gap-3 group"
          @click="$emit('voir-beneficiaire', b)"
        >
          <!-- Initiales -->
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
            :class="getScoreBgClass(b.score)"
          >
            {{ getInitiales(b) }}
          </div>

          <!-- Infos bénéficiaire -->
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-slate-800 truncate group-hover:text-blue-700 transition-colors">
              {{ b.nom_complet }}
            </p>
            <p class="text-xs text-slate-500">
              {{ b.sexe === "M" ? "M" : b.sexe === "F" ? "F" : "—" }}
              <template v-if="b.age"> • {{ b.age }} ans</template>
              <template v-if="b.quartier"> • {{ b.quartier }}</template>
            </p>
          </div>

          <!-- Score + niveau -->
          <div class="flex items-center gap-2 flex-shrink-0">
            <span
              class="text-sm font-black"
              :class="getScoreTextClass(b.score)"
            >{{ b.score }}/100</span>
            <span
              class="inline-block w-1.5 h-1.5 rounded-full"
              :class="getScoreBgClass(b.score)"
            ></span>
            <ChevronRight :size="14" class="text-slate-300 group-hover:text-blue-400 transition-colors" />
          </div>
        </button>

        <div v-if="!zone.beneficiaires || zone.beneficiaires.length === 0" class="px-4 py-4 text-center">
          <p class="text-xs text-slate-400 italic">Aucun bénéficiaire dans cette zone.</p>
        </div>

        <!-- Bouton pour voir le tableau complet -->
        <div class="px-4 py-3 bg-slate-50/50">
          <button
            @click="goToTableau"
            class="w-full flex items-center justify-center gap-2 text-xs font-semibold py-2 px-3 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm hover:shadow-md transition-all"
          >
            <TableProperties :size="13" />
            Voir le tableau complet
            <ArrowRight :size="13" />
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { Users, ChevronDown, ChevronRight, TableProperties, ArrowRight } from "lucide-vue-next";

const router = useRouter();

const props = defineProps({
  zone: { type: Object, required: true },
  rang: { type: Number, default: 1 },
});

defineEmits(["voir-beneficiaire"]);

const expanded = ref(false);

function goToTableau() {
  router.push({
    name: "beneficiaires-zone",
    params: { zoneId: props.zone.id },
    query: { nom: props.zone.nom, region: props.zone.region },
  });
}

// ── Helpers couleurs ───────────────────────────────────────────────────────────
function getScoreTextClass(score) {
  if (score >= 80) return "text-red-600";
  if (score >= 60) return "text-orange-500";
  if (score >= 40) return "text-yellow-600";
  return "text-green-600";
}

function getScoreBgClass(score) {
  if (score >= 80) return "bg-red-500";
  if (score >= 60) return "bg-orange-400";
  if (score >= 40) return "bg-yellow-400";
  return "bg-green-500";
}

function getInitiales(b) {
  const p = b.prenom || "";
  const n = b.nom || "";
  return ((p[0] || "") + (n[0] || "")).toUpperCase();
}

// ── Classes dynamiques ─────────────────────────────────────────────────────────
const score = computed(() => props.zone.score_moyen || 0);

const cardBgClass = computed(() => {
  if (!expanded.value) return "bg-white";
  if (score.value >= 80) return "bg-red-50/30";
  if (score.value >= 60) return "bg-orange-50/30";
  if (score.value >= 40) return "bg-yellow-50/30";
  return "bg-green-50/30";
});

const rangBgClass = computed(() => {
  if (score.value >= 80) return "bg-red-500";
  if (score.value >= 60) return "bg-orange-400";
  if (score.value >= 40) return "bg-yellow-400";
  return "bg-green-500";
});

const scoreTextClass = computed(() => getScoreTextClass(score.value));

const niveauBadgeClass = computed(() => {
  if (score.value >= 80) return "bg-red-100 text-red-700";
  if (score.value >= 60) return "bg-orange-100 text-orange-700";
  if (score.value >= 40) return "bg-yellow-100 text-yellow-700";
  return "bg-green-100 text-green-700";
});

const niveauDotClass = computed(() => getScoreBgClass(score.value));

const progressBarClass = computed(() => {
  if (score.value >= 80) return "bg-red-500";
  if (score.value >= 60) return "bg-orange-400";
  if (score.value >= 40) return "bg-yellow-400";
  return "bg-green-500";
});
</script>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}
.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 800px;
}
</style>
