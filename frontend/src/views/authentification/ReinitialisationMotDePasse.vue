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
            Choisissez un nouveau mot de passe sécurisé.
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
            Réinitialiser le mot de passe
          </h2>
          <p class="text-slate-700 font-medium mb-8">
            Entrez et confirmez votre nouveau mot de passe.
          </p>

          <form @submit.prevent="enregistrer" novalidate class="space-y-5">
            <!-- Nouveau mot de passe -->
            <div>
              <label
                class="block text-xs font-bold uppercase text-gray-800 mb-1.5"
              >
                Nouveau mot de passe <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  v-model="form.password"
                  @input="touchField('password')"
                  placeholder="********"
                  class="w-full h-12 rounded-lg border px-4 pr-20 text-sm focus:outline-none focus:ring-2 transition"
                  :class="
                    touched.password && errors.password
                      ? 'border-red-500 focus:ring-red-500/20'
                      : 'border-slate-300 focus:ring-bleu-nuit/30'
                  "
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-500 font-semibold"
                >
                  {{ showPassword ? "Masquer" : "Afficher" }}
                </button>
              </div>
              <p
                v-if="touched.password && errors.password"
                class="mt-1 text-xs text-red-600"
              >
                {{ errors.password }}
              </p>
              <!-- Indicateur de force -->
              <div v-if="form.password" class="mt-2 space-y-1">
                <div class="flex gap-1">
                  <div
                    v-for="i in 4"
                    :key="i"
                    class="h-1 flex-1 rounded-full transition-all"
                    :class="
                      passwordStrength >= i ? strengthColor : 'bg-slate-200'
                    "
                  ></div>
                </div>
                <p class="text-xs" :class="strengthTextColor">
                  {{ strengthLabel }}
                </p>
              </div>
            </div>

            <!-- Confirmation -->
            <div>
              <label
                class="block text-xs font-bold uppercase text-gray-800 mb-1.5"
              >
                Confirmation du mot de passe <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  :type="showConfirmation ? 'text' : 'password'"
                  v-model="form.confirmation"
                  @input="touchField('confirmation')"
                  placeholder="********"
                  class="w-full h-12 rounded-lg border px-4 pr-20 text-sm focus:outline-none focus:ring-2 transition"
                  :class="
                    touched.confirmation && errors.confirmation
                      ? 'border-red-500 focus:ring-red-500/20'
                      : 'border-slate-300 focus:ring-bleu-nuit/30'
                  "
                />
                <button
                  type="button"
                  @click="showConfirmation = !showConfirmation"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-500 font-semibold"
                >
                  {{ showConfirmation ? "Masquer" : "Afficher" }}
                </button>
              </div>
              <p
                v-if="touched.confirmation && errors.confirmation"
                class="mt-1 text-xs text-red-600"
              >
                {{ errors.confirmation }}
              </p>
            </div>

            <p
              v-if="serverError"
              class="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2"
            >
              {{ serverError }}
            </p>
            <p
              v-if="successMsg"
              class="text-xs text-emerald-600 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2"
            >
              {{ successMsg }}
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
              {{
                loading
                  ? "Enregistrement..."
                  : "Enregistrer le nouveau mot de passe"
              }}
            </button>

            <RouterLink
              to="/connexion"
              class="flex h-12 items-center justify-center rounded-lg border border-bleu-nuit text-bleu-nuit font-bold text-sm hover:bg-bleu-nuit/10 transition"
            >
              Retour à la connexion
            </RouterLink>
          </form>
        </div>

        <div
          class="border-t border-slate-200 pt-5 flex flex-col gap-3 text-xs text-gray-600 lg:flex-row lg:justify-between"
        >
          <div>🔒 Lien de réinitialisation sécurisé à usage unique</div>
          <div>Assistance : support@barakagive.org</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import api from "@/services/api.js";
import { useFormValidation, rules } from "@/composables/useFormValidation.js";

const router = useRouter();
const route = useRoute();
const { errors, validate } = useFormValidation();

const showPassword = ref(false);
const showConfirmation = ref(false);
const loading = ref(false);
const serverError = ref("");
const successMsg = ref("");
const touched = reactive({ password: false, confirmation: false });

const form = reactive({ password: "", confirmation: "" });

// ── Indicateur de force ───────────────────────────────────────────────────────
const passwordStrength = computed(() => {
  const p = form.password;
  if (!p) return 0;
  let score = 0;
  if (p.length >= 8) score++;
  if (/[A-Z]/.test(p)) score++;
  if (/\d/.test(p)) score++;
  if (/[@$!%*?&_\-#^]/.test(p)) score++;
  return score;
});

const strengthColor = computed(
  () =>
    ["bg-red-500", "bg-red-500", "bg-amber-500", "bg-emerald-500"][
      passwordStrength.value - 1
    ] || "bg-slate-200"
);
const strengthTextColor = computed(
  () =>
    ["text-red-600", "text-red-600", "text-amber-600", "text-emerald-600"][
      passwordStrength.value - 1
    ] || "text-slate-400"
);
const strengthLabel = computed(
  () =>
    ["Très faible", "Faible", "Moyen", "Fort"][passwordStrength.value - 1] || ""
);

const touchField = (field) => {
  touched[field] = true;
  runValidation();
};

const runValidation = () =>
  validate({
    password: [rules.password, form.password],
    confirmation: [rules.passwordConfirm, form.confirmation, form.password],
  });

const enregistrer = async () => {
  touched.password = true;
  touched.confirmation = true;
  if (!runValidation()) return;

  loading.value = true;
  serverError.value = "";
  successMsg.value = "";
  try {
    const token = route.query.token || route.params.token;
    await api.post("/api/accounts/password-reset/confirm/", {
      token,
      password: form.password,
      password_confirm: form.confirmation,
    });
    successMsg.value = "Mot de passe réinitialisé avec succès ! Redirection...";
    setTimeout(() => router.push("/connexion"), 2000);
  } catch (err) {
    serverError.value =
      err?.response?.data?.detail ||
      "Lien invalide ou expiré. Redemandez un lien.";
  } finally {
    loading.value = false;
  }
};
</script>
