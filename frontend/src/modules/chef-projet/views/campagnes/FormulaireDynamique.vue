<template>
  <div class="w-full max-w-[1152px] border-slate-200/60 inline-flex flex-col justify-start items-start p-8 min-h-screen">
    <div class="self-stretch mb-6">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h2 class="text-3xl font-bold" style="color: #744D03">
              {{ titreFormulaire }}
            </h2>
            <span
              v-if="currentForm"
              class="px-2.5 py-1 text-xs font-semibold rounded-full"
              :class="currentForm.statut === 'PUBLIE' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
            >
              {{ currentForm.statut === 'PUBLIE' ? 'Publié' : 'Brouillon' }}
            </span>
          </div>
          <p class="text-gray-600 text-sm mt-1">
            Configurez les questions de collecte qui seront remplies par les agents de terrain pour cette campagne.
          </p>
        </div>

        <div class="flex gap-3">
          <router-link
            to="/chef-projet/campagnes"
            class="border font-semibold px-5 py-2.5 rounded-lg text-sm flex items-center gap-2 hover:bg-slate-50 transition"
            style="border-color: #744D03; color: #744D03"
          >
            Retour aux campagnes
          </router-link>

          <button
            v-if="currentForm && currentForm.statut !== 'PUBLIE'"
            @click="publier"
            :disabled="publishing || !questions.length"
            class="text-white px-5 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2 transition disabled:opacity-50"
            style="background-color: #021427"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            {{ publishing ? "Publication..." : "Publier le formulaire" }}
          </button>
        </div>
      </div>
    </div>

    <LoadingSpinner v-if="loadingInit" message="Chargement du formulaire de campagne..." />
    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="w-full mb-6" />

    <div v-if="!loadingInit" class="self-stretch flex flex-col gap-6">
      <div v-if="formsList.length > 1 || showNewFormButton" class="bg-white border border-slate-200/60 rounded-xl p-4 shadow-xs-sm">
        <div class="flex items-center justify-between mb-3">
          <div>
            <h3 class="text-sm font-bold uppercase text-slate-900">Formulaires de cette campagne</h3>
            <p class="text-xs text-gray-500 mt-1">
              Une campagne peut avoir plusieurs versions de formulaire.
            </p>
          </div>
          <button
            type="button"
            @click="createNewForm"
            :disabled="creatingForm"
            class="px-3 py-2 bg-bleu-nuit text-white text-xs font-semibold rounded-lg hover:bg-[#01111eff] disabled:opacity-50 transition"
          >
            {{ creatingForm ? 'Création...' : 'Nouveau formulaire' }}
          </button>
        </div>

        <div v-if="formsList.length" class="flex flex-wrap gap-2">
          <button
            v-for="form in formsList"
            :key="form.id"
            type="button"
            @click="selectForm(form)"
            class="px-3 py-2 rounded-lg border text-xs font-semibold transition"
            :class="currentForm?.id === form.id ? 'bg-bleu-nuit text-white border-bleu-nuit' : 'bg-white text-slate-700 border-slate-200 hover:border-bleu-nuit'"
          >
            {{ form.nom }} <span class="font-normal opacity-80">({{ form.statut === 'PUBLIE' ? 'Publié' : 'Brouillon' }})</span>
          </button>
        </div>
        <p v-else class="text-xs text-gray-500">Aucun formulaire pour cette campagne.</p>
      </div>

      <div v-if="currentForm" class="self-stretch flex flex-col lg:flex-row justify-start items-start gap-8">
        <FormBuilder
          :questions="questions"
          @ajouter-question="ouvrirModal"
          @mettre-a-jour="mettreAJourQuestion"
          @supprimer="supprimerQuestion"
          @dupliquer="dupliquerQuestion"
          @ajouter-option="ajouterOption"
          @supprimer-option="supprimerOption"
        />

        <ApercuFormulaire :questions="questions" />
      </div>
    </div>

<TypeQuestionModal
      :ouvert="modalOuvert"
      :types-questions="typesQuestions"
      @selectionner="ajouterNouvelleQuestion"
      @fermer="fermerModal"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useFormBuilder } from "@/composables/useFormBuilder.js"
import { useFormStore } from "@/stores/form.js"
import { useCampaignStore } from "@/stores/campaign.js"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import FormBuilder from "@/modules/chef-projet/components/campagnes/FormBuilder.vue"
import ApercuFormulaire from "@/modules/chef-projet/components/campagnes/ApercuFormulaire.vue"
import TypeQuestionModal from "@/modules/chef-projet/components/campagnes/TypeQuestionModal.vue"

const route = useRoute()
const router = useRouter()
const formStore = useFormStore()
const campaignStore = useCampaignStore()

const loadingInit = ref(true)
const publishing = ref(false)
const modalOuvert = ref(false)
const currentForm = ref(null)
const formsList = ref([])
const creatingForm = ref(false)
const showNewFormButton = ref(false)
const feedback = reactive({ type: "success", message: "" })

const {
  questions,
  typesQuestions,
  loadFromBackendFields,
  prepareForBackend,
  ajouterOption,
  supprimerOption,
} = useFormBuilder()

const campagneId = route.params.id

const titreFormulaire = ref("Formulaire dynamique")

const chargerFormulaire = async () => {
  loadingInit.value = true
  feedback.message = ""
  try {
    const forms = await formStore.fetchForms()
    formsList.value = forms.filter((f) => String(f.campagne?.id) === String(campagneId))

    if (formsList.value.length === 0) {
      showNewFormButton.value = true
      await createNewForm()
      return
    }

    showNewFormButton.value = true
    const found = formsList.value[0]
    currentForm.value = found
    titreFormulaire.value = found?.nom || "Formulaire dynamique"
    const fullForm = await formStore.fetchForm(found.id)
    currentForm.value = fullForm
    loadFromBackendFields(fullForm.fields || [], fullForm.id)
  } catch (err) {
    feedback.type = "error"
    feedback.message = formStore.error || "Erreur lors du chargement du formulaire."
  } finally {
    loadingInit.value = false
  }
}

const createNewForm = async () => {
  if (creatingForm.value) return
  creatingForm.value = true
  feedback.message = ""
  try {
    let campagneName = "Campagne"
    try {
      const camp = await campaignStore.fetchCampaign(campagneId)
      campagneName = camp.nom
    } catch (e) {
      const existing = campaignStore.campaigns.find((c) => String(c.id) === String(campagneId))
      campagneName = existing?.nom || campagneName
    }

    const found = await formStore.createForm({
      campagne_id: campagneId,
      nom: `Formulaire de collecte - ${campagneName}`,
      fields: [],
    })

    await formStore.fetchForms().catch(() => {})
    formsList.value = formStore.forms.filter((f) => String(f.campagne?.id) === String(campagneId))

    currentForm.value = found
    titreFormulaire.value = found?.nom || `Formulaire de collecte - ${campagneName}`
    loadFromBackendFields([], found.id)
    feedback.type = "success"
    feedback.message = "Nouveau formulaire créé."
  } catch (err) {
    feedback.type = "error"
    feedback.message = formStore.error || "Erreur lors de la création du formulaire."
  } finally {
    creatingForm.value = false
  }
}

const selectForm = async (form) => {
  if (!form) return
  feedback.message = ""
  try {
    const fullForm = await formStore.fetchForm(form.id)
    currentForm.value = fullForm
    titreFormulaire.value = fullForm?.nom || "Formulaire dynamique"
    loadFromBackendFields(fullForm.fields || [], fullForm.id)
  } catch (err) {
    feedback.type = "error"
    feedback.message = formStore.error || "Erreur lors du chargement du formulaire."
  }
}

onMounted(() => {
  chargerFormulaire()
})

const ouvrirModal = () => {
  modalOuvert.value = true
}

const fermerModal = () => {
  modalOuvert.value = false
}

const ajouterNouvelleQuestion = async (type) => {
  fermerModal()
  if (!currentForm.value) return

  feedback.message = ""
  const tempQ = {
    libelle: "Nouvelle question",
    type: type,
    obligatoire: false,
    options:
      type === "liste"
        ? ["Option 1", "Option 2"]
        : type === "selection-multiple"
          ? ["Option 1", "Option 2"]
          : [],
  }

  const payload = prepareForBackend(tempQ, questions.value.length)

  try {
    await formStore.addQuestion(currentForm.value.id, payload)
    const fullForm = await formStore.fetchForm(currentForm.value.id)
    currentForm.value = fullForm
    loadFromBackendFields(fullForm.fields || [], fullForm.id)
    feedback.type = "success"
    feedback.message = "Question ajoutée."
  } catch (err) {
    feedback.type = "error"
    feedback.message = formStore.error || "Erreur lors de l'ajout de la question."
  }
}

const mettreAJourQuestion = async (id, champ, valeur) => {
  const q = questions.value.find((item) => item.id === id)
  if (!q) return

  q[champ] = valeur
  const payload = prepareForBackend(q, q.ordre)

  try {
    await formStore.updateQuestion(id, payload)
  } catch (err) {
    console.error("Erreur mise à jour question:", err)
  }
}

const supprimerQuestion = async (id) => {
  if (!confirm("Voulez-vous supprimer cette question ?")) return
  try {
    await formStore.deleteQuestion(id)
    const fullForm = await formStore.fetchForm(currentForm.value.id)
    currentForm.value = fullForm
    loadFromBackendFields(fullForm.fields || [], fullForm.id)
    feedback.type = "success"
    feedback.message = "Question supprimée."
  } catch (err) {
    feedback.type = "error"
    feedback.message = formStore.error || "Erreur lors de la suppression."
  }
}

const dupliquerQuestion = async (id) => {
  try {
    await formStore.duplicateQuestion(id)
    const fullForm = await formStore.fetchForm(currentForm.value.id)
    currentForm.value = fullForm
    loadFromBackendFields(fullForm.fields || [], fullForm.id)
    feedback.type = "success"
    feedback.message = "Question dupliquée."
  } catch (err) {
    feedback.type = "error"
    feedback.message = formStore.error || "Erreur lors de la duplication."
  }
}

const publier = async () => {
  if (!currentForm.value) return
  publishing.value = true
  feedback.message = ""

  try {
    await formStore.publishForm(currentForm.value.id)
    currentForm.value.statut = "PUBLIE"
    feedback.type = "success"
    feedback.message = "Formulaire publié avec succès ! Il est désormais accessible sur le terrain."
    setTimeout(() => {
      router.push("/chef-projet/campagnes")
    }, 1200)
  } catch (err) {
    feedback.type = "error"
    feedback.message = formStore.error || "Erreur lors de la publication du formulaire."
  } finally {
    publishing.value = false
  }
}
</script>

