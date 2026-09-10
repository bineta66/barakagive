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
          Choisissez un nouveau mot de passe sécurisé
          pour votre compte.
        </p>
      </div>
    </div>

    <!-- ===== Colonne droite ===== -->
    <div class="w-full lg:w-1/2 bg-white flex items-center justify-center px-6 py-10">
      <div class="w-full max-w-md">
        <h2 class="text-4xl font-bold text-amber-800 mb-3">
          Mot de passe oublié ?
        </h2>

        <p class="text-slate-700 font-medium leading-6 mb-8">
          Entrez votre adresse email et nous vous enverrons un lien
          pour réinitialiser votre mot de passe.
        </p>

        <form @submit.prevent="sendLink" class="space-y-6">
          <!-- Email -->
          <div>
            <label class="block text-xs font-bold tracking-wider uppercase text-gray-700 mb-2">
              Email
            </label>

            <div class="relative">
              <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                ✉
              </span>

              <input
                v-model="email"
                type="email"
                placeholder="Votre adresse email"
                class="w-full h-12 rounded-md border border-slate-300 bg-slate-50 pl-11 pr-4 focus:outline-none focus:ring-2 focus:ring-amber-700"
                required
              />
            </div>
          </div>

          <!-- Bouton -->
          <button
            type="submit"
            class="w-full h-12 rounded-md bg-amber-800 hover:bg-amber-900 text-white font-semibold uppercase tracking-wide transition"
          >
            Envoyer le lien
          </button>
        </form>

        <!-- Retour -->
        <div class="border-t border-slate-200 mt-8 pt-6">
          <RouterLink
            to="/connexion"
            class="text-sm font-bold text-slate-800 hover:text-amber-800 flex items-center gap-2"
          >
            ← Retour à la connexion
          </RouterLink>
        </div>

        <!-- Footer -->
        <div class="mt-10 flex items-start gap-3 text-xs text-slate-600 leading-5">
          <span>🔒</span>
          <p>
            Transmission chiffrée de bout en bout • Assistance HQ :
            <span class="font-semibold">support@barakagive.org</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"

const email = ref("")

const sendLink = () => {
  alert(`Un lien de réinitialisation a été envoyé à ${email.value}`)
  email.value = ""
}
</script>