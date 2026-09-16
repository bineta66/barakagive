<template>
  <div class="max-w-4xl mx-auto p-4 sm:p-6 space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-slate-900">Collecte sur le terrain</h1>
        <p class="text-sm text-slate-500 mt-1">
          Enregistrement d'un bénéficiaire et saisie du questionnaire de collecte.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <span
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold"
          :class="isOnline ? 'bg-emerald-50 text-emerald-700' : 'bg-orange-50 text-orange-700'"
        >
          <span class="w-2 h-2 rounded-full" :class="isOnline ? 'bg-emerald-500' : 'bg-orange-500'"></span>
          {{ isOnline ? 'En ligne' : 'Mode hors-ligne actif' }}
        </span>
      </div>
    </div>

    <!-- Alertes & Messages -->
    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-4" />

    <!-- Formulaire d'enregistrement -->
    <form @submit.prevent="submitCollecte" class="space-y-6">
      <!-- 1. Sélection Campagne & Zone -->
      <div class="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs-sm space-y-4">
        <h2 class="text-lg font-bold text-or flex items-center gap-2 border-b pb-2">
          <span>1. Contexte d'intervention</span>
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold uppercase text-slate-700 mb-1.5">Campagne *</label>
            <select
              v-model="selectedCampagneId"
              @change="onCampagneChange"
              required
              class="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm bg-white focus:ring-2 focus:ring-or/30 outline-none"
            >
              <option value="">Sélectionner une campagne...</option>
              <option v-for="c in campaignStore.campaigns" :key="c.id" :value="c.id">
                {{ c.nom }} ({{ c.code_campagne }})
              </option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold uppercase text-slate-700 mb-1.5">Zone d'intervention *</label>
            <select
              v-model="selectedZoneId"
              required
              :disabled="!zonesDisponibles.length"
              class="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm bg-white focus:ring-2 focus:ring-or/30 outline-none disabled:bg-slate-100"
            >
              <option value="">Sélectionner une zone...</option>
              <option v-for="z in zonesDisponibles" :key="z.id" :value="z.id">
                {{ z.nom }} ({{ z.region }})
              </option>
            </select>
            <p v-if="selectedCampagneId && !zonesDisponibles.length" class="text-xs text-amber-600 mt-1">
              Aucune zone directement associée à cette campagne.
            </p>
          </div>
        </div>

        <div v-if="loadingForm" class="pt-2">
          <LoadingSpinner message="Chargement du formulaire de collecte associé..." />
        </div>
        <div v-else-if="selectedCampagneId && !formulaireActif" class="p-3 bg-amber-50 text-amber-800 text-xs rounded-lg">
          Aucun formulaire publié pour cette campagne. Les questions additionnelles ne s'afficheront pas.
        </div>
      </div>

      <!-- 2. Informations du Bénéficiaire -->
      <div class="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs-sm space-y-4">
        <h2 class="text-lg font-bold text-or flex items-center gap-2 border-b pb-2">
          <span>2. Informations personnelles du bénéficiaire</span>
        </h2>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold uppercase text-slate-700 mb-1.5">Nom de famille *</label>
            <input
              v-model="beneficiary.nom"
              type="text"
              required
              placeholder="Ex: Ndiaye"
              class="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-or/30 outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold uppercase text-slate-700 mb-1.5">Prénom(s) *</label>
            <input
              v-model="beneficiary.prenom"
              type="text"
              required
              placeholder="Ex: Fatou"
              class="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-or/30 outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold uppercase text-slate-700 mb-1.5">Téléphone *</label>
            <input
              v-model="beneficiary.telephone"
              type="tel"
              required
              placeholder="Ex: +221 77 123 45 67"
              class="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-or/30 outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold uppercase text-slate-700 mb-1.5">Sexe *</label>
            <select
              v-model="beneficiary.sexe"
              required
              class="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm bg-white focus:ring-2 focus:ring-or/30 outline-none"
            >
              <option value="FEMME">Femme</option>
              <option value="HOMME">Homme</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold uppercase text-slate-700 mb-1.5">Date de naissance *</label>
            <input
              v-model="beneficiary.date_naissance"
              type="date"
              required
              class="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-or/30 outline-none"
            />
          </div>

          <!-- Position GPS -->
          <div>
            <div class="flex justify-between items-center mb-1.5">
              <label class="block text-xs font-bold uppercase text-slate-700">Coordonnées GPS *</label>
              <button
                type="button"
                @click="detecterGPS"
                class="text-xs text-bleu-nuit hover:underline font-semibold flex items-center gap-1"
              >
                <MapPin :size="12" />
                Détecter ma position
              </button>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <input
                v-model="beneficiary.latitude"
                type="number"
                step="any"
                required
                placeholder="Latitude"
                class="border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-or/30 outline-none"
              />
              <input
                v-model="beneficiary.longitude"
                type="number"
                step="any"
                required
                placeholder="Longitude"
                class="border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-or/30 outline-none"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Formulaire Dynamique de Campagne -->
      <div
        v-if="formulaireActif && questionsFormulaire.length > 0"
        class="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs-sm space-y-5"
      >
        <div class="border-b pb-2">
          <h2 class="text-lg font-bold text-or">
            3. Questionnaire spécifique : {{ formulaireActif.nom }}
          </h2>
          <p class="text-xs text-slate-500 mt-0.5">
            Répondez aux questions définies par le Chef de projet.
          </p>
        </div>

        <div class="space-y-4">
          <div
            v-for="(q, idx) in questionsFormulaire"
            :key="q.id"
            class="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2"
          >
            <div class="flex items-center justify-between">
              <label class="text-sm font-semibold text-slate-900">
                <span class="text-or font-bold mr-1">{{ idx + 1 }}.</span>
                {{ q.label }}
                <span v-if="q.obligatoire" class="text-red-500 ml-1">*</span>
              </label>
              <span class="text-xs text-slate-400 font-mono">{{ q.type }}</span>
            </div>

            <!-- Champs dynamiques -->
            <!-- TEXT -->
            <input
              v-if="q.type === 'TEXT'"
              v-model="reponses[q.id]"
              :required="q.obligatoire"
              :placeholder="q.placeholder || 'Saisissez votre réponse...'"
              type="text"
              class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-or/30 outline-none"
            />

            <!-- NUMBER -->
            <input
              v-else-if="q.type === 'NUMBER'"
              v-model.number="reponses[q.id]"
              :required="q.obligatoire"
              :placeholder="q.placeholder || '0'"
              type="number"
              class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-or/30 outline-none"
            />

            <!-- PHONE -->
            <input
              v-else-if="q.type === 'PHONE'"
              v-model="reponses[q.id]"
              :required="q.obligatoire"
              :placeholder="q.placeholder || '+221 ...'"
              type="tel"
              class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-or/30 outline-none"
            />

            <!-- DATE -->
            <input
              v-else-if="q.type === 'DATE'"
              v-model="reponses[q.id]"
              :required="q.obligatoire"
              type="date"
              class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-or/30 outline-none"
            />

            <!-- YES_NO -->
            <div v-else-if="q.type === 'YES_NO'" class="flex gap-4 pt-1">
              <label class="flex items-center gap-2 cursor-pointer text-sm">
                <input
                  type="radio"
                  :name="'q_' + q.id"
                  :value="true"
                  v-model="reponses[q.id]"
                  :required="q.obligatoire"
                  class="text-bleu-nuit focus:ring-or/30"
                />
                <span>Oui</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer text-sm">
                <input
                  type="radio"
                  :name="'q_' + q.id"
                  :value="false"
                  v-model="reponses[q.id]"
                  :required="q.obligatoire"
                  class="text-bleu-nuit focus:ring-or/30"
                />
                <span>Non</span>
              </label>
            </div>

            <!-- SELECT -->
            <select
              v-else-if="q.type === 'SELECT'"
              v-model="reponses[q.id]"
              :required="q.obligatoire"
              class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-or/30 outline-none"
            >
              <option value="">Sélectionner une option...</option>
              <option v-for="opt in (q.options || [])" :key="opt" :value="opt">
                {{ opt }}
              </option>
            </select>

            <!-- CHECKBOX (Multi-select) -->
            <div v-else-if="q.type === 'CHECKBOX'" class="grid grid-cols-2 gap-2 pt-1">
              <label
                v-for="opt in (q.options || [])"
                :key="opt"
                class="flex items-center gap-2 text-sm cursor-pointer"
              >
                <input
                  type="checkbox"
                  :value="opt"
                  v-model="reponses[q.id]"
                  class="rounded text-bleu-nuit focus:ring-or/30"
                />
                <span>{{ opt }}</span>
              </label>
            </div>

            <!-- TEXTAREA -->
            <textarea
              v-else
              v-model="reponses[q.id]"
              :required="q.obligatoire"
              :placeholder="q.placeholder || 'Saisie détaillée...'"
              rows="2"
              class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-or/30 outline-none"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Bouton de Soumission -->
      <div class="flex justify-end gap-3 pt-4 border-t">
        <router-link
          to="/agent/dashboard"
          class="px-5 py-3 border border-slate-300 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
        >
          Annuler
        </router-link>

        <button
          type="submit"
          :disabled="submitting || !selectedCampagneId || !selectedZoneId"
          class="px-8 py-3 bg-bleu-nuit text-white font-bold rounded-xl shadow-xs-sm hover:bg-[#01111eff] transition disabled:opacity-50 flex items-center gap-2"
        >
          <Send :size="18" />
          <span>{{ submitting ? 'Enregistrement...' : 'Enregistrer le bénéficiaire' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { MapPin, Send } from "lucide-vue-next"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useCampaignStore } from "@/stores/campaign.js"
import { useZoneStore } from "@/stores/zone.js"
import { useFormStore } from "@/stores/form.js"
import { useBeneficiaryStore } from "@/stores/beneficiary.js"

const route = useRoute()
const router = useRouter()
const campaignStore = useCampaignStore()
const zoneStore = useZoneStore()
const formStore = useFormStore()
const beneficiaryStore = useBeneficiaryStore()

const isOnline = ref(typeof navigator !== "undefined" ? navigator.onLine : true)
if (typeof window !== "undefined") {
  window.addEventListener("online", () => (isOnline.value = true))
  window.addEventListener("offline", () => (isOnline.value = false))
}

const selectedCampagneId = ref("")
const selectedZoneId = ref("")
const formulaireActif = ref(null)
const questionsFormulaire = ref([])
const loadingForm = ref(false)
const submitting = ref(false)
const feedback = reactive({ type: "success", message: "" })

const beneficiary = reactive({
  nom: "",
  prenom: "",
  telephone: "",
  sexe: "FEMME",
  date_naissance: "1990-01-01",
  latitude: "14.6937",
  longitude: "-17.4441",
})

const reponses = reactive({})

const zonesDisponibles = computed(() => {
  if (!selectedCampagneId.value) return zoneStore.zones
  const camp = campaignStore.campaigns.find((c) => c.id === selectedCampagneId.value)
  if (camp && camp.zones && camp.zones.length > 0) {
    return camp.zones
  }
  return zoneStore.zones
})

onMounted(async () => {
  await Promise.allSettled([
    campaignStore.fetchCampaigns(),
    zoneStore.fetchZones(),
    formStore.fetchForms(),
  ])

  // Select the campaign from the requested route.
  const routeCampaignId = route.params.id || route.query.campagne
  if (routeCampaignId) {
    selectedCampagneId.value = String(routeCampaignId)
    await onCampagneChange()
  }

  detecterGPS()
})

const detecterGPS = () => {
  if (typeof navigator !== "undefined" && navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        beneficiary.latitude = pos.coords.latitude.toFixed(6)
        beneficiary.longitude = pos.coords.longitude.toFixed(6)
      },
      () => {},
      { timeout: 5000 }
    )
  }
}

const onCampagneChange = async () => {
  formulaireActif.value = null
  questionsFormulaire.value = []
  Object.keys(reponses).forEach((k) => delete reponses[k])

  if (!selectedCampagneId.value) return

  // Auto-select first zone if available
  const camp = campaignStore.campaigns.find((c) => c.id === selectedCampagneId.value)
  if (camp?.zones?.length) {
    selectedZoneId.value = camp.zones[0].id
  }

  loadingForm.value = true
  try {
    const forms = await formStore.fetchForms()
    const found = forms.find(
      (f) => f.campagne?.id === selectedCampagneId.value && f.statut === "PUBLIE"
    ) || forms.find((f) => f.campagne?.id === selectedCampagneId.value)

    if (found) {
      const full = await formStore.fetchForm(found.id)
      formulaireActif.value = full
      questionsFormulaire.value = full.fields || []

      // Initialize default values for questions
      for (const q of questionsFormulaire.value) {
        if (q.type === "CHECKBOX") reponses[q.id] = []
        else if (q.type === "YES_NO") reponses[q.id] = null
        else reponses[q.id] = ""
      }
    }
  } catch (err) {
    console.error("Erreur chargement formulaire:", err)
  } finally {
    loadingForm.value = false
  }
}

const submitCollecte = async () => {
  submitting.value = true
  feedback.message = ""

  // Prepare responses payload
  const formattedResponses = []
  for (const q of questionsFormulaire.value) {
    const val = reponses[q.id]
    if (val !== undefined && val !== null && val !== "") {
      formattedResponses.push({
        question_id: q.id,
        value: val,
      })
    }
  }

  // Build local_id and payload
  const localId = typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `local-${Date.now()}`
  const deviceId = "agent-browser-" + (typeof navigator !== "undefined" ? navigator.userAgent.substring(0, 30) : "web")

  const payload = {
    campagne_id: selectedCampagneId.value,
    formulaire_id: formulaireActif.value?.id || "00000000-0000-0000-0000-000000000000",
    zone_id: selectedZoneId.value,
    local_id: localId,
    device_id: deviceId,
    beneficiary: {
      nom: beneficiary.nom,
      prenom: beneficiary.prenom,
      telephone: beneficiary.telephone,
      sexe: beneficiary.sexe,
      date_naissance: beneficiary.date_naissance,
      latitude: String(beneficiary.latitude),
      longitude: String(beneficiary.longitude),
    },
    responses: formattedResponses,
  }

  try {
    const res = await beneficiaryStore.submitBeneficiary(payload)
    if (res.offline) {
      feedback.type = "warning"
      feedback.message = "Données enregistrées en local (mode hors-ligne). Elles seront synchronisées dès le retour du réseau."
    } else {
      feedback.type = "success"
      feedback.message = "Bénéficiaire enregistré et validé avec succès sur le serveur !"
    }

    // Reset personal info
    beneficiary.nom = ""
    beneficiary.prenom = ""
    beneficiary.telephone = ""
    Object.keys(reponses).forEach((k) => {
      if (Array.isArray(reponses[k])) reponses[k] = []
      else reponses[k] = ""
    })
  } catch (err) {
    feedback.type = "error"
    if (err.status === 409 || err.message?.includes("déjà inscrit")) {
      feedback.message = "Doublon détecté : ce bénéficiaire est déjà enregistré pour cette campagne."
    } else {
      feedback.message = beneficiaryStore.error || "Erreur lors de l'enregistrement du bénéficiaire."
    }
  } finally {
    submitting.value = false
  }
}
</script>

