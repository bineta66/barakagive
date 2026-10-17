<template>
  <div class="min-h-screen bg-white">
    <div class="grid min-h-screen lg:grid-cols-2">
      <!-- Gauche -->
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
            Connectez-vous à votre compte BarakaGive.
          </p>
        </div>
      </div>

      <!-- Droite -->
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
          <h2 class="text-3xl font-bold text-bleu-nuit mb-2">Connexion</h2>
          <p class="text-slate-600 font-medium mb-8">
            Connectez-vous à votre compte BarakaGive.
          </p>

          <form @submit.prevent="login" novalidate class="space-y-5">
            <!-- Email -->
            <div>
              <label
                class="block text-xs font-bold uppercase text-gray-800 mb-1.5"
              >
                Email professionnel <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.email"
                type="email"
                @input="touchField('email')"
                placeholder="coordination@barakagive.org"
                class="w-full h-12 rounded-lg border px-4 text-sm focus:outline-none focus:ring-2 transition"
                :class="
                  touched.email && errors.email
                    ? 'border-red-500 focus:ring-red-500/20'
                    : 'border-slate-300 focus:ring-bleu-nuit/30'
                "
              />
              <p
                v-if="touched.email && errors.email"
                class="mt-1 text-xs text-red-600"
              >
                {{ errors.email }}
              </p>
            </div>

            <!-- Mot de passe -->
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
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-500 font-semibold hover:text-bleu-nuit transition"
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
            </div>

            <!-- Options -->
            <div class="flex items-center justify-between">
              <label
                class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer"
              >
                <input
                  type="checkbox"
                  v-model="form.remember"
                  class="rounded border-slate-300"
                />
                Se souvenir de moi
              </label>
              <RouterLink
                to="/mot-de-passe-oublie"
                class="text-sm font-semibold text-bleu-nuit hover:underline"
              >
                Mot de passe oublié ?
              </RouterLink>
            </div>

            <!-- Erreur serveur -->
            <div
              v-if="errorMessage"
              class="rounded-lg border p-4"
              :class="
                isInactiveAccount
                  ? 'bg-amber-50 border-amber-200'
                  : 'bg-red-50 border-red-200'
              "
            >
              <p
                class="text-sm font-medium"
                :class="isInactiveAccount ? 'text-amber-800' : 'text-red-700'"
              >
                {{ errorMessage }}
              </p>
              <div v-if="isInactiveAccount" class="mt-3 flex gap-2">
                <RouterLink
                  to="/activation-compte"
                  class="text-xs font-semibold text-amber-700 underline hover:text-amber-900"
                >
                  Activer mon compte
                </RouterLink>
                <span class="text-amber-400">·</span>
                <button
                  type="button"
                  @click="renvoyerActivation"
                  :disabled="renvoyant"
                  class="text-xs font-semibold text-amber-700 underline hover:text-amber-900 disabled:opacity-50"
                >
                  {{ renvoyant ? "Envoi..." : "Renvoyer l'email d'activation" }}
                </button>
              </div>
            </div>

            <!-- Bouton -->
            <button
              type="submit"
              :disabled="loading"
              class="w-full h-12 rounded-lg bg-bleu-nuit hover:bg-[#0a2540] text-white font-semibold uppercase transition flex items-center justify-center gap-2 disabled:opacity-60"
            >
              <span
                v-if="loading"
                class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
              ></span>
              {{ loading ? "Connexion en cours..." : "Se connecter" }}
            </button>
          </form>
        </div>

        <div
          class="border-t border-slate-200 pt-5 flex flex-col gap-3 text-xs text-gray-600 lg:flex-row lg:justify-between"
        >
          <div class="flex items-center gap-2">🔒 Connexion sécurisée</div>
          <div>Assistance : support@barakagive.org</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.js";
import { useFormValidation, rules } from "@/composables/useFormValidation.js";
import api from "@/services/api.js";

const router = useRouter();
const authStore = useAuthStore();
const { errors, validate } = useFormValidation();

const showPassword = ref(false);
const loading = ref(false);
const renvoyant = ref(false);
const errorMessage = ref("");
const isInactiveAccount = ref(false);

const form = reactive({ email: "", password: "", remember: false });

// touched : affiche les erreurs seulement après blur ou submit
const touched = reactive({ email: false, password: false });

const touchField = (field) => {
  touched[field] = true;
  validate({
    email: [rules.email, form.email],
    password: [rules.required, form.password],
  });
};

const login = async () => {
  touched.email = true;
  touched.password = true;

  const valid = validate({
    email: [rules.email, form.email],
    password: [rules.required, form.password],
  });
  if (!valid) return;

  loading.value = true;
  errorMessage.value = "";
  isInactiveAccount.value = false;
  try {
    const user = await authStore.login(form.email, form.password);
    router.push(authStore.getDefaultRouteForRole(user.role));
  } catch (err) {
    const msg = authStore.error || "Identifiants invalides.";
    errorMessage.value = msg;
    if (msg.toLowerCase().includes("activ")) isInactiveAccount.value = true;
  } finally {
    loading.value = false;
  }
};

const renvoyerActivation = async () => {
  if (!form.email) {
    errorMessage.value = "Veuillez saisir votre email pour renvoyer le lien.";
    return;
  }
  renvoyant.value = true;
  try {
    await api.post("/api/accounts/resend-activation/", { email: form.email });
    errorMessage.value =
      "Email d'activation renvoyé. Vérifiez votre boîte mail.";
    isInactiveAccount.value = false;
  } catch {
    errorMessage.value =
      "Impossible de renvoyer l'email. Contactez le support.";
  } finally {
    renvoyant.value = false;
  }
};
</script>
