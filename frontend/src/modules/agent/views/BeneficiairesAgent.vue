<template>
  <main class="mx-auto max-w-5xl space-y-4 px-4 py-5 sm:px-6">
    <header><p class="text-xs font-bold uppercase tracking-widest text-bleu-nuit">Suivi terrain</p><h1 class="mt-1 text-2xl font-bold text-slate-900">Mes bénéficiaires</h1><p class="mt-1 text-sm text-slate-600">Bénéficiaires collectés dans vos campagnes et zones affectées.</p></header>
    <label class="block"><span class="sr-only">Rechercher un bénéficiaire</span><input v-model="search" class="min-h-12 w-full rounded-xl border border-slate-300 px-4" type="search" placeholder="Rechercher par nom ou prénom" @input="onSearch" /></label>
    <p v-if="error" class="rounded-lg bg-red-50 p-3 text-sm text-red-800">{{ error }}</p>
    <div class="space-y-3">
      <article v-for="person in people" :key="person.id" class="rounded-2xl border border-slate-200 bg-white p-4">
        <div class="flex flex-wrap items-start justify-between gap-3"><div><h2 class="font-bold text-slate-900">{{ person.prenom }} {{ person.nom }}</h2><p class="mt-1 text-sm text-slate-600">{{ person.campagne?.nom || person.campagne }} · {{ person.zone?.nom || 'Zone' }}</p></div><div class="text-right"><p class="text-sm font-semibold text-slate-800">{{ status(person.statut) }}</p><p v-if="person.score_vulnerabilite != null" class="text-xs text-slate-500">Score calculé : {{ person.score_vulnerabilite }}/100</p></div></div>
      </article>
    </div>
    <p v-if="!loading && !people.length" class="rounded-xl bg-white p-6 text-center text-slate-600">Aucun bénéficiaire trouvé.</p>
    <div class="flex items-center justify-between"><span class="text-sm text-slate-500">{{ store.pagination.count }} bénéficiaire(s)</span><div class="flex gap-2"><button class="min-h-11 rounded-xl border px-4 disabled:opacity-40" :disabled="page <= 1 || loading" @click="changePage(-1)">Précédent</button><button class="min-h-11 rounded-xl border px-4 disabled:opacity-40" :disabled="page * 20 >= store.pagination.count || loading" @click="changePage(1)">Suivant</button></div></div>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useBeneficiaryStore } from '@/stores/beneficiary.js'
const store = useBeneficiaryStore()
const people = ref([]), search = ref(''), page = ref(1), loading = ref(false), error = ref('')
let timer
const status = (value) => ({ IDENTIFIE: 'Identifié', EVALUE: 'Évalué', PRIORITAIRE: 'Prioritaire', PRIS_EN_CHARGE: 'Pris en charge', SORTI: 'Sorti' }[value] || value || 'Identifié')
async function fetchPeople() { loading.value = true; error.value = ''; try { people.value = await store.fetchBeneficiaries({ page: page.value, page_size: 20, search: search.value }) } catch { error.value = 'Impossible de charger les bénéficiaires.' } finally { loading.value = false } }
function onSearch() { clearTimeout(timer); page.value = 1; timer = setTimeout(fetchPeople, 250) }
function changePage(delta) { page.value += delta; fetchPeople() }
onMounted(fetchPeople)
</script>
