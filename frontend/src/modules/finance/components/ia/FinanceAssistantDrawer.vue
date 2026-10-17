<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div
        v-if="store.isOpen"
        class="fixed inset-0 z-[9999] flex"
        @keydown.esc="store.closeAssistant"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/40 backdrop-blur-sm"
          @click="store.closeAssistant"
        />

        <!-- Panneau -->
        <div
          class="relative ml-auto w-full max-w-xl h-full bg-white flex flex-col overflow-hidden border-l border-slate-200"
        >
          <!-- ── HEADER ─────────────────────────────────────── -->
          <div
            class="flex-shrink-0 px-5 py-4 flex items-center justify-between bg-bleu-nuit text-white"
          >
            <div class="flex items-center gap-3">
              <!-- Icône orbe -->
              <div
                class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors duration-500"
                :class="headerIconBg"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="white"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"
                  />
                </svg>
              </div>
              <div>
                <h2 class="text-sm font-bold text-white leading-tight">
                  Contrôleur Financier
                </h2>
                <div class="flex items-center gap-1.5 mt-0.5">
                  <span
                    class="w-2 h-2 rounded-full transition-colors duration-500"
                    :class="alertDotClass"
                  />
                  <p class="text-[11px] font-medium text-slate-300">
                    {{ alertLabel }}
                  </p>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-1">
              <button
                v-if="store.hasMessages"
                @click="store.clearHistory"
                class="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/10 transition text-xs flex items-center gap-1.5"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                  />
                </svg>
                <span class="hidden sm:inline text-xs">Effacer</span>
              </button>
              <button
                @click="store.closeAssistant"
                class="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/10 transition"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M18 6 6 18M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- ── BANNIÈRE ALERTE ────────────────────────────── -->
          <div
            v-if="store.alertLevel !== 'GREEN'"
            class="flex-shrink-0 flex items-center gap-3 px-5 py-2.5 border-b text-sm"
            :class="alertBannerClass"
          >
            <span
              class="w-2 h-2 rounded-full flex-shrink-0 animate-pulse"
              :class="alertDotClass"
            />
            <p class="text-xs font-medium flex-1" :class="alertBannerTextClass">
              {{ alertBannerMessage }}
            </p>
            <button
              @click="analyserSituation"
              :disabled="store.isLoading"
              class="text-xs font-bold px-3 py-1 rounded-lg transition disabled:opacity-50"
              :class="alertBannerBtnClass"
            >
              Analyser →
            </button>
          </div>

          <!-- ── ZONE MESSAGES ──────────────────────────────── -->
          <div
            ref="scrollContainer"
            class="flex-1 overflow-y-auto px-4 py-5 space-y-4 bg-slate-50/40"
          >
            <!-- Écran d'accueil — pas encore de messages -->
            <div v-if="!store.hasMessages" class="space-y-5">
              <!-- KPI Cards -->
              <div v-if="homeData" class="grid grid-cols-2 gap-3">
                <div class="bg-white border border-slate-200/60 rounded-xl p-3">
                  <p class="text-xs text-slate-400 mb-1">Budget total</p>
                  <p class="text-sm font-bold text-bleu-nuit">
                    {{ formatMontant(homeData.budget_total) }} FCFA
                  </p>
                </div>
                <div class="bg-white border border-slate-200/60 rounded-xl p-3">
                  <p class="text-xs text-slate-400 mb-1">Dépenses</p>
                  <p class="text-sm font-bold text-slate-800">
                    {{ formatMontant(homeData.depenses) }} FCFA
                  </p>
                </div>
                <div class="bg-white border border-slate-200/60 rounded-xl p-3">
                  <p class="text-xs text-slate-400 mb-1">Solde disponible</p>
                  <p
                    class="text-sm font-bold"
                    :class="
                      (homeData.solde ?? 0) >= 0
                        ? 'text-emerald-600'
                        : 'text-red-600'
                    "
                  >
                    {{ formatMontant(homeData.solde) }} FCFA
                  </p>
                </div>
                <div class="bg-white border border-slate-200/60 rounded-xl p-3">
                  <p class="text-xs text-slate-400 mb-1">Taux d'exécution</p>
                  <p class="text-sm font-bold text-bleu-nuit">
                    {{ homeData.taux_execution ?? 0 }}%
                  </p>
                  <div
                    class="w-full h-1 bg-slate-100 rounded-full mt-1.5 overflow-hidden"
                  >
                    <div
                      class="h-full rounded-full transition-all"
                      :class="progressBarClass(homeData.taux_execution)"
                      :style="{
                        width:
                          Math.min(homeData.taux_execution ?? 0, 100) + '%',
                      }"
                    />
                  </div>
                </div>
              </div>

              <!-- Message d'accueil -->
              <div class="bg-white border border-slate-200/60 rounded-xl p-4">
                <p class="text-sm font-semibold text-bleu-nuit mb-1">
                  Bonjour 👋
                </p>
                <p class="text-sm text-slate-600 leading-relaxed">
                  Je suis votre contrôleur financier. Posez-moi une question sur
                  vos budgets, dépenses, dons ou justificatifs — je vous réponds
                  avec les données de votre organisation.
                </p>
              </div>

              <!-- Suggestions -->
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase mb-2">
                  Questions fréquentes
                </p>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <button
                    v-for="s in store.quickSuggestions"
                    :key="s.id"
                    @click="sendSuggestion(s.text)"
                    :disabled="store.isLoading"
                    class="text-left px-3 py-2.5 text-xs bg-white border border-slate-200 rounded-xl hover:border-bleu-nuit/40 hover:bg-bleu-nuit/5 transition text-slate-700 font-medium disabled:opacity-50"
                  >
                    {{ s.text }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Messages de conversation -->
            <template v-else>
              <FinanceChatMessage
                v-for="msg in store.messages"
                :key="msg.id"
                :message="msg"
              />
            </template>
          </div>

          <!-- ── INPUT ─────────────────────────────────────── -->
          <AssistantInput
            :disabled="store.isLoading || audioProcessing"
            :external-error="audioError"
            @send="handleSend"
            @send-audio="handleSendAudio"
          />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick, computed } from "vue";
import { useRoute } from "vue-router";
import api from "@/services/api.js";
import { useFinanceAssistantStore } from "@/stores/financeAssistant.js";
import FinanceChatMessage from "./FinanceChatMessage.vue";
import AssistantInput from "@/components/ia/AssistantInput.vue";

const store = useFinanceAssistantStore();
const route = useRoute();
const scrollContainer = ref(null);
const audioProcessing = ref(false);
const audioError = ref("");

const pageContext = computed(() => {
  const parts = route.path.split("/").filter(Boolean);
  const segment = parts[1];
  const type = ({ budgets: "budget", "lignes-budgetaires": "line", financements: "financement", dons: "don", depenses: "expense" })[segment];
  const rawId = parts[2];
  return type ? { type, ...(rawId ? { id: rawId } : {}) } : null;
});

const homeData = computed(() => store.homeData);

// ── Formatters ────────────────────────────────────────────────
const formatMontant = (val) => {
  if (val == null) return "0";
  return new Intl.NumberFormat("fr-FR").format(val);
};

const progressBarClass = (taux) => {
  if (!taux) return "bg-emerald-500";
  if (taux >= 90) return "bg-red-600";
  if (taux >= 75) return "bg-orange-500";
  if (taux >= 50) return "bg-amber-400";
  return "bg-emerald-500";
};

// ── Alerte ───────────────────────────────────────────────────
const alertDotClass = computed(
  () =>
    ({
      RED: "bg-red-500",
      ORANGE: "bg-orange-500",
      YELLOW: "bg-amber-400",
      GREEN: "bg-emerald-500",
    }[store.alertLevel] || "bg-emerald-500")
);

const alertLabel = computed(
  () =>
    ({
      RED: "Situation critique",
      ORANGE: "Attention requise",
      YELLOW: "À surveiller",
      GREEN: "Tout va bien",
    }[store.alertLevel] || "Tout va bien")
);

const headerIconBg = computed(
  () =>
    ({
      RED: "bg-red-600",
      ORANGE: "bg-orange-500",
      YELLOW: "bg-amber-500",
      GREEN: "bg-emerald-600",
    }[store.alertLevel] || "bg-emerald-600")
);

const alertBannerClass = computed(
  () =>
    ({
      RED: "bg-red-50 border-red-200",
      ORANGE: "bg-orange-50 border-orange-200",
      YELLOW: "bg-amber-50 border-amber-200",
    }[store.alertLevel] || "")
);

const alertBannerTextClass = computed(
  () =>
    ({
      RED: "text-red-700",
      ORANGE: "text-orange-700",
      YELLOW: "text-amber-700",
    }[store.alertLevel] || "")
);

const alertBannerBtnClass = computed(
  () =>
    ({
      RED: "bg-red-100 hover:bg-red-200 text-red-800",
      ORANGE: "bg-orange-100 hover:bg-orange-200 text-orange-800",
      YELLOW: "bg-amber-100 hover:bg-amber-200 text-amber-800",
    }[store.alertLevel] || "")
);

const alertBannerMessage = computed(
  () =>
    ({
      RED: "Le budget est presque épuisé — une action est nécessaire.",
      ORANGE:
        "Le rythme de dépenses est élevé, vérifiez les postes prioritaires.",
      YELLOW: "Les dépenses sont en hausse, gardez un œil sur le solde.",
    }[store.alertLevel] || "")
);

// ── Actions ───────────────────────────────────────────────────
const analyserSituation = () => {
  const questions = {
    RED: "La situation est critique. Explique-moi ce qui se passe avec le budget et ce que je dois faire maintenant.",
    ORANGE:
      "Je vois qu'il y a un risque sur le budget. Explique-moi la situation et tes recommandations.",
    YELLOW:
      "Le niveau de vigilance est jaune. Qu'est-ce qui se passe et que me recommandes-tu ?",
  };
  const q = questions[store.alertLevel];
  if (q) store.sendMessage(q);
};

// ── Scroll & Focus ────────────────────────────────────────────
const scrollToBottom = () => {
  nextTick(() => {
    const el = scrollContainer.value;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  });
};

watch(() => store.messages.length, scrollToBottom);
watch(() => store.messages[store.messages.length - 1]?.content, scrollToBottom);
watch(
  () => store.isOpen,
  (open) => {
    if (open) nextTick(() => scrollToBottom());
  }
);

const handleSend = async (question, clearDraft) => {
  if (!question?.trim() || store.isLoading) return;
  const sent = await store.sendMessage(question, pageContext.value);
  if (sent) clearDraft?.();
};

const handleSendAudio = async (blob, durationSeconds, clearRecording) => {
  if (store.isLoading || audioProcessing.value) return;
  audioError.value = "";
    audioProcessing.value = true;
  try {
    const form = new FormData();
    const mime = blob.type?.split(";", 1)[0] || "audio/webm";
    const extension = ({ "audio/ogg": "ogg", "audio/wav": "wav", "audio/x-wav": "wav", "audio/mp4": "m4a", "audio/x-m4a": "m4a", "audio/mpeg": "mp3", "audio/mp3": "mp3" })[mime] || "webm";
    form.append("audio", blob, `message-vocal.${extension}`);
    form.append("duration_seconds", String(durationSeconds));
    const { data } = await api.post("/api/assistant/audio/", form, { timeout: 95000 });
    const transcript = String(data?.transcription || "").trim();
    if (!transcript) throw new Error("La transcription ne contient aucun texte.");
    const sent = await store.sendMessage(transcript, pageContext.value, { blob, durationSeconds });
    if (sent) clearRecording?.();
    else audioError.value = "La question vocale a été transcrite, mais l’assistant n’a pas pu répondre.";
  } catch (error) {
    audioError.value = error?.response?.data?.detail || "La transcription vocale est momentanément indisponible.";
  } finally {
    audioProcessing.value = false;
  }
};

const sendSuggestion = (t) => store.sendMessage(t, pageContext.value);
</script>

<style scoped>
.drawer-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.drawer-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
.drawer-enter-from .relative.ml-auto,
.drawer-leave-to .relative.ml-auto {
  transform: translateX(100%);
}
</style>
