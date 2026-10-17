<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs"
    @click.self="fermer"
  >
    <div
      class="bg-white border border-slate-200/80 rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
    >
      <!-- En-tête -->
      <div
        class="p-6 border-b border-slate-100 flex items-center justify-between"
      >
        <div>
          <h2 class="text-xl font-bold text-bleu-nuit">
            {{ projet ? "Modifier le projet" : "Nouveau projet humanitaire" }}
          </h2>
          <p class="text-xs text-slate-500 mt-1">
            {{
              projet
                ? "Mettez à jour les informations du projet."
                : "Créez un nouveau projet humanitaire pour votre ONG."
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

      <!-- Alerte Erreur -->
      <div v-if="erreurGlobale" class="p-6 pb-0">
        <AlertMessage
          type="error"
          :message="erreurGlobale"
          :dismissible="true"
          @dismiss="erreurGlobale = ''"
        />
      </div>

      <!-- Formulaire -->
      <form @submit.prevent="submit" class="p-6 space-y-4">
        <!-- Nom du projet -->
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">
            Nom du projet <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.name"
            type="text"
            placeholder="Ex : Programme de Secours Alimentaire et Nutrition 2026"
            class="w-full border rounded-lg px-3.5 py-2.5 text-sm outline-none transition focus:ring-2"
            :class="
              fErr.name
                ? 'border-red-400 bg-red-50/30 focus:ring-red-500/20'
                : 'border-slate-200 focus:ring-bleu-nuit/30'
            "
          />
          <p v-if="fErr.name" class="text-xs text-red-500 mt-1">
            {{ fErr.name }}
          </p>
        </div>

        <!-- Région & Budget -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">
              Région d'intervention <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.region"
              class="w-full border rounded-lg px-3.5 py-2.5 text-sm outline-none transition bg-white focus:ring-2"
              :class="
                fErr.region
                  ? 'border-red-400 bg-red-50/30 focus:ring-red-500/20'
                  : 'border-slate-200 focus:ring-bleu-nuit/30'
              "
            >
              <option value="">Sélectionner une région...</option>
              <option v-for="r in senegalRegions" :key="r" :value="r">
                {{ r }}
              </option>
            </select>
            <p v-if="fErr.region" class="text-xs text-red-500 mt-1">
              {{ fErr.region }}
            </p>
          </div>

          <div>
            <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">
              Budget alloué (FCFA)
            </label>
            <input
              v-model.number="form.budget"
              type="number"
              min="0"
              max="9999999999999.99"
              step="0.01"
              placeholder="Ex : 25000000"
              class="w-full border rounded-lg px-3.5 py-2.5 text-sm outline-none transition focus:ring-2"
              :class="
                fErr.budget
                  ? 'border-red-400 bg-red-50/30 focus:ring-red-500/20'
                  : 'border-slate-200 focus:ring-bleu-nuit/30'
              "
            />
            <p v-if="fErr.budget" class="text-xs text-red-500 mt-1">
              {{ fErr.budget }}
            </p>
          </div>
        </div>

        <!-- Calendrier -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">
              Date de début <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.start_date"
              type="date"
              class="w-full border rounded-lg px-3.5 py-2.5 text-sm outline-none transition focus:ring-2"
              :class="
                fErr.start_date
                  ? 'border-red-400 bg-red-50/30 focus:ring-red-500/20'
                  : 'border-slate-200 focus:ring-bleu-nuit/30'
              "
            />
            <p v-if="fErr.start_date" class="text-xs text-red-500 mt-1">
              {{ fErr.start_date }}
            </p>
          </div>

          <div>
            <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">
              Date de fin <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.end_date"
              type="date"
              class="w-full border rounded-lg px-3.5 py-2.5 text-sm outline-none transition focus:ring-2"
              :class="
                fErr.end_date
                  ? 'border-red-400 bg-red-50/30 focus:ring-red-500/20'
                  : 'border-slate-200 focus:ring-bleu-nuit/30'
              "
            />
            <p v-if="fErr.end_date" class="text-xs text-red-500 mt-1">
              {{ fErr.end_date }}
            </p>
          </div>
        </div>

        <!-- Objectif -->
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">
            Objectif humanitaire <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="form.objectif"
            rows="2"
            maxlength="2000"
            placeholder="Impact attendu et bénéficiaires cibles..."
            class="w-full border rounded-lg px-3.5 py-2.5 text-sm outline-none transition resize-none focus:ring-2"
            :class="
              fErr.objectif
                ? 'border-red-400 bg-red-50/30 focus:ring-red-500/20'
                : 'border-slate-200 focus:ring-bleu-nuit/30'
            "
          ></textarea>
          <p v-if="fErr.objectif" class="text-xs text-red-500 mt-1">
            {{ fErr.objectif }}
          </p>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">
            Description
          </label>
          <textarea
            v-model="form.description"
            rows="2"
            maxlength="500"
            placeholder="Cadre opérationnel et notes..."
            class="w-full border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm outline-none transition resize-none focus:ring-2 focus:ring-bleu-nuit/30"
          ></textarea>
          <p v-if="fErr.description" class="text-xs text-red-500 mt-1">{{ fErr.description }}</p>
        </div>

        <!-- Pied de page -->
        <div class="pt-4 border-t border-slate-100 flex items-center justify-between">
          <button
            v-if="projet"
            @click="confirmerSuppression = true"
            type="button"
            class="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition"
          >
            <Trash2 :size="16" /> Supprimer
          </button>
          <div v-else></div>

          <div class="flex items-center gap-3">
            <BoutonSecondary type="button" @click="fermer">
              Annuler
            </BoutonSecondary>

            <button
              type="submit"
              :disabled="submitting || saving"
              class="px-5 py-2.5 bg-bleu-nuit text-white font-semibold text-sm rounded-lg hover:bg-[#01111eff] transition shadow-xs disabled:opacity-50 flex items-center gap-2"
            >
              <span
                v-if="submitting || saving"
                class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
              ></span>
              {{ submitting || saving ? "Enregistrement..." : projet ? "Mettre à jour" : "Enregistrer" }}
            </button>
          </div>
        </div>
      </form>
    </div>

    <!-- Modal confirmation suppression -->
    <Teleport to="body">
      <div
        v-if="confirmerSuppression"
        class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs"
        @click.self="confirmerSuppression = false"
      >
        <div class="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full">
          <div
            class="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center mx-auto mb-4"
          >
            <Trash2 :size="22" class="text-red-600" />
          </div>
          <h3 class="text-center font-bold text-slate-900 mb-2">
            Supprimer le projet
          </h3>
          <p class="text-center text-sm text-slate-500 mb-6">
            Voulez-vous vraiment supprimer <strong>{{ form.name }}</strong> ?
            Cette action est irréversible.
          </p>
          <div class="flex gap-3">
            <button
              @click="confirmerSuppression = false"
              class="flex-1 px-4 py-2 border border-slate-200 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              Annuler
            </button>
            <button
              @click="supprimer"
              class="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-semibold transition"
            >
              Supprimer
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from "vue";
import { X, Trash2 } from "lucide-vue-next";
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue";
import AlertMessage from "@/components/ui/AlertMessage.vue";
import { useFormValidation, rules } from "@/composables/useFormValidation.js";

const props = defineProps({
  ouvert: { type: Boolean, default: false },
  projet: { type: Object, default: null },
  saving: { type: Boolean, default: false },
});

const emit = defineEmits(["fermer", "save", "delete"]);

const { errors: fErr, validate: fValidate, resetErrors } = useFormValidation();

const submitting = ref(false);
const confirmerSuppression = ref(false);
const erreurGlobale = ref("");

const senegalRegions = [
  "Dakar", "Thiès", "Diourbel", "Fatick", "Kaolack", "Kaffrine",
  "Saint-Louis", "Louga", "Matam", "Tambacounda", "Kédougou",
  "Kolda", "Sédhiou", "Ziguinchor"
];

const form = reactive({
  name: "",
  region: "",
  budget: 0,
  start_date: "",
  end_date: "",
  objectif: "",
  description: "",
});

const initForm = () => {
  resetErrors();
  erreurGlobale.value = "";
  if (props.projet) {
    form.name = props.projet.name || props.projet.nom || "";
    form.region = props.projet.region || "";
    form.budget = Number(props.projet.budget || 0);
    form.start_date = props.projet.start_date || props.projet.debut || "";
    form.end_date = props.projet.end_date || props.projet.fin || "";
    form.objectif = props.projet.objectif || "";
    form.description = props.projet.description || "";
  } else {
    const today = new Date().toISOString().split("T")[0];
    const in3Months = new Date(Date.now() + 90 * 86400000).toISOString().split("T")[0];
    form.name = "";
    form.region = "";
    form.budget = 0;
    form.start_date = today;
    form.end_date = in3Months;
    form.objectif = "";
    form.description = "";
  }
};

watch(
  () => props.ouvert,
  (val) => {
    if (val) initForm();
  },
  { immediate: true }
);

watch(
  () => props.projet,
  () => {
    if (props.ouvert) initForm();
  }
);

const fermer = () => {
  confirmerSuppression.value = false;
  emit("fermer");
};

const submit = async () => {
  if (submitting.value || props.saving) return;
  erreurGlobale.value = "";

  const ok = fValidate({
    name: [rules.nomLong, form.name],
    budget: [rules.montantNonNegatif, form.budget],
    region: [rules.select, form.region],
    start_date: [rules.date, form.start_date],
    end_date: [rules.dateFin, form.end_date, form.start_date],
    objectif: [(value) => rules.required(value) || rules.maxLength(2000)(value), form.objectif],
    description: [rules.description, form.description],
  });

  if (!ok) {
    erreurGlobale.value = "Veuillez corriger les champs en rouge.";
    return;
  }

  submitting.value = true;
  try {
    const payload = {
      name: form.name.trim(),
      region: form.region,
      budget: Number(form.budget || 0),
      start_date: form.start_date,
      end_date: form.end_date,
      objectif: form.objectif.trim(),
      description: form.description ? form.description.trim() : "",
    };

    if (props.projet?.id) {
      payload.id = props.projet.id;
    }

    emit("save", payload);
  } catch (err) {
    erreurGlobale.value = err.message || "Erreur lors de la soumission.";
  } finally {
    submitting.value = false;
  }
};

const supprimer = () => {
  confirmerSuppression.value = false;
  emit("delete", props.projet?.id);
};
</script>
