<template>
  <div class="flex h-screen bg-white overflow-hidden">
    <!-- Sidebar historique des conversations -->
    <aside
      class="w-72 border-r border-slate-200/60 flex flex-col bg-gradient-to-b from-white to-slate-50/30"
    >
      <!-- Header -->
      <div class="p-4 border-b border-slate-200/60">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <div
              class="w-8 h-8 rounded-lg bg-gradient-to-br from-bleu-nuit to-bleu-clair flex items-center justify-center"
            >
              <i class="pi pi-sparkles text-white text-sm"></i>
            </div>
            <span class="font-semibold text-bleu-nuit">Assistant IA</span>
          </div>
          <button
            @click="startNewConversation"
            class="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            title="Nouvelle conversation"
          >
            <i class="pi pi-plus text-bleu-nuit"></i>
          </button>
        </div>
      </div>

      <!-- Liste des conversations (historique) -->
      <div class="flex-1 overflow-y-auto p-3 space-y-2">
        <div
          v-if="conversationHistory.length === 0"
          class="text-center py-8 text-slate-400 text-sm"
        >
          Aucune conversation pour le moment
        </div>
        <button
          v-for="conv in conversationHistory"
          :key="conv.id"
          @click="loadConversation(conv.id)"
          :class="[
            'w-full text-left p-3 rounded-lg transition-all duration-200',
            currentConversationId === conv.id
              ? 'bg-bleu-clair/10 border border-bleu-clair/30'
              : 'hover:bg-slate-100 border border-transparent',
          ]"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-bleu-nuit truncate">
                {{ conv.title }}
              </p>
              <p class="text-xs text-slate-500 mt-1">
                {{ formatDate(conv.lastUpdate) }}
              </p>
            </div>
            <button
              @click.stop="deleteConversation(conv.id)"
              class="p-1 hover:bg-red-100 rounded text-slate-400 hover:text-red-600 transition-colors"
            >
              <i class="pi pi-trash text-xs"></i>
            </button>
          </div>
        </button>
      </div>

      <!-- Footer utilisateur -->
      <div class="p-4 border-t border-slate-200/60 bg-white">
        <div class="flex items-center gap-3">
          <div
            class="w-9 h-9 rounded-full bg-gradient-to-br from-or to-or-clair flex items-center justify-center text-white font-semibold text-sm"
          >
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-bleu-nuit truncate">
              {{ userName }}
            </p>
            <p class="text-xs text-slate-500">Gérant</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- Zone principale de chat -->
    <main class="flex-1 flex flex-col">
      <!-- Header -->
      <header
        class="h-16 border-b border-slate-200/60 px-6 flex items-center justify-between bg-white"
      >
        <div class="flex items-center gap-3">
          <i class="pi pi-comment text-bleu-nuit text-xl"></i>
          <div>
            <h1 class="text-lg font-semibold text-bleu-nuit">
              Assistant Exécutif
            </h1>
            <p class="text-xs text-slate-500">
              Analyse en temps réel de vos données
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span
            v-if="isOnline"
            class="flex items-center gap-2 text-xs text-green-600"
          >
            <span
              class="w-2 h-2 rounded-full bg-green-500 animate-pulse"
            ></span>
            En ligne
          </span>
        </div>
      </header>

      <!-- Zone de messages -->
      <div
        ref="messagesContainer"
        class="flex-1 overflow-y-auto px-6 py-6 space-y-6"
        :class="{ 'flex items-center justify-center': messages.length === 0 }"
      >
        <!-- Écran d'accueil si aucun message -->
        <div v-if="messages.length === 0" class="max-w-2xl w-full">
          <div class="text-center mb-8">
            <div
              class="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-bleu-nuit to-bleu-clair flex items-center justify-center"
            >
              <i class="pi pi-sparkles text-white text-3xl"></i>
            </div>
            <h2 class="text-2xl font-bold text-bleu-nuit mb-2">
              Bonjour {{ firstName }} 👋
            </h2>
            <p class="text-slate-600">
              Comment puis-je vous aider aujourd'hui ?
            </p>
          </div>

          <!-- Suggestions rapides -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <button
              v-for="suggestion in quickSuggestions"
              :key="suggestion.id"
              @click="handleQuickSuggestion(suggestion.text)"
              class="p-4 text-left rounded-xl border border-slate-200/60 hover:border-bleu-clair hover:bg-bleu-clair/5 transition-all duration-200 group"
            >
              <div class="flex items-start gap-3">
                <div
                  class="w-10 h-10 rounded-lg bg-gradient-to-br from-bleu-nuit/10 to-bleu-clair/10 flex items-center justify-center group-hover:from-bleu-nuit/20 group-hover:to-bleu-clair/20 transition-colors"
                >
                  <i :class="['text-bleu-nuit', suggestion.icon]"></i>
                </div>
                <div class="flex-1">
                  <p class="text-sm font-medium text-bleu-nuit mb-1">
                    {{ suggestion.title }}
                  </p>
                  <p class="text-xs text-slate-500 line-clamp-2">
                    {{ suggestion.text }}
                  </p>
                </div>
              </div>
            </button>
          </div>
          <div v-if="audioProcessing" class="mt-5 flex items-center justify-center gap-2 text-sm text-slate-500">
            <i class="pi pi-spin pi-spinner"></i> Transcription du message vocal…
          </div>
        </div>

        <!-- Liste des messages -->
        <div v-else class="max-w-4xl mx-auto w-full space-y-6">
          <AssistantMessage
            v-for="(message, index) in messages"
            :key="index"
            :message="message"
          />
          <div v-if="audioProcessing" class="flex justify-start">
            <div class="flex items-center gap-2 rounded-2xl bg-slate-100 p-4 text-slate-500">
              <i class="pi pi-spin pi-spinner"></i>
              <span class="text-sm">Transcription du message vocal…</span>
            </div>
          </div>
          <div v-if="loading" class="flex justify-start">
            <div class="max-w-[80%] bg-slate-100 rounded-2xl p-4">
              <div class="flex items-center gap-2 text-slate-500">
                <i class="pi pi-spin pi-spinner"></i>
                <span class="text-sm">L'assistant réfléchit...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Zone de saisie fixe en bas -->
      <div class="border-t border-slate-200/60 bg-white p-4">
        <div class="max-w-4xl mx-auto">
          <AssistantInput :disabled="loading || audioProcessing" :external-error="audioError" @send="handleSend" @send-audio="handleSendAudio" />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from "vue";
import { storeToRefs } from "pinia";
import { useAssistantStore } from "@/stores/assistant";
import { useAuthStore } from "@/stores/auth";
import AssistantMessage from "@/components/ia/AssistantMessage.vue";
import AssistantInput from "@/components/ia/AssistantInput.vue";
import api from "@/services/api.js";

const assistantStore = useAssistantStore();
const authStore = useAuthStore();

const {
  messages,
  isLoading: loading,
  error,
  quickSuggestions,
} = storeToRefs(assistantStore);

const inputMessage = ref("");
const messagesContainer = ref(null);
const isOnline = ref(true);
const audioProcessing = ref(false);
const audioError = ref("");

// Gestion de l'historique des conversations
const conversationHistory = ref([]);
const currentConversationId = ref(null);

// Infos utilisateur
const userName = computed(() => authStore.user?.nom_complet || "Utilisateur");
const firstName = computed(() => {
  const name = authStore.user?.nom_complet || "Utilisateur";
  return name.split(" ")[0];
});
const userInitials = computed(() => {
  const name = authStore.user?.nom_complet || "U";
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
});

// Auto-scroll vers le bas lors de nouveaux messages
watch(
  messages,
  async () => {
    await nextTick();
    scrollToBottom();
  },
  { deep: true }
);

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTo({
      top: messagesContainer.value.scrollHeight,
      behavior: "smooth",
    });
  }
};

const handleSend = async (messageText, clearDraft) => {
  // messageText vient directement de AssistantInput via emit("send", q)
  const text = (
    typeof messageText === "string" ? messageText : inputMessage.value || ""
  ).trim();
  if (!text || loading.value) return;

  inputMessage.value = "";

  const sent = await assistantStore.sendMessage(text);
  if (sent) clearDraft?.();

  // Mettre à jour la conversation actuelle
  updateCurrentConversation();
};

const handleSendAudio = async (blob, durationSeconds, clearRecording) => {
  if (!blob || loading.value || audioProcessing.value) return;
  audioProcessing.value = true;
  audioError.value = "";
  try {
    const formData = new FormData();
    const mime = blob.type?.split(";", 1)[0] || "audio/webm";
    const extension = ({ "audio/ogg": "ogg", "audio/wav": "wav", "audio/x-wav": "wav", "audio/mp4": "m4a", "audio/x-m4a": "m4a", "audio/mpeg": "mp3", "audio/mp3": "mp3" })[mime] || "webm";
    formData.append("audio", blob, `message-vocal.${extension}`);
    formData.append("duration_seconds", String(durationSeconds));
    const transcriptionResponse = await api.post("/api/assistant/audio/", formData, {
      timeout: 95000,
    });
    const transcription = String(transcriptionResponse.data?.transcription || "").trim();
    if (!transcription) throw new Error("Je n’ai pas réussi à comprendre clairement votre message vocal. Pouvez-vous réessayer ?");

    await assistantStore.sendMessage(transcription, { voiceBlob: blob, voiceDuration: durationSeconds });
    clearRecording?.();
    updateCurrentConversation();
  } catch (err) {
    audioError.value = err.response?.data?.detail || err.message || "Impossible de transcrire cet audio. Veuillez réessayer.";
  } finally {
    audioProcessing.value = false;
  }
};

const handleQuickSuggestion = async (text) => {
  if (!text || loading.value) return;
  await assistantStore.sendMessage(text.trim());
  updateCurrentConversation();
};

// Gestion de l'historique
const loadConversationHistory = () => {
  try {
    const stored = localStorage.getItem("barakagive_conversations");
    if (stored) {
      conversationHistory.value = JSON.parse(stored);
    }
  } catch (e) {
    console.error("Erreur chargement historique:", e);
  }
};

const saveConversationHistory = () => {
  try {
    localStorage.setItem(
      "barakagive_conversations",
      JSON.stringify(conversationHistory.value)
    );
  } catch (e) {
    console.error("Erreur sauvegarde historique:", e);
  }
};

const startNewConversation = () => {
  // Sauvegarder la conversation actuelle si elle existe
  if (messages.value.length > 0 && currentConversationId.value) {
    updateCurrentConversation();
  }

  // Démarrer nouvelle conversation
  currentConversationId.value = Date.now().toString();
  // Vider les messages du store (setup store Pinia — pas de $reset())
  assistantStore.messages = [];
  assistantStore.error = null;
};

const updateCurrentConversation = () => {
  if (!currentConversationId.value || messages.value.length === 0) return;

  const existingIndex = conversationHistory.value.findIndex(
    (c) => c.id === currentConversationId.value
  );

  const title =
    messages.value[0]?.content?.slice(0, 60) || "Nouvelle conversation";
  const conversation = {
    id: currentConversationId.value,
    title,
    messages: messages.value.map(({ audioUrl, audioUnavailable, ...message }) => message),
    lastUpdate: Date.now(),
  };

  if (existingIndex >= 0) {
    conversationHistory.value[existingIndex] = conversation;
  } else {
    conversationHistory.value.unshift(conversation);
  }

  // Limiter à 50 conversations
  if (conversationHistory.value.length > 50) {
    conversationHistory.value = conversationHistory.value.slice(0, 50);
  }

  saveConversationHistory();
};

const loadConversation = (id) => {
  const conv = conversationHistory.value.find((c) => c.id === id);
  if (!conv) return;

  currentConversationId.value = id;
  assistantStore.messages = [...conv.messages];
  void assistantStore.restoreVoiceAudio();
};

const deleteConversation = (id) => {
  conversationHistory.value = conversationHistory.value.filter(
    (c) => c.id !== id
  );
  saveConversationHistory();

  if (currentConversationId.value === id) {
    startNewConversation();
  }
};

const formatDate = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "À l'instant";
  if (diffMins < 60) return `Il y a ${diffMins}min`;
  if (diffHours < 24) return `Il y a ${diffHours}h`;
  if (diffDays < 7) return `Il y a ${diffDays}j`;

  return date.toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
};

onMounted(() => {
  loadConversationHistory();

  // Créer un ID de conversation si pas de messages existants
  if (!currentConversationId.value) {
    currentConversationId.value = Date.now().toString();
  }

  // Sauvegarder la conversation toutes les 30 secondes si active
  setInterval(() => {
    if (messages.value.length > 0) {
      updateCurrentConversation();
    }
  }, 30000);
});
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
