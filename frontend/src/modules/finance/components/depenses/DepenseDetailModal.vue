<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="$emit('fermer')"
  >
    <div
      class="bg-white border border-slate-200 rounded-2xl shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
    >
      <!-- Header -->
      <div
        class="p-6 border-b border-slate-100 flex items-start justify-between"
      >
        <div>
          <h2 class="text-xl font-bold text-bleu-nuit">
            {{ isEditing ? "Modifier la dépense" : "Détail de la dépense" }}
          </h2>
          <p class="text-sm text-slate-500 mt-1 font-mono">
            {{ depense.reference }}
          </p>
        </div>
        <button
          @click="$emit('fermer')"
          class="text-slate-400 hover:text-slate-600 transition p-1"
        >
          <X :size="20" />
        </button>
      </div>

      <!-- Mode Lecture -->
      <div v-if="!isEditing" class="p-6 space-y-5">
        <!-- Infos principales -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Projet</p>
            <p class="text-sm font-semibold text-slate-900 mt-1">
              {{ depense.projet_nom || "—" }}
            </p>
          </div>
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Campagne</p>
            <p class="text-sm font-semibold text-slate-900 mt-1">
              {{ depense.campagne_nom || "—" }}
            </p>
          </div>
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Catégorie</p>
            <p class="text-sm text-slate-700 mt-1">{{ depense.categorie }}</p>
          </div>
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">
              Fournisseur
            </p>
            <p class="text-sm text-slate-700 mt-1">
              {{ depense.fournisseur || "—" }}
            </p>
          </div>
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Montant</p>
            <p class="text-sm font-bold text-red-500 mt-1">
              -{{ formatMontant(depense.montant) }} FCFA
            </p>
          </div>
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Date</p>
            <p class="text-sm text-slate-700 mt-1">{{ depense.date }}</p>
          </div>
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Statut</p>
            <p class="mt-1">
              <span
                class="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-full"
                :class="statutClass(depense.statut)"
              >
                {{ depense.statut }}
              </span>
            </p>
          </div>
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Région</p>
            <p class="text-sm text-slate-700 mt-1">
              {{ depense.region_nom || "—" }}
            </p>
          </div>
        </div>

        <!-- Description -->
        <div v-if="depense.description">
          <p class="text-xs font-bold uppercase text-slate-500">Description</p>
          <p class="text-sm text-slate-600 mt-1 whitespace-pre-line">
            {{ depense.description }}
          </p>
        </div>

        <!-- Justifications -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <p class="text-xs font-bold uppercase text-slate-500">
              Justificatifs ({{ justifications.length }})
            </p>
            <button
              @click="showUpload = true"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-bleu-nuit/10 text-bleu-nuit hover:bg-bleu-nuit/20 transition"
            >
              <Upload :size="14" /> Ajouter
            </button>
          </div>

          <!-- Liste justifications -->
          <div v-if="justifications.length > 0" class="space-y-2">
            <div
              v-for="justif in justifications"
              :key="justif.id"
              class="flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2.5"
            >
              <div
                class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                :class="typeFileClass(justif.type_fichier)"
              >
                <span class="text-[10px] font-bold uppercase">
                  {{ justif.type_fichier }}
                </span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-slate-800 truncate">
                  {{ justif.fichier?.split("/").pop() || "Fichier" }}
                </p>
                <p class="text-xs text-slate-400">
                  {{ justif.created_at?.slice(0, 10) }} •
                  <span
                    class="font-semibold"
                    :class="justifStatutColor(justif.statut)"
                  >
                    {{ justif.statut }}
                  </span>
                </p>
              </div>
              <div class="flex items-center gap-1.5">
                <a
                  v-if="justif.url"
                  :href="justif.url"
                  target="_blank"
                  class="p-1.5 rounded hover:bg-bleu-nuit/10 text-bleu-nuit transition"
                  title="Voir"
                >
                  <ExternalLink :size="14" />
                </a>
                <button
                  @click="handleDeleteJustification(justif.id)"
                  class="p-1.5 rounded hover:bg-red-50 text-red-400 hover:text-red-600 transition"
                  title="Supprimer"
                  :disabled="deletingJustif"
                >
                  <Trash2 :size="14" />
                </button>
              </div>
            </div>
          </div>
          <div
            v-else
            class="bg-amber-50 border border-amber-200 rounded-lg px-3 py-3 text-center"
          >
            <p class="text-xs text-amber-700 font-medium">
              Aucun justificatif. Ajoutez un document pour valider cette
              dépense.
            </p>
          </div>

          <!-- Zone upload inline -->
          <div
            v-if="showUpload"
            class="mt-3 bg-slate-50 border border-slate-200 rounded-lg p-4"
          >
            <div
              class="border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition"
              :class="
                uploadFile
                  ? 'border-bleu-nuit/40 bg-bleu-nuit/5'
                  : 'border-slate-200 hover:border-bleu-nuit/40'
              "
              @click="$refs.fileInput.click()"
              @dragover.prevent
              @drop.prevent="onDrop"
            >
              <p v-if="!uploadFile" class="text-sm text-slate-500">
                Cliquez ou glissez un fichier (PDF, JPG, PNG — max 10 Mo)
              </p>
              <div v-else class="flex items-center gap-2 justify-center">
                <span class="text-sm font-semibold text-bleu-nuit">{{
                  uploadFile.name
                }}</span>
                <button
                  @click.stop="uploadFile = null"
                  class="text-red-400 hover:text-red-600"
                >
                  <X :size="14" />
                </button>
              </div>
            </div>
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              accept=".pdf,.jpg,.jpeg,.png"
              @change="uploadFile = $event.target.files[0]"
            />
            <div class="flex justify-end gap-2 mt-3">
              <button
                @click="
                  showUpload = false;
                  uploadFile = null;
                "
                class="px-3 py-1.5 text-xs font-medium text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-100 transition"
              >
                Annuler
              </button>
              <button
                @click="handleUpload"
                :disabled="!uploadFile || uploading"
                class="px-4 py-1.5 text-xs font-semibold text-white bg-bleu-nuit rounded-lg hover:bg-[#0a2540] transition disabled:opacity-60"
              >
                {{ uploading ? "Envoi..." : "Téléverser" }}
              </button>
            </div>
            <p v-if="uploadError" class="text-xs text-red-500 mt-2">
              {{ uploadError }}
            </p>
          </div>
        </div>
      </div>

      <!-- Mode Édition -->
      <div v-else class="p-6 space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label
              class="block text-xs font-semibold uppercase text-slate-600 mb-1"
            >
              Catégorie <span class="text-red-500">*</span>
            </label>
            <input
              v-model="editForm.categorie"
              type="text"
              placeholder="Ex: Transport, Matériel..."
              class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 transition"
              :class="
                !editForm.categorie?.trim() && editError
                  ? 'border-red-400 bg-red-50'
                  : 'border-slate-200'
              "
            />
          </div>
          <div>
            <label
              class="block text-xs font-semibold uppercase text-slate-600 mb-1"
            >
              Fournisseur
            </label>
            <input
              v-model="editForm.fournisseur"
              type="text"
              class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            />
          </div>
          <div>
            <label
              class="block text-xs font-semibold uppercase text-slate-600 mb-1"
            >
              Montant <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="editForm.montant"
              type="number"
              min="1"
              class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 transition"
              :class="
                (!editForm.montant || editForm.montant <= 0) && editError
                  ? 'border-red-400 bg-red-50'
                  : 'border-slate-200'
              "
            />
          </div>
          <div>
            <label
              class="block text-xs font-semibold uppercase text-slate-600 mb-1"
            >
              Date <span class="text-red-500">*</span>
            </label>
            <input
              v-model="editForm.date"
              type="date"
              class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 transition"
              :class="
                !editForm.date && editError
                  ? 'border-red-400 bg-red-50'
                  : 'border-slate-200'
              "
            />
          </div>
        </div>
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Description
          </label>
          <textarea
            v-model="editForm.description"
            rows="3"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 resize-none"
          ></textarea>
        </div>
        <p
          v-if="editError"
          class="text-xs text-red-500 bg-red-50 border border-red-200 rounded-lg px-3 py-2"
        >
          {{ editError }}
        </p>
      </div>

      <!-- Footer actions -->
      <div
        class="bg-slate-50 px-6 py-4 flex justify-between border-t border-slate-100"
      >
        <div>
          <button
            v-if="!isEditing"
            @click="confirmDelete = true"
            class="px-4 py-2 text-sm font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition"
          >
            <Trash2 :size="14" class="inline mr-1" /> Supprimer
          </button>
        </div>
        <div class="flex gap-3">
          <button
            v-if="!isEditing"
            @click="startEdit"
            class="px-4 py-2 text-sm font-medium text-bleu-nuit border border-bleu-nuit/20 rounded-lg hover:bg-bleu-nuit/10 transition"
          >
            <Pencil :size="14" class="inline mr-1" /> Modifier
          </button>
          <button
            v-if="isEditing"
            @click="isEditing = false"
            class="px-4 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-100 transition"
          >
            Annuler
          </button>
          <button
            v-if="isEditing"
            @click="saveEdit"
            :disabled="saving"
            class="px-5 py-2 bg-bleu-nuit text-white rounded-lg text-sm font-semibold hover:bg-[#0a2540] transition disabled:opacity-60"
          >
            {{ saving ? "Enregistrement..." : "Enregistrer" }}
          </button>
          <button
            v-if="!isEditing"
            @click="$emit('fermer')"
            class="px-4 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-100 transition"
          >
            Fermer
          </button>
        </div>
      </div>

      <!-- Confirmation suppression -->
      <div
        v-if="confirmDelete"
        class="fixed inset-0 z-[60] flex items-center justify-center bg-black/40"
        @click.self="confirmDelete = false"
      >
        <div class="bg-white rounded-xl shadow-lg p-6 max-w-sm w-full mx-4">
          <h3 class="text-lg font-bold text-slate-900 mb-2">
            Confirmer la suppression
          </h3>
          <p class="text-sm text-slate-600 mb-4">
            Voulez-vous vraiment supprimer la dépense
            <strong>{{ depense.reference }}</strong> ? Cette action est
            irréversible.
          </p>
          <div class="flex justify-end gap-3">
            <button
              @click="confirmDelete = false"
              class="px-4 py-2 text-sm border border-slate-200 rounded-lg text-slate-700 hover:bg-slate-100 transition"
            >
              Annuler
            </button>
            <button
              @click="handleDelete"
              :disabled="deleting"
              class="px-4 py-2 text-sm font-semibold text-white bg-red-600 rounded-lg hover:bg-red-700 transition disabled:opacity-60"
            >
              {{ deleting ? "Suppression..." : "Supprimer" }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { X, Upload, ExternalLink, Trash2, Pencil } from "lucide-vue-next";
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js";
import { parseApiError } from "@/modules/finance/utils/parseApiError.js";

const props = defineProps({
  ouvert: Boolean,
  depense: { type: Object, required: true },
});
const emit = defineEmits(["fermer", "deleted"]);

const store = useFinanceStore();

// -- State
const isEditing = ref(false);
const saving = ref(false);
const editError = ref("");
const editForm = ref({});

const confirmDelete = ref(false);
const deleting = ref(false);

const showUpload = ref(false);
const uploadFile = ref(null);
const uploading = ref(false);
const uploadError = ref("");
const deletingJustif = ref(false);

// -- Computed
const justifications = computed(() => props.depense?.justifications || []);

const formatMontant = (v) => Number(v || 0).toLocaleString("fr-FR");

const statutClass = (s) => {
  const map = {
    EN_ATTENTE: "bg-amber-100 text-amber-700",
    VERIFIE: "bg-bleu-accent/10 text-or",
    APPROUVE: "bg-emerald-100 text-emerald-700",
    REJETE: "bg-red-100 text-red-700",
  };
  return map[s] || "bg-slate-100 text-slate-600";
};

const typeFileClass = (type) => {
  const map = {
    pdf: "bg-red-50 text-red-600",
    jpg: "bg-yellow-50 text-yellow-700",
    png: "bg-green-50 text-green-700",
  };
  return map[type] || "bg-slate-100 text-slate-600";
};

const justifStatutColor = (s) => {
  const map = {
    CONFORME: "text-emerald-600",
    A_VERIFIER: "text-amber-600",
    NON_CONFORME: "text-red-600",
  };
  return map[s] || "text-slate-500";
};

// -- Edit
const startEdit = () => {
  editForm.value = {
    categorie: props.depense.categorie,
    fournisseur: props.depense.fournisseur || "",
    montant: props.depense.montant,
    date: props.depense.date,
    description: props.depense.description || "",
  };
  editError.value = "";
  isEditing.value = true;
};

const saveEdit = async () => {
  // Validation
  editError.value = "";
  if (!editForm.value.categorie?.trim()) {
    editError.value = "La catégorie est obligatoire.";
    return;
  }
  const montant = Number(editForm.value.montant);
  if (!editForm.value.montant || !Number.isFinite(montant) || montant <= 0 || montant > 9999999999999.99) {
    editError.value = "Saisissez un montant valide supérieur à 0, dans la limite autorisée.";
    return;
  }
  if (!editForm.value.date) {
    editError.value = "La date est obligatoire.";
    return;
  }

  saving.value = true;
  try {
    await store.updateExpense(props.depense.id, editForm.value);
    isEditing.value = false;
    emit("fermer");
  } catch (e) {
    editError.value = parseApiError(e);
  } finally {
    saving.value = false;
  }
};

// -- Delete
const handleDelete = async () => {
  deleting.value = true;
  try {
    await store.deleteExpense(props.depense.id);
    confirmDelete.value = false;
    emit("deleted");
    emit("fermer");
  } catch (e) {
    // silent
  } finally {
    deleting.value = false;
  }
};

// -- Upload Justification
const onDrop = (e) => {
  const file = e.dataTransfer.files[0];
  if (file) uploadFile.value = file;
};

const handleUpload = async () => {
  if (!uploadFile.value) return;
  uploading.value = true;
  uploadError.value = "";
  try {
    const ext = uploadFile.value.name.split(".").pop().toLowerCase();
    const typeFichier = ext === "jpeg" ? "jpg" : ext.slice(0, 20);
    await store.uploadJustification(
      props.depense.id,
      uploadFile.value,
      typeFichier
    );
    uploadFile.value = null;
    showUpload.value = false;
    // Refresh will be triggered by store
  } catch (e) {
    uploadError.value = parseApiError(e);
  } finally {
    uploading.value = false;
  }
};

// -- Delete Justification
const handleDeleteJustification = async (justifId) => {
  if (!confirm("Supprimer ce justificatif ?")) return;
  deletingJustif.value = true;
  try {
    await store.deleteJustification(justifId);
  } catch (e) {
    // silent
  } finally {
    deletingJustif.value = false;
  }
};
</script>
