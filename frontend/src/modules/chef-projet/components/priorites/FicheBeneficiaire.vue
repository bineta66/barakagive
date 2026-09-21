<template>
  <!-- Overlay -->
  <Transition name="overlay-fade">
    <div
      v-if="beneficiaire"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      @click.self="$emit('fermer')"
    >
      <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="$emit('fermer')" />

      <!-- Panel -->
      <Transition name="modal-pop">
        <div
          v-if="beneficiaire"
          class="relative z-10 bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden"
        >
          <!-- Header -->
          <div class="flex items-start justify-between p-5 border-b border-slate-100">
            <div class="flex items-center gap-3">
              <!-- Avatar initiales -->
              <div
                class="w-11 h-11 rounded-full flex items-center justify-center text-white font-bold text-base flex-shrink-0"
                :class="badgeBgClass"
              >
                {{ initiales }}
              </div>
              <div>
                <h2 class="text-base font-bold text-slate-800 leading-tight">
                  {{ beneficiaire.nom_complet }}
                </h2>
                <p class="text-xs text-slate-500 mt-0.5">
                  {{ beneficiaire.sexe === "M" ? "Homme" : beneficiaire.sexe === "F" ? "Femme" : "Autre" }}
                  <template v-if="beneficiaire.age"> • {{ beneficiaire.age }} ans</template>
                </p>
              </div>
            </div>
            <button
              @click="$emit('fermer')"
              class="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
            >
              <X :size="16" />
            </button>
          </div>

          <!-- Contenu scrollable -->
          <div class="overflow-y-auto flex-1 p-5 space-y-5">

            <!-- Score principal -->
            <div
              class="rounded-xl p-4 flex items-center justify-between"
              :class="scoreBgClass"
            >
              <div>
                <p class="text-xs font-semibold uppercase tracking-wider opacity-70">
                  Score de vulnérabilité
                </p>
                <p class="text-3xl font-black mt-0.5" :class="scoreTextClass">
                  {{ beneficiaire.score }}<span class="text-base font-semibold opacity-60">/100</span>
                </p>
              </div>
              <div class="text-right">
                <span
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-bold"
                  :class="niveauBadgeClass"
                >
                  <span class="w-2 h-2 rounded-full" :class="niveauDotClass"></span>
                  {{ beneficiaire.niveau }}
                </span>
              </div>
            </div>

            <!-- Informations personnelles -->
            <div>
              <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                Informations
              </h3>
              <div class="grid grid-cols-2 gap-3">
                <InfoLine icon="Phone" label="Téléphone" :value="beneficiaire.telephone" />
                <InfoLine icon="MapPin" label="Quartier" :value="beneficiaire.quartier || '—'" />
                <InfoLine icon="Map" label="Région" :value="beneficiaire.region || '—'" />
                <InfoLine icon="Navigation" label="Zone" :value="beneficiaire.zone_nom || '—'" />
              </div>
            </div>

            <!-- Tableau des critères -->
            <div>
              <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                Critères ayant donné le score
              </h3>

              <div v-if="beneficiaire.criteres && beneficiaire.criteres.length > 0" class="rounded-xl border border-slate-200 overflow-hidden">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-200">
                      <th class="text-left text-xs font-semibold text-slate-500 px-4 py-2.5">Critère</th>
                      <th class="text-center text-xs font-semibold text-slate-500 px-3 py-2.5">Réponse</th>
                      <th class="text-right text-xs font-semibold text-slate-500 px-4 py-2.5">Points</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100">
                    <tr
                      v-for="(critere, idx) in beneficiaire.criteres"
                      :key="idx"
                      class="transition-colors"
                      :class="critere.obtenu ? 'bg-red-50/40' : 'bg-white'"
                    >
                      <td class="px-4 py-3 text-slate-700 font-medium text-xs">
                        <span class="flex items-center gap-2">
                          <span
                            class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                            :class="critere.obtenu ? 'bg-red-400' : 'bg-slate-300'"
                          ></span>
                          {{ critere.nom }}
                        </span>
                      </td>
                      <td class="px-3 py-3 text-center">
                        <span
                          class="inline-block px-2 py-0.5 rounded-md text-xs font-semibold"
                          :class="
                            critere.reponse === 'Oui'
                              ? 'bg-red-100 text-red-700'
                              : critere.reponse === 'Non'
                              ? 'bg-slate-100 text-slate-500'
                              : 'bg-slate-100 text-slate-400'
                          "
                        >
                          {{ critere.reponse }}
                        </span>
                      </td>
                      <td class="px-4 py-3 text-right">
                        <span
                          class="font-bold text-sm"
                          :class="critere.points > 0 ? 'text-red-600' : 'text-slate-400'"
                        >
                          +{{ critere.points }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                  <!-- Total -->
                  <tfoot>
                    <tr class="bg-slate-50 border-t-2 border-slate-300">
                      <td class="px-4 py-3 text-xs font-bold text-slate-600 uppercase tracking-wide" colspan="2">
                        Score final
                      </td>
                      <td class="px-4 py-3 text-right">
                        <span class="text-lg font-black" :class="scoreTextClass">
                          {{ beneficiaire.score }}/100
                        </span>
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>

              <div v-else class="text-center py-6 text-sm text-slate-400 italic bg-slate-50 rounded-xl">
                Aucun critère de vulnérabilité configuré pour ce projet.
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from "vue";
import { X, Phone, MapPin, Map, Navigation } from "lucide-vue-next";

// Mini-composant inline pour les lignes d'info
const InfoLine = {
  props: ["label", "value"],
  template: `
    <div class="bg-slate-50 rounded-lg px-3 py-2">
      <p class="text-xs text-slate-400 font-medium">{{ label }}</p>
      <p class="text-sm text-slate-700 font-semibold mt-0.5 truncate">{{ value || '—' }}</p>
    </div>
  `,
};

const props = defineProps({
  beneficiaire: { type: Object, default: null },
});

defineEmits(["fermer"]);

const initiales = computed(() => {
  if (!props.beneficiaire) return "";
  const p = props.beneficiaire.prenom || "";
  const n = props.beneficiaire.nom || "";
  return ((p[0] || "") + (n[0] || "")).toUpperCase();
});

const scoreBgClass = computed(() => {
  const s = props.beneficiaire?.score || 0;
  if (s >= 80) return "bg-red-50 border border-red-100";
  if (s >= 60) return "bg-orange-50 border border-orange-100";
  if (s >= 40) return "bg-yellow-50 border border-yellow-100";
  return "bg-green-50 border border-green-100";
});

const scoreTextClass = computed(() => {
  const s = props.beneficiaire?.score || 0;
  if (s >= 80) return "text-red-600";
  if (s >= 60) return "text-orange-500";
  if (s >= 40) return "text-yellow-600";
  return "text-green-600";
});

const badgeBgClass = computed(() => {
  const s = props.beneficiaire?.score || 0;
  if (s >= 80) return "bg-red-500";
  if (s >= 60) return "bg-orange-400";
  if (s >= 40) return "bg-yellow-400";
  return "bg-green-500";
});

const niveauBadgeClass = computed(() => {
  const s = props.beneficiaire?.score || 0;
  if (s >= 80) return "bg-red-100 text-red-700";
  if (s >= 60) return "bg-orange-100 text-orange-700";
  if (s >= 40) return "bg-yellow-100 text-yellow-700";
  return "bg-green-100 text-green-700";
});

const niveauDotClass = computed(() => {
  const s = props.beneficiaire?.score || 0;
  if (s >= 80) return "bg-red-500";
  if (s >= 60) return "bg-orange-400";
  if (s >= 40) return "bg-yellow-400";
  return "bg-green-500";
});
</script>

<style scoped>
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.25s ease;
}
.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

.modal-pop-enter-active {
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.modal-pop-leave-active {
  transition: all 0.2s ease;
}
.modal-pop-enter-from,
.modal-pop-leave-to {
  opacity: 0;
  transform: scale(0.92) translateY(16px);
}
</style>

