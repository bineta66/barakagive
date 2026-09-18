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
            Créez votre organisation en 3 étapes. Aucun mot de passe n'est demandé pendant l'inscription.
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

          <div class="mb-8">
            <div class="flex items-center gap-3">
              <div v-for="step in steps" :key="step.key" class="flex items-center gap-2">
                <div
                  class="flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold"
                  :class="step.key <= currentStep ? 'bg-or text-white' : 'bg-slate-200 text-slate-600'"
                >
                  {{ step.key }}
                </div>
                <span class="hidden text-sm font-semibold sm:inline" :class="step.key <= currentStep ? 'text-slate-900' : 'text-slate-500'">
                  {{ step.label }}
                </span>
              </div>
              <div v-if="currentStep < 3" class="mx-3 h-px flex-1 bg-slate-200"></div>
            </div>
          </div>

          <AlertMessage v-if="errorMessage" type="error" :message="errorMessage" :dismissible="true" @dismiss="errorMessage = ''" class="mb-6" />
          <AlertMessage v-if="successMessage" type="success" :message="successMessage" class="mb-6" />

          <div v-if="!successMessage" class="space-y-6">
            <div v-if="currentStep === 1">
              <h2 class="text-xl font-bold text-bleu-nuit mb-1">Informations de l'ONG</h2>
              <p class="text-sm text-slate-600 mb-6">Renseignez les informations officielles de votre organisation.</p>
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
              </div>
              <div class="mt-6 flex justify-end">
                <button type="button" @click="nextStep" class="h-11 rounded-lg bg-or px-6 text-sm font-semibold text-white hover:bg-[#6b4203]">Suivant</button>
              </div>
            </div>

            <div v-if="currentStep === 2">
              <h2 class="text-xl font-bold text-bleu-nuit mb-1">Documents de vérification</h2>
              <p class="text-sm text-slate-600 mb-6">Ces documents permettront au Super Admin de vérifier que votre organisation est légalement reconnue.</p>
              <div class="space-y-4">
                <div class="rounded-lg border border-slate-200 p-4">
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Récépissé de l'ONG (PDF) *</label>
                  <input type="file" accept="application/pdf" class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm file:mr-3 file:border-0 file:bg-slate-100 file:px-3 file:py-1 file:text-xs file:font-semibold" @change="(e) => onFileChange(e, 'receipt')" />
                  <div v-if="files.receipt" class="mt-2 text-xs text-slate-600">{{ files.receipt.name }} - {{ formatSize(files.receipt.size) }} <button type="button" class="ml-2 text-red-600 underline" @click="files.receipt = null">Remplacer</button></div>
                </div>
                <div class="rounded-lg border border-slate-200 p-4">
                  <label class="mb-1 block text-xs font-semibold text-slate-700">NINEA ou Registre (PDF) *</label>
                  <input type="file" accept="application/pdf" class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm file:mr-3 file:border-0 file:bg-slate-100 file:px-3 file:py-1 file:text-xs file:font-semibold" @change="(e) => onFileChange(e, 'ninea')" />
                  <div v-if="files.ninea" class="mt-2 text-xs text-slate-600">{{ files.ninea.name }} - {{ formatSize(files.ninea.size) }} <button type="button" class="ml-2 text-red-600 underline" @click="files.ninea = null">Remplacer</button></div>
                </div>
                <div class="rounded-lg border border-slate-200 p-4">
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Statuts de l'association (PDF) *</label>
                  <input type="file" accept="application/pdf" class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm file:mr-3 file:border-0 file:bg-slate-100 file:px-3 file:py-1 file:text-xs file:font-semibold" @change="(e) => onFileChange(e, 'statutes')" />
                  <div v-if="files.statutes" class="mt-2 text-xs text-slate-600">{{ files.statutes.name }} - {{ formatSize(files.statutes.size) }} <button type="button" class="ml-2 text-red-600 underline" @click="files.statutes = null">Remplacer</button></div>
                </div>
              </div>
              <div class="mt-6 flex justify-between">
                <button type="button" @click="currentStep -= 1" class="h-11 rounded-lg border border-slate-300 px-6 text-sm font-semibold text-slate-700 hover:bg-slate-50">Précédent</button>
                <button type="button" @click="nextStep" class="h-11 rounded-lg bg-or px-6 text-sm font-semibold text-white hover:bg-[#6b4203]">Suivant</button>
              </div>
            </div>

            <div v-if="currentStep === 3">
              <h2 class="text-xl font-bold text-bleu-nuit mb-1">Informations du Gérant</h2>
              <p class="text-sm text-slate-600 mb-6">Ces informations serviront à créer le compte principal de l'ONG.</p>
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
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Email du Gérant *</label>
                  <input v-model="form.manager_email" type="email" placeholder="gerant@ong.org" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
                <div>
                  <label class="mb-1 block text-xs font-semibold text-slate-700">Téléphone *</label>
                  <input v-model="form.manager_phone" type="text" placeholder="+221 77 000 00 00" required class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-or focus:ring-2 focus:ring-or/20" />
                </div>
              </div>

              <div class="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                <p class="font-semibold mb-2">Que se passe-t-il ensuite ?</p>
                <ol class="list-decimal list-inside space-y-1">
                  <li>Votre demande sera envoyée au Super Admin.</li>
                  <li>Vos documents seront vérifiés.</li>
                  <li>Vous recevrez un email d'activation après approbation.</li>
                  <li>Votre essai gratuit de 30 jours commencera lors de votre première connexion.</li>
                </ol>
              </div>

              <div class="mt-6 flex justify-between">
                <button type="button" @click="currentStep -= 1" class="h-11 rounded-lg border border-slate-300 px-6 text-sm font-semibold text-slate-700 hover:bg-slate-50">Précédent</button>
                <button type="button" @click="submitRegistration" :disabled="loading" class="h-11 rounded-lg bg-or px-6 text-sm font-semibold text-white hover:bg-[#6b4203] disabled:opacity-60">
                  {{ loading ? "Inscription en cours..." : "Créer mon ONG" }}
                </button>
              </div>
            </div>
          </div>

          <div v-else class="mt-8 rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-emerald-900">
            <h3 class="text-lg font-bold">Demande envoyée avec succès</h3>
            <p class="mt-2 text-sm leading-6">
              Votre dossier est en attente de validation par le Super Admin. Nous vous enverrons un email dès que votre ONG sera approuvée.
            </p>
            <RouterLink to="/connexion" class="mt-5 inline-block font-bold text-emerald-800 underline">
              Retour à la connexion
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

const currentStep = ref(1)
const steps = [
  { key: 1, label: "Informations" },
  { key: 2, label: "Documents" },
  { key: 3, label: "Gérant" },
]
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
  manager_first_name: "",
  manager_last_name: "",
  manager_email: "",
  manager_phone: "",
})

const files = reactive({
  receipt: null,
  ninea: null,
  statutes: null,
})

const formatSize = (bytes) => {
  if (!bytes) return "0 octet"
  const mb = bytes / (1024 * 1024)
  return mb >= 1 ? `${mb.toFixed(2)} Mo` : `${(bytes / 1024).toFixed(2)} Ko`
}

const onFileChange = (event, key) => {
  const file = event.target.files?.[0] || null
  files[key] = file
}

const validateStep = () => {
  if (currentStep.value === 1) {
    if (!form.name || !form.email || !form.phone || !form.country || !form.region || !form.address || !form.intervention_domain) {
      errorMessage.value = "Veuillez remplir tous les champs obligatoires."
      return false
    }
  }
  if (currentStep.value === 2) {
    if (!files.receipt || !files.ninea || !files.statutes) {
      errorMessage.value = "Veuillez joindre les 3 documents PDF requis."
      return false
    }
  }
  if (currentStep.value === 3) {
    if (!form.manager_first_name || !form.manager_last_name || !form.manager_email || !form.manager_phone) {
      errorMessage.value = "Veuillez remplir les informations du gérant."
      return false
    }
  }
  return true
}

const nextStep = () => {
  errorMessage.value = ""
  if (!validateStep()) return
  if (currentStep.value < 3) currentStep.value += 1
}

const submitRegistration = async () => {
  loading.value = true
  errorMessage.value = ""
  successMessage.value = ""

  const payload = new FormData()
  Object.entries(form).forEach(([key, value]) => {
    if (value !== null && value !== "") payload.append(key, value)
  })
  Object.entries(files).forEach(([key, file]) => {
    if (file) payload.append(`document_${key}`, file)
  })

  try {
    await api.post("/api/organizations/register/", payload, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    successMessage.value = "Demande envoyée avec succès."
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    loading.value = false
  }
}
</script>
