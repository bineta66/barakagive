<template>
  <div class="self-stretch border-b last:border-b-0" style="border-color: #744D03">
    <div class="self-stretch p-6 flex justify-between items-start gap-4">
      <div class="flex-1 inline-flex flex-col justify-start items-start gap-3">
        <div class="self-stretch inline-flex justify-start items-center gap-3">
          <span class="text-sm font-bold" style="color: #744D03">{{ index + 1 }}.</span>
          <input
            v-model="question.libelle"
            @input="mettreAJour"
            type="text"
            placeholder="Question sans titre"
            class="flex-1 text-base font-medium text-gray-900 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-gray-400"
          />
        </div>

        <div class="self-stretch flex items-center gap-2">
          <span class="text-xs font-medium px-2 py-1 rounded text-white" style="background-color: #744D03">{{ typeLabel }}</span>
        </div>

        <div class="self-stretch mt-2">
          <div v-if="question.type === 'texte'" class="self-stretch p-3 border border-gray-300 rounded bg-white hover:border-gray-400 transition">
            <span class="text-sm text-gray-400">Réponse texte</span>
          </div>

          <div v-else-if="question.type === 'nombre'" class="self-stretch p-3 border border-gray-300 rounded bg-white hover:border-gray-400 transition">
            <span class="text-sm text-gray-400">0</span>
          </div>

          <div v-else-if="question.type === 'liste'" class="self-stretch flex flex-col gap-2">
            <div v-for="(option, idx) in question.options" :key="idx" class="flex items-center gap-2">
              <input
                v-model="question.options[idx]"
                @input="mettreAJourOption(question, idx)"
                type="text"
                class="flex-1 rounded-lg border px-3 py-2 text-sm"
                style="border-color: #744D03; background-color: #fff"
              />
            </div>
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 border border-gray-300 rounded-sm"></div>
              <input
                v-model="optionTemp"
                @keyup.enter="ajouterOptionLocale"
                type="text"
                placeholder="Ajouter une option..."
                class="flex-1 text-sm text-gray-700 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-gray-400"
                autocomplete="off"
              />
              <button
                @click="ajouterOptionLocale"
                class="text-xs font-semibold px-2 py-1 rounded border"
                style="border-color: #744D03; color: #744D03"
                type="button"
              >
                Ajouter
              </button>
            </div>
          </div>

          <div v-else-if="question.type === 'selection-multiple'" class="self-stretch flex flex-col gap-2">
            <div v-for="(option, idx) in question.options" :key="idx" class="flex items-center gap-2">
              <input type="checkbox" disabled />
              <input
                v-model="question.options[idx]"
                @input="mettreAJourOption(question, idx)"
                type="text"
                class="flex-1 rounded-lg border px-3 py-2 text-sm"
                style="border-color: #744D03; background-color: #fff"
              />
            </div>
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 border border-gray-300 rounded-sm"></div>
              <input
                v-model="optionTemp"
                @keyup.enter="ajouterOptionLocale"
                type="text"
                placeholder="Ajouter une option..."
                class="flex-1 text-sm text-gray-700 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-gray-400"
                autocomplete="off"
              />
              <button
                @click="ajouterOptionLocale"
                class="text-xs font-semibold px-2 py-1 rounded border"
                style="border-color: #744D03; color: #744D03"
                type="button"
              >
                Ajouter
              </button>
            </div>
          </div>

          <div v-else-if="question.type === 'oui-non'" class="self-stretch flex gap-3">
            <div class="flex-1 p-3 border border-gray-300 rounded bg-white hover:border-gray-400 transition text-center">
              <span class="text-sm text-gray-700">Oui</span>
            </div>
            <div class="flex-1 p-3 border border-gray-300 rounded bg-white hover:border-gray-400 transition text-center">
              <span class="text-sm text-gray-700">Non</span>
            </div>
          </div>

          <div v-else-if="question.type === 'date'" class="self-stretch p-3 border border-gray-300 rounded bg-white hover:border-gray-400 transition">
            <span class="text-sm text-gray-400">JJ/MM/AAAA</span>
          </div>

          <div v-else-if="question.type === 'telephone'" class="self-stretch p-3 border border-gray-300 rounded bg-white hover:border-gray-400 transition">
            <span class="text-sm text-gray-400">+221 77 000 00 00</span>
          </div>

          <div v-else-if="question.type === 'photo'" class="self-stretch p-6 border-2 border-dashed border-gray-300 rounded bg-white hover:border-gray-400 transition flex flex-col items-center justify-center gap-2 cursor-pointer">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            <span class="text-sm text-gray-500">Ajouter une photo</span>
          </div>

          <div v-else-if="question.type === 'gps'" class="self-stretch p-3 bg-or/10 border border-or/30 rounded">
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 text-bleu-nuit" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
              </svg>
              <span class="text-sm font-medium text-bleu-nuit">14.1386° N, 16.0743° W</span>
            </div>
            <p class="text-xs text-gray-500 mt-1">Coordonnées GPS générées automatiquement</p>
          </div>
        </div>

        <div v-if="question.type === 'liste' || question.type === 'selection-multiple'" class="flex items-center gap-2 mt-2">
          <input
            v-model="optionTemp"
            @keyup.enter="ajouterOptionLocale"
            type="text"
            placeholder="Ajouter une option..."
            class="flex-1 rounded-lg border px-3 py-2 text-sm focus:ring-2 focus:ring-or/30 outline-none"
            style="border-color: #744D03; background-color: #fff"
            autocomplete="off"
          />
          <button
            @click="ajouterOptionLocale"
            class="text-sm font-semibold hover:underline"
            style="color: #021427"
          >
            + Ajouter
          </button>
        </div>
      </div>

      <div class="flex items-center gap-1">
        <button
          @click="dupliquer"
          class="p-2 text-gray-400 hover:text-[#021427] transition"
          title="Dupliquer"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
          </svg>
        </button>
        <button
          @click="supprimer"
          class="p-2 text-gray-400 hover:text-red-600 transition"
          title="Supprimer"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
        </button>
      </div>

      <div class="flex justify-end items-center">
        <button
          @click="toggleObligatoire"
          class="relative inline-flex items-center focus:outline-none"
        >
          <span class="mr-2 text-xs font-medium text-gray-500">{{ question.obligatoire ? 'Obligatoire' : 'Facultatif' }}</span>
          <span
            class="relative inline-block w-10 h-5 rounded-full transition-colors duration-200 ease-in-out"
            :class="question.obligatoire ? '' : 'bg-gray-300'"
            :style="question.obligatoire ? 'background-color: #021427' : ''"
          >
            <span
              class="absolute left-0.5 top-0.5 bg-white w-4 h-4 rounded-full transition-transform duration-200 ease-in-out"
              :class="question.obligatoire ? 'translate-x-5' : 'translate-x-0'"
            ></span>
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"

const props = defineProps({
  question: {
    type: Object,
    required: true,
  },
  index: {
    type: Number,
    required: true,
  },
})

const emit = defineEmits(["supprimer", "dupliquer", "mettre-a-jour", "ajouter-option", "supprimer-option"])

const optionTemp = ref("")

const mettreAJourOption = (question, index) => {
  emit("mettre-a-jour", question.id, "options", [...question.options])
}

const typeLabels = {
  texte: "Texte",
  nombre: "Nombre",
  liste: "Liste déroulante",
  "selection-multiple": "Sélection multiple",
  "oui-non": "Oui/Non",
  date: "Date",
  telephone: "Téléphone",
  photo: "Texte long / Photo",
  gps: "GPS",
}

const typeLabel = computed(() => typeLabels[props.question.type] || props.question.type)

const toggleObligatoire = () => {
  props.question.obligatoire = !props.question.obligatoire
  emit("mettre-a-jour", props.question.id, "obligatoire", props.question.obligatoire)
}

const mettreAJour = () => {
  emit("mettre-a-jour", props.question.id, "libelle", props.question.libelle)
}

const ajouterOptionLocale = () => {
  if (optionTemp.value.trim()) {
    emit("ajouter-option", props.question.id, optionTemp.value.trim())
    optionTemp.value = ""
  }
}

const supprimerOptionLocale = (index) => {
  emit("supprimer-option", props.question.id, index)
}

const dupliquer = () => {
  emit("dupliquer", props.question.id)
}

const supprimer = () => {
  emit("supprimer", props.question.id)
}
</script>


