<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs"
    @click.self="fermer"
  >
    <div
      class="bg-white border border-slate-200 rounded-2xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
    >
      <div
        class="p-6 border-b border-slate-100 flex justify-between items-center"
      >
        <div>
          <h2 class="text-xl font-bold text-bleu-nuit">
            {{ don ? "Modifier le don" : "Nouveau don" }}
          </h2>
          <p class="text-sm text-slate-500 mt-1">
            {{
              don
                ? "Modifiez les informations du financement reçu"
                : "Enregistrer un financement reçu pour votre organisation"
            }}
          </p>
        </div>
        <button
          @click="fermer"
          class="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition"
        >
          <X :size="20" />
        </button>
      </div>

      <form @submit.prevent="submit" class="p-6 space-y-4">
        <!-- Donateur -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Donateur <span class="text-red-500">*</span>
          </label>

          <AsyncSearchSelect
            v-model="form.donateur"
            :model-label="don?.donateur_nom || ''"
            endpoint="/api/finance/donateurs/"
            label-key="nom"
            value-key="id"
            placeholder="Rechercher un donateur…"
            manual-option="Créer un nouveau donateur"
          />

          <!-- Saisie libre si "Autre" ou saisie manuelle -->
          <input
            v-if="form.donateur === '__autre__'"
            v-model="form.donateurLibre"
            type="text"
            minlength="2"
            placeholder="Nom du donateur"
            maxlength="255"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 mt-2"
            :class="errors.donateur ? 'border-red-400' : 'border-slate-200'"
          />

          <p v-if="errors.donateur" class="text-xs text-red-500 mt-1">
            {{ errors.donateur }}
          </p>
        </div>

        <!-- Campagne (optionnel) -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Campagne
            <span class="text-slate-400 font-normal normal-case ml-1"
              >(optionnel)</span
            >
          </label>
          <AsyncSearchSelect
            v-model="form.campagne"
            :model-label="don?.campagne_nom || ''"
            endpoint="/api/campaigns/"
            label-key="nom"
            value-key="id"
            placeholder="Rechercher une campagne (optionnel)…"
          />
          <button v-if="form.campagne" type="button" class="mt-1 text-xs text-slate-500 underline" @click="form.campagne = ''">Effacer la campagne</button>
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
            placeholder="Ex : 1000000"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            :class="errors.montant ? 'border-red-400' : 'border-slate-200'"
          />
          <p v-if="errors.montant" class="text-xs text-red-500 mt-1">
            {{ errors.montant }}
          </p>
        </div>

        <!-- Moyen de paiement -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Moyen de paiement <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.moyen_paiement"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
          >
            <option value="VIREMENT">Virement bancaire</option>
            <option value="ESPECE">Espèce</option>
            <option value="CHEQUE">Chèque</option>
            <option value="CARTE">Carte bancaire</option>
          </select>
        </div>

        <!-- Date -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Date de réception <span class="text-red-500">*</span>
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
            <span class="text-slate-400 font-normal normal-case ml-1"
              >(optionnel)</span
            >
          </label>
          <textarea
            v-model="form.observation"
            rows="2"
            maxlength="2000"
            placeholder="Notes ou remarques..."
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
          {{ loading || saving ? "Enregistrement..." : don ? "Mettre à jour" : "Enregistrer" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from "vue";
import { X } from "lucide-vue-next";
import AsyncSearchSelect from "@/components/ui/AsyncSearchSelect.vue";
import { financeService } from "@/modules/finance/services/financeService.js";

const props = defineProps({
  ouvert: { type: Boolean, default: false },
  don: { type: Object, default: null },
  erreurBackend: { type: String, default: "" },
  saving: { type: Boolean, default: false },
});

const emit = defineEmits(["fermer", "save"]);

const loading = ref(false);
const erreurGenerale = ref("");

const errors = reactive({
  donateur: "",
  montant: "",
  date: "",
  observation: "",
});

const dateAujourdhui = new Date().toISOString().split("T")[0];

const form = ref({
  donateur: "",
  donateurLibre: "",
  campagne: "",
  montant: "",
  moyen_paiement: "VIREMENT",
  date: dateAujourdhui,
  observation: "",
});

watch(
  () => props.erreurBackend,
  (val) => {
    if (val) erreurGenerale.value = val;
  }
);

const initForm = () => {
  resetErrors();
  erreurGenerale.value = "";
  if (props.don) {
    form.value = {
      donateur: props.don.donateur_id || props.don.donateur?.id || props.don.donateur || "",
      donateurLibre: "",
      campagne: props.don.campagne_id || props.don.campagne?.id || props.don.campagne || "",
      montant: props.don.montant || "",
      moyen_paiement: props.don.moyen_paiement || "VIREMENT",
      date: props.don.date || dateAujourdhui,
      observation: props.don.observation || "",
    };
  } else {
    form.value = {
      donateur: "",
      donateurLibre: "",
      campagne: "",
      montant: "",
      moyen_paiement: "VIREMENT",
      date: dateAujourdhui,
      observation: "",
    };
  }
};

watch(
  () => props.ouvert,
  (val) => {
    if (val) {
      initForm();
    }
  }
);

watch(
  () => props.don,
  () => {
    if (props.ouvert) initForm();
  }
);

const donateurNom = computed(() => {
  if (form.value.donateur === "__autre__") {
    return form.value.donateurLibre.trim();
  }
  return "";
});

const resetErrors = () => {
  errors.donateur = "";
  errors.montant = "";
  errors.date = "";
  errors.observation = "";
  erreurGenerale.value = "";
};

const validate = () => {
  resetErrors();
  let valid = true;

  if (!form.value.donateur) {
    errors.donateur = "Veuillez sélectionner ou créer un donateur.";
    valid = false;
  } else if (form.value.donateur === "__autre__" && (donateurNom.value.length < 2 || donateurNom.value.length > 255)) {
    errors.donateur = "Le nom du donateur doit contenir entre 2 et 255 caractères.";
    valid = false;
  }
  const montant = Number(form.value.montant);
  if (!form.value.montant || !Number.isFinite(montant) || montant <= 0 || montant > 9999999999999.99 || Math.round(montant * 100) !== montant * 100) {
    errors.montant = "Saisissez un montant valide supérieur à 0, dans la limite autorisée.";
    valid = false;
  }
  if (!form.value.date || form.value.date > dateAujourdhui) {
    errors.date = !form.value.date ? "La date est obligatoire." : "La date ne peut pas être dans le futur.";
    valid = false;
  }
  if (!["VIREMENT", "ESPECE", "CHEQUE", "CARTE"].includes(form.value.moyen_paiement)) {
    erreurGenerale.value = "Sélectionnez un moyen de paiement valide.";
    valid = false;
  }
  if ((form.value.observation || "").trim().length > 2000) {
    errors.observation = "L'observation ne peut pas dépasser 2 000 caractères.";
    valid = false;
  }
  return valid;
};

onMounted(() => {
  if (props.ouvert) initForm();
});

const submit = async () => {
  if (loading.value || props.saving) return;
  if (!validate()) return;
  loading.value = true;
  erreurGenerale.value = "";
  try {
    let donateurId = form.value.donateur;
    if (donateurId === "__autre__") {
      const response = await financeService.createDonor({ nom: donateurNom.value });
      donateurId = response.data.id;
    }
    const payload = {
      donateur: donateurId,
      montant: Number(form.value.montant),
      moyen_paiement: form.value.moyen_paiement,
      date: form.value.date,
    };
    if (form.value.campagne) payload.campagne = form.value.campagne;
    if (form.value.observation?.trim())
      payload.observation = form.value.observation.trim();

    if (props.don?.id) {
      payload.id = props.don.id;
    }

    emit("save", payload);
  } catch (error) {
    console.error("Erreur lors de l'enregistrement:", error);
    erreurGenerale.value = "Erreur lors de l'enregistrement: " + error.message;
  } finally {
    loading.value = false;
  }
};

const fermer = () => {
  form.value = {
    donateur: "",
    donateurLibre: "",
    campagne: "",
    montant: "",
    moyen_paiement: "VIREMENT",
    date: dateAujourdhui,
    observation: "",
  };
  resetErrors();
  emit("fermer");
};
</script>
