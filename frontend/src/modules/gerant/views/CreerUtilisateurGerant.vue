<template>
  <div class="min-h-screen bg-white flex justify-center items-start py-8 px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-4xl bg-white rounded-2xl border border-slate-200/60 p-8 shadow-xs-sm">
      <!-- En-tête -->
      <div class="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
        <div>
          <h2 class="text-3xl font-bold text-or">Inviter un nouveau collaborateur</h2>
          <p class="text-gray-600 text-sm mt-1">
            Le collaborateur recevra un lien d'activation sécurisé par email pour définir son mot de passe.
          </p>
        </div>
        <BoutonSecondary to="/gerant/utilisateurs">
          <ArrowLeft :size="16" />
          Retour
        </BoutonSecondary>
      </div>

      <!-- Alertes -->
      <AlertMessage v-if="error" type="error" :message="error" :dismissible="true" @dismiss="error = null" class="mb-6" />
      <AlertMessage v-if="successMessage" type="success" :message="successMessage" class="mb-6" />

      <form @submit.prevent="soumettreFormulaire" class="space-y-8">
        <!-- Section 1 : Informations personnelles -->
        <div>
          <h3 class="text-xl font-bold text-or mb-4 pb-2 border-b">1. Informations personnelles</h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Prénom -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Prénom *</label>
              <input
                v-model="form.first_name"
                type="text"
                required
                placeholder="Ex : Moussa"
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
              />
            </div>

            <!-- Nom -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Nom *</label>
              <input
                v-model="form.last_name"
                type="text"
                required
                placeholder="Ex : Diop"
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
              />
            </div>

            <!-- Email -->
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Adresse e-mail professionnelle *</label>
              <div class="relative">
                <Mail :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  v-model="form.email"
                  type="email"
                  required
                  placeholder="m.diop@ong-partenaire.org"
                  class="w-full rounded-lg border border-gray-300 bg-slate-50 pl-10 pr-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
                />
              </div>
            </div>

            <!-- Téléphone -->
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Téléphone / WhatsApp *</label>
              <div class="relative">
                <Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  v-model="form.phone"
                  type="tel"
                  required
                  placeholder="+221 77 000 00 00"
                  class="w-full rounded-lg border border-gray-300 bg-slate-50 pl-10 pr-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Section 2 : Rôle opérationnel -->
        <div>
          <h3 class="text-xl font-bold text-or mb-4 pb-2 border-b">2. Rôle opérationnel</h3>

          <p class="text-xs text-slate-500 mb-4">
            Sélectionnez les prérogatives accordées à ce membre au sein de votre ONG.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <label
              class="border rounded-xl p-4 cursor-pointer transition flex flex-col justify-between"
              :class="form.role === 'CHEF_PROJET' ? 'border-or bg-or/5 ring-2 ring-or/30' : 'border-slate-200 hover:bg-slate-50'"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="font-bold text-sm text-slate-900">Chef de projet</span>
                <input type="radio" v-model="form.role" value="CHEF_PROJET" class="text-or focus:ring-or" />
              </div>
              <p class="text-xs text-slate-500">
                Gère les campagnes, configure les zones et conçoit les formulaires dynamiques.
              </p>
            </label>

            <label
              class="border rounded-xl p-4 cursor-pointer transition flex flex-col justify-between"
              :class="form.role === 'FINANCE' ? 'border-or bg-or/5 ring-2 ring-or/30' : 'border-slate-200 hover:bg-slate-50'"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="font-bold text-sm text-slate-900">Responsable Finance</span>
                <input type="radio" v-model="form.role" value="FINANCE" class="text-or focus:ring-or" />
              </div>
              <p class="text-xs text-slate-500">
                Supervise les budgets des projets et le suivi financier de l'ONG.
              </p>
            </label>

            <label
              class="border rounded-xl p-4 cursor-pointer transition flex flex-col justify-between"
              :class="form.role === 'AGENT' ? 'border-or bg-or/5 ring-2 ring-or/30' : 'border-slate-200 hover:bg-slate-50'"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="font-bold text-sm text-slate-900">Agent Terrain</span>
                <input type="radio" v-model="form.role" value="AGENT" class="text-or focus:ring-or" />
              </div>
              <p class="text-xs text-slate-500">
                Collecte les données terrain et enregistre les bénéficiaires sur mobile.
              </p>
            </label>
          </div>
        </div>

        <!-- Boutons d'action -->
        <div class="pt-6 border-t flex justify-end gap-4">
          <BoutonSecondary to="/gerant/utilisateurs">
            Annuler
          </BoutonSecondary>

          <button
            type="submit"
            :disabled="loading"
            class="px-6 py-2.5 bg-bleu-nuit text-white font-semibold text-sm rounded-lg hover:bg-[#01111eff] transition shadow-xs flex items-center gap-2 disabled:opacity-50"
          >
            <span v-if="loading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>{{ loading ? "Envoi de l'invitation..." : "Inviter le collaborateur" }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue"
import { useRouter } from "vue-router"
import { ArrowLeft, Mail, Phone } from "lucide-vue-next"
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import ExecutiveOrbitalIA from "@/components/ia/ExecutiveOrbitalIA.vue"

const router = useRouter()
const store = useGerantStore()

const loading = ref(false)
const error = ref(null)
const successMessage = ref("")

const form = reactive({
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  role: "CHEF_PROJET",
})

const soumettreFormulaire = async () => {
  loading.value = true
  error.value = null
  successMessage.value = ""

  try {
    await store.createUser({
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      phone: form.phone,
      role: form.role,
    })

    successMessage.value = `Invitation envoyée avec succès à ${form.email}.`
    setTimeout(() => {
      router.push("/gerant/utilisateurs")
    }, 1500)
  } catch (err) {
    error.value = store.error || "Une erreur est survenue lors de la création de l'utilisateur."
  } finally {
loading.value = false
  }

}
</script>

<ExecutiveOrbitalIA />
