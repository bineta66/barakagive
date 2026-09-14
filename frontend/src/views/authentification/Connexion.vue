<template>
  <div class="min-h-screen bg-slate-100">
    <div class="grid min-h-screen lg:grid-cols-2">
      <!-- ===== Partie gauche ===== -->
      <div class="relative hidden lg:flex items-end justify-center bg-bleu-nuit overflow-hidden pb-20">
        <!-- Image de fond -->
        <img
          src="@/assets/images/imagelogo.png"
          alt="Fond"
          class="absolute inset-0 w-full h-full object-cover opacity-70"
        />

        <div class="absolute inset-0 bg-bleu-nuit/40"></div>

        <div class="relative z-10 flex flex-col items-center text-center px-10">
          <p class="text-xl text-white font-semibold leading-8 max-w-sm">
            Connectez-vous Ã  votre compte BarakaGive.
          </p>

          
        </div>
      </div>

      <!-- ===== Partie droite ===== -->
      <div class="flex flex-col justify-between bg-white px-8 py-10 lg:px-20">
        <div></div>

        <div class="mx-auto w-full max-w-md">
          <!-- Logo -->
          <div class="flex items-center justify-center gap-3 mb-10">
            <img
              src="@/assets/images/logologin.png"
              alt="Logo"
              class="w-14 h-14 object-contain"
            />
            <h1 class="text-2xl font-bold text-or">
              BarakaGive
            </h1>
          </div>

          <!-- Titre -->
          <h2 class="text-3xl font-bold text-or mb-2">
            Connexion
          </h2>

          <p class="text-slate-700 font-medium mb-8">
            Connectez-vous Ã  votre compte BarakaGive.
          </p>

          <!-- Formulaire -->
          <form @submit.prevent="login" class="space-y-6">
            <!-- Email -->
            <div>
              <label class="block text-xs font-bold uppercase text-gray-800 mb-2">
                Email professionnel
              </label>

              <div class="relative">
                <input
                  v-model="form.email"
                  type="email"
                  class="w-full h-12 rounded-md border border-slate-300 px-4 focus:outline-none focus:ring-2 focus:ring-or/30"
                  placeholder="coordination@barakagive.org"
                />
              </div>
            </div>

            <!-- Mot de passe -->
            <div>
              <label class="block text-xs font-bold uppercase text-gray-800 mb-2">
                Mot de passe
              </label>

              <div class="relative">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  v-model="form.password"
                  class="w-full h-12 rounded-md border border-slate-300 px-4 pr-12 focus:outline-none focus:ring-2 focus:ring-or/30"
                  placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢"
                />

                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500"
                >
                  {{ showPassword ? "ðŸ™ˆ" : "ðŸ‘" }}
                </button>
              </div>
            </div>

            <!-- Options -->
            <div class="flex items-center justify-between">
              <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input type="checkbox" v-model="form.remember" class="rounded border-slate-300" />
                Se souvenir de moi
              </label>

              <RouterLink to="/mot-de-passe-oublie" class="text-sm font-semibold text-bleu-nuit hover:text-or">
                Mot de passe oubliÃ© ?
              </RouterLink>
            </div>

            <!-- Bouton -->
            <button
              class="w-full h-12 rounded-md bg-or hover:bg-[#6b4203] text-white font-semibold uppercase transition"
            >
              Se connecter
            </button>
          </form>

          <!-- Lien activation -->
          <div class="mt-8 text-center">
            <span class="text-sm text-gray-600">
              PremiÃ¨re connexion ou compte non activÃ© ?
            </span>
            <RouterLink
              to="/activation-compte"
              class="block text-sm font-bold text-bleu-nuit hover:text-or mt-1"
            >
              Activer votre compte
            </RouterLink>
          </div>
        </div>

        <!-- Footer -->
        <div class="border-t border-slate-200 pt-5 flex flex-col gap-3 text-xs text-gray-600 lg:flex-row lg:justify-between">
          <div class="flex items-center gap-2">
            ðŸ”’ Connexion sÃ©curisÃ©e
          </div>

          <div>
            Assistance : support@barakagive.org
          </div>
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
  alert(`Connexion simulÃ©e pour ${form.email}`)
}
</script>

