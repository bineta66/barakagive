<template>
  <!-- Overlay backdrop -->
  <Transition name="backdrop">
    <div
      v-if="ouvert"
      class="fixed inset-0 z-30 bg-slate-900/30 backdrop-blur-sm"
      @click="$emit('fermer')"
    />
  </Transition>

  <!-- Drawer panel -->
  <Transition name="drawer-slide">
    <aside
      v-if="ouvert"
      class="fixed right-0 top-0 z-40 h-screen w-full max-w-xl bg-white shadow-2xl flex flex-col overflow-hidden"
    >
      <!-- Header du drawer -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-white flex-shrink-0">
        <div class="flex items-center gap-3">
          <div
            class="w-9 h-9 rounded-xl flex items-center justify-center"
            :class="headerBadgeClass"
          >
            <MapPin :size="18" class="text-white" />
          </div>
          <div>
            <h2 class="text-lg font-bold text-slate-800 leading-tight">
              {{ region || "Région" }}
            </h2>
            <p v-if="detail" class="text-xs text-slate-500">
              {{ detail.total_beneficiaires }} bénéficiaire{{ detail.total_beneficiaires > 1 ? "s" : "" }}
              &bull; {{ detail.zones?.length || 0 }} zone{{ (detail.zones?.length || 0) > 1 ? "s" : "" }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span
            v-if="detail"
            class="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold"
            :class="scoreBadgeClass"
          >
            <span class="w-1.5 h-1.5 rounded-full" :class="scoreDotClass"></span>
            {{ detail.score_region }}/100
          </span>
          <button
            @click="$emit('fermer')"
            class="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
          >
            <X :size="16" />
          </button>
        </div>
      </div>

      <!-- Contenu scrollable -->
      <div class="flex-1 overflow-y-auto">

        <!-- État de chargement -->
        <div v-if="chargement" class="flex flex-col items-center justify-center py-20 gap-3">
          <div class="w-10 h-10 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
          <p class="text-sm text-slate-500">Chargement des données...</p>
        </div>

        <!-- Contenu chargé -->
        <div v-else-if="detail" class="px-6 py-5 space-y-5">

          <!-- Score région -->
          <div
            class="rounded-xl p-4 border flex items-center gap-4"
            :class="scoreCardClass"
          >
            <div class="flex-1">
              <p class="text-xs font-semibold uppercase tracking-wider opacity-70">Score régional moyen</p>
              <p class="text-4xl font-black mt-0.5" :class="scoreNumClass">
                {{ detail.score_region }}
                <span class="text-base font-semibold opacity-60">/100</span>
              </p>
            </div>
            <div class="text-5xl font-black opacity-10 select-none" :class="scoreNumClass">
              {{ detail.score_region }}
            </div>
          </div>

          <!-- Résumé automatique -->
          <div class="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <div class="flex items-start gap-2">
              <Sparkles :size="16" class="text-blue-500 mt-0.5 flex-shrink-0" />
              <p class="text-sm text-slate-700 leading-relaxed">
                {{ detail.summary }}
              </p>
            </div>
          </div>

          <!-- Zones classées -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-sm font-bold text-slate-700">
                Zones classées par priorité
              </h3>
              <span class="text-xs text-slate-400">
                {{ detail.zones?.length || 0 }} zone{{ (detail.zones?.length || 0) > 1 ? "s" : "" }}
              </span>
            </div>

            <div class="space-y-3">
              <CardZone
                v-for="(zone, idx) in detail.zones"
                :key="zone.id"
                :zone="zone"
                :rang="idx + 1"
                @voir-beneficiaires="(b) => $emit('voir-beneficiaire', b)"
              />
            </div>
          </div>

          <!-- Message vide -->
          <div v-if="!detail.zones || detail.zones.length === 0" class="text-center py-8">
            <MapPin :size="32" class="text-slate-300 mx-auto mb-2" />
            <p class="text-sm text-slate-400 italic">Aucune zone disponible pour cette région.</p>
          </div>
        </div>

        <!-- Erreur -->
        <div v-else-if="erreur" class="flex flex-col items-center justify-center py-20 gap-2 px-6 text-center">
          <AlertCircle :size="32" class="text-red-400" />
          <p class="text-sm text-red-600 font-medium">{{ erreur }}</p>
          <p class="text-xs text-slate-400">Vérifiez que ce projet a des bénéficiaires dans cette région.</p>
        </div>

        <!-- Région sans données -->
        <div v-else class="flex flex-col items-center justify-center py-20 gap-2 px-6 text-center">
          <MapPin :size="32" class="text-slate-300" />
          <p class="text-sm text-slate-400 italic">Cliquez sur une région de la carte.</p>
        </div>
      </div>
    </aside>
  </Transition>
</template>

<script setup>
import { computed } from "vue";
import { X, MapPin, Sparkles, AlertCircle } from "lucide-vue-next";
import CardZone from "./CardZone.vue";

const props = defineProps({
  ouvert: { type: Boolean, default: false },
  region: { type: String, default: null },
  detail: { type: Object, default: null },
  chargement: { type: Boolean, default: false },
  erreur: { type: String, default: null },
});

defineEmits(["fermer", "voir-beneficiaire"]);

const score = computed(() => props.detail?.score_region || 0);

const headerBadgeClass = computed(() => {
  if (score.value >= 80) return "bg-red-500";
  if (score.value >= 60) return "bg-orange-400";
  if (score.value >= 40) return "bg-yellow-400";
  return "bg-green-500";
});

const scoreBadgeClass = computed(() => {
  if (score.value >= 80) return "bg-red-100 text-red-700";
  if (score.value >= 60) return "bg-orange-100 text-orange-700";
  if (score.value >= 40) return "bg-yellow-100 text-yellow-700";
  return "bg-green-100 text-green-700";
});

const scoreDotClass = computed(() => {
  if (score.value >= 80) return "bg-red-500";
  if (score.value >= 60) return "bg-orange-400";
  if (score.value >= 40) return "bg-yellow-400";
  return "bg-green-500";
});

const scoreCardClass = computed(() => {
  if (score.value >= 80) return "bg-red-50 border-red-100";
  if (score.value >= 60) return "bg-orange-50 border-orange-100";
  if (score.value >= 40) return "bg-yellow-50 border-yellow-100";
  return "bg-green-50 border-green-100";
});

const scoreNumClass = computed(() => {
  if (score.value >= 80) return "text-red-600";
  if (score.value >= 60) return "text-orange-500";
  if (score.value >= 40) return "text-yellow-600";
  return "text-green-600";
});
</script>

<style scoped>
.backdrop-enter-active,
.backdrop-leave-active {
  transition: opacity 0.3s ease;
}
.backdrop-enter-from,
.backdrop-leave-to {
  opacity: 0;
}

.drawer-slide-enter-active {
  transition: transform 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.drawer-slide-leave-active {
  transition: transform 0.28s ease-in;
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(100%);
}
</style>

