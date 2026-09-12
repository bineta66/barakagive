<template>
  <div class="min-h-screen bg-slate-100">
    <div class="grid min-h-screen lg:grid-cols-2">
      <!-- ===== Partie gauche ===== -->
      <div class="relative hidden lg:flex items-end justify-center bg-slate-900 overflow-hidden pb-20">
        <!-- Image de fond -->
        <img
          src="@/assets/images/imagelogo.png"
          alt="Fond"
          class="absolute inset-0 w-full h-full object-cover opacity-70"
        />

        <div class="absolute inset-0 bg-slate-900/40"></div>

        <div class="relative z-10 flex flex-col items-center text-center px-10">
          <p class="text-xl text-white font-semibold leading-8 max-w-sm">
            Choisissez un nouveau mot de passe sécurisé pour votre compte.
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
            <h1 class="text-2xl font-bold text-yellow-800">
              BarakaGive
            </h1>
          </div>

          <!-- Titre -->
          <h2 class="text-3xl font-bold text-yellow-800 mb-2">
            Réinitialiser le mot de passe
          </h2>

          <p class="text-slate-700 font-medium mb-8">
            Entrez votre nouveau mot de passe.
          </p>

          <!-- Formulaire -->
          <form @submit.prevent="enregistrer" class="space-y-6">
            <!-- Nouveau mot de passe -->
            <div>
              <label class="block text-xs font-bold uppercase text-gray-800 mb-2">
                Nouveau mot de passe
              </label>

              <div class="relative">
                <input
                  :type="voirMotDePasse ? 'text' : 'password'"
                  v-model="form.password"
                  class="w-full h-12 rounded-md border border-slate-300 px-4 pr-12 focus:outline-none focus:ring-2 focus:ring-yellow-700"
                  placeholder="••••••••••••"
                />

                <button
                  type="button"
                  @click="voirMotDePasse = !voirMotDePasse"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500"
                >
                  👁
                </button>
              </div>
            </div>

            <!-- Confirmation -->
            <div>
              <label class="block text-xs font-bold uppercase text-gray-800 mb-2">
                Confirmation du mot de passe
              </label>

              <div class="relative">
                <input
                  :type="voirConfirmation ? 'text' : 'password'"
                  v-model="form.confirmation"
                  class="w-full h-12 rounded-md border border-slate-300 px-4 pr-12 focus:outline-none focus:ring-2 focus:ring-yellow-700"
                  placeholder="••••••••••••"
                />

                <button
                  type="button"
                  @click="voirConfirmation = !voirConfirmation"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500"
                >
                  👁
                </button>
              </div>
            </div>

            <!-- Information -->
            <div class="flex items-start gap-2 text-xs text-gray-700">
              <input type="checkbox" checked disabled class="mt-1" />
              <p>
                Utilisez un mot de passe suffisamment long et difficile à deviner.
              </p>
            </div>

            <!-- Bouton -->
            <button
              class="w-full h-12 rounded-md bg-yellow-800 hover:bg-yellow-900 text-white font-semibold uppercase transition"
            >
              Enregistrer le nouveau mot de passe
            </button>

            <!-- Retour -->
            <RouterLink
              to="/connexion"
              class="flex h-12 items-center justify-center rounded-md border border-yellow-800 text-yellow-800 font-bold text-sm hover:bg-yellow-50 transition"
            >
              ← Retour à la connexion
            </RouterLink>
          </form>
        </div>

        <!-- Footer -->
        <div class="border-t border-slate-200 pt-5 flex flex-col gap-3 text-xs text-gray-600 lg:flex-row lg:justify-between">
          <div class="flex items-center gap-2">
            🔒 Lien de réinitialisation sécurisé à usage unique
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

const voirMotDePasse = ref(false)
const voirConfirmation = ref(false)

const form = reactive({
  password: "",
  confirmation: "",
})

const enregistrer = () => {
  if (form.password !== form.confirmation) {
    alert("Les mots de passe ne correspondent pas.")
    return
  }

  alert("Mot de passe réinitialisé avec succès !")
}
</script>
