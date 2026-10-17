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
            {{ bailleur ? "Modifier le bailleur" : "Nouveau bailleur" }}
          </h2>
          <p class="text-sm text-slate-500 mt-0.5">
            {{
              bailleur
                ? "Modifiez les informations"
                : "Créez un nouveau bailleur de fonds"
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
        <!-- Nom -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Nom de l'organisation <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.nom"
            type="text"
            placeholder="DG ECHO, USAID, AFD, UNICEF..."
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            required
            @input="validateField('nom')"
          />
          <p v-if="erreurs.nom" class="mt-1 text-xs text-red-600">{{ erreurs.nom }}</p>
        </div>

        <!-- Email de contact -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Email de contact <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.email"
            type="email"
            placeholder="contact@organisation.org"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            required
            @input="validateField('email')"
          />
          <p v-if="erreurs.email" class="mt-1 text-xs text-red-600">{{ erreurs.email }}</p>
        </div>

        <!-- Téléphone -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Téléphone
            <span class="text-slate-400 font-normal normal-case"
              >(optionnel)</span
            >
          </label>
          <input
            v-model="form.telephone"
            type="tel"
            placeholder="+221 77 000 00 00"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
            @input="validateField('telephone')"
          />
          <p v-if="erreurs.telephone" class="mt-1 text-xs text-red-600">{{ erreurs.telephone }}</p>
        </div>

        <!-- Type -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Type <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.type"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
            required
            @change="validateField('type')"
          >
            <option value="">Sélectionner</option>
            <option value="International">International</option>
            <option value="National">National</option>
            <option value="Institutionnel">Institutionnel</option>
            <option value="Gouvernemental">Gouvernemental</option>
          </select>
          <p v-if="erreurs.type" class="mt-1 text-xs text-red-600">{{ erreurs.type }}</p>
        </div>

        <!-- Adresse -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Adresse
            <span class="text-slate-400 font-normal normal-case"
              >(optionnel)</span
            >
          </label>
          <input
            v-model="form.adresse"
            type="text"
            placeholder="Adresse ou localisation"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
          />
        </div>

        <!-- Statut -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
            >Statut</label
          >
          <select
            v-model="form.actif"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
          >
            <option :value="true">Actif</option>
            <option :value="false">Inactif</option>
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
          {{ saving ? "Enregistrement..." : bailleur ? "Mettre à jour" : "Enregistrer" }}
        </BoutonPrimary>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from "vue";
import { X } from "lucide-vue-next";
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue";
import BoutonTertiary from "@/components/ui/BoutonTertiary.vue";

const props = defineProps({
  ouvert: Boolean,
  bailleur: { type: Object, default: null },
  saving: { type: Boolean, default: false },
  erreurBackend: { type: String, default: "" },
});
const emit = defineEmits(["fermer", "save"]);

const erreur = ref("");
const erreurs = reactive({ nom: "", email: "", telephone: "", type: "" });

const form = ref({
  nom: "",
  email: "",
  telephone: "",
  type: "",
  adresse: "",
  actif: true,
});

watch(
  () => props.ouvert,
  (val) => {
    erreur.value = "";
    if (val && props.bailleur) {
      form.value = {
        nom: props.bailleur.nom || "",
        email: props.bailleur.email || props.bailleur.contact || "",
        telephone: props.bailleur.telephone || "",
        type: props.bailleur.type || "",
        adresse: props.bailleur.adresse || "",
        actif: props.bailleur.actif !== false,
      };
    } else if (val) {
      form.value = {
        nom: "",
        email: "",
        telephone: "",
        type: "",
        adresse: "",
        actif: true,
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
  Object.keys(erreurs).forEach((key) => (erreurs[key] = ""));
  emit("fermer");
};

const validateField = (field) => {
  const value = String(form.value[field] ?? "").trim();
  if (["nom", "email", "type"].includes(field) && !value) erreurs[field] = "Ce champ est obligatoire.";
  else if (field === "nom" && (!/[A-Za-zÀ-ÿ]/.test(value) || value.length < 2 || value.length > 255)) erreurs.nom = "Saisissez un nom valide.";
  else if (field === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value)) erreurs.email = "Veuillez saisir une adresse e-mail valide.";
  else if (field === "telephone" && value && !/^(\+221\s?)?(70|75|76|77|78)\s?\d{3}\s?\d{2}\s?\d{2}$/.test(value)) erreurs.telephone = "Veuillez saisir un numéro de téléphone valide.";
  else erreurs[field] = "";
  return !erreurs[field];
};

const submit = () => {
  if (props.saving) return;
  erreur.value = "";
  const valid = ["nom", "email", "telephone", "type"].map(validateField).every(Boolean);
  if (!valid) {
    erreur.value = "Veuillez corriger les champs indiqués.";
    return;
  }

  emit("save", {
    nom: form.value.nom.trim(),
    email: form.value.email.trim(),
    telephone: form.value.telephone?.trim() || "",
    type: form.value.type,
    adresse: form.value.adresse?.trim() || "",
    actif: form.value.actif,
    // Pour rétro-compatibilité avec les affichages existants
    contact: form.value.email.trim(),
    statut: form.value.actif ? "Reçu" : "En attente",
  });
};
</script>
