<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="fermer"
  >
    <div
      class="bg-white border border-slate-200 rounded-2xl shadow-lg max-w-md w-full max-h-[90vh] overflow-y-auto"
    >
      <div class="p-6 border-b border-slate-100 flex justify-between items-center">
        <div>
          <h2 class="text-xl font-bold text-bleu-nuit">
            {{ depense ? "Modifier la dépense" : "Nouvelle dépense" }}
          </h2>
          <p class="text-sm text-slate-500 mt-1">
            {{
              depense
                ? "Modifiez les informations de la dépense enregistrée."
                : "Enregistrer une dépense liée à une campagne ou un budget."
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
        <!-- Projet (UI / Filtrage) -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Projet <span class="text-red-500">*</span>
            <span class="text-slate-400 font-normal normal-case ml-1"
              ></span
            >
          </label>
          <AsyncSearchSelect
            v-model="form.projetId"
            :model-label="depense?.projet_nom || ''"
            endpoint="/api/projects/"
            label-key="name"
            value-key="id"
            placeholder="Rechercher un projet (optionnel)…"
            @update:model-value="onProjetChange"
          />
          <p v-if="errors.projetId" class="mt-1 text-xs text-red-500">{{ errors.projetId }}</p>
          <button v-if="form.projetId" type="button" class="mt-1 text-xs text-slate-500 underline" @click="onProjetChange('')">Effacer le projet</button>
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
            :model-label="depense?.campagne_nom || ''"
            :extra-params="campaignSearchParams"
            endpoint="/api/campaigns/"
            label-key="nom"
            value-key="id"
            placeholder="Rechercher une campagne (optionnel)…"
            @select="onCampagneChange"
          />
          <button v-if="form.campagne" type="button" class="mt-1 text-xs text-slate-500 underline" @click="form.campagne = ''">Effacer la campagne</button>
        </div>

        <!-- Budget (optionnel) -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Budget associé
            <span class="text-slate-400 font-normal normal-case ml-1"
              >(optionnel)</span
            >
          </label>
          <select
            v-model="form.budget"
            @change="onBudgetChange"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
          >
            <option value="">Aucun budget associé</option>
            <option v-for="b in budgetsFiltres" :key="b.id" :value="b.id">
              {{ b.source_financement || b.projet_nom || b.nom || ('Budget #' + (b.id ? String(b.id).slice(0, 8) : '')) }} ({{ formatMontant(b.montant) }} FCFA)
            </option>
          </select>
          <p
            v-if="budgetsFiltres.length === 0 && !loadingData"
            class="text-xs text-amber-600 mt-1"
          >
            Aucun budget disponible.
          </p>
        </div>

        <!-- Zones d'intervention (sélection multiple par cases à cocher) -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Zones d'intervention <span class="text-red-500">*</span>
            <span class="text-slate-400 font-normal normal-case ml-1"
              >(Cochez une ou plusieurs zones)</span
            >
          </label>

          <div v-if="zonesAvailable" :class="errors.region ? 'rounded border border-red-400 p-2' : ''">
            <AsyncSearchMultiSelect
              v-model="form.selectedZones"
              endpoint="/api/zones/"
              label-key="nom"
              value-key="id"
              secondary-key="region_nom"
              placeholder="Rechercher les zones de la dépense…"
              @selected-options="onSelectedZones"
              @available="zonesAvailable = $event > 0"
            />
          </div>

          <!-- Fallback : Select région si pas de zones configurées -->
          <select
            v-else
            v-model="form.region"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            :class="errors.region ? 'border-red-400' : 'border-slate-200'"
          >
            <option value="">Sélectionner une région</option>
            <option
              v-for="r in regions"
              :key="r.id || r.nom || r"
              :value="r.id || r"
            >
              {{ r.nom || r.name || r.region || r }}
            </option>
          </select>

          <p v-if="errors.region" class="text-xs text-red-500 mt-1">
            {{ errors.region }}
          </p>
          <p
            v-if="!zonesAvailable && regions.length === 0 && !loadingData"
            class="text-xs text-amber-600 mt-1"
          >
            Aucune zone ou région disponible.
          </p>
        </div>

        <!-- Catégorie -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Catégorie <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.categorie"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            :class="errors.categorie ? 'border-red-400' : 'border-slate-200'"
          >
            <option value="">Sélectionner une catégorie</option>
            <option v-for="category in financeCategories" :key="category" :value="category">{{ category }}</option>
            <option v-if="form.categorie && !financeCategories.includes(form.categorie)" :value="form.categorie">{{ form.categorie }} (valeur existante)</option>
          </select>
          <p v-if="errors.categorie" class="text-xs text-red-500 mt-1">
            {{ errors.categorie }}
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
            placeholder="Ex: 25000"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            :class="errors.montant ? 'border-red-400' : 'border-slate-200'"
          />
          <p v-if="errors.montant" class="text-xs text-red-500 mt-1">
            {{ errors.montant }}
          </p>
        </div>

        <!-- Fournisseur -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Fournisseur
            <span class="text-slate-400 font-normal normal-case ml-1"
              >(optionnel)</span
            >
          </label>
          <input
            v-model="form.fournisseur"
            type="text"
            placeholder="Nom du fournisseur ou prestataire"
            maxlength="255"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
          />
          <p v-if="errors.fournisseur" class="text-xs text-red-500 mt-1">{{ errors.fournisseur }}</p>
        </div>

        <!-- Date -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Date <span class="text-red-500">*</span>
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

        <!-- Description -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Description
            <span class="text-slate-400 font-normal normal-case ml-1"
              >(optionnel)</span
            >
          </label>
          <textarea
            v-model="form.description"
            rows="2"
            maxlength="2000"
            placeholder="Description ou détails supplémentaires..."
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 resize-none"
          ></textarea>
          <p v-if="errors.description" class="text-xs text-red-500 mt-1">{{ errors.description }}</p>
        </div>

        <!-- Erreur générale -->
        <div
          v-if="erreurGenerale"
          class="bg-red-50 border border-red-200 rounded-lg px-3 py-2"
        >
          <p class="text-xs text-red-600 font-semibold mb-1">
            Erreur d'enregistrement
          </p>
          <p class="text-xs text-red-600 whitespace-pre-line">
            {{ erreurGenerale }}
          </p>
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
          {{ loading || saving ? "Enregistrement..." : depense ? "Mettre à jour" : "Enregistrer" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, reactive } from "vue";
import api from "@/services/api.js";
import { FINANCE_CATEGORIES } from "@/modules/finance/constants/categories.js";
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js";
import AsyncSearchSelect from "@/components/ui/AsyncSearchSelect.vue";
import AsyncSearchMultiSelect from "@/components/ui/AsyncSearchMultiSelect.vue";

const financeCategories = FINANCE_CATEGORIES;

const props = defineProps({
  ouvert: Boolean,
  depense: {
    type: Object,
    default: null,
  },
  erreurBackend: {
    type: String,
    default: "",
  },
  saving: { type: Boolean, default: false },
  initialBudgetId: { type: String, default: "" },
});
const emit = defineEmits(["fermer", "save"]);

const financeStore = useFinanceStore();

const loading = ref(false);
const loadingData = ref(false);
const erreurGenerale = ref("");

watch(
  () => props.erreurBackend,
  (val) => {
    if (val) erreurGenerale.value = val;
  }
);

const regions = ref([]);
const zones = ref([]);
const zonesAvailable = ref(true);
const tousLesBudgets = ref([]);

const errors = reactive({
  projetId: "",
  region: "",
  categorie: "",
  montant: "",
  date: "",
  fournisseur: "",
  description: "",
});

const dateAujourdhui = new Date().toISOString().split("T")[0];

const form = ref({
  projetId: "", // UI filter
  campagne: "", // UUID Campaign (optionnel)
  budget: "", // UUID Budget (optionnel)
  selectedZones: [], // Array IDs des zones cochées
  region: "", // integer Region PK (obligatoire backend)
  categorie: "", // string ≤100
  montant: "", // decimal > 0
  fournisseur: "", // string ≤255 (optionnel)
  date: "", // YYYY-MM-DD
  description: "", // text (optionnel)
});

const getProjetId = (item) => {
  if (!item) return null;
  if (typeof item.projet === "object" && item.projet !== null) {
    return item.projet.id ?? item.projet.pk;
  }
  return item.projet_id ?? item.projet ?? item.project;
};

const budgetsFiltres = computed(() => {
  let list = tousLesBudgets.value;
  if (!list || list.length === 0) {
    const b = financeStore.budgets;
    list = Array.isArray(b) ? b : (b?.results || []);
  }
  if (!form.value.projetId) return list;
  const pid = String(form.value.projetId);
  return list.filter((b) => String(getProjetId(b)) === pid);
});

const campaignSearchParams = computed(() => ({ projet: form.value.projetId || undefined }));

const formatMontant = (v) => Number(v || 0).toLocaleString("fr-FR");

const onProjetChange = (projectId) => {
  form.value.projetId = projectId || "";
  form.value.campagne = "";
  form.value.budget = "";
};

const onCampagneChange = (campaign) => {
  const projectId = campaign?.projet?.id;
  if (projectId && !form.value.projetId) form.value.projetId = projectId;
};

const onBudgetChange = () => {
  if (!form.value.budget) return;
  const list = tousLesBudgets.value.length > 0 ? tousLesBudgets.value : (Array.isArray(financeStore.budgets) ? financeStore.budgets : []);
  const found = list.find((b) => String(b.id) === String(form.value.budget));
  if (found) {
    const pId = getProjetId(found);
    if (pId && !form.value.projetId) {
      form.value.projetId = pId;
    }
  }
};

const onZonesChange = () => {
  if (!form.value.selectedZones || form.value.selectedZones.length === 0) {
    form.value.region = "";
    return;
  }
  const selectedZoneObjs = zones.value.filter((z) =>
    form.value.selectedZones.includes(z.id)
  );

  const regionNames = selectedZoneObjs
    .map((z) => z.region_nom || z.region)
    .filter(Boolean);

  if (regionNames.length > 0) {
    const targetName = String(regionNames[0]).toLowerCase().trim();
    const match = regions.value.find((r) => {
      const rName = String(r.nom || r.name || r.region || "")
        .toLowerCase()
        .trim();
      return rName === targetName;
    });
    if (match) {
      form.value.region = match.id;
    } else if (regions.value.length > 0) {
      form.value.region = regions.value[0].id;
    }
  }
};

const onSelectedZones = (options) => {
  zones.value = options;
  onZonesChange();
};

const resetErrors = () => {
  errors.projetId = "";
  errors.region = "";
  errors.categorie = "";
  errors.montant = "";
  errors.date = "";
  errors.fournisseur = "";
  errors.description = "";
  erreurGenerale.value = "";
};

const validate = () => {
  resetErrors();
  let valid = true;

  if (!form.value.projetId) {
    errors.projetId = "Veuillez sélectionner un projet.";
    valid = false;
  }

  if (zonesAvailable.value) {
    if (!form.value.selectedZones || form.value.selectedZones.length === 0) {
      errors.region = "Veuillez cocher au moins une zone d'intervention.";
      valid = false;
    }
  } else if (!form.value.region) {
    errors.region = "Veuillez sélectionner une région.";
    valid = false;
  }

  if (!form.value.categorie?.trim() || form.value.categorie.trim().length > 100) {
    errors.categorie = !form.value.categorie?.trim() ? "La catégorie est obligatoire." : "La catégorie ne peut pas dépasser 100 caractères.";
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
  if ((form.value.fournisseur || "").trim().length > 255) {
    errors.fournisseur = "Le fournisseur ne peut pas dépasser 255 caractères.";
    valid = false;
  }
  if ((form.value.description || "").trim().length > 2000) {
    errors.description = "La description ne peut pas dépasser 2 000 caractères.";
    valid = false;
  }
  return valid;
};

const chargerDonnees = async () => {
  loadingData.value = true;
  if (!form.value.date) form.value.date = dateAujourdhui;
  try {
    const [regionsRes, budgetsRes] = await Promise.all([
      api.get("/api/regions/").catch(() => null),
      api.get("/api/finance/budgets/").catch(() => null),
      financeStore.fetchBudgets().catch(() => {}),
    ]);

    if (regionsRes?.data) {
      regions.value = regionsRes.data?.results ?? (Array.isArray(regionsRes.data) ? regionsRes.data : []);
    }
    if (budgetsRes?.data) {
      tousLesBudgets.value = budgetsRes.data?.results ?? (Array.isArray(budgetsRes.data) ? budgetsRes.data : []);
    }
  } catch (e) {
    console.error("DepenseFormModal chargement:", e);
  } finally {
    loadingData.value = false;
  }
};

const initForm = () => {
  resetErrors();
  if (props.depense) {
    form.value = {
      projetId: props.depense.projet_id || (props.depense.budget && typeof props.depense.budget === 'object' ? props.depense.budget.projet_id : "") || "",
      campagne: (typeof props.depense.campagne === 'object' && props.depense.campagne !== null ? props.depense.campagne.id : props.depense.campagne) || "",
      budget: (typeof props.depense.budget === 'object' && props.depense.budget !== null ? props.depense.budget.id : props.depense.budget) || "",
      selectedZones: [],
      region: (typeof props.depense.region === 'object' && props.depense.region !== null ? props.depense.region.id : props.depense.region) || "",
      categorie: props.depense.categorie || "",
      montant: props.depense.montant || "",
      fournisseur: props.depense.fournisseur || "",
      date: props.depense.date || dateAujourdhui,
      description: props.depense.description || "",
    };
  } else {
    form.value = {
      projetId: "",
      campagne: "",
      budget: props.initialBudgetId || "",
      selectedZones: [],
      region: "",
      categorie: "",
      montant: "",
      fournisseur: "",
      date: dateAujourdhui,
      description: "",
    };
  }
};

watch(
  () => props.ouvert,
  (val) => {
    if (val) {
      initForm();
      chargerDonnees();
    }
  }
);

watch(
  () => props.depense,
  () => {
    if (props.ouvert) initForm();
  }
);

onMounted(() => {
  chargerDonnees();
  if (props.ouvert) initForm();
});

const submit = () => {
  if (loading.value || props.saving) return;
  if (!validate()) return;
  loading.value = true;
  try {
    if (form.value.selectedZones.length > 0 && !form.value.region) {
      onZonesChange();
    }
    const finalRegionId =
      Number(form.value.region) || (regions.value[0]?.id ? Number(regions.value[0].id) : 1);

    let descriptionFinale = form.value.description?.trim() || "";
    if (form.value.selectedZones.length > 0) {
      const selectedNames = zones.value
        .filter((z) => form.value.selectedZones.includes(z.id))
        .map((z) => z.nom)
        .join(", ");
      const prefixZones = `Zones concernées : ${selectedNames}`;
      descriptionFinale = descriptionFinale
        ? `${descriptionFinale}\n(${prefixZones})`
        : prefixZones;
    }

    const payload = {
      projet: Number(form.value.projetId),
      region: finalRegionId,
      categorie: form.value.categorie.trim(),
      montant: Number(form.value.montant),
      date: form.value.date,
    };

    if (form.value.campagne) payload.campagne = form.value.campagne;
    if (form.value.budget) payload.budget = form.value.budget;
    if (form.value.fournisseur?.trim())
      payload.fournisseur = form.value.fournisseur.trim();
    if (descriptionFinale) payload.description = descriptionFinale;
    if (props.depense?.id) payload.id = props.depense.id;

    emit("save", payload);
  } finally {
    loading.value = false;
  }
};

const fermer = () => {
  form.value = {
    projetId: "",
    campagne: "",
    budget: "",
    selectedZones: [],
    region: "",
    categorie: "",
    montant: "",
    fournisseur: "",
    date: dateAujourdhui,
    description: "",
  };
  resetErrors();
  emit("fermer");
};
</script>
