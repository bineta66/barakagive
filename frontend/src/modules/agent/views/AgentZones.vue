<template>
  <main class="mx-auto max-w-5xl space-y-5 px-4 py-5 sm:px-6">
    <header>
      <p class="text-xs font-bold uppercase tracking-widest text-bleu-nuit">Affectations</p>
      <h1 class="mt-1 text-2xl font-bold text-slate-900">Mes zones</h1>
      <p class="mt-1 text-sm text-slate-600">Zones liées à vos campagnes et objectifs de collecte.</p>
    </header>

    <p v-if="error" class="rounded-lg bg-red-50 p-3 text-sm text-red-800">{{ error }}</p>

    <div class="grid gap-3 sm:grid-cols-2">
      <article v-for="zone in paginatedZones" :key="`${zone.campagne_id}:${zone.id}`" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="font-bold text-slate-900">{{ zone.nom }}</h2>
            <p class="mt-1 text-sm text-slate-500">{{ zone.campagne }}</p>
            <p class="text-xs text-slate-500">{{ zone.projet }}</p>
          </div>
          <MapPin class="shrink-0 text-bleu-nuit" :size="20" />
        </div>
        <div class="mt-4 grid grid-cols-1 min-[360px]:grid-cols-3 gap-2 rounded-xl bg-slate-50 p-3 text-center">
          <div><p class="text-lg font-bold">{{ zone.beneficiaires }}</p><p class="text-xs text-slate-500">Collectés</p></div>
          <div><p class="text-lg font-bold">{{ zone.objectif }}</p><p class="text-xs text-slate-500">Objectif</p></div>
          <div><p class="text-lg font-bold">{{ zone.restant }}</p><p class="text-xs text-slate-500">Restants</p></div>
        </div>
        <BoutonPrimary :to="`/agent/campagnes/${zone.campagne_id}/formulaire?zone_id=${encodeURIComponent(zone.id)}`" class="mt-3 w-full min-h-11">
          Collecter dans cette zone
        </BoutonPrimary>
      </article>
    </div>

    <nav v-if="totalPages > 1" class="flex flex-wrap items-center justify-between gap-3" aria-label="Pagination des zones">
      <p class="text-sm text-slate-600">{{ rangeStart }}–{{ rangeEnd }} sur {{ zones.length }} zones</p>
      <div class="flex items-center gap-2">
        <button type="button" class="min-h-10 rounded-xl border border-slate-300 px-3 text-sm font-semibold text-bleu-nuit transition hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-bleu-nuit disabled:cursor-not-allowed disabled:opacity-50" :disabled="currentPage === 1" @click="currentPage--">Précédent</button>
        <span class="text-sm text-slate-600">Page {{ currentPage }} / {{ totalPages }}</span>
        <button type="button" class="min-h-10 rounded-xl border border-slate-300 px-3 text-sm font-semibold text-bleu-nuit transition hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-bleu-nuit disabled:cursor-not-allowed disabled:opacity-50" :disabled="currentPage === totalPages" @click="currentPage++">Suivant</button>
      </div>
    </nav>

    <p v-if="!loading && !zones.length" class="rounded-2xl bg-white p-6 text-center text-slate-600">Aucune zone ne vous est affectée.</p>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { MapPin } from 'lucide-vue-next'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import api from '@/services/api.js'

const pageSize = 4
const zones = ref([])
const currentPage = ref(1)
const loading = ref(true)
const error = ref('')
const totalPages = computed(() => Math.ceil(zones.value.length / pageSize))
const paginatedZones = computed(() => zones.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))
const rangeStart = computed(() => zones.value.length ? (currentPage.value - 1) * pageSize + 1 : 0)
const rangeEnd = computed(() => Math.min(currentPage.value * pageSize, zones.value.length))

onMounted(async () => {
  try {
    const { data } = await api.get('/api/agent/zones/')
    zones.value = Array.isArray(data) ? data : []
  } catch {
    error.value = 'Impossible de charger vos zones affectées.'
  } finally {
    loading.value = false
  }
})
</script>
