<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="fermer"
  >
    <div
      class="bg-white border border-slate-200 rounded-2xl shadow-lg max-w-md w-full"
    >
      <div class="p-6 border-b border-slate-100">
        <h2 class="text-xl font-bold text-bleu-nuit">
          Ajouter un justificatif
        </h2>
        <p class="text-sm text-slate-500 mt-1">
          Joindre une pièce justificative (PDF, JPG, PNG — max 10 Mo)
        </p>
        <!-- Info dépense -->
        <div
          v-if="depense"
          class="mt-3 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2"
        >
          <p class="text-xs text-slate-500">Dépense concernée</p>
          <p class="text-sm font-semibold text-bleu-nuit">
            {{ depense.reference }}
          </p>
          <p class="text-xs text-slate-500">
            {{ depense.categorie }} — {{ depense.projet_nom }}
          </p>
        </div>
      </div>

      <div class="p-6 space-y-4">
        <!-- Zone de dépôt -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-2"
          >
            Fichier <span class="text-red-500">*</span>
          </label>
          <div
            class="border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition"
            :class="
              selectedFile
                ? 'border-bleu-nuit/40 bg-bleu-nuit/5'
                : 'border-slate-200 hover:border-bleu-nuit/40 hover:bg-bleu-nuit/5'
            "
            @click="$refs.fileInput.click()"
            @dragover.prevent
            @drop.prevent="handleDrop"
          >
            <!-- Pas de fichier -->
            <div v-if="!selectedFile">
              <svg
                class="w-10 h-10 text-slate-300 mx-auto mb-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p class="text-sm text-slate-500">
                Cliquez ou glissez un fichier ici
              </p>
              <p class="text-xs text-slate-400 mt-1">
                PDF, JPG, PNG — max 10 Mo
              </p>
            </div>
            <!-- Fichier sélectionné -->
            <div v-else class="flex items-center gap-3">
              <!-- Icône selon type -->
              <div
                class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                :class="typeInfo.bg"
              >
                <span class="text-xs font-bold" :class="typeInfo.text">{{
                  typeInfo.label
                }}</span>
              </div>
              <div class="flex-1 text-left">
                <p class="text-sm font-semibold text-slate-800 truncate">
                  {{ selectedFile.name }}
                </p>
                <p class="text-xs text-slate-500">
                  {{ formatFileSize(selectedFile.size) }} • {{ typeInfo.label }}
                </p>
              </div>
              <button
                type="button"
                @click.stop="clearFile"
                class="text-slate-400 hover:text-red-500 transition p-1 rounded"
              >
                <svg
                  class="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>
          <input
            ref="fileInput"
            type="file"
            class="hidden"
            accept=".pdf,.jpg,.jpeg,.png"
            @change="handleFileChange"
          />
          <p v-if="errors.fichier" class="text-xs text-red-500 mt-1">
            {{ errors.fichier }}
          </p>
        </div>

        <!-- Erreur générale (erreurs backend) -->
        <div
          v-if="erreurBackend || erreurGenerale"
          class="bg-red-50 border border-red-200 rounded-lg px-3 py-2"
        >
          <p class="text-xs text-red-600 font-semibold mb-1">Erreur</p>
          <p class="text-xs text-red-600 whitespace-pre-line">
            {{ erreurBackend || erreurGenerale }}
          </p>
        </div>
      </div>

      <div
        class="bg-slate-50 px-6 py-4 flex justify-end gap-3 border-t border-slate-100"
      >
        <button
          @click="fermer"
          type="button"
          class="px-4 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-100 transition"
        >
          Annuler
        </button>
        <button
          @click="submit"
          :disabled="chargement || !selectedFile"
          type="button"
          class="px-5 py-2 bg-bleu-nuit text-white rounded-lg text-sm font-semibold hover:bg-[#0a2540] transition disabled:opacity-60 flex items-center gap-2"
        >
          <span
            v-if="chargement"
            class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
          ></span>
          {{ chargement ? "Téléversement..." : "Téléverser" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  ouvert: Boolean,
  depense: { type: Object, default: null },
  erreurBackend: { type: String, default: "" },
  chargement: { type: Boolean, default: false },
});
const emit = defineEmits(["fermer", "save"]);

const fileInput = ref(null);
const selectedFile = ref(null);
const erreurGenerale = ref("");
const errors = ref({ fichier: "" });

// ── Type fichier auto-détecté depuis extension ───────────────
const EXTENSIONS = {
  pdf: { label: "PDF", bg: "bg-red-50", text: "text-red-600" },
  jpg: { label: "JPG", bg: "bg-yellow-50", text: "text-yellow-700" },
  jpeg: { label: "JPG", bg: "bg-yellow-50", text: "text-yellow-700" },
  png: { label: "PNG", bg: "bg-green-50", text: "text-green-700" },
};

const getExtension = (file) =>
  file?.name?.split(".").pop()?.toLowerCase() ?? "";

const typeInfo = computed(() => {
  const ext = getExtension(selectedFile.value);
  return (
    EXTENSIONS[ext] ?? {
      label: ext.toUpperCase(),
      bg: "bg-slate-100",
      text: "text-slate-600",
    }
  );
});

// type_fichier envoyé au backend — ≤20 chars requis
const typeFichier = computed(() => {
  const ext = getExtension(selectedFile.value);
  if (ext === "jpeg") return "jpg"; // normalisation
  return ext.slice(0, 20);
});

const FORMATS_ACCEPTES = ["pdf", "jpg", "jpeg", "png"];

const validerFichier = (file) => {
  errors.value.fichier = "";
  erreurGenerale.value = "";
  if (!file) return false;
  const ext = getExtension(file);
  if (!FORMATS_ACCEPTES.includes(ext)) {
    errors.value.fichier = "Format non accepté. Utilisez PDF, JPG ou PNG.";
    return false;
  }
  if (file.size > 10 * 1024 * 1024) {
    errors.value.fichier = "Le fichier dépasse 10 Mo.";
    return false;
  }
  return true;
};

const handleFileChange = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  if (validerFichier(file)) selectedFile.value = file;
  else {
    selectedFile.value = null;
    e.target.value = "";
  }
};

const handleDrop = (e) => {
  const file = e.dataTransfer.files[0];
  if (!file) return;
  if (validerFichier(file)) selectedFile.value = file;
  else selectedFile.value = null;
};

const clearFile = () => {
  selectedFile.value = null;
  errors.value.fichier = "";
  if (fileInput.value) fileInput.value.value = "";
};

const formatFileSize = (bytes) => {
  if (!bytes) return "0 B";
  const k = 1024,
    sizes = ["B", "KB", "MB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return (bytes / Math.pow(k, i)).toFixed(1) + " " + sizes[i];
};

const submit = async () => {
  if (props.chargement) return;
  if (!selectedFile.value) {
    errors.value.fichier = "Veuillez sélectionner un fichier.";
    return;
  }
  if (!validerFichier(selectedFile.value)) return;

  erreurGenerale.value = "";
  emit("save", {
    depenseId: props.depense?.id,
    file: selectedFile.value,
    type_fichier: typeFichier.value,
  });
};

const fermer = () => {
  clearFile();
  erreurGenerale.value = "";
  emit("fermer");
};
</script>
