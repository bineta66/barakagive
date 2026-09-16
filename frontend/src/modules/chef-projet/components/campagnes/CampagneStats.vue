<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
      <div>
        <p class="text-xs font-bold uppercase text-slate-900">Total campagnes</p>
        <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.total }}</h3>
      </div>
      <ClipboardList class="text-bleu-nuit" :size="28" />
    </div>

    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
      <div>
        <p class="text-xs font-bold uppercase text-slate-900">Actives</p>
        <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.actives }}</h3>
      </div>
      <Activity class="text-bleu-nuit" :size="28" />
    </div>

    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
      <div>
        <p class="text-xs font-bold uppercase text-slate-900">Planifiées</p>
        <h3 class="text-xl font-bold text-slate-800 mt-2">{{ statistiques.planifiees }}</h3>
      </div>
      <Calendar class="text-bleu-nuit" :size="28" />
    </div>

    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
      <div>
        <p class="text-xs font-bold uppercase text-slate-900">Terminées</p>
        <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.terminees }}</h3>
      </div>
      <CheckCircle class="text-bleu-nuit" :size="28" />
    </div>
  </div>
</template>

<script setup>
import { ClipboardList, Activity, Calendar, CheckCircle } from "lucide-vue-next"

defineProps({
  statistiques: {
    type: Object,
    required: true,
  },
})
</script>


