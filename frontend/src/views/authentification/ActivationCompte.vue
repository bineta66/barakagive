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
            Activez votre compte pour accéder à la plateforme.
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
            Activer mon compte
          </h2>
          <p class="text-slate-700 font-medium mb-8">
            Définissez votre mot de passe pour activer votre compte.
          </p>

          <form @submit.prevent="activateAccount" novalidate class="space-y-5">
            <!-- Nouveau mot de passe -->
            <div>
              <label
                class="block text-xs font-bold uppercase text-gray-800 mb-1.5"
              >
                Mot de passe <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  v-model="form.password"
                  @input="touchField('password')"
                  placeholder="Minimum 8 caractères"
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
                Confirmation <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  :type="showConfirm ? 'text' : 'password'"
                  v-model="form.confirmPassword"
                  @input="touchField('confirmPassword')"
                  placeholder="Répétez le mot de passe"
                  class="w-full h-12 rounded-lg border px-4 pr-20 text-sm focus:outline-none focus:ring-2 transition"
                  :class="
                    touched.confirmPassword && errors.confirmPassword
                      ? 'border-red-500 focus:ring-red-500/20'
                      : 'border-slate-300 focus:ring-bleu-nuit/30'
                  "
                />
                <button
                  type="button"
                  @click="showConfirm = !showConfirm"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-500 font-semibold"
                >
                  {{ showConfirm ? "Masquer" : "Afficher" }}
                </button>
              </div>
              <p
                v-if="touched.confirmPassword && errors.confirmPassword"
                class="mt-1 text-xs text-red-600"
              >
                {{ errors.confirmPassword }}
              </p>
            </div>

            <div
              class="flex items-start gap-2 text-xs text-slate-600 bg-slate-50 rounded-lg p-3"
            >
              <svg
                class="w-4 h-4 text-bleu-nuit flex-shrink-0 mt-0.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p>
                Minimum 8 caractères avec au moins 1 majuscule, 1 minuscule, 1
                chiffre et 1 caractère spécial.
              </p>
            </div>

            <AlertMessage
              v-if="errorMessage"
              type="error"
              :message="errorMessage"
              :dismissible="true"
              @dismiss="errorMessage = ''"
            />
            <AlertMessage
              v-if="successMessage"
              type="success"
              :message="successMessage"
            />

            <button
              type="submit"
              :disabled="loading"
              class="w-full h-12 rounded-lg bg-bleu-nuit hover:bg-[#0a2540] text-white font-semibold uppercase transition disabled:opacity-60 flex items-center justify-center gap-2"
            >
              <span
                v-if="loading"
                class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
              ></span>
              {{ loading ? "Activation en cours..." : "Activer mon compte" }}
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
          <div>Transmission chiffrée de bout en bout</div>
          <div>Assistance : support@barakagive.org</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.js";
import { useFormValidation, rules } from "@/composables/useFormValidation.js";
import AlertMessage from "@/components/ui/AlertMessage.vue";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const { errors, validate } = useFormValidation();

const showPassword = ref(false);
const showConfirm = ref(false);
const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const token = ref("");
const touched = reactive({ password: false, confirmPassword: false });

const form = reactive({ password: "", confirmPassword: "" });

// ── Indicateur de force ───────────────────────────────────────────────────────
const passwordStrength = computed(() => {
  const p = form.password;
  if (!p) return 0;
  let s = 0;
  if (p.length >= 8) s++;
  if (/[A-Z]/.test(p)) s++;
  if (/\d/.test(p)) s++;
  if (/[@$!%*?&_\-#^]/.test(p)) s++;
  return s;
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
    ] || ""
);
const strengthLabel = computed(
  () =>
    ["Très faible", "Faible", "Moyen", "Fort"][passwordStrength.value - 1] || ""
);

onMounted(() => {
  token.value = String(route.params.token || route.query.token || "");
});

const touchField = (field) => {
  touched[field] = true;
  runValidation();
};

const runValidation = () =>
  validate({
    password: [rules.password, form.password],
    confirmPassword: [
      rules.passwordConfirm,
      form.confirmPassword,
      form.password,
    ],
  });

const activateAccount = async () => {
  touched.password = true;
  touched.confirmPassword = true;
  if (!runValidation()) return;
  if (!token.value) {
    errorMessage.value = "Le jeton d'activation est manquant.";
    return;
  }

  loading.value = true;
  errorMessage.value = "";
  successMessage.value = "";
  try {
    await authStore.activateAccount(
      token.value,
      form.password,
      form.confirmPassword
    );
    successMessage.value =
      "Votre compte a été activé avec succès ! Redirection vers la connexion...";
    form.password = "";
    form.confirmPassword = "";
    setTimeout(() => router.push("/connexion"), 2000);
  } catch (err) {
    errorMessage.value =
      authStore.error || err?.response?.data?.detail || "Lien d'activation invalide ou expiré.";
  } finally {
    loading.value = false;
  }
};
</script>
