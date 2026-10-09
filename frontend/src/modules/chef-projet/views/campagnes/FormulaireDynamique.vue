<template>
  <div
    class="w-full min-w-0 max-w-[1152px] border-slate-200/60 flex flex-col justify-start items-start p-4 sm:p-8 min-h-screen"
  >
    <div class="self-stretch mb-6">
      <div
        class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
      >
        <div>
          <div class="mb-3 flex flex-wrap items-center justify-between gap-x-5 gap-y-2">
            <BreadcrumbNav :items="breadcrumbItems" class="!mb-0" />
            <router-link
              :to="campaign ? `/chef-projet/campagnes/${campagneId}` : '/chef-projet/campagnes'"
              class="shrink-0 text-sm font-semibold text-[#00313C] hover:text-[#D20C4F] hover:underline"
            >
              ← Retour à la campagne
            </router-link>
          </div>
          <div class="flex items-center gap-3">
            <h2 class="text-3xl font-bold text-bleu-nuit">
              Formulaire de collecte
            </h2>
            <span
              v-if="currentForm"
              class="px-2.5 py-1 text-xs font-semibold rounded-full"
              :class="
                currentForm.statut === 'PUBLIE'
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-amber-100 text-amber-800'
              "
            >
              {{ currentForm.statut === "PUBLIE" ? "Publié" : "Brouillon" }}
            </span>
          </div>
        </div>

        <div class="flex gap-3">
          <button
            v-if="currentForm && currentForm.statut !== 'PUBLIE'"
            @click="publier"
            :disabled="publishing || !questions.length"
            class="bg-bleu-nuit hover:bg-[#0a2540] text-white px-5 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2 transition disabled:opacity-50"
          >
            <svg
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              ></path>
            </svg>
            {{ publishing ? "Publication..." : "Publier le formulaire" }}
          </button>
        </div>
      </div>
    </div>

    <LoadingSpinner
      v-if="loadingInit"
      message="Chargement du formulaire de campagne..."
    />
    <AlertMessage
      v-if="feedback.message"
      :type="feedback.type"
      :message="feedback.message"
      class="w-full mb-6"
    />

    <section v-if="propositions.length" class="mb-6 rounded-2xl border border-rose-100 bg-rose-50/40 p-5">
      <div class="mb-4"><h3 class="font-bold text-[#00313C]">Analyse des critères et propositions IA</h3><p v-if="aiSummary" class="mt-2 rounded-xl border border-rose-100 bg-white p-3 text-sm leading-6 text-slate-700">{{ aiSummary }}</p><p class="mt-2 text-sm text-slate-600">Examinez chaque suggestion avant de l’ajouter au formulaire.</p></div>
      <div class="grid gap-3 xl:grid-cols-2">
        <article v-for="(proposal, index) in propositions" :key="index" class="rounded-xl border border-slate-200 bg-white p-4">
          <div class="mb-2 flex items-center justify-between gap-2"><span class="rounded-full bg-rose-50 px-2.5 py-1 text-xs font-semibold text-[#D20C4F]">{{ critereNom(proposal.critere_id) }} · {{ criterePoids(proposal.critere_id) }} pts</span><button @click="propositions.splice(index, 1)" class="text-xs font-medium text-slate-500 hover:text-red-600">Supprimer</button></div>
          <input v-model="proposal.question" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-800 focus:border-[#D20C4F] focus:outline-none" aria-label="Question proposée">
          <p class="mt-2 text-xs text-slate-500">Type : {{ typeLabel(proposal.type) }}</p>
          <div v-if="proposal.options?.length" class="mt-2 flex flex-wrap gap-1.5"><span v-for="option in proposal.options" :key="option" class="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">{{ option }}</span></div>
          <button @click="accepterProposition(proposal, index)" class="mt-3 rounded-lg bg-[#00313C] px-3 py-2 text-xs font-semibold text-white hover:bg-[#064652]">✓ Accepter et ajouter</button>
        </article>
      </div>
    </section>

    <div v-if="!loadingInit" class="self-stretch flex flex-col gap-6">
      <div
        v-if="formsList.length > 1 || showNewFormButton"
        class="bg-white border border-slate-200/60 rounded-xl p-4 shadow-xs-sm"
      >
        <div class="flex items-center justify-between mb-3">
          <div>
            <h3 class="text-sm font-bold uppercase text-slate-900">
              Formulaires de cette campagne
            </h3>
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
            {{ creatingForm ? "Création..." : "Nouveau formulaire" }}
          </button>
        </div>

        <div v-if="formsList.length" class="flex flex-wrap gap-2">
          <button
            v-for="form in formsList"
            :key="form.id"
            type="button"
            @click="selectForm(form)"
            class="px-3 py-2 rounded-lg border text-xs font-semibold transition"
            :class="
              currentForm?.id === form.id
                ? 'bg-bleu-nuit text-white border-bleu-nuit'
                : 'bg-white text-slate-700 border-slate-200 hover:border-bleu-nuit'
            "
          >
            {{ form.nom }}
            <span class="font-normal opacity-80"
              >({{ form.statut === "PUBLIE" ? "Publié" : "Brouillon" }})</span
            >
          </button>
        </div>
        <p v-else class="text-xs text-gray-500">
          Aucun formulaire pour cette campagne.
        </p>
      </div>

      <div
        v-if="currentForm"
        class="self-stretch flex flex-col xl:flex-row justify-start items-start gap-6"
      >
        <FormBuilder
          :questions="questions"
          :criteres="criteres"
          @ajouter-question="ouvrirModal"
          @mettre-a-jour="mettreAJourQuestion"
          @supprimer="supprimerQuestion"
          @dupliquer="dupliquerQuestion"
          @ajouter-option="ajouterOptionEtSauver"
          @supprimer-option="supprimerOptionEtSauver"
          @reorder="reordonnerQuestion"
        />

        <ApercuFormulaire :questions="questions" :title="titreFormulaire" />
      </div>
      <div v-if="currentForm" class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-5">
        <button @click="genererQuestions" :disabled="generating || !criteres.length" class="rounded-xl bg-bleu-nuit px-5 py-2.5 text-sm font-semibold text-white hover:bg-[#0a2540] disabled:opacity-50">{{ generating ? 'Analyse des critères…' : '✦ Générer avec l’IA' }}</button>
        <div class="flex flex-wrap justify-end gap-3">
        <button @click="enregistrerBrouillon" :disabled="saving" class="rounded-xl border border-[#00313C] px-5 py-2.5 text-sm font-semibold text-[#00313C] hover:bg-slate-50 disabled:opacity-50">{{ saving ? 'Enregistrement…' : 'Enregistrer comme brouillon' }}</button>
        <button v-if="currentForm.statut !== 'PUBLIE'" @click="publier" :disabled="publishing || !questions.length" class="rounded-xl bg-bleu-nuit px-5 py-2.5 text-sm font-semibold text-white hover:bg-[#0a2540] disabled:opacity-50">{{ publishing ? 'Publication…' : 'Enregistrer et publier' }}</button>
        </div>
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
import { ref, reactive, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useFormBuilder } from "@/composables/useFormBuilder.js";
import { useFormStore } from "@/stores/form.js";
import { useCampaignStore } from "@/stores/campaign.js";
import { useProjectStore } from "@/stores/project.js";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import AlertMessage from "@/components/ui/AlertMessage.vue";
import BreadcrumbNav from "@/components/ui/BreadcrumbNav.vue";
import FormBuilder from "@/modules/chef-projet/components/campagnes/FormBuilder.vue";
import ApercuFormulaire from "@/modules/chef-projet/components/campagnes/ApercuFormulaire.vue";
import TypeQuestionModal from "@/modules/chef-projet/components/campagnes/TypeQuestionModal.vue";

const route = useRoute();
const router = useRouter();
const formStore = useFormStore();
const campaignStore = useCampaignStore();
const projectStore = useProjectStore();

const loadingInit = ref(true);
const publishing = ref(false);
const modalOuvert = ref(false);
const currentForm = ref(null);
const formsList = ref([]);
const creatingForm = ref(false);
const showNewFormButton = ref(false);
const feedback = reactive({ type: "success", message: "" });
const campaign = ref(null);
const propositions = ref([]);
const aiSummary = ref("");
const generating = ref(false);
const saving = ref(false);
const criteres = computed(() => projectStore.criteria || []);
const campaignName = computed(() => campaign.value?.nom || "");
const projectName = computed(() => campaign.value?.projet?.name || campaign.value?.projet?.nom || "");
const breadcrumbItems = computed(() => [
  ...(campaign.value?.projet?.id || campaign.value?.projet_id
    ? [{ label: projectName.value || "Projet", to: `/chef-projet/projets/${campaign.value.projet?.id || campaign.value.projet_id}` }]
    : []),
  ...(campaign.value ? [{ label: campaignName.value || "Campagne", to: `/chef-projet/campagnes/${campagneId}` }] : []),
  { label: "Formulaire" },
]);

const {
  questions,
  typesQuestions,
  loadFromBackendFields,
  prepareForBackend,
  ajouterOption,
  supprimerOption,
} = useFormBuilder();

const campagneId = route.params.id;

const titreFormulaire = ref("Formulaire dynamique");

const chargerFormulaire = async () => {
  loadingInit.value = true;
  feedback.message = "";
  try {
    try {
      campaign.value = await campaignStore.fetchCampaign(campagneId);
      const projectId = campaign.value?.projet?.id || campaign.value?.projet_id;
      if (projectId) await projectStore.fetchCriteria(projectId);
    } catch (_) { /* le formulaire reste accessible si les critères ne chargent pas */ }
    const forms = await formStore.fetchForms();
    formsList.value = forms.filter(
      (f) => String(f.campagne?.id) === String(campagneId)
    );

    if (formsList.value.length === 0) {
      showNewFormButton.value = true;
      await createNewForm();
      return;
    }

    showNewFormButton.value = true;
    const found = formsList.value[0];
    currentForm.value = found;
    titreFormulaire.value = found?.nom || "Formulaire dynamique";
    const fullForm = await formStore.fetchForm(found.id);
    currentForm.value = fullForm;
    loadFromBackendFields(fullForm.fields || [], fullForm.id);
  } catch (err) {
    feedback.type = "error";
    feedback.message =
      formStore.error || "Erreur lors du chargement du formulaire.";
  } finally {
    loadingInit.value = false;
  }
};

const critereNom = id => criteres.value.find(c => String(c.id) === String(id))?.nom || "Critère du projet";
const criterePoids = id => criteres.value.find(c => String(c.id) === String(id))?.poids ?? 0;
const typeLabel = type => ({ TEXT: "Texte court", TEXTAREA: "Texte long", NUMBER: "Nombre", DATE: "Date", YES_NO: "Oui / Non", RADIO: "Choix unique", CHECKBOX: "Choix multiple", SELECT: "Liste déroulante", PHONE: "Téléphone", EMAIL: "Email", PHOTO: "Photo", FILE: "Fichier", GPS: "Localisation GPS", SCALE: "Échelle de 1 à 5" })[type] || typesQuestions.find(t => t.id === type)?.label || type;

const genererQuestions = async () => {
  generating.value = true;
  feedback.message = "";
  try {
    const generated = await formStore.generateQuestions(campagneId);
    aiSummary.value = generated.resume || "";
    propositions.value = (generated.questions || []).map(q => ({ ...q, options: Array.isArray(q.options) ? q.options : [] }));
    feedback.type = "success";
    feedback.message = `${propositions.value.length} proposition(s) à valider.`;
  } catch (err) {
    feedback.type = "error";
    feedback.message = formStore.error || "Impossible de générer les questions.";
  } finally { generating.value = false; }
};

const accepterProposition = async (proposal, index) => {
  const q = {
    libelle: proposal.question, type: proposal.type, backendType: proposal.type,
    obligatoire: false, options: proposal.options, aide: proposal.aide || "",
    critere: proposal.critere_id, source: "IA",
  };
  try {
    await enregistrerQuestion(q);
    propositions.value.splice(index, 1);
    feedback.type = "success";
    feedback.message = "Question ajoutée au formulaire.";
  } catch (err) {
    feedback.type = "error";
    feedback.message = formStore.error || "Impossible d’ajouter cette proposition.";
  }
};

const enregistrerQuestion = async (question) => {
  const payload = prepareForBackend(question, questions.value.length);
  payload.critere = question.critere || null;
  payload.source = question.source || "MANUEL";
  payload.aide = question.aide || "";
  await formStore.addQuestion(currentForm.value.id, payload);
  const full = await formStore.fetchForm(currentForm.value.id);
  currentForm.value = full;
  loadFromBackendFields(full.fields || [], full.id);
};

const enregistrerBrouillon = async () => {
  if (!currentForm.value) return;
  saving.value = true;
  try {
    await formStore.updateForm(currentForm.value.id, { statut: "BROUILLON" });
    feedback.type = "success";
    feedback.message = "Brouillon enregistré.";
  } catch (err) {
    feedback.type = "error";
    feedback.message = formStore.error || "Erreur lors de l’enregistrement.";
  } finally { saving.value = false; }
};

const reordonnerQuestion = async ({ id, direction }) => {
  const index = questions.value.findIndex(q => String(q.id) === String(id));
  const target = index + direction;
  if (index < 0 || target < 0 || target >= questions.value.length) return;
  const [item] = questions.value.splice(index, 1);
  questions.value.splice(target, 0, item);
  try {
    await formStore.reorderQuestions(currentForm.value.id, questions.value.map((q, ordre) => ({ id: q.id, ordre })));
    const full = await formStore.fetchForm(currentForm.value.id);
    loadFromBackendFields(full.fields || [], full.id);
  } catch (err) {
    feedback.type = "error";
    feedback.message = formStore.error || "Impossible de réorganiser les questions.";
  }
};

const createNewForm = async () => {
  if (creatingForm.value) return;
  creatingForm.value = true;
  feedback.message = "";
  try {
    let campagneName = "Campagne";
    try {
      const camp = await campaignStore.fetchCampaign(campagneId);
      campagneName = camp.nom;
    } catch (e) {
      const existing = campaignStore.campaigns.find(
        (c) => String(c.id) === String(campagneId)
      );
      campagneName = existing?.nom || campagneName;
    }

    const found = await formStore.createForm({
      campagne_id: campagneId,
      nom: `Formulaire de collecte - ${campagneName}`,
      fields: [],
    });

    await formStore.fetchForms().catch(() => {});
    formsList.value = formStore.forms.filter(
      (f) => String(f.campagne?.id) === String(campagneId)
    );

    currentForm.value = found;
    titreFormulaire.value =
      found?.nom || `Formulaire de collecte - ${campagneName}`;
    loadFromBackendFields([], found.id);
    feedback.type = "success";
    feedback.message = "Nouveau formulaire créé.";
  } catch (err) {
    feedback.type = "error";
    feedback.message =
      formStore.error || "Erreur lors de la création du formulaire.";
  } finally {
    creatingForm.value = false;
  }
};

const selectForm = async (form) => {
  if (!form) return;
  feedback.message = "";
  try {
    const fullForm = await formStore.fetchForm(form.id);
    currentForm.value = fullForm;
    titreFormulaire.value = fullForm?.nom || "Formulaire dynamique";
    loadFromBackendFields(fullForm.fields || [], fullForm.id);
  } catch (err) {
    feedback.type = "error";
    feedback.message =
      formStore.error || "Erreur lors du chargement du formulaire.";
  }
};

onMounted(() => {
  chargerFormulaire();
});

const ouvrirModal = () => {
  modalOuvert.value = true;
};

const fermerModal = () => {
  modalOuvert.value = false;
};

const ajouterNouvelleQuestion = async (type) => {
  fermerModal();
  if (!currentForm.value) return;

  feedback.message = "";
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
    source: "MANUEL",
  };

  const payload = prepareForBackend(tempQ, questions.value.length);

  try {
    payload.source = "MANUEL";
    await formStore.addQuestion(currentForm.value.id, payload);
    const fullForm = await formStore.fetchForm(currentForm.value.id);
    currentForm.value = fullForm;
    loadFromBackendFields(fullForm.fields || [], fullForm.id);
    feedback.type = "success";
    feedback.message = "Question ajoutée.";
  } catch (err) {
    feedback.type = "error";
    feedback.message =
      formStore.error || "Erreur lors de l'ajout de la question.";
  }
};

const mettreAJourQuestion = async (id, champ, valeur) => {
  const q = questions.value.find((item) => item.id === id);
  if (!q) return;

  q[champ] = valeur;
  const payload = prepareForBackend(q, q.ordre);

  try {
    await formStore.updateQuestion(id, payload);
  } catch (err) {
    console.error("Erreur mise à jour question:", err);
  }
};

const ajouterOptionEtSauver = async (id, option) => {
  ajouterOption(id, option);
  const q = questions.value.find(item => item.id === id);
  if (q) await mettreAJourQuestion(id, "options", [...q.options]);
};

const supprimerOptionEtSauver = async (id, index) => {
  supprimerOption(id, index);
  const q = questions.value.find(item => item.id === id);
  if (q) await mettreAJourQuestion(id, "options", [...q.options]);
};

const supprimerQuestion = async (id) => {
  if (!confirm("Voulez-vous supprimer cette question ?")) return;
  try {
    await formStore.deleteQuestion(id);
    const fullForm = await formStore.fetchForm(currentForm.value.id);
    currentForm.value = fullForm;
    loadFromBackendFields(fullForm.fields || [], fullForm.id);
    feedback.type = "success";
    feedback.message = "Question supprimée.";
  } catch (err) {
    feedback.type = "error";
    feedback.message = formStore.error || "Erreur lors de la suppression.";
  }
};

const dupliquerQuestion = async (id) => {
  try {
    await formStore.duplicateQuestion(id);
    const fullForm = await formStore.fetchForm(currentForm.value.id);
    currentForm.value = fullForm;
    loadFromBackendFields(fullForm.fields || [], fullForm.id);
    feedback.type = "success";
    feedback.message = "Question dupliquée.";
  } catch (err) {
    feedback.type = "error";
    feedback.message = formStore.error || "Erreur lors de la duplication.";
  }
};

const publier = async () => {
  if (!currentForm.value) return;
  publishing.value = true;
  feedback.message = "";

  try {
    await formStore.publishForm(currentForm.value.id);
    currentForm.value.statut = "PUBLIE";
    feedback.type = "success";
    feedback.message =
      "Formulaire publié avec succès ! Il est désormais accessible sur le terrain.";
    setTimeout(() => {
      router.push("/chef-projet/campagnes");
    }, 1200);
  } catch (err) {
    feedback.type = "error";
    feedback.message =
      formStore.error || "Erreur lors de la publication du formulaire.";
  } finally {
    publishing.value = false;
  }
};
</script>

