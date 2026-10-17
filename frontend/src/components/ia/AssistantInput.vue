<template>
  <div class="border-t border-slate-200 bg-white px-3 py-3 sm:px-4">
    <div v-if="recording" class="rounded-2xl border border-rose-200 bg-rose-50/70 p-3 sm:p-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-2 text-sm font-semibold text-slate-800">
          <span class="relative flex h-3 w-3">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-rose-500 opacity-50"></span>
            <span class="relative inline-flex h-3 w-3 rounded-full bg-rose-600"></span>
          </span>
          Enregistrement en cours
          <span class="font-mono tabular-nums text-slate-600">{{ formatDuration(recordingSeconds) }}</span>
        </div>
        <div class="flex items-center gap-2">
          <button type="button" class="rounded-xl px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-white" @click="cancelRecording">Annuler</button>
          <button type="button" class="rounded-xl bg-[#021427] px-3 py-2 text-xs font-semibold text-white hover:bg-[#032040]" @click="finishRecording">Terminer</button>
        </div>
      </div>
      <div class="mt-3 flex h-7 items-center gap-1 overflow-hidden" aria-hidden="true">
        <span v-for="bar in waveformBars" :key="bar" class="w-1 rounded-full bg-rose-400 animate-pulse" :style="{ height: `${10 + ((bar * 17 + recordingSeconds * 11) % 18)}px`, animationDelay: `${bar * 35}ms` }"></span>
      </div>
      <p v-if="recordingSeconds >= maxDurationSeconds" class="mt-2 text-xs text-slate-600">Durée maximale atteinte. Écoutez l’enregistrement avant de l’envoyer.</p>
    </div>

    <div v-else-if="recordedUrl && recordedBlob" class="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2 sm:gap-3 sm:p-3">
      <audio ref="previewAudio" :src="recordedUrl" controls class="min-w-[180px] flex-1" aria-label="Écouter le message vocal avant envoi"></audio>
      <span class="font-mono text-xs tabular-nums text-slate-500">{{ formatDuration(recordingSeconds) }}</span>
      <button type="button" :disabled="disabled" class="flex h-10 w-10 items-center justify-center rounded-xl text-slate-500 hover:bg-white hover:text-rose-600 disabled:opacity-40" aria-label="Supprimer l’enregistrement" title="Supprimer" @click="discardRecording">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18M8 6V4h8v2m3 0-1 14H6L5 6m4 4v6m6-6v6"/></svg>
      </button>
      <button type="button" :disabled="disabled || !recordedBlob" class="flex h-10 w-10 items-center justify-center rounded-xl bg-[#021427] text-white hover:bg-[#032040] disabled:opacity-40" aria-label="Envoyer le message vocal" title="Envoyer le vocal" @click="sendRecording">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
      </button>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="flex items-end gap-2 sm:gap-3">
      <div class="relative min-w-0 flex-1 rounded-2xl border border-slate-200 bg-slate-50 transition-all duration-200 focus-within:border-[#CCA43B]/60 focus-within:ring-2 focus-within:ring-[#CCA43B]/20">
        <textarea ref="textareaRef" v-model="draft" maxlength="4000" :disabled="disabled" placeholder="Écrire un message…" rows="1" class="min-h-[44px] max-h-[140px] w-full resize-none rounded-2xl bg-transparent px-4 py-3 text-sm leading-relaxed text-slate-800 placeholder:text-slate-400 focus:outline-none" @keydown.enter.exact.prevent="handleSubmit" @input="autoResize" />
      </div>

      <button type="button" :disabled="disabled || !recordingSupported" :aria-label="recordingSupported ? 'Enregistrer un message vocal' : 'Enregistrement audio indisponible dans ce navigateur'" :title="recordingSupported ? 'Enregistrer un message vocal' : 'Enregistrement audio indisponible dans ce navigateur'" class="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl border border-slate-200 bg-white text-[#021427] transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-[#CCA43B]/40 disabled:cursor-not-allowed disabled:opacity-40" @click="startRecording">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="2" width="6" height="13" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3m-4 0h8"/></svg>
      </button>

      <button type="submit" :disabled="!canSend" class="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#CCA43B]/40" :class="canSend ? 'cursor-pointer bg-[#021427] hover:bg-[#032040]' : 'cursor-not-allowed bg-slate-200'" aria-label="Envoyer">
        <svg v-if="disabled" class="h-5 w-5 animate-spin text-slate-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.4 0 0 5.4 0 12h4z"/></svg>
        <svg v-else class="h-5 w-5" :class="canSend ? 'text-[#CCA43B]' : 'text-slate-400'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
      </button>
    </form>

    <p v-if="voiceError || externalError" role="status" class="mt-2 text-center text-xs text-rose-600">{{ voiceError || externalError }}</p>
    <p v-else-if="!recording" class="mt-2 text-center text-[10px] text-slate-400">Entrée pour envoyer · Maj+Entrée pour une nouvelle ligne · Le vocal est transcrit avant envoi</p>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onBeforeUnmount } from "vue";

const props = defineProps({
  disabled: { type: Boolean, default: false },
  externalError: { type: String, default: "" },
});
const emit = defineEmits(["send", "send-audio"]);
const MAX_AUDIO_BYTES = 15 * 1024 * 1024;
const maxDurationSeconds = 120;
const waveformBars = Array.from({ length: 32 }, (_, index) => index + 1);

const draft = ref("");
const textareaRef = ref(null);
const previewAudio = ref(null);
const recording = ref(false);
const recordingSeconds = ref(0);
const recordedBlob = ref(null);
const recordedUrl = ref("");
const voiceError = ref("");
const recordingSupported = computed(() => typeof window !== "undefined" && Boolean(navigator.mediaDevices?.getUserMedia && window.MediaRecorder));

let recorder = null;
let mediaStream = null;
let recordingTimer = null;
let chunks = [];
let cancelOnStop = false;

const canSend = computed(() => !props.disabled && draft.value.trim().length > 0);
const formatDuration = seconds => `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;

const autoResize = () => {
  const element = textareaRef.value;
  if (!element) return;
  element.style.height = "auto";
  element.style.height = `${Math.min(element.scrollHeight, 140)}px`;
};

const stopTracks = () => {
  mediaStream?.getTracks().forEach(track => track.stop());
  mediaStream = null;
};

const clearTimer = () => {
  if (recordingTimer) clearInterval(recordingTimer);
  recordingTimer = null;
};

const finalizeRecording = () => {
  clearTimer();
  stopTracks();
  recording.value = false;
  if (cancelOnStop) {
    cancelOnStop = false;
    chunks = [];
    return;
  }
  const blob = new Blob(chunks, { type: recorder?.mimeType || "audio/webm" });
  chunks = [];
  if (!blob.size) {
    voiceError.value = "L’enregistrement est vide. Réessayez.";
    return;
  }
  if (blob.size > MAX_AUDIO_BYTES) {
    voiceError.value = "Le fichier audio est trop volumineux. Enregistrez un message plus court.";
    return;
  }
  recordingSeconds.value = Math.max(1, recordingSeconds.value);
  recordedBlob.value = blob;
  recordedUrl.value = URL.createObjectURL(blob);
};

const startRecording = async () => {
  if (!recordingSupported.value || props.disabled) {
    voiceError.value = "L’enregistrement audio n’est pas pris en charge par ce navigateur.";
    return;
  }
  voiceError.value = "";
  discardRecording();
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mimeType = ["audio/webm;codecs=opus", "audio/ogg;codecs=opus", "audio/mp4", "audio/webm"]
      .find(type => MediaRecorder.isTypeSupported?.(type));
    recorder = new MediaRecorder(mediaStream, mimeType ? { mimeType } : undefined);
    chunks = [];
    cancelOnStop = false;
    recorder.ondataavailable = event => { if (event.data?.size) chunks.push(event.data); };
    recorder.onstop = finalizeRecording;
    recorder.onerror = () => {
      voiceError.value = "L’enregistrement a échoué. Vérifiez l’accès au microphone.";
      stopTracks();
      clearTimer();
      recording.value = false;
    };
    recorder.start(250);
    recording.value = true;
    recordingSeconds.value = 0;
    recordingTimer = setInterval(() => {
      recordingSeconds.value += 1;
      if (recordingSeconds.value >= maxDurationSeconds) finishRecording();
    }, 1000);
  } catch (error) {
    stopTracks();
    voiceError.value = error?.name === "NotAllowedError"
      ? "Autorisez l’accès au microphone dans votre navigateur."
      : "Impossible d’accéder au microphone. Vérifiez son branchement et réessayez.";
  }
};

const finishRecording = () => {
  if (recorder?.state === "recording") recorder.stop();
};

const cancelRecording = () => {
  cancelOnStop = true;
  if (recorder?.state === "recording") recorder.stop();
  else {
    clearTimer();
    stopTracks();
    recording.value = false;
  }
  recordingSeconds.value = 0;
};

const discardRecording = () => {
  if (recordedUrl.value) URL.revokeObjectURL(recordedUrl.value);
  recordedUrl.value = "";
  recordedBlob.value = null;
  if (previewAudio.value) previewAudio.value.currentTime = 0;
};

const sendRecording = () => {
  if (!recordedBlob.value || props.disabled) return;
  emit("send-audio", recordedBlob.value, recordingSeconds.value, () => {
    discardRecording();
    recordingSeconds.value = 0;
  });
};

const handleSubmit = () => {
  if (!canSend.value) return;
  const question = draft.value.trim();
  emit("send", question, () => {
    if (draft.value.trim() !== question) return;
    draft.value = "";
    nextTick(() => { if (textareaRef.value) textareaRef.value.style.height = "auto"; });
  });
};

const focus = () => nextTick(() => textareaRef.value?.focus());
defineExpose({ focus });

onBeforeUnmount(() => {
  cancelOnStop = true;
  if (recorder?.state === "recording") recorder.stop();
  clearTimer();
  stopTracks();
  discardRecording();
});
</script>
