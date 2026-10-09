<template>
  <div class="min-h-screen bg-white">
    <div class="grid min-h-screen lg:grid-cols-2">
      <div
        class="relative hidden lg:flex items-end justify-center bg-bleu-nuit overflow-hidden pb-20"
      >
        <img
          src="@/assets/images/imagelogo.png"
          alt="Fond"
          class="absolute inset-0 w-full h-full object-cover opacity-70"
        />
        <div class="absolute inset-0 bg-bleu-nuit/40"></div>
        <div class="relative z-10 flex flex-col items-center text-center px-10">
          <p class="text-xl text-white font-semibold leading-8 max-w-sm">
            Réinitialisez votre mot de passe en toute sécurité.
          </p>
        </div>
      </div>

      <div class="flex flex-col justify-between bg-white px-8 py-10 lg:px-20">
        <div></div>
        <div class="mx-auto w-full max-w-md">
          <div class="flex items-center justify-center gap-3 mb-10">
            <img
              src="@/assets/images/logologin.png"
              alt="Logo"
              class="w-14 h-14 object-contain"
            />
            <h1 class="text-2xl font-bold text-bleu-nuit">BarakaGive</h1>
          </div>
          <h2 class="text-3xl font-bold text-bleu-nuit mb-2">
            Mot de passe oublié ?
          </h2>
          <p class="text-slate-700 font-medium mb-8">
            Entrez votre adresse email et nous vous enverrons un lien de
            réinitialisation.
          </p>

          <div
            v-if="successMessage"
            class="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-6"
          >
            <p class="text-sm font-medium text-emerald-800">
              {{ successMessage }}
            </p>
          </div>

          <form v-else @submit.prevent="sendLink" novalidate class="space-y-5">
            <div>
              <label
                class="block text-xs font-bold uppercase text-gray-800 mb-1.5"
              >
                Email <span class="text-red-500">*</span>
              </label>
              <input
                v-model="email"
                type="email"
                @input="touchEmail"
                placeholder="Votre adresse email"
                class="w-full h-12 rounded-lg border px-4 text-sm focus:outline-none focus:ring-2 transition"
                :class="
                  touched && errors.email
                    ? 'border-red-500 focus:ring-red-500/20'
                    : 'border-slate-300 focus:ring-bleu-nuit/30'
                "
              />
              <p
                v-if="touched && errors.email"
                class="mt-1 text-xs text-red-600"
              >
                {{ errors.email }}
              </p>
            </div>

            <p
              v-if="serverError"
              class="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2"
            >
              {{ serverError }}
            </p>

            <button
              type="submit"
              :disabled="loading"
              class="w-full h-12 rounded-lg bg-bleu-nuit hover:bg-[#0a2540] text-white font-semibold uppercase transition disabled:opacity-60 flex items-center justify-center gap-2"
            >
              <span
                v-if="loading"
                class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
              ></span>
              {{ loading ? "Envoi en cours..." : "Envoyer le lien" }}
            </button>
          </form>

          <div class="mt-8 text-center">
            <RouterLink
              to="/connexion"
              class="text-sm font-bold text-bleu-nuit hover:underline flex items-center justify-center gap-2"
            >
              ← Retour à la connexion
            </RouterLink>
          </div>
        </div>

        <div
          class="border-t border-slate-200 pt-5 flex flex-col gap-3 text-xs text-gray-600 lg:flex-row lg:justify-between"
        >
          <div>🔒 Transmission chiffrée de bout en bout</div>
          <div>Assistance : support@barakagive.org</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import api from "@/services/api.js";
import { useFormValidation, rules } from "@/composables/useFormValidation.js";

const { errors, validate } = useFormValidation();
const email = ref("");
const touched = ref(false);
const loading = ref(false);
const serverError = ref("");
const successMessage = ref("");

const touchEmail = () => {
  touched.value = true;
  validate({ email: [rules.email, email.value] });
};

const sendLink = async () => {
  touched.value = true;
  const valid = validate({ email: [rules.email, email.value] });
  if (!valid) return;

  loading.value = true;
  serverError.value = "";
  try {
    await api.post("/api/accounts/password-reset/", { email: email.value });
    successMessage.value = "Si cette adresse correspond à un compte actif, un lien de réinitialisation sera envoyé. Vérifiez votre boîte mail.";
  } catch (err) {
    serverError.value =
      err?.response?.data?.detail ||
      "Impossible d'envoyer le lien. Réessayez plus tard.";
  } finally {
    loading.value = false;
  }
};
</script>
