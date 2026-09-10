<template>
  <div class="min-h-screen flex bg-slate-100">
    <!-- ===== Colonne gauche ===== -->
    <div class="hidden lg:flex lg:w-1/2 bg-[#021427] relative items-center justify-center overflow-hidden">
      <div class="relative z-10 flex flex-col items-center text-center px-10">
        <!-- Logo -->
        <img src="@/assets/images/image.png" alt="Logo BarakaGive" class="w-36 h-36 object-contain mb-8" />

        <h1 class="text-3xl font-bold text-white mb-6">
          Nous sommes là pour vous aider
        </h1>

        <!-- Progress -->
        <div class="flex items-center mb-6">
          <div class="w-10 h-[2px] bg-sky-700"></div>
          <div class="w-2 h-2 bg-emerald-400 rounded-full mx-3"></div>
          <div class="w-10 h-[2px] bg-sky-700"></div>
        </div>

        <p class="text-white/90 font-medium leading-7">
          Connectez-vous à votre compte BarakaGive
        </p>
      </div>
    </div>

    <!-- ===== Colonne droite ===== -->
    <div class="w-full lg:w-1/2 bg-white flex items-center justify-center px-6 py-10">
      <div class="w-full max-w-md">
        <h2 class="text-4xl font-bold text-amber-800 mb-3">
          Connexion
        </h2>

        <p class="text-slate-700 font-medium leading-6 mb-8">
          Connectez-vous à votre compte BarakaGive
        </p>

        <form @submit.prevent="login" class="space-y-6">
          <!-- Email -->
          <div>
            <label class="block text-xs font-bold tracking-wider uppercase text-gray-700 mb-2">
              Email professionnel
            </label>

            <div class="relative">
              <input
                v-model="form.email"
                type="email"
                placeholder="coordination@barakagive.org"
                class="w-full h-12 rounded-md border border-slate-300 bg-slate-50 pl-4 pr-4 focus:outline-none focus:ring-2 focus:ring-amber-700"
                required
              />
            </div>
          </div>

          <!-- Mot de passe -->
          <div>
            <label class="block text-xs font-bold tracking-wider uppercase text-gray-700 mb-2">
              Mot de passe
            </label>

            <div class="relative">
              <input
                :type="showPassword ? 'text' : 'password'"
                v-model="form.password"
                placeholder="••••••••••••"
                class="w-full h-12 rounded-md border border-slate-300 bg-slate-50 pl-4 pr-12 focus:outline-none focus:ring-2 focus:ring-amber-700"
                required
              />

              <button
                type="button"
                class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                @click="showPassword = !showPassword"
              >
                {{ showPassword ? "🙈" : "👁" }}
              </button>
            </div>
          </div>

          <!-- Options -->
          <div class="flex items-center justify-between">
            <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
              <input type="checkbox" v-model="form.remember" class="rounded border-slate-300" />
              Se souvenir de moi sur cet appareil sécurisé
            </label>

            <RouterLink to="/mot-de-passe-oublie" class="text-sm font-semibold text-amber-800 hover:text-amber-900">
              Mot de passe oublié ?
            </RouterLink>
          </div>

          <!-- Bouton -->
          <button
            type="submit"
            class="w-full h-12 rounded-md bg-amber-800 hover:bg-amber-900 text-white font-semibold uppercase tracking-wide transition"
          >
            Se connecter
          </button>
        </form>

        <!-- Lien activation -->
        <div class="mt-8 text-center">
          <span class="text-sm text-slate-600">
            Première connexion ou compte non activé ?
          </span>
          <RouterLink
            to="/activation-compte"
            class="block text-sm font-bold text-amber-800 hover:text-amber-900 mt-1"
          >
            Activer votre compte
          </RouterLink>
        </div>

        <!-- Footer -->
        <div class="mt-10 flex items-start gap-3 text-xs text-slate-600 leading-5">
          <span>🔒</span>
          <p>
            Connexion sécurisée • Assistance HQ :
            <span class="font-semibold">support@barakagive.org</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue"

const showPassword = ref(false)

const form = reactive({
  email: "",
  password: "",
  remember: false,
})

const login = () => {
  alert(`Connexion simulée pour ${form.email}`)
}
</script>
