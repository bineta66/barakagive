<template>
  <div
    v-if="ouvert"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="fermer"
  >
    <div
      class="bg-white border border-slate-200 rounded-2xl shadow-lg max-w-lg w-full"
    >
      <div
        class="p-6 border-b border-slate-100 flex justify-between items-center"
      >
        <div>
          <h2 class="text-xl font-bold text-bleu-nuit">
            {{ utilisateur ? "Modifier l'utilisateur" : "Nouvel utilisateur" }}
          </h2>
          <p class="text-sm text-slate-500 mt-0.5">
            {{
              utilisateur
                ? "Modifiez les informations"
                : "Créer un nouvel utilisateur"
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
        <!-- Prénom -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Prénom <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.first_name"
            type="text"
            @input="touchField('first_name')"
            placeholder="Prénom"
            class="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 transition"
            :class="
              touched.first_name && errors.first_name
                ? 'border-red-500 focus:ring-red-500/20'
                : 'border-slate-200 focus:ring-bleu-nuit/30'
            "
          />
          <p v-if="touched.first_name && errors.first_name" class="mt-1 text-xs text-red-600">
            {{ errors.first_name }}
          </p>
        </div>

        <!-- Nom -->
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">
            Nom <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.last_name"
            type="text"
            @input="touchField('last_name')"
            placeholder="Nom"
            class="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 transition"
            :class="touched.last_name && errors.last_name ? 'border-red-500 focus:ring-red-500/20' : 'border-slate-200 focus:ring-bleu-nuit/30'"
          />
          <p v-if="touched.last_name && errors.last_name" class="mt-1 text-xs text-red-600">{{ errors.last_name }}</p>
        </div>

        <!-- Email -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Email <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.email"
            type="email"
            @input="touchField('email')"
            placeholder="nom@barakagive.org"
            class="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 transition"
            :class="
              touched.email && errors.email
                ? 'border-red-500 focus:ring-red-500/20'
                : 'border-slate-200 focus:ring-bleu-nuit/30'
            "
          />
          <p
            v-if="touched.email && errors.email"
            class="mt-1 text-xs text-red-600"
          >
            {{ errors.email }}
          </p>
        </div>

        <!-- Téléphone -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Téléphone
            <span class="text-slate-400 font-normal normal-case"
              >(optionnel — format : 77 000 00 00)</span
            >
          </label>
          <input
            v-model="form.telephone"
            type="tel"
            @input="touchField('telephone')"
            placeholder="77 000 00 00"
            class="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 transition"
            :class="
              touched.telephone && errors.telephone
                ? 'border-red-500 focus:ring-red-500/20'
                : 'border-slate-200 focus:ring-bleu-nuit/30'
            "
          />
          <p
            v-if="touched.telephone && errors.telephone"
            class="mt-1 text-xs text-red-600"
          >
            {{ errors.telephone }}
          </p>
        </div>

        <!-- Rôle -->
        <div>
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
          >
            Rôle <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.role"
            @change="touchField('role')"
            :disabled="!!utilisateur"
            class="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 transition bg-white"
            :class="
              touched.role && errors.role
                ? 'border-red-500 focus:ring-red-500/20'
                : 'border-slate-200 focus:ring-bleu-nuit/30'
            "
          >
            <option value="">Sélectionner un rôle</option>
            <option value="CHEF_PROJET">Chef de projet</option>
            <option value="FINANCE">Responsable Finance</option>
            <option value="AGENT">Agent Terrain</option>
          </select>
          <p
            v-if="touched.role && errors.role"
            class="mt-1 text-xs text-red-600"
          >
            {{ errors.role }}
          </p>
        </div>

        <!-- Le statut se modifie avec l'action dédiée de la liste. -->
        <div v-if="!utilisateur">
          <label
            class="block text-xs font-semibold uppercase text-slate-600 mb-1"
            >Statut</label
          >
          <select
            v-model="form.statut"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
          >
            <option value="Actif">Actif</option>
            <option value="Inactif">Inactif</option>
          </select>
        </div>

        <!-- Erreur générale -->
        <p
          v-if="erreurGenerale"
          class="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2"
        >
          {{ erreurGenerale }}
        </p>
      </form>

      <div
        class="bg-slate-50 px-6 py-4 flex justify-end gap-3 border-t border-slate-100"
      >
        <BoutonTertiary @click="fermer">Annuler</BoutonTertiary>
        <BoutonPrimary @click="submit" :disabled="saving">
          {{ saving ? "Enregistrement..." : utilisateur ? "Mettre à jour" : "Enregistrer" }}
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
import { useFormValidation, rules } from "@/composables/useFormValidation.js";

const props = defineProps({
  ouvert: Boolean,
  utilisateur: { type: Object, default: null },
  saving: { type: Boolean, default: false },
});
const emit = defineEmits(["fermer", "save"]);

const { errors, validate, resetErrors } = useFormValidation();
const erreurGenerale = ref("");
const touched = reactive({
  first_name: false,
  last_name: false,
  email: false,
  telephone: false,
  role: false,
});

const form = ref({
  first_name: "",
  last_name: "",
  email: "",
  role: "",
  telephone: "",
  statut: "Actif",
});

watch(
  () => props.ouvert,
  (val) => {
    if (val) {
      if (props.utilisateur) {
        form.value = {
          ...props.utilisateur,
          telephone: props.utilisateur.phone || props.utilisateur.telephone || "",
        };
      } else {
        form.value = {
          first_name: "",
          last_name: "",
          email: "",
          role: "",
          telephone: "",
          statut: "Actif",
        };
      }
      resetErrors();
      erreurGenerale.value = "";
      Object.keys(touched).forEach((k) => (touched[k] = false));
    }
  },
  { immediate: true }
);

const touchField = (field) => {
  touched[field] = true;
  runValidation();
};

const runValidation = () =>
  validate({
    first_name: [rules.nom, form.value.first_name],
    last_name: [rules.nom, form.value.last_name],
    email: [rules.email, form.value.email],
    role: [rules.select, form.value.role],
    ...(form.value.telephone
      ? { telephone: [rules.phone, form.value.telephone] }
      : {}),
  });

const fermer = () => emit("fermer");

const submit = () => {
  if (props.saving) return;
  Object.keys(touched).forEach((k) => (touched[k] = true));
  if (!runValidation()) {
    erreurGenerale.value = "Veuillez corriger les champs en rouge.";
    return;
  }
  erreurGenerale.value = "";
  const payload = {
    first_name: form.value.first_name.trim(),
    last_name: form.value.last_name.trim(),
    email: form.value.email.trim(),
    phone: form.value.telephone?.trim() || "",
  };
  if (!props.utilisateur) payload.role = form.value.role;
  emit("save", payload);
};
</script>
