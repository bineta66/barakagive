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
            RÃ©initialisez votre mot de passe en toute sÃ©curitÃ©.
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
            Mot de passe oubliÃ© ?
          </h2>

          <p class="text-slate-700 font-medium mb-8">
            Entrez votre adresse email et nous vous enverrons un lien pour rÃ©initialiser votre mot de passe.
          </p>

          <!-- Formulaire -->
          <form @submit.prevent="sendLink" class="space-y-6">
            <!-- Email -->
            <div>
              <label class="block text-xs font-bold uppercase text-gray-800 mb-2">
                Email
              </label>

              <div class="relative">
                <input
                  v-model="email"
                  type="email"
                  class="w-full h-12 rounded-md border border-slate-300 px-4 focus:outline-none focus:ring-2 focus:ring-or/30"
                  placeholder="Votre adresse email"
                />
              </div>
            </div>

            <!-- Bouton -->
            <button
              class="w-full h-12 rounded-md bg-or hover:bg-[#6b4203] text-white font-semibold uppercase transition"
            >
              Envoyer le lien
            </button>
          </form>

          <!-- Retour -->
          <div class="mt-8 text-center">
            <RouterLink
              to="/connexion"
              class="text-sm font-bold text-gray-800 hover:text-or flex items-center justify-center gap-2"
            >
              â† Retour Ã  la connexion
            </RouterLink>
          </div>
        </div>

        <!-- Footer -->
        <div class="border-t border-slate-200 pt-5 flex flex-col gap-3 text-xs text-gray-600 lg:flex-row lg:justify-between">
          <div class="flex items-center gap-2">
            ðŸ”’ Transmission chiffrÃ©e de bout en bout
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
import { ref } from "vue"

const email = ref("")

const sendLink = () => {
  alert(`Un lien de rÃ©initialisation a Ã©tÃ© envoyÃ© Ã  ${email.value}`)
  email.value = ""
}
</script>

