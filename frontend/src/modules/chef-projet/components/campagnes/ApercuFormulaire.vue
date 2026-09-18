<template>
  <div class="w-80 flex flex-col justify-start items-start gap-4">
    <div class="self-stretch bg-white rounded-xl border p-6" style="border-color: #744D03">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background-color: #021427">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-bold" style="color: #744D03">Aperçu</h3>
      </div>

      <div class="self-stretch flex flex-col justify-start items-start gap-1 mb-4">
        <div class="self-stretch justify-center text-gray-900 text-sm font-bold">Enrôlement et dotation</div>
        <div class="self-stretch justify-center text-gray-500 text-xs">Aperçu du formulaire terrain</div>
      </div>

      <div class="self-stretch flex flex-col justify-start items-start gap-3">
        <div
          v-for="question in questions"
          :key="question.id"
          class="self-stretch p-4 bg-gray-50 rounded-lg border"
          style="border-color: #744D03"
        >
          <div class="flex items-center gap-2 mb-2">
            <span class="text-sm font-medium text-gray-700">{{ question.libelle }}</span>
            <span v-if="question.obligatoire" class="text-red-500 text-xs">*</span>
          </div>

          <div v-if="question.type === 'texte'" class="self-stretch p-2 bg-white border border-gray-300 rounded">
            <div class="text-xs text-gray-400">Texte de réponse...</div>
          </div>

          <div v-else-if="question.type === 'nombre'" class="self-stretch p-2 bg-white border border-gray-300 rounded">
            <div class="text-xs text-gray-400">0</div>
          </div>

          <div v-else-if="question.type === 'liste'" class="self-stretch flex flex-col gap-1">
            <div v-for="(option, idx) in question.options" :key="idx" class="self-stretch p-2 bg-white border border-gray-300 rounded flex items-center gap-2">
              <div class="w-4 h-4 border border-gray-300 rounded-sm"></div>
              <span class="text-xs text-gray-700">{{ option }}</span>
            </div>
          </div>

          <div v-else-if="question.type === 'oui-non'" class="self-stretch flex gap-2">
            <div class="flex-1 p-2 bg-white border border-gray-300 rounded text-center text-xs text-gray-700">Oui</div>
            <div class="flex-1 p-2 bg-white border border-gray-300 rounded text-center text-xs text-gray-700">Non</div>
          </div>

          <div v-else-if="question.type === 'date'" class="self-stretch p-2 bg-white border border-gray-300 rounded">
            <div class="text-xs text-gray-400">JJ/MM/AAAA</div>
          </div>

          <div v-else-if="question.type === 'telephone'" class="self-stretch p-2 bg-white border border-gray-300 rounded">
            <div class="text-xs text-gray-400">+221 77 000 00 00</div>
          </div>

          <div v-else-if="question.type === 'photo'" class="self-stretch p-4 bg-white border border-dashed border-gray-300 rounded flex flex-col items-center justify-center">
            <svg class="w-6 h-6 text-gray-400 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.01M3 9a2 2 0 012-2h.01M3 9a2 2 0 012-2h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div class="text-xs text-gray-400">Ajouter une photo</div>
          </div>

          <div v-else-if="question.type === 'gps'" class="self-stretch p-3 bg-or/10 border border-or/30 rounded">
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4" style="color: #021427" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
              </svg>
              <div class="text-xs font-semibold" style="color: #021427">14.1386° N, 16.0743° W</div>
            </div>
            <div class="text-[10px] text-gray-500 mt-1">Généré automatiquement</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  questions: {
    type: Array,
    required: true,
  },
})
</script>


