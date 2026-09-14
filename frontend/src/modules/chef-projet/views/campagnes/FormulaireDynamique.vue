<template>
  <div class="w-full max-w-[1152px] border-slate-200/60 inline-flex flex-col justify-start items-start p-8">
    <div class="self-stretch mb-8">
      <div class="flex justify-between items-center">
          <div>
            <h2 class="text-3xl font-bold" style="color: #744D03">Formulaire dynamique</h2>
            <p class="text-gray-600 text-sm mt-1">Configurez les questions de collecte qui seront remplies par les agents de terrain.</p>
          </div>
        <div class="flex gap-3">
          <router-link
            to="/chef-projet/campagnes"
            class="border font-semibold px-5 py-2.5 rounded-lg text-sm flex items-center gap-2"
            style="border-color: #744D03; color: #744D03"
          >
            Retour aux campagnes
          </router-link>
          <button
            @click="publier"
            class="text-white px-5 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2"
            style="background-color: #021427"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            Publier le formulaire
          </button>
        </div>
      </div>
    </div>

      <div class="self-stretch flex justify-start items-start gap-8">
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
      @selectionner="ajouterQuestion"
      @fermer="fermerModal"
    />
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useFormBuilder } from "@/composables/useFormBuilder.js"
import FormBuilder from "@/modules/chef-projet/components/campagnes/FormBuilder.vue"
import ApercuFormulaire from "@/modules/chef-projet/components/campagnes/ApercuFormulaire.vue"
import TypeQuestionModal from "@/modules/chef-projet/components/campagnes/TypeQuestionModal.vue"

const router = useRouter()
const {
  questions,
  typesQuestions,
  statistiques,
  ajouterQuestion,
  supprimerQuestion,
  dupliquerQuestion,
  mettreAJourQuestion,
  ajouterOption,
  supprimerOption,
} = useFormBuilder()

const modalOuvert = ref(false)

const ouvrirModal = () => {
  modalOuvert.value = true
}

const fermerModal = () => {
  modalOuvert.value = false
}

const publier = () => {
  alert("Formulaire publiÃ© avec succÃ¨s !")
  router.push("/chef-projet/campagnes")
}
</script>

