<template>
  <div
    class="min-h-screen bg-white flex justify-center items-start py-8 px-4 sm:px-6 lg:px-8"
  >
    <div
      class="w-full max-w-4xl bg-white rounded-2xl border border-slate-200/60 p-8 shadow-xs-sm"
    >
      <div
        class="flex items-center justify-between mb-6 pb-4 border-b border-slate-100"
      >
        <div>
          <h2 class="text-3xl font-bold text-bleu-nuit">
            Inviter un nouveau collaborateur
          </h2>
          <p class="text-gray-600 text-sm mt-1">
            Le collaborateur recevra un lien d'activation sécurisé par email
            pour définir son mot de passe.
          </p>
        </div>
        <BoutonSecondary to="/gerant/utilisateurs"
          ><ArrowLeft :size="16" />Retour</BoutonSecondary
        >
      </div>

      <AlertMessage
        v-if="error"
        type="error"
        :message="error"
        :dismissible="true"
        @dismiss="error = null"
        class="mb-6"
      />
      <AlertMessage
        v-if="successMessage"
        type="success"
        :message="successMessage"
        class="mb-6"
      />

      <form @submit.prevent="soumettreFormulaire" novalidate class="space-y-8">
        <!-- Section 1 : Informations personnelles -->
        <div>
          <h3 class="text-xl font-bold text-bleu-nuit mb-4 pb-2 border-b">
            1. Informations personnelles
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Prénom -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1"
                >Prénom <span class="text-red-500">*</span></label
              >
              <input
                v-model="form.first_name"
                type="text"
                @input="touchField('first_name')"
                placeholder="Ex : Moussa"
                class="w-full rounded-lg border bg-slate-50 px-4 py-2.5 focus:ring-2 outline-none text-sm transition"
                :class="
                  touched.first_name && errors.first_name
                    ? 'border-red-500 focus:ring-red-500/20'
                    : 'border-gray-300 focus:ring-bleu-nuit/30'
                "
              />
              <p
                v-if="touched.first_name && errors.first_name"
                class="mt-1 text-xs text-red-600"
              >
                {{ errors.first_name }}
              </p>
            </div>

            <!-- Nom -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1"
                >Nom <span class="text-red-500">*</span></label
              >
              <input
                v-model="form.last_name"
                type="text"
                @input="touchField('last_name')"
                placeholder="Ex : Diop"
                class="w-full rounded-lg border bg-slate-50 px-4 py-2.5 focus:ring-2 outline-none text-sm transition"
                :class="
                  touched.last_name && errors.last_name
                    ? 'border-red-500 focus:ring-red-500/20'
                    : 'border-gray-300 focus:ring-bleu-nuit/30'
                "
              />
              <p
                v-if="touched.last_name && errors.last_name"
                class="mt-1 text-xs text-red-600"
              >
                {{ errors.last_name }}
              </p>
            </div>

            <!-- Email -->
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1"
                >Adresse e-mail <span class="text-red-500">*</span></label
              >
              <div class="relative">
                <Mail
                  :size="16"
                  class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                />
                <input
                  v-model="form.email"
                  type="email"
                  @input="touchField('email')"
                  placeholder="m.diop@ong-partenaire.org"
                  class="w-full rounded-lg border bg-slate-50 pl-10 pr-4 py-2.5 focus:ring-2 outline-none text-sm transition"
                  :class="
                    touched.email && errors.email
                      ? 'border-red-500 focus:ring-red-500/20'
                      : 'border-gray-300 focus:ring-bleu-nuit/30'
                  "
                />
              </div>
              <p
                v-if="touched.email && errors.email"
                class="mt-1 text-xs text-red-600"
              >
                {{ errors.email }}
              </p>
            </div>

            <!-- Téléphone -->
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Téléphone <span class="text-red-500">*</span>
                <span class="text-xs font-normal text-slate-400 ml-1"
                  >(Format Sénégal : 77 000 00 00)</span
                >
              </label>
              <div class="relative">
                <Phone
                  :size="16"
                  class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                />
                <input
                  v-model="form.phone"
                  type="tel"
                  @input="touchField('phone')"
                  placeholder="77 000 00 00"
                  class="w-full rounded-lg border bg-slate-50 pl-10 pr-4 py-2.5 focus:ring-2 outline-none text-sm transition"
                  :class="
                    touched.phone && errors.phone
                      ? 'border-red-500 focus:ring-red-500/20'
                      : 'border-gray-300 focus:ring-bleu-nuit/30'
                  "
                />
              </div>
              <p
                v-if="touched.phone && errors.phone"
                class="mt-1 text-xs text-red-600"
              >
                {{ errors.phone }}
              </p>
            </div>
          </div>
        </div>

        <!-- Section 2 : Rôle opérationnel -->
        <div>
          <h3 class="text-xl font-bold text-bleu-nuit mb-4 pb-2 border-b">
            2. Rôle opérationnel <span class="text-red-500">*</span>
          </h3>
          <p class="text-xs text-slate-500 mb-4">
            Sélectionnez les prérogatives accordées à ce membre au sein de votre
            ONG.
          </p>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <label
              v-for="r in rolesDisponibles"
              :key="r.value"
              class="border rounded-xl p-4 cursor-pointer transition flex flex-col justify-between"
              :class="
                form.role === r.value
                  ? 'border-bleu-nuit bg-bleu-nuit/5 ring-2 ring-bleu-nuit/30'
                  : 'border-slate-200 hover:bg-slate-50'
              "
            >
              <div class="flex items-center justify-between mb-2">
                <span class="font-bold text-sm text-slate-900">{{
                  r.label
                }}</span>
                <input
                  type="radio"
                  v-model="form.role"
                  :value="r.value"
                  class="text-bleu-nuit focus:ring-bleu-nuit"
                />
              </div>
              <p class="text-xs text-slate-500">{{ r.description }}</p>
            </label>
          </div>
          <p
            v-if="touched.role && errors.role"
            class="mt-2 text-xs text-red-600"
          >
            {{ errors.role }}
          </p>
        </div>

        <div class="pt-6 border-t flex justify-end gap-4">
          <BoutonSecondary to="/gerant/utilisateurs">Annuler</BoutonSecondary>
          <button
            type="submit"
            :disabled="loading"
            class="px-6 py-2.5 bg-bleu-nuit text-white font-semibold text-sm rounded-lg hover:bg-[#01111eff] transition shadow-xs flex items-center gap-2 disabled:opacity-50"
          >
            <span
              v-if="loading"
              class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
            ></span>
            {{
              loading ? "Envoi de l'invitation..." : "Inviter le collaborateur"
            }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ArrowLeft, Mail, Phone } from "lucide-vue-next";
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js";
import { useFormValidation, rules } from "@/composables/useFormValidation.js";
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue";
import AlertMessage from "@/components/ui/AlertMessage.vue";

const router = useRouter();
const store = useGerantStore();
const { errors, validate } = useFormValidation();

const loading = ref(false);
const error = ref(null);
const successMessage = ref("");
const touched = reactive({
  first_name: false,
  last_name: false,
  email: false,
  phone: false,
  role: false,
});

const form = reactive({
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  role: "CHEF_PROJET",
});

const rolesDisponibles = [
  {
    value: "CHEF_PROJET",
    label: "Chef de projet",
    description:
      "Gère les campagnes, configure les zones et conçoit les formulaires dynamiques.",
  },
  {
    value: "FINANCE",
    label: "Responsable Finance",
    description:
      "Supervise les budgets des projets et le suivi financier de l'ONG.",
  },
  {
    value: "AGENT",
    label: "Agent Terrain",
    description:
      "Collecte les données terrain et enregistre les bénéficiaires sur mobile.",
  },
];

const touchField = (field) => {
  touched[field] = true;
  runValidation();
};

const runValidation = () =>
  validate({
    first_name: [rules.nom, form.first_name],
    last_name: [rules.nom, form.last_name],
    email: [rules.email, form.email],
    phone: [rules.phone, form.phone],
    role: [rules.select, form.role],
  });

const soumettreFormulaire = async () => {
  Object.keys(touched).forEach((k) => (touched[k] = true));
  if (!runValidation()) {
    error.value = "Veuillez corriger les champs en rouge.";
    return;
  }

  loading.value = true;
  error.value = null;
  successMessage.value = "";
  try {
    await store.createUser({
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      role: form.role,
    });
    successMessage.value = `Invitation envoyée avec succès à ${form.email}.`;
    setTimeout(() => router.push("/gerant/utilisateurs"), 1500);
  } catch (err) {
    error.value =
      store.error ||
      "Une erreur est survenue lors de la création de l'utilisateur.";
  } finally {
    loading.value = false;
  }
};
</script>
