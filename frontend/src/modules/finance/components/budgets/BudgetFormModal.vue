<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="fermer"
  >
    <div
      class="bg-white border border-slate-200 rounded-2xl shadow-lg max-w-md w-full"
    >
      <!-- Header -->
      <div class="p-6 border-b border-slate-100 flex justify-between items-center">
        <div>
          <h2 class="text-xl font-bold text-bleu-nuit">
            {{ budget ? "Modifier le budget" : "Nouveau budget" }}
          </h2>
          <p class="text-sm text-slate-500 mt-1">
            {{ budget ? "Modifier les informations du budget" : "Créer un budget alloué à un projet" }}
          </p>
        </div>

      </div>

      <form @submit.prevent="submit" class="p-6 space-y-4">
        <!-- Projet -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Projet <span class="text-red-500">*</span>
          </label>
          <AsyncSearchSelect
            v-model="form.projet"
            :model-label="budget?.projet_nom || ''"
            endpoint="/api/projects/"
            label-key="name"
            value-key="id"
            placeholder="Rechercher un projet…"
          />
          <p v-if="errors.projet" class="text-xs text-red-500 mt-1">
            {{ errors.projet }}
          </p>
        </div>

        <!-- Montant -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Montant (FCFA) <span class="text-red-500">*</span>
          </label>
          <input
            v-model.number="form.montant"
            type="number"
            min="1"
            max="9999999999999.99"
            step="0.01"
            placeholder="Ex: 500000"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            :class="errors.montant ? 'border-red-400' : 'border-slate-200'"
          />
          <p v-if="errors.montant" class="text-xs text-red-500 mt-1">
            {{ errors.montant }}
          </p>
        </div>

        <!-- Source de financement -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Source de financement <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.source_financement"
            type="text"
            placeholder="Ex: Fonds propres, Subvention UE, UNICEF..."
            maxlength="255"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            :class="
              errors.source_financement ? 'border-red-400' : 'border-slate-200'
            "
          />
          <p v-if="errors.source_financement" class="text-xs text-red-500 mt-1">
            {{ errors.source_financement }}
          </p>
        </div>

        <!-- Date -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Date d'allocation <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.date"
            type="date"
            :max="dateAujourdhui"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            :class="errors.date ? 'border-red-400' : 'border-slate-200'"
          />
          <p v-if="errors.date" class="text-xs text-red-500 mt-1">
            {{ errors.date }}
          </p>
        </div>

        <!-- Observation -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Observation
            <span class="text-slate-400 font-normal normal-case"
              >(optionnel)</span
            >
          </label>
          <textarea
            v-model="form.observation"
            rows="2"
            maxlength="2000"
            placeholder="Remarques ou notes supplémentaires..."
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 resize-none"
          ></textarea>
          <p v-if="errors.observation" class="text-xs text-red-500 mt-1">{{ errors.observation }}</p>
        </div>

        <!-- Erreur générale -->
        <div
          v-if="erreurGenerale"
          class="bg-red-50 border border-red-200 rounded-lg px-3 py-2"
        >
          <p class="text-xs text-red-600 font-semibold mb-1">
            Erreur d'enregistrement
          </p>
          <p class="text-xs text-red-600">{{ erreurGenerale }}</p>
        </div>
      </form>

      <!-- Footer -->
      <div
        class="bg-white px-6 py-4 flex justify-end gap-3 border-t border-slate-100"
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
          :disabled="loading || saving"
          type="button"
          class="px-5 py-2 bg-bleu-nuit text-white rounded-lg text-sm font-semibold hover:bg-[#0a2540] transition disabled:opacity-60 flex items-center gap-2"
        >
          <span
            v-if="loading || saving"
            class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
          ></span>
          {{ loading || saving ? "Enregistrement..." : "Enregistrer" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, inject, watch } from "vue";
import AsyncSearchSelect from "@/components/ui/AsyncSearchSelect.vue";


const props = defineProps({
  ouvert: Boolean,
  budget: Object,
  erreurBackend: { type: String, default: "" },
  saving: { type: Boolean, default: false },
});
const emit = defineEmits(["fermer", "save"]);

const loading = ref(false);
const erreurGenerale = ref("");

watch(() => props.erreurBackend, (message) => {
  if (message) erreurGenerale.value = message;
});

// Utiliser le système global de connexion
const isOnline = inject("isOnline", ref(true));

const errors = reactive({
  projet: "",
  montant: "",
  source_financement: "",
  date: "",
  observation: "",
});

const form = ref({
  projet: "",
  montant: "",
  source_financement: "",
  date: "",
  observation: "",
});

const dateAujourdhui = new Date().toISOString().split("T")[0];

const resetErrors = () => {
  errors.projet = "";
  errors.montant = "";
  errors.source_financement = "";
  errors.date = "";
  errors.observation = "";
  erreurGenerale.value = "";
};

const validate = () => {
  resetErrors();
  let valid = true;

  if (!form.value.projet) {
    errors.projet = "Veuillez sélectionner un projet.";
    valid = false;
  }
  const montant = Number(form.value.montant);
  if (!form.value.montant || !Number.isFinite(montant) || montant <= 0 || montant > 9999999999999.99 || Math.round(montant * 100) !== montant * 100) {
    errors.montant = "Saisissez un montant valide supérieur à 0, dans la limite autorisée.";
    valid = false;
  }
  const source = form.value.source_financement?.trim() || "";
  if (!source || source.length > 255 || !/^[\p{L} ]+$/u.test(source)) {
    errors.source_financement = !source
      ? "La source de financement est obligatoire."
      : source.length > 255
        ? "La source ne peut pas dépasser 255 caractères."
        : "Utilisez uniquement des lettres et des espaces.";
    valid = false;
  }
  if (!form.value.date || form.value.date > dateAujourdhui) {
    errors.date = !form.value.date ? "La date est obligatoire." : "La date ne peut pas être dans le futur.";
    valid = false;
  }
  if ((form.value.observation || "").trim().length > 2000) {
    errors.observation = "L'observation ne peut pas dépasser 2 000 caractères.";
    valid = false;
  }
  return valid;
};

onMounted(async () => {
  // Pré-remplir la date à aujourd'hui ou depuis le budget existant
  if (props.budget) {
    form.value.projet = props.budget.projet_id || props.budget.projet;
    form.value.montant = props.budget.montant;
    form.value.source_financement = props.budget.source_financement;
    form.value.date = props.budget.date || dateAujourdhui;
    form.value.observation = props.budget.observation || "";
  } else {
    form.value.date = dateAujourdhui;
  }
});

const submit = async () => {
  if (loading.value || props.saving) return;
  if (!validate()) return;

  loading.value = true;
  erreurGenerale.value = "";
  try {
    const payload = {
      projet: form.value.projet, // integer PK
      montant: Number(form.value.montant), // decimal
      source_financement: form.value.source_financement.trim(),
      date: form.value.date, // YYYY-MM-DD
    };
    if (form.value.observation?.trim()) {
      payload.observation = form.value.observation.trim();
    }

    // Mode édition : inclure l'ID
    if (props.budget) {
      payload.id = props.budget.id;
    }

    // Les budgets ne disposent pas d'une file hors ligne dédiée. Ne pas
    // détourner la file des bénéficiaires : cela créerait une fausse collecte.
    if (!isOnline.value) {
      erreurGenerale.value = "Connexion indisponible : le budget n'a pas été enregistré. Rétablissez la connexion puis réessayez.";
      return;
    } else {
      // Mode en ligne - envoyer normalement
      emit("save", payload);
    }
  } catch (e) {
    console.error("Erreur lors de l'enregistrement:", e);
    erreurGenerale.value = "Une erreur inattendue s'est produite: " + e.message;
  } finally {
    loading.value = false;
  }
};

const fermer = () => {
  form.value = {
    projet: "",
    montant: "",
    source_financement: "",
    date: dateAujourdhui,
    observation: "",
  };
  resetErrors();
  emit("fermer");
};
</script>
