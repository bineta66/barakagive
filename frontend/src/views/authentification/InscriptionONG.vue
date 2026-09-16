<template>
  <main class="min-h-screen bg-white">
    <div class="grid min-h-screen lg:grid-cols-2">
      <section class="relative hidden overflow-hidden bg-bleu-nuit lg:flex lg:flex-col lg:justify-end lg:pb-20">
        <img
          src="@/assets/images/imagelogo.png"
          alt="Une équipe BarakaGive"
          class="absolute inset-0 h-full w-full object-cover opacity-60"
        />
        <div class="absolute inset-0 bg-bleu-nuit/60"></div>
        <div class="relative z-10 px-12 text-white">
          <p class="mb-3 text-sm font-bold uppercase tracking-[0.2em] text-or">BarakaGive</p>
          <h1 class="max-w-lg text-4xl font-bold leading-tight">Rejoignez BarakaGive avec votre ONG</h1>
          <p class="mt-4 max-w-lg text-slate-200">
            Créez votre organisation et recevez par email les accès du premier gérant.
          </p>
        </div>
      </section>

      <section class="flex min-h-screen items-start justify-center bg-white px-6 py-10 sm:px-10 lg:overflow-y-auto lg:px-16">
        <div class="w-full max-w-2xl">
          <div class="mb-8 flex items-center gap-3">
            <img src="@/assets/images/logologin.png" alt="Logo BarakaGive" class="h-12 w-12 object-contain" />
            <div>
              <p class="text-xl font-bold text-or">BarakaGive</p>
              <p class="text-xs text-slate-500">Inscription ONG</p>
            </div>
          </div>

          <h2 class="text-3xl font-bold text-bleu-nuit">Créer votre organisation</h2>
          <p class="mt-2 text-sm leading-6 text-slate-600">
            Remplissez les informations de votre ONG et de son premier gérant. Aucun mot de passe n'est demandé ici.
          </p>

          <AlertMessage
            v-if="errorMessage"
            type="error"
            :message="errorMessage"
            :dismissible="true"
            @dismiss="errorMessage = ''"
            class="mt-6"
          />
          <AlertMessage
            v-if="successMessage"
            type="success"
            :message="successMessage"
            class="mt-6"
          />

          <form v-if="!successMessage" class="mt-8 space-y-6" @submit.prevent="submitRegistration">
            <fieldset class="space-y-4">
              <legend class="border-b border-slate-200 pb-2 text-xs font-bold uppercase tracking-wider text-or">
                Informations de l'ONG
              </legend>
              <div class="grid gap-4 sm:grid-cols-2">
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Nom de l'ONG *</label>
                  <input v-model="form.name" type="text" placeholder="Secours Solidarité Sahel" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Acronyme</label>
                  <input v-model="form.acronym" type="text" placeholder="3S" class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Email officiel *</label>
                  <input v-model="form.email" type="email" placeholder="contact@ong.org" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Téléphone *</label>
                  <input v-model="form.phone" type="text" placeholder="+221 33 800 00 00" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Pays *</label>
                  <input v-model="form.country" type="text" placeholder="Sénégal" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Région *</label>
                  <input v-model="form.region" type="text" placeholder="Dakar" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div class="sm:col-span-2">
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Adresse *</label>
                  <input v-model="form.address" type="text" placeholder="Point E, Dakar" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div class="sm:col-span-2">
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Domaine d'intervention *</label>
                  <input v-model="form.intervention_domain" type="text" placeholder="Education, santé, solidarité..." required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div class="sm:col-span-2">
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Logo de l'ONG</label>
                  <input
                    type="file"
                    accept="image/*"
                    class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm file:mr-3 file:border-0 file:bg-slate-100 file:px-3 file:py-1 file:text-xs file:font-semibold"
                    @change="form.logo = $event.target.files?.[0] || null"
                  />
                  <p class="mt-1 text-xs text-slate-400">Facultatif. PNG, JPG ou WEBP.</p>
                </div>
              </div>
            </fieldset>

            <fieldset class="space-y-4">
              <legend class="border-b border-slate-200 pb-2 text-xs font-bold uppercase tracking-wider text-or">
                Informations du premier gérant
              </legend>
              <div class="grid gap-4 sm:grid-cols-2">
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Prénom *</label>
                  <input v-model="form.manager_first_name" type="text" placeholder="Amadou" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Nom *</label>
                  <input v-model="form.manager_last_name" type="text" placeholder="Diallo" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Email du gérant *</label>
                  <input v-model="form.manager_email" type="email" placeholder="gerant@ong.org" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Téléphone du gérant *</label>
                  <input v-model="form.manager_phone" type="text" placeholder="+221 77 000 00 00" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
              </div>
            </fieldset>

            <button
              type="submit"
              :disabled="loading"
              class="flex h-12 w-full items-center justify-center rounded-lg bg-or font-semibold text-white transition hover:bg-[#6b4203] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {{ loading ? "Inscription en cours..." : "Créer mon ONG" }}
            </button>

            <RouterLink to="/connexion" class="block text-center text-sm font-semibold text-bleu-nuit hover:text-or">
              Vous avez déjà un compte ? Se connecter
            </RouterLink>
          </form>

          <div v-else class="mt-8 rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-emerald-900">
            <h3 class="text-lg font-bold">Inscription enregistrée</h3>
            <p class="mt-2 text-sm leading-6">
              Un email d'activation a été envoyé à l'adresse du gérant. Il pourra définir son mot de passe et accéder à son tableau de bord depuis ce lien.
            </p>
            <RouterLink to="/connexion" class="mt-5 inline-block font-bold text-emerald-800 underline">
              Aller à la connexion
            </RouterLink>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { reactive, ref } from "vue"
import { RouterLink } from "vue-router"
import api, { getErrorMessage } from "@/services/api.js"
import AlertMessage from "@/components/ui/AlertMessage.vue"

const loading = ref(false)
const errorMessage = ref("")
const successMessage = ref("")

const form = reactive({
  name: "",
  acronym: "",
  email: "",
  phone: "",
  address: "",
  region: "",
  country: "Sénégal",
  intervention_domain: "",
  logo: null,
  manager_first_name: "",
  manager_last_name: "",
  manager_email: "",
  manager_phone: "",
})

const submitRegistration = async () => {
  loading.value = true
  errorMessage.value = ""
  const payload = new FormData()

  Object.entries(form).forEach(([key, value]) => {
    if (value !== null && value !== "") payload.append(key, value)
  })

  try {
    await api.post("/api/organizations/register/", payload, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    successMessage.value = "Votre ONG est enregistrée. Consultez l'email du gérant pour activer son compte."
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    loading.value = false
  }
}
</script>

