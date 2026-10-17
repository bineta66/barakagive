<template>
  <!-- Message utilisateur -->
  <div v-if="message.role === 'user'" class="flex justify-end gap-3">
    <div class="max-w-[80%]">
      <div v-if="message.voice" class="space-y-2 rounded-2xl rounded-br-sm bg-[#021427] px-4 py-3 text-white shadow-sm">
        <div class="flex items-center gap-2 text-xs font-semibold text-white/90">
          <span aria-hidden="true">🎙️</span>
          <span>Message vocal</span>
          <span class="font-mono tabular-nums text-white/70">{{ formatDuration(message.durationSeconds) }}</span>
        </div>
        <audio v-if="message.audioUrl" :src="message.audioUrl" controls class="w-full max-w-[280px]" aria-label="Réécouter le message vocal" />
        <p v-else class="text-xs text-white/70">Audio indisponible sur cet appareil.</p>
        <p v-if="message.transcription || message.content" class="border-t border-white/15 pt-2 text-xs leading-5 text-white/90">
          <span class="mb-1 block font-semibold text-white/70">Transcription</span>
          “{{ message.transcription || message.content }}”
        </p>
      </div>
      <div v-else
        class="px-4 py-3 rounded-2xl rounded-br-sm text-sm leading-relaxed bg-[#021427] text-white shadow-sm"
      >
        {{ message.content }}
      </div>
      <p class="text-[10px] text-slate-400 mt-1 text-right">
        {{ formatTime(message.timestamp) }}
      </p>
    </div>

    <!-- Avatar utilisateur -->
    <div
      class="w-8 h-8 rounded-full bg-bleu-nuit/15 border border-bleu-nuit/30 flex-shrink-0 flex items-center justify-center text-xs font-bold text-bleu-nuit mt-auto"
    >
      G
    </div>
  </div>

  <!-- Message assistant -->
  <div v-else class="flex justify-start gap-3">
    <!-- Avatar IA -->
    <div
      class="w-8 h-8 rounded-full bg-[#021427] border border-[#CCA43B]/40 flex-shrink-0 flex items-center justify-center mt-auto"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="15"
        height="15"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#CCA43B"
        stroke-width="1.8"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path
          d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5
                 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2
                 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0
                 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"
        />
      </svg>
    </div>

    <div class="max-w-[82%]">
      <!-- Skeleton de chargement -->
      <div v-if="message.loading" class="flex items-center gap-2 px-4 py-3">
        <span
          v-for="i in 3"
          :key="i"
          class="w-2 h-2 rounded-full bg-[#CCA43B]/60 animate-bounce"
          :style="{ animationDelay: `${(i - 1) * 0.15}s` }"
        />
        <span class="text-xs text-slate-400 ml-1">Analyse en cours…</span>
      </div>

      <!-- Réponse réelle -->
      <div
        v-else
        class="px-4 py-3 rounded-2xl rounded-bl-sm text-sm leading-relaxed shadow-sm"
        :class="
          message.isError
            ? 'bg-red-50 border border-red-200 text-red-800'
            : 'bg-slate-50 border border-slate-200/80 text-slate-800'
        "
      >
        <!-- Rendu texte avec sauts de ligne et mise en forme légère -->
        <div class="space-y-2">
          <template v-for="(block, i) in parsedBlocks" :key="i">
            <!-- Ligne vide → espacement -->
            <div v-if="block.type === 'empty'" class="h-1" />

            <!-- Ligne normale -->
            <p
              v-else-if="block.type === 'text'"
              class="leading-relaxed"
              v-html="block.html"
            />

            <!-- Puce de liste -->
            <div
              v-else-if="block.type === 'bullet'"
              class="flex items-start gap-2"
            >
              <span
                class="mt-1.5 w-1.5 h-1.5 rounded-full bg-[#CCA43B] flex-shrink-0"
              />
              <p class="leading-relaxed" v-html="block.html" />
            </div>
          </template>
        </div>
      </div>

      <p class="text-[10px] text-slate-400 mt-1">
        {{ formatTime(message.timestamp) }}
      </p>
      <button v-if="message.role !== 'user' && !message.loading && message.content && speechSupported" type="button" class="mt-1 text-[11px] font-medium text-slate-400 hover:text-[#021427]" @click="toggleSpeech">
        {{ speaking ? 'Arrêter la lecture' : 'Écouter la réponse' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";

const props = defineProps({
  message: { type: Object, required: true },
});

const speechSupported = typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
const speaking = ref(false);

watch(
  () => [props.message.loading, props.message.content, props.message.voiceResponse],
  ([loading, content, voiceResponse]) => {
    if (!voiceResponse || loading || !content || !speechSupported) return;
    window.speechSynthesis.cancel();
    const spokenText = String(content)
      .replace(/```[\s\S]*?```/g, " ")
      .replace(/[*_`#>\[\]()]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
    if (!spokenText) return;
    const utterance = new SpeechSynthesisUtterance(spokenText);
    utterance.lang = "fr-FR";
    utterance.onend = utterance.onerror = () => { speaking.value = false; };
    window.speechSynthesis.speak(utterance);
    speaking.value = true;
  },
);

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

const formatDuration = (seconds = 0) => `${String(Math.floor(Number(seconds || 0) / 60)).padStart(2, "0")}:${String(Number(seconds || 0) % 60).padStart(2, "0")}`;

const toggleSpeech = () => {
  if (!speechSupported) return;
  if (speaking.value) {
    window.speechSynthesis.cancel();
    speaking.value = false;
    return;
  }
  const utterance = new SpeechSynthesisUtterance(props.message.content);
  utterance.lang = "fr-FR";
  utterance.onend = utterance.onerror = () => { speaking.value = false; };
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
  speaking.value = true;
};

onBeforeUnmount(() => {
  if (speaking.value && speechSupported) window.speechSynthesis.cancel();
});

// Transforme le texte brut en blocs (paragraphes, listes, etc.)
const parsedBlocks = computed(() => {
  let text = props.message.content || "";
  if (!text) return [];

  // Protection : si le contenu est du JSON brut, on ne l'affiche pas tel quel
  // (cas où le backend a renvoyé un objet au lieu d'une réponse textuelle)
  const trimmed = text.trim();
  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    try {
      const parsed = JSON.parse(trimmed);
      // Si le JSON a un champ "answer", on l'utilise
      if (parsed && typeof parsed === "object" && parsed.answer) {
        text = parsed.answer;
      } else {
        // JSON sans champ answer → message d'erreur lisible
        text =
          "Le service IA a retourné une réponse dans un format inattendu. Veuillez réessayer.";
      }
    } catch {
      // Pas du JSON valide malgré les accolades → laisser tel quel
    }
  }

  return text.split("\n").map((line) => {
    const trimmed = line.trim();

    if (!trimmed) return { type: "empty" };

    // Puces Markdown : - item ou * item ou • item
    const bulletMatch = trimmed.match(/^[-*•]\s+(.+)/);
    if (bulletMatch) {
      return { type: "bullet", html: formatInline(bulletMatch[1]) };
    }

    // Numérotation : 1. item
    const numMatch = trimmed.match(/^\d+\.\s+(.+)/);
    if (numMatch) {
      return { type: "bullet", html: formatInline(numMatch[1]) };
    }

    return { type: "text", html: formatInline(trimmed) };
  });
});

// Mise en forme inline : **gras**, *italique*, chiffres colorés
function formatInline(text) {
  return (
    text
      // **bold**
      .replace(
        /\*\*(.+?)\*\*/g,
        '<strong class="font-semibold text-slate-900">$1</strong>'
      )
      // *italic*
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      // Montants FCFA → colorés en or
      .replace(
        /([\d\s]+(?:\s?\d{3})*(?:,\d+)?\s*FCFA)/g,
        '<span class="font-semibold text-[#744D03]">$1</span>'
      )
      // Pourcentages → bleu nuit
      .replace(
        /(\d+(?:[,.]\d+)?\s*%)/g,
        '<span class="font-semibold text-[#021427]">$1</span>'
      )
  );
}
</script>
