<template>
  <div class="self-stretch border-b border-slate-100 last:border-b-0">
    <div class="self-stretch min-w-0 p-3 flex flex-col-reverse items-stretch gap-3 sm:flex-row sm:items-start sm:gap-4 sm:p-6">
      <!-- Corps de la question -->
      <div class="min-w-0 w-full flex-1 inline-flex flex-col justify-start items-start gap-3 sm:w-auto">
        <!-- Numéro + libellé -->
        <div class="self-stretch min-w-0 inline-flex justify-start items-center gap-2 sm:gap-3">
          <span class="text-sm font-bold text-bleu-nuit">{{ index + 1 }}.</span>
          <input
            v-model="question.libelle"
            @input="mettreAJour"
            type="text"
            placeholder="Question sans titre"
            class="min-w-0 w-full flex-1 text-sm font-medium text-slate-900 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-slate-400 sm:text-base"
          />
        </div>

        <!-- Badge type -->
        <div class="self-stretch flex flex-wrap items-center gap-2">
          <span
            class="text-xs font-semibold px-2.5 py-1 rounded-full bg-bleu-nuit/10 text-bleu-nuit"
          >
            {{ typeLabel }}
          </span>
          <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">{{ question.source === 'IA' ? 'Suggestion IA validée' : 'Ajout manuel' }}</span>
        </div>
        <select :value="question.critere || ''" @change="emit('mettre-a-jour', question.id, 'critere', $event.target.value || null)" class="w-full max-w-sm rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-600">
          <option value="">Aucun critère associé</option><option v-for="critere in criteres" :key="critere.id" :value="critere.id">{{ critere.nom }} · {{ critere.poids }} pts</option>
        </select>
        <input :value="question.aide" @input="emit('mettre-a-jour', question.id, 'aide', $event.target.value)" placeholder="Description ou aide (facultatif)" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-xs text-slate-600">

        <!-- Aperçu du champ selon le type -->
        <div class="self-stretch mt-1 w-full">
          <div
            v-if="question.type === 'texte'"
            class="p-3 border border-slate-200 rounded-lg bg-slate-50"
          >
            <span class="text-sm text-slate-400">Réponse texte libre…</span>
          </div>

          <div
            v-else-if="question.type === 'nombre'"
            class="p-3 border border-slate-200 rounded-lg bg-slate-50"
          >
            <span class="text-sm text-slate-400">0</span>
          </div>

          <div
            v-else-if="
              question.type === 'liste' ||
              question.type === 'selection-multiple' || question.type === 'choix-unique'
            "
            class="self-stretch flex flex-col gap-2"
          >
            <div
              v-for="(option, idx) in question.options"
              :key="idx"
              class="flex min-w-0 items-center gap-2"
            >
              <component
                :is="question.type === 'liste' ? 'div' : 'input'"
                v-if="question.type !== 'liste'"
                :type="question.type === 'choix-unique' ? 'radio' : 'checkbox'"
                disabled
                class="w-4 h-4 rounded border-slate-300 text-bleu-nuit"
              />
              <div
                v-if="question.type === 'liste'"
                class="w-4 h-4 rounded-full border border-slate-300 flex-shrink-0"
              ></div>
              <input
                v-model="question.options[idx]"
                @input="mettreAJourOption(question, idx)"
                type="text"
                class="min-w-0 flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
              />
            </div>
            <!-- Ajouter option -->
            <div class="mt-1 flex flex-wrap items-center gap-2">
              <div
                class="w-4 h-4 rounded border border-slate-300 flex-shrink-0"
              ></div>
              <input
                v-model="optionTemp"
                @keyup.enter="ajouterOptionLocale"
                type="text"
                placeholder="Ajouter une option..."
                class="min-w-0 flex-1 text-sm text-slate-700 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-slate-400"
                autocomplete="off"
              />
              <button
                @click="ajouterOptionLocale"
                type="button"
                class="text-xs font-semibold px-2.5 py-1 rounded-lg border border-bleu-nuit text-bleu-nuit hover:bg-bleu-nuit hover:text-white transition"
              >
                + Ajouter
              </button>
            </div>
          </div>

          <div
            v-else-if="question.type === 'oui-non'"
            class="self-stretch flex gap-3"
          >
            <div
              class="flex-1 p-3 border border-slate-200 rounded-lg bg-slate-50 text-center"
            >
              <span class="text-sm text-slate-600">Oui</span>
            </div>
            <div
              class="flex-1 p-3 border border-slate-200 rounded-lg bg-slate-50 text-center"
            >
              <span class="text-sm text-slate-600">Non</span>
            </div>
          </div>

          <div
            v-else-if="question.type === 'date'"
            class="p-3 border border-slate-200 rounded-lg bg-slate-50"
          >
            <span class="text-sm text-slate-400">JJ/MM/AAAA</span>
          </div>

          <div
            v-else-if="question.type === 'telephone'"
            class="p-3 border border-slate-200 rounded-lg bg-slate-50"
          >
            <span class="text-sm text-slate-400">+221 77 000 00 00</span>
          </div>

          <div
            v-else-if="question.type === 'photo'"
            class="p-6 border-2 border-dashed border-slate-200 rounded-lg bg-slate-50 flex flex-col items-center justify-center gap-2 cursor-pointer hover:border-bleu-nuit/40 transition"
          >
            <svg
              class="w-8 h-8 text-slate-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
            <span class="text-sm text-slate-500">Ajouter une photo</span>
          </div>

          <div
            v-else-if="question.type === 'gps'"
            class="p-3 bg-bleu-nuit/5 border border-bleu-nuit/20 rounded-lg"
          >
            <div class="flex items-center gap-2">
              <svg
                class="w-4 h-4 text-bleu-nuit"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
              </svg>
              <span class="text-sm font-medium text-bleu-nuit"
                >14.1386° N, 16.0743° W</span
              >
            </div>
            <p class="text-xs text-slate-500 mt-1">
              Coordonnées GPS générées automatiquement
            </p>
          </div>
        </div>
      </div>

      <!-- Actions droite -->
      <div class="flex w-full flex-row flex-wrap items-center justify-between gap-2 sm:w-auto sm:flex-shrink-0 sm:flex-col sm:items-center sm:gap-3">
        <!-- Toggle obligatoire -->
        <button
          @click="toggleObligatoire"
          class="flex items-center gap-2 focus:outline-none"
        >
          <span class="text-xs font-medium text-slate-500 whitespace-nowrap">
            {{ question.obligatoire ? "Obligatoire" : "Facultatif" }}
          </span>
          <span
            class="relative inline-block w-10 h-5 rounded-full transition-colors duration-200"
            :class="question.obligatoire ? 'bg-bleu-nuit' : 'bg-slate-300'"
          >
            <span
              class="absolute left-0.5 top-0.5 bg-white w-4 h-4 rounded-full shadow transition-transform duration-200"
              :class="question.obligatoire ? 'translate-x-5' : 'translate-x-0'"
            ></span>
          </span>
        </button>

        <!-- Dupliquer / Supprimer -->
        <div class="flex gap-1">
          <button @click="emit('reorder', { id: question.id, direction: -1 })" :disabled="index === 0" title="Monter" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 disabled:opacity-30">↑</button>
          <button @click="emit('reorder', { id: question.id, direction: 1 })" :disabled="index === questionsCount - 1" title="Descendre" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 disabled:opacity-30">↓</button>
          <button
            @click="dupliquer"
            title="Dupliquer"
            class="p-2 text-slate-400 hover:text-bleu-nuit hover:bg-bleu-nuit/8 rounded-lg transition"
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
                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
          </button>
          <button
            @click="supprimer"
            title="Supprimer"
            class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
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
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  question: { type: Object, required: true },
  index: { type: Number, required: true },
  criteres: { type: Array, default: () => [] },
  questionsCount: { type: Number, default: 0 },
});

const emit = defineEmits([
  "supprimer",
  "dupliquer",
  "mettre-a-jour",
  "ajouter-option",
  "supprimer-option",
  "reorder",
]);

const optionTemp = ref("");

const typeLabels = {
  texte: "Texte libre",
  "texte-long": "Texte long",
  email: "Email",
  nombre: "Nombre",
  liste: "Liste déroulante",
  "choix-unique": "Choix unique",
  "selection-multiple": "Sélection multiple",
  "oui-non": "Oui / Non",
  date: "Date",
  telephone: "Téléphone",
  photo: "Photo / Texte long",
  gps: "GPS",
  fichier: "Fichier",
  echelle: "Échelle de 1 à 5",
};

const typeLabel = computed(
  () => typeLabels[props.question.type] || props.question.type
);

const toggleObligatoire = () => {
  props.question.obligatoire = !props.question.obligatoire;
  emit(
    "mettre-a-jour",
    props.question.id,
    "obligatoire",
    props.question.obligatoire
  );
};

const mettreAJour = () => {
  emit("mettre-a-jour", props.question.id, "libelle", props.question.libelle);
};

const mettreAJourOption = (question, index) => {
  emit("mettre-a-jour", question.id, "options", [...question.options]);
};

const ajouterOptionLocale = () => {
  if (optionTemp.value.trim()) {
    emit("ajouter-option", props.question.id, optionTemp.value.trim());
    optionTemp.value = "";
  }
};

const dupliquer = () => emit("dupliquer", props.question.id);
const supprimer = () => emit("supprimer", props.question.id);
</script>
