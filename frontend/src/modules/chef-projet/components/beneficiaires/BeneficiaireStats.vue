<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 shadow-xs-[0px_1px_2px_0px_rgba(0,0,0,0.05)]">
      <p class="text-xs font-bold uppercase text-slate-900">Total bénéficiaires</p>
      <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.total }}</h3>
    </div>
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 shadow-xs-[0px_1px_2px_0px_rgba(0,0,0,0.05)]">
      <p class="text-xs font-bold uppercase text-slate-900">Critiques</p>
      <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.critiques }}</h3>
    </div>
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 shadow-xs-[0px_1px_2px_0px_rgba(0,0,0,0.05)]">
      <p class="text-xs font-bold uppercase text-slate-900">Élevés</p>
      <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.eleves }}</h3>
    </div>
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 shadow-xs-[0px_1px_2px_0px_rgba(0,0,0,0.05)]">
      <p class="text-xs font-bold uppercase text-slate-900">Zones actives</p>
      <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.zones }}</h3>
    </div>
  </div>
</template>

<script setup>
defineProps({
  statistiques: {
    type: Object,
    required: true,
  },
})
</script>


