<template>
  <div class="flex h-full flex-col rounded-xl bg-white p-6">
    <div class="mb-4 flex items-center justify-between border-b border-slate-100 pb-3">
      <span class="text-sm font-bold uppercase tracking-wide text-slate-700">Activite recente</span>
      <span class="text-xs text-slate-400">{{ activities.length ? 'Donnees enregistrees' : 'Aucune donnee' }}</span>
    </div>
    <div v-if="activities.length" class="space-y-4">
      <div v-for="activity in activities" :key="activity.id" class="flex gap-3">
        <span class="mt-1.5 size-2 shrink-0 rounded-full bg-bleu-nuit"></span>
        <div><p class="text-xs font-medium text-slate-800">{{ activity.label }} <span class="font-semibold">{{ activity.detail }}</span></p><p class="mt-1 text-xs text-slate-400">{{ activity.actor || 'Auteur non renseigne' }} ? {{ formatDate(activity.at) }}</p></div>
      </div>
    </div>
    <p v-else class="rounded-lg bg-slate-50 px-3 py-5 text-sm text-slate-500">Aucune activite enregistree.</p>
  </div>
</template>

<script setup>
import dayjs from 'dayjs'
const props = defineProps({ activities: { type: Array, default: () => [] } })
const formatDate = value => value ? dayjs(value).format('DD MMM YYYY HH:mm') : ''
</script>
