<template>
  <div
    @click.self="handleClose"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
  >
    <div class="bg-white border border-slate-200/60 rounded-xl w-full max-w-lg">
      <!-- Header -->
      <div
        class="px-6 py-4 border-b border-slate-100 flex items-center justify-between"
      >
        <div>
          <h2 class="text-lg font-bold text-slate-900">
            Nouvelle collecte terrain
          </h2>
          <p class="text-xs text-slate-500 mt-0.5">
            Enregistrer une collecte hors ligne
          </p>
        </div>
        <button
          @click="handleClose"
          class="p-1.5 text-slate-400 hover:text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition"
        >
          <X :size="18" />
        </button>
      </div>

      <!-- Body -->
      <div class="px-6 py-5 space-y-4">
        <!-- Date -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Date de la collecte <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.date"
            type="date"
            :max="today"
            class="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 transition"
            :class="
              errors.date ? 'border-red-400 bg-red-50' : 'border-slate-200'
            "
          />
          <p v-if="errors.date" class="text-xs text-red-500 mt-1">
            {{ errors.date }}
          </p>
        </div>

        <!-- Campagne -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Campagne <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.campagne_id"
            class="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white transition"
            :class="
              errors.campagne ? 'border-red-400 bg-red-50' : 'border-slate-200'
            "
          >
            <option value="">— Sélectionner une campagne —</option>
            <option v-for="c in campaigns" :key="c.id" :value="c.id">
              {{ c.nom }}
            </option>
          </select>
          <p v-if="errors.campagne" class="text-xs text-red-500 mt-1">
            {{ errors.campagne }}
          </p>
        </div>

        <!-- Zone -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Zone géographique <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.zone_id"
            class="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white transition"
            :class="
              errors.zone ? 'border-red-400 bg-red-50' : 'border-slate-200'
            "
          >
            <option value="">— Sélectionner une zone —</option>
            <option v-for="z in zones" :key="z.id" :value="z.id">
              {{ z.nom }} ({{ z.region }})
            </option>
          </select>
          <p v-if="errors.zone" class="text-xs text-red-500 mt-1">
            {{ errors.zone }}
          </p>
        </div>

        <!-- Montant -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Montant collecté (FCFA)
            <span class="text-slate-400 font-normal normal-case"
              >(optionnel)</span
            >
          </label>
          <input
            v-model.number="form.montant"
            type="number"
            min="0"
            placeholder="0"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
          />
        </div>

        <!-- Erreur globale -->
        <p
          v-if="erreurGlobale"
          class="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2"
        >
          {{ erreurGlobale }}
        </p>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-slate-100 flex gap-3 justify-end">
        <button
          @click="handleClose"
          class="px-4 py-2 border border-slate-200 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
        >
          Annuler
        </button>
        <button
          @click="handleSubmit"
          :disabled="isSubmitting"
          class="px-5 py-2 bg-bleu-nuit text-white rounded-lg text-sm font-semibold hover:bg-[#0a2540] transition disabled:opacity-50"
        >
          <span v-if="isSubmitting" class="flex items-center gap-2">
            <span
              class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"
            ></span>
            Enregistrement...
          </span>
          <span v-else>Enregistrer</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { X } from "lucide-vue-next";
import { SyncStore } from "@/stores/syncDB";
import { useSync } from "@/composables/useSync";
import { useCampaignStore } from "@/stores/campaign";
import { useZoneStore } from "@/stores/zone";

const emit = defineEmits(["close"]);

const campaignStore = useCampaignStore();
const zoneStore = useZoneStore();
const { updateStats } = useSync();

const today = new Date().toISOString().split("T")[0];

const form = ref({
  date: today,
  campagne_id: "",
  zone_id: "",
  montant: 0,
});

const errors = reactive({ date: "", campagne: "", zone: "" });
const erreurGlobale = ref("");
const isSubmitting = ref(false);

const campaigns = computed(() => campaignStore.campaigns || []);
const zones = computed(() => zoneStore.zones || []);

onMounted(async () => {
  try {
    if (campaigns.value.length === 0) await campaignStore.fetchAgentCampaigns();
    if (zones.value.length === 0) await zoneStore.fetchZones();
  } catch {
    /* silencieux */
  }
});

const valider = () => {
  errors.date = "";
  errors.campagne = "";
  errors.zone = "";
  erreurGlobale.value = "";
  let valide = true;

  if (!form.value.date) {
    errors.date = "La date est obligatoire.";
    valide = false;
  }
  if (!form.value.campagne_id) {
    errors.campagne = "Sélectionnez une campagne.";
    valide = false;
  }
  if (!form.value.zone_id) {
    errors.zone = "Sélectionnez une zone.";
    valide = false;
  }

  return valide;
};

const handleClose = () => emit("close");

const handleSubmit = async () => {
  if (!valider()) return;

  isSubmitting.value = true;
  try {
    const campagne = campaigns.value.find(
      (c) => c.id === form.value.campagne_id
    );
    const zone = zones.value.find((z) => z.id === form.value.zone_id);

    await SyncStore.createBeneficiaire({
      prenom: "Collecte",
      nom: campagne?.nom || "Campagne",
      date_naissance: form.value.date,
      telephone: "",
      adresse: zone?.nom || "Zone",
      campagne: form.value.campagne_id,
      zone: form.value.zone_id,
      montant: form.value.montant,
      type: "collecte",
    });

    await updateStats();
    emit("close");
  } catch (error) {
    erreurGlobale.value =
      "Erreur lors de l'enregistrement. Veuillez réessayer.";
  } finally {
    isSubmitting.value = false;
  }
};
</script>
