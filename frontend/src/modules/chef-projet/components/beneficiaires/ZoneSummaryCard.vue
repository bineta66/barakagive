<template>
  <div class="bg-white border border-slate-200/60 rounded-xl shadow-[0px_1px_2px_0px_rgba(0,0,0,0.05)] overflow-hidden">
    <div class="p-6">
      <h3 class="text-lg font-bold text-gray-900">Fiche de synthÃ¨se</h3>
      <p class="text-xs text-gray-500 mt-1">RÃ©gion / Zone sÃ©lectionnÃ©e</p>
    </div>
    <div class="p-6 space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <p class="text-xs font-semibold text-gray-500">RÃ©gion</p>
          <p class="text-sm font-medium text-gray-900 mt-1">{{ synthese.region }}</p>
        </div>
        <div>
          <p class="text-xs font-semibold text-gray-500">Zone</p>
          <p class="text-sm font-medium text-gray-900 mt-1">{{ synthese.zone }}</p>
        </div>
        <div>
          <p class="text-xs font-semibold text-gray-500">Total bÃ©nÃ©ficiaires</p>
          <p class="text-sm font-medium text-gray-900 mt-1">{{ synthese.totalBeneficiaires }}</p>
        </div>
        <div>
          <p class="text-xs font-semibold text-gray-500">Campagnes actives</p>
          <p class="text-sm font-medium text-gray-900 mt-1">{{ synthese.campagnesActives }}</p>
        </div>
        <div class="col-span-2">
          <p class="text-xs font-semibold text-gray-500">Projet principal</p>
          <p class="text-sm font-medium text-gray-900 mt-1">{{ synthese.projetPrincipal }}</p>
        </div>
        <div class="col-span-2">
          <p class="text-xs font-semibold text-gray-500">Urgences Ã©levÃ©es (Score IA)</p>
          <p class="text-sm font-medium text-red-700 mt-1">{{ synthese.urgencesElevees }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  synthese: {
    type: Object,
    required: true,
  },
})
</script>

