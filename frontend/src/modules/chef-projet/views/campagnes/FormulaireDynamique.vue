<template>
  <div class="w-full max-w-[1152px] border-slate-200/60 inline-flex flex-col justify-start items-start p-8 min-h-screen">
    <div class="self-stretch mb-6">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h2 class="text-3xl font-bold" style="color: #744D03">Formulaire dynamique</h2>
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

    <div v-if="!loadingInit" class="self-stretch flex flex-col lg:flex-row justify-start items-start gap-8">
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

const chargerFormulaire = async () => {
  loadingInit.value = true
  feedback.message = ""
  try {
    const forms = await formStore.fetchForms()
    let found = forms.find((f) => f.campagne?.id === campagneId)

    if (!found) {
      // Auto-create a draft form for this campaign
      let campagneName = "Campagne"
      try {
        const camp = await campaignStore.fetchCampaign(campagneId)
        campagneName = camp.nom
      } catch (e) {}

      found = await formStore.createForm({
        campagne_id: campagneId,
        nom: `Formulaire de collecte - ${campagneName}`,
        fields: [],
      })
    }

    // Load full details with fields
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
    options: type === "liste" ? ["Option 1", "Option 2"] : [],
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

