<template>
  <!-- Message utilisateur -->
  <div v-if="message.role === 'user'" class="flex justify-end gap-3">
    <div class="max-w-[80%]">
      <div
        class="px-4 py-3 rounded-2xl rounded-br-sm text-sm leading-relaxed bg-[#021427] text-white shadow-sm font-medium"
      >
        <div v-if="message.isVoice" class="mb-2 text-[11px] text-white/70">
          Message vocal · {{ formatDuration(message.durationSeconds) }}
        </div>
        <audio v-if="message.isVoice && message.audioUrl" :src="message.audioUrl" controls class="mb-2 block max-w-full" aria-label="Écouter le message vocal" />
        <p>{{ typeof message.content === "string" ? message.content : JSON.stringify(message.content) }}</p>
      </div>
      <p class="text-[10px] text-slate-400 mt-1 text-right font-medium">
        {{ formatTime(message.timestamp) }}
      </p>
    </div>
    <!-- Avatar Responsable Finance -->
    <div
      class="w-8 h-8 rounded-full bg-[#CCA43B]/20 border border-[#CCA43B]/50 flex-shrink-0 flex items-center justify-center text-xs font-bold text-[#744D03] mt-auto shadow-sm"
    >
      RF
    </div>
  </div>

  <!-- Message assistant -->
  <div v-else class="flex justify-start gap-3">
    <!-- Avatar IA Finance (pièce dorée) -->
    <div
      class="w-8 h-8 rounded-full bg-[#021427] border border-[#CCA43B]/40 flex-shrink-0 flex items-center justify-center mt-auto shadow-md"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#CCA43B"
        stroke-width="1.8"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="12" cy="12" r="8" />
        <path
          d="M9.5 9.5c.5-1 1.5-1.5 2.5-1.5 1.4 0 2.5.9 2.5 2s-.8 1.5-2 2c-1.2.5-2 1-2 2.5"
        />
        <path d="M12 18v-1.5" />
      </svg>
    </div>

    <div class="max-w-[85%] sm:max-w-[88%] w-full">
      <!-- Indicateur de chargement -->
      <div
        v-if="message.loading"
        class="flex items-center gap-2 px-4 py-3 bg-white border border-slate-200/80 rounded-2xl rounded-bl-sm shadow-xs"
      >
        <span
          v-for="i in 3"
          :key="i"
          class="w-2 h-2 rounded-full bg-[#CCA43B] animate-bounce"
          :style="{ animationDelay: `${(i - 1) * 0.15}s` }"
        />
        <span class="text-xs font-semibold text-slate-600 ml-1"
          >Analyse financière experte en cours...</span
        >
      </div>

      <!-- Réponse réelle -->
      <div
        v-else
        class="px-4 py-3.5 rounded-2xl rounded-bl-sm text-sm leading-relaxed shadow-sm transition-all duration-300"
        :class="
          message.isError
            ? 'bg-red-50 border border-red-200 text-red-800'
            : 'bg-white border border-slate-200/80 text-slate-800'
        "
      >
        <!-- Badge alerte si présent -->
        <div
          v-if="message.alert && message.alert !== 'GREEN' && !message.isError"
          class="mb-3 px-3 py-1.5 rounded-xl border flex items-center gap-2"
          :class="alertCardHeaderClass(message.alert)"
        >
          <span
            class="w-2.5 h-2.5 rounded-full flex-shrink-0"
            :class="alertDotClass(message.alert)"
          />
          <span
            class="text-xs font-bold uppercase tracking-wide"
            :class="alertTextClass(message.alert)"
          >
            Niveau d'Alerte : {{ alertLabel(message.alert) }}
          </span>
        </div>

        <!-- Blocs de texte parsés avec cartes structurées pour Observation, Risque, Recommandation, Prédiction -->
        <div class="space-y-3">
          <template v-for="(block, i) in parsedBlocks" :key="i">
            <div v-if="block.type === 'empty'" class="h-0.5" />

            <!-- CARTE OBSERVATION -->
            <div
              v-else-if="block.section === 'OBSERVATION'"
              class="bg-bleu-accent/10 border border-bleu-accent/20 rounded-xl p-3 space-y-1"
            >
              <div
                class="flex items-center gap-1.5 text-bleu-nuit font-bold text-xs uppercase tracking-wider"
              >
                <span>📌</span>
                <span>Observation & Diagnostic</span>
              </div>
              <p
                class="text-xs sm:text-sm text-bleu-nuit leading-relaxed"
                v-html="block.html"
              />
            </div>

            <!-- CARTE RISQUE -->
            <div
              v-else-if="block.section === 'RISQUE'"
              class="bg-amber-50/80 border border-amber-200 rounded-xl p-3 space-y-1"
            >
              <div
                class="flex items-center gap-1.5 text-amber-900 font-bold text-xs uppercase tracking-wider"
              >
                <span>⚠️</span>
                <span>Analyse des Risques</span>
              </div>
              <p
                class="text-xs sm:text-sm text-amber-950 leading-relaxed"
                v-html="block.html"
              />
            </div>

            <!-- CARTE RECOMMANDATION -->
            <div
              v-else-if="block.section === 'RECOMMANDATION'"
              class="bg-emerald-50/80 border border-emerald-200 rounded-xl p-3 space-y-1"
            >
              <div
                class="flex items-center gap-1.5 text-emerald-900 font-bold text-xs uppercase tracking-wider"
              >
                <span>💡</span>
                <span>Recommandations d'Action</span>
              </div>
              <p
                class="text-xs sm:text-sm text-emerald-950 leading-relaxed"
                v-html="block.html"
              />
            </div>

            <!-- CARTE PRÉDICTION -->
            <div
              v-else-if="block.section === 'PREDICTION'"
              class="bg-bleu-accent/10 border border-bleu-accent/20 rounded-xl p-3 space-y-1"
            >
              <div
                class="flex items-center gap-1.5 text-bleu-nuit font-bold text-xs uppercase tracking-wider"
              >
                <span>🔮</span>
                <span>Prédiction & Projections</span>
              </div>
              <p
                class="text-xs sm:text-sm text-bleu-nuit leading-relaxed"
                v-html="block.html"
              />
            </div>

            <!-- En-tête générique -->
            <h4
              v-else-if="block.type === 'heading'"
              class="font-bold text-[#021427] text-sm mt-3 mb-1 border-b border-slate-100 pb-1 flex items-center gap-2"
              v-html="block.html"
            />

            <!-- Puce -->
            <div
              v-else-if="block.type === 'bullet'"
              class="flex items-start gap-2 text-slate-700 text-xs sm:text-sm"
            >
              <span
                class="mt-1.5 w-1.5 h-1.5 rounded-full bg-[#CCA43B] flex-shrink-0"
              />
              <p class="leading-relaxed" v-html="block.html" />
            </div>

            <!-- Texte normal -->
            <p
              v-else
              class="text-xs sm:text-sm text-slate-700 leading-relaxed"
              v-html="block.html"
            />
          </template>
        </div>
        <button v-if="!message.loading && !message.isError" type="button" class="mt-3 text-xs font-semibold text-bleu-nuit hover:underline" @click="speakResponse">Écouter la réponse</button>
      </div>
      <p class="text-[10px] text-slate-400 mt-1 font-medium">
        {{ formatTime(message.timestamp) }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, watch } from "vue";

const props = defineProps({ message: { type: Object, required: true } });

watch(
  () => [props.message.loading, props.message.content, props.message.voiceResponse],
  ([loading, content, voiceResponse]) => {
    if (!voiceResponse || loading || !content || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const spokenText = String(content)
      .replace(/```[\s\S]*?```/g, " ")
      .replace(/[*_`#>\[\]()]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
    if (!spokenText) return;
    const utterance = new SpeechSynthesisUtterance(spokenText);
    utterance.lang = "fr-FR";
    window.speechSynthesis.speak(utterance);
  },
);

onBeforeUnmount(() => {
  if (typeof window !== "undefined" && "speechSynthesis" in window) window.speechSynthesis.cancel();
});

const formatTime = (iso) => {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleTimeString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
};

const formatDuration = (seconds) => `${String(Math.floor(Number(seconds || 0) / 60)).padStart(2, "0")}:${String(Number(seconds || 0) % 60).padStart(2, "0")}`;
const speakResponse = () => {
  if (!("speechSynthesis" in window) || !props.message.content) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(String(props.message.content));
  utterance.lang = "fr-FR";
  window.speechSynthesis.speak(utterance);
};

const alertDotClass = (a) =>
  ({
    RED: "bg-red-500 animate-pulse",
    ORANGE: "bg-orange-500 animate-pulse",
    YELLOW: "bg-amber-400",
  }[a] || "bg-emerald-500");

const alertTextClass = (a) =>
  ({
    RED: "text-red-700",
    ORANGE: "text-orange-700",
    YELLOW: "text-amber-700",
  }[a] || "text-emerald-700");

const alertCardHeaderClass = (a) =>
  ({
    RED: "bg-red-50 border-red-200",
    ORANGE: "bg-orange-50 border-orange-200",
    YELLOW: "bg-amber-50 border-amber-200",
  }[a] || "bg-emerald-50 border-emerald-200");

const alertLabel = (a) =>
  ({
    RED: "🔴 Critique (Dépassement / Insolvabilité)",
    ORANGE: "🟠 Risque Élevé (Vigilance urgente)",
    YELLOW: "🟡 Attention (Surveillance budgétaire)",
  }[a] || "🟢 Situation Saine");

const parsedBlocks = computed(() => {
  // Protection : s'assurer que content est une string
  let raw = props.message.content;
  if (!raw) return [];
  if (typeof raw !== "string") {
    try {
      raw = JSON.stringify(raw);
    } catch {
      raw = String(raw);
    }
  }
  let text = raw;

  // Protection JSON brut
  const trimmed = text.trim();
  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    try {
      const parsed = JSON.parse(trimmed);
      if (parsed?.answer) text = parsed.answer;
      else
        text =
          "Le service IA a retourné un format inattendu. Veuillez réessayer.";
    } catch {
      /* pas du JSON */
    }
  }

  const lines = text.split("\n");
  const blocks = [];
  let currentSection = null;

  for (let rawLine of lines) {
    const t = rawLine.trim();
    if (!t) {
      blocks.push({ type: "empty" });
      continue;
    }

    // Détection de section structurée (OBSERVATION, RISQUE, RECOMMANDATION, PREDICTION)
    const upper = t.toUpperCase();
    if (upper.includes("OBSERVATION") || upper.includes("📌")) {
      currentSection = "OBSERVATION";
      const cleanLine = t
        .replace(/^#{1,3}\s*/, "")
        .replace(/^📌\s*/, "")
        .replace(/^OBSERVATION/i, "")
        .replace(/^:\s*/, "");
      if (cleanLine.trim()) {
        blocks.push({
          type: "section",
          section: "OBSERVATION",
          html: formatInline(cleanLine),
        });
      }
      continue;
    } else if (upper.includes("RISQUE") || upper.includes("⚠️")) {
      currentSection = "RISQUE";
      const cleanLine = t
        .replace(/^#{1,3}\s*/, "")
        .replace(/^⚠️\s*/, "")
        .replace(/^RISQUE/i, "")
        .replace(/^:\s*/, "");
      if (cleanLine.trim()) {
        blocks.push({
          type: "section",
          section: "RISQUE",
          html: formatInline(cleanLine),
        });
      }
      continue;
    } else if (upper.includes("RECOMMANDATION") || upper.includes("💡")) {
      currentSection = "RECOMMANDATION";
      const cleanLine = t
        .replace(/^#{1,3}\s*/, "")
        .replace(/^💡\s*/, "")
        .replace(/^RECOMMANDATION/i, "")
        .replace(/^S/i, "")
        .replace(/^:\s*/, "");
      if (cleanLine.trim()) {
        blocks.push({
          type: "section",
          section: "RECOMMANDATION",
          html: formatInline(cleanLine),
        });
      }
      continue;
    } else if (
      upper.includes("PRÉDICTION") ||
      upper.includes("PREDICTION") ||
      upper.includes("🔮")
    ) {
      currentSection = "PREDICTION";
      const cleanLine = t
        .replace(/^#{1,3}\s*/, "")
        .replace(/^🔮\s*/, "")
        .replace(/^PRÉDICTION/i, "")
        .replace(/^PREDICTION/i, "")
        .replace(/^:\s*/, "");
      if (cleanLine.trim()) {
        blocks.push({
          type: "section",
          section: "PREDICTION",
          html: formatInline(cleanLine),
        });
      }
      continue;
    }

    // Si on est à l'intérieur d'une section active
    if (currentSection && !t.startsWith("#")) {
      blocks.push({
        type: "section",
        section: currentSection,
        html: formatInline(t),
      });
      continue;
    }

    // Reset section if new heading
    if (t.startsWith("#")) {
      currentSection = null;
    }

    // Titre markdown ##
    const headingMatch = t.match(/^#{1,3}\s+(.+)/);
    if (headingMatch) {
      blocks.push({ type: "heading", html: formatInline(headingMatch[1]) });
      continue;
    }

    // Puce ou liste
    const bulletMatch = t.match(/^[-*•]\s+(.+)/);
    if (bulletMatch) {
      blocks.push({ type: "bullet", html: formatInline(bulletMatch[1]) });
      continue;
    }

    const numMatch = t.match(/^\d+\.\s+(.+)/);
    if (numMatch) {
      blocks.push({ type: "bullet", html: formatInline(numMatch[1]) });
      continue;
    }

    blocks.push({ type: "text", html: formatInline(t) });
  }

  return blocks;
});

function formatInline(text) {
  return text
    .replace(
      /\*\*(.+?)\*\*/g,
      '<strong class="font-semibold text-slate-900">$1</strong>'
    )
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(
      /([\d\s]+(?:\s?\d{3})*(?:,\d+)?\s*FCFA)/g,
      '<span class="font-bold text-[#744D03]">$1</span>'
    )
    .replace(
      /(\d+(?:[,.]\d+)?\s*%)/g,
      '<span class="font-bold text-[#021427]">$1</span>'
    )
    .replace(
      /(DEP-[\w-]+|DON-[\w-]+)/g,
      '<code class="text-xs bg-slate-100 px-1 py-0.5 rounded font-mono">$1</code>'
    );
}
</script>
