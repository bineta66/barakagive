<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="fermer"
  >
    <div
      class="bg-white border border-slate-200 rounded-2xl shadow-lg max-w-lg w-full max-h-[90vh] overflow-y-auto"
    >
      <div
        class="p-6 border-b border-slate-100 flex justify-between items-center"
      >
        <div>
          <h2 class="text-xl font-bold text-bleu-nuit">
            {{ partenaire ? "Modifier le partenaire" : "Nouveau partenaire" }}
          </h2>
          <p class="text-sm text-slate-500 mt-0.5">
            {{
              partenaire
                ? "Modifiez les informations"
                : "Créez un nouveau partenaire"
            }}
          </p>
        </div>
        <button
          @click="fermer"
          class="text-slate-400 hover:text-slate-600 transition"
        >
          <X class="w-6 h-6" />
        </button>
      </div>

      <form @submit.prevent="submit" novalidate class="p-6 space-y-4">
        <!-- Nom organisation -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Nom de l'organisation <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.nom"
            type="text"
            placeholder="Croissant-Rouge Sahélien, MSF..."
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            required
            @input="validateField('nom')"
          />
          <p v-if="erreurs.nom" class="mt-1 text-xs text-red-600">{{ erreurs.nom }}</p>
        </div>

        <!-- Domaine d'intervention -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Domaine d'intervention <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.domaine"
            type="text"
            placeholder="Secours, Santé, Eau, Éducation..."
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            required
            @input="validateField('domaine')"
          />
          <p v-if="erreurs.domaine" class="mt-1 text-xs text-red-600">{{ erreurs.domaine }}</p>
        </div>

        <!-- Recherche de zone limitée à l'organisation courante -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Zone d'intervention <span class="text-red-500">*</span>
          </label>
          <AsyncSearchSelect
            v-model="form.zone"
            endpoint="/api/zones/"
            label-key="nom"
            value-key="nom"
            secondary-key="region_nom"
            placeholder="Rechercher une zone…"
            manual-option="Autre zone (saisie manuelle)"
            @update:model-value="validateField('zone')"
          />
          <p v-if="erreurs.zone" class="mt-1 text-xs text-red-600">{{ erreurs.zone }}</p>
          <input
            v-if="form.zone === '__autre__'"
            v-model="form.zoneLibre"
            type="text"
            placeholder="Zone d'intervention"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 mt-2"
            @input="validateField('zone')"
          />
        </div>

        <!-- Recherche de projet limitée au périmètre accessible -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Projet associé
            <span class="text-slate-400 font-normal normal-case"
              >(optionnel)</span
            >
          </label>
          <AsyncSearchSelect
            v-model="form.projet"
            endpoint="/api/projects/"
            label-key="name"
            value-key="name"
            placeholder="Rechercher un projet (optionnel)…"
          />
          <button v-if="form.projet" type="button" class="mt-1 text-xs text-slate-500 underline" @click="form.projet = ''">Effacer le projet</button>
        </div>

        <!-- Contact / Email -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Contact / Email <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.contact"
            type="email"
            placeholder="contact@organisation.org"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            required
            @input="validateField('contact')"
          />
          <p v-if="erreurs.contact" class="mt-1 text-xs text-red-600">{{ erreurs.contact }}</p>
        </div>

        <!-- Statut -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
            >Statut</label
          >
          <select
            v-model="form.statut"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
          >
            <option value="ACTIF">Actif</option>
            <option value="INACTIF">Inactif</option>
          </select>
        </div>

        <p
          v-if="erreur"
          class="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2"
        >
          {{ erreur }}
        </p>
      </form>

      <div
        class="bg-slate-50 px-6 py-4 flex justify-end gap-3 border-t border-slate-100"
      >
        <BoutonTertiary @click="fermer">Annuler</BoutonTertiary>
        <BoutonPrimary @click="submit" :disabled="saving">
          {{ saving ? "Enregistrement..." : partenaire ? "Mettre à jour" : "Enregistrer" }}
        </BoutonPrimary>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from "vue";
import { X } from "lucide-vue-next";
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue";
import BoutonTertiary from "@/components/ui/BoutonTertiary.vue";
import AsyncSearchSelect from "@/components/ui/AsyncSearchSelect.vue";

const props = defineProps({
  ouvert: Boolean,
  partenaire: { type: Object, default: null },
  saving: { type: Boolean, default: false },
  erreurBackend: { type: String, default: "" },
});
const emit = defineEmits(["fermer", "save"]);

const erreur = ref("");
const erreurs = reactive({ nom: "", domaine: "", zone: "", contact: "" });


// Résolution zone (select ou saisie libre)
const zoneResolue = computed(() =>
  form.value.zone === "__autre__"
    ? form.value.zoneLibre?.trim()
    : form.value.zone
);

const form = ref({
  nom: "",
  domaine: "",
  zone: "",
  zoneLibre: "",
  projet: "",
  contact: "",
  statut: "ACTIF",
});

watch(
  () => props.ouvert,
  (val) => {
    erreur.value = "";
    if (val && props.partenaire) {
      form.value = {
        nom: props.partenaire.nom || "",
        domaine: props.partenaire.domaine || "",
        zone: props.partenaire.zone || "",
        zoneLibre: "",
        projet: props.partenaire.projet || "",
        contact: props.partenaire.contact || props.partenaire.email || "",
        statut: props.partenaire.statut || "ACTIF",
      };
    } else if (val) {
      form.value = {
        nom: "",
        domaine: "",
        zone: "",
        zoneLibre: "",
        projet: "",
        contact: "",
        statut: "ACTIF",
      };
    }
  },
  { immediate: true }
);

watch(() => props.erreurBackend, (value) => {
  if (value) erreur.value = value;
});

const fermer = () => {
  erreur.value = "";
  emit("fermer");
};

const submit = () => {
  if (props.saving) return;
  erreur.value = "";
  const valid = ["nom", "domaine", "zone", "contact"].map(validateField).every(Boolean);
  if (!valid) {
    erreur.value = "Veuillez corriger les champs indiqués.";
    return;
  }

  emit("save", {
    nom: form.value.nom.trim(),
    domaine: form.value.domaine.trim(),
    zone: zoneResolue.value,
    projet: form.value.projet || "",
    contact: form.value.contact.trim(),
    statut: form.value.statut,
  });
};

const validateField = (field) => {
  const value = field === "zone" ? (form.value.zone === "__autre__" ? form.value.zoneLibre : form.value.zone) : form.value[field];
  const normalized = String(value ?? "").trim();
  if (!normalized) erreurs[field] = "Ce champ est obligatoire.";
  else if (field === "nom" && (!/[A-Za-zÀ-ÿ]/.test(normalized) || normalized.length < 2 || normalized.length > 255)) erreurs.nom = "Saisissez un nom valide.";
  else if (field === "domaine" && normalized.length > 100) erreurs.domaine = "Le domaine ne peut pas dépasser 100 caractères.";
  else if (field === "contact" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(normalized)) erreurs.contact = "Veuillez saisir une adresse e-mail valide.";
  else erreurs[field] = "";
  return !erreurs[field];
};
</script>
