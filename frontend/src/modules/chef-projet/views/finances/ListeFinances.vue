<template>
  <main class="min-h-screen space-y-6 bg-gradient-to-br from-slate-50 via-cyan-50/40 to-white p-4 sm:p-6">
    <header>
      <h1 class="text-3xl font-bold text-bleu-nuit">Finances</h1>
      <p class="mt-1 text-sm text-slate-600">Suivez les budgets, les dépenses et les financements de vos projets.</p>
    </header>

    <p v-if="error" role="alert" class="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{{ error }}</p>
    <div v-if="loading" class="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Chargement des données financières…</div>

    <template v-else-if="!error">
      <section class="grid w-full grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3" aria-label="Indicateurs financiers">
        <KpiCard title="Budget alloué" :value="currency(summary.budget_total)" :icon="Wallet" />
        <KpiCard title="Budget disponible" :value="currency(summary.budget_disponible)" :icon="PiggyBank" :tone="summary.budget_disponible < 0 ? 'danger' : 'neutral'" />
        <KpiCard title="Taux d’exécution" :value="summary.budget_total > 0 ? `${summary.taux_execution} %` : 'Non disponible'" :icon="Activity" />
      </section>

      <section class="glass-surface rounded-2xl p-4" aria-label="Filtres financiers">
        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <label class="relative xl:col-span-2">
            <span class="sr-only">Rechercher un projet</span>
            <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
            <input v-model="search" type="search" placeholder="Projet ou code…" class="filter-input pl-9" />
          </label>
          <label><span class="sr-only">Projet</span>
            <select v-model="filters.project_id" class="filter-input"><option value="">Tous les projets</option><option v-for="p in data.projets_accessibles" :key="p.id" :value="p.id">{{ p.nom }}</option></select>
          </label>
          <label><span class="sr-only">Campagne</span>
            <select v-model="filters.campaign_id" class="filter-input"><option value="">Toutes les campagnes</option><option v-for="c in visibleCampaigns" :key="c.id" :value="c.id">{{ c.nom }}</option></select>
          </label>
          <label><span class="sr-only">Statut du budget</span>
            <select v-model="filters.budget_status" class="filter-input"><option value="">Tous les statuts budgétaires</option><option value="APPROUVE">Approuvé</option><option value="EN_COURS">En cours</option><option value="CLOTURE">Clôturé</option></select>
          </label>
          <button type="button" class="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="resetFilters"><RotateCcw :size="16" /> Réinitialiser</button>
        </div>
      </section>

      <div v-if="summary.budget_total > 0" class="flex items-start gap-3 rounded-xl border p-4 text-sm" :class="summary.budget_disponible < 0 ? 'border-red-200 bg-red-50 text-red-800' : 'border-emerald-200 bg-emerald-50 text-emerald-900'">
        <component :is="summary.budget_disponible < 0 ? TriangleAlert : CircleCheck" :size="18" class="mt-0.5 shrink-0" />
        <p>{{ summary.budget_disponible < 0 ? 'Alerte : les engagements de dépenses dépassent le budget alloué.' : 'Les engagements enregistrés restent dans le budget alloué.' }} Le disponible tient compte des dépenses en attente, vérifiées et approuvées.</p>
      </div>

      <section class="grid gap-4 xl:grid-cols-2">
        <article class="panel">
          <h2 class="panel-title">Budget et dépenses par projet</h2>
          <DashboardChart v-if="visibleProjects.length" type="bar" :data="projectChart" :height="300" value-format="currency" />
          <EmptyState v-else titre="Aucune donnée de projet" description="Aucun budget ou mouvement ne correspond aux filtres." container-class="min-h-[220px]" />
        </article>
        <article class="panel">
          <h2 class="panel-title">Taux d’exécution par projet</h2>
          <DashboardChart v-if="projectsWithBudget.length" type="bar" :data="executionChart" :height="300" horizontal value-format="percent" />
          <EmptyState v-else titre="Taux indisponible" description="Les projets sélectionnés n’ont pas de budget de référence." container-class="min-h-[220px]" />
        </article>
        <article class="panel">
          <h2 class="panel-title">Évolution mensuelle des dépenses</h2>
          <DashboardChart v-if="data.depenses_par_mois?.length" type="line" :data="monthlyChart" :height="280" value-format="currency" />
          <EmptyState v-else titre="Aucune dépense sur la période" description="Les dépenses approuvées apparaîtront ici lorsqu’elles existent." container-class="min-h-[200px]" />
        </article>
        <article class="panel">
          <h2 class="panel-title">Dépenses par ligne budgétaire</h2>
          <DashboardChart v-if="topLines.length" type="bar" :data="lineChart" :height="280" horizontal value-format="currency" />
          <EmptyState v-else titre="Aucune dépense par ligne" description="Aucune dépense approuvée n’est associée aux lignes budgétaires filtrées." container-class="min-h-[200px]" />
        </article>

      </section>

      <section class="grid min-w-0 items-start gap-4 xl:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
        <article class="panel">
        <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div><h2 class="panel-title">Suivi financier par projet</h2><p class="mt-1 text-xs text-slate-500">Le disponible inclut les engagements de dépenses enregistrés.</p></div>
          <span class="text-xs text-slate-500">{{ visibleProjects.length }} projet(s)</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[760px] text-sm">
            <thead class="bg-slate-50 text-left text-xs uppercase text-slate-600"><tr><th class="px-3 py-3">Projet</th><th class="px-3 py-3 text-right">Budget</th><th class="px-3 py-3 text-right">Dépenses approuvées</th><th class="px-3 py-3 text-right">Disponible</th><th class="px-3 py-3 text-right">Exécution</th><th class="px-3 py-3">Statut</th><th class="px-3 py-3"></th></tr></thead>
            <tbody>
              <tr v-for="p in pagedProjects" :key="p.id" class="border-t border-slate-100 hover:bg-slate-50"><td class="px-3 py-3"><strong class="block text-slate-800">{{ p.nom }}</strong><span class="text-xs text-slate-500">{{ p.code }}</span></td><td class="px-3 py-3 text-right">{{ currency(p.budget) }}</td><td class="px-3 py-3 text-right">{{ currency(p.depenses) }}</td><td class="px-3 py-3 text-right" :class="p.disponible < 0 ? 'font-semibold text-red-700' : ''">{{ currency(p.disponible) }}</td><td class="px-3 py-3 text-right">{{ p.taux_execution == null ? 'Non disponible' : `${p.taux_execution} %` }}</td><td class="px-3 py-3"><span class="rounded-full px-2 py-1 text-xs" :class="p.disponible < 0 ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-700'">{{ p.disponible < 0 ? 'Dépassement' : p.budget > 0 ? 'Dans le budget' : 'Sans budget' }}</span></td><td class="px-3 py-3 text-right"><RouterLink :to="`/chef-projet/finances/${p.id}`" class="inline-flex items-center gap-1 text-xs font-semibold text-bleu-nuit hover:underline"><Eye :size="15" /> Détails</RouterLink></td></tr>
              <tr v-if="!pagedProjects.length"><td colspan="7" class="px-3 py-8 text-center text-slate-500">Aucun projet ne correspond à la recherche.</td></tr>
            </tbody>
          </table>
        </div>
        <div v-if="projectPages > 1" class="mt-4 flex items-center justify-between border-t pt-3 text-xs"><span>Page {{ page }} sur {{ projectPages }}</span><div class="flex gap-2"><button class="page-button" :disabled="page <= 1" @click="page--">Précédent</button><button class="page-button" :disabled="page >= projectPages" @click="page++">Suivant</button></div></div>
        </article>
        <article class="panel">
          <h2 class="panel-title">Financements reçus par projet</h2>
          <DashboardChart v-if="receivedByProject.length" type="bar" :data="fundingChart" :height="280" horizontal value-format="currency" />
          <EmptyState v-else titre="Aucun financement reçu" description="Les financements apparaîtront ici après leur passage au statut reçu." container-class="min-h-[200px]" />
        </article>
      </section>

      <section class="panel">
        <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"><div><h2 class="panel-title">Lignes budgétaires</h2><p class="mt-1 text-xs text-slate-500">Le montant retenu est le montant révisé lorsqu’il est renseigné, sinon le montant prévu.</p></div><input v-model="lineSearch" type="search" placeholder="Rechercher une ligne ou un projet…" class="filter-input sm:max-w-xs" /></div>
        <div class="overflow-x-auto"><table class="w-full min-w-[800px] text-sm"><thead class="bg-slate-50 text-left text-xs uppercase text-slate-600"><tr><th class="px-3 py-3"><button @click="toggleLineSort('libelle')">Ligne <ArrowUpDown :size="13" class="inline" /></button></th><th class="px-3 py-3">Projet</th><th class="px-3 py-3 text-right"><button @click="toggleLineSort('budget')">Budget <ArrowUpDown :size="13" class="inline" /></button></th><th class="px-3 py-3 text-right">Dépenses</th><th class="px-3 py-3 text-right">Solde</th><th class="px-3 py-3 text-right">Exécution</th><th class="px-3 py-3">Alerte</th><th class="px-3 py-3">Détails</th></tr></thead><tbody><tr v-for="line in visibleLines" :key="line.id" class="border-t border-slate-100"><td class="px-3 py-3"><strong>{{ line.libelle }}</strong><span v-if="line.categorie" class="block text-xs text-slate-500">{{ line.categorie }}</span></td><td class="px-3 py-3">{{ line.projet }}</td><td class="px-3 py-3 text-right">{{ currency(line.budget) }}</td><td class="px-3 py-3 text-right">{{ currency(line.depenses) }}</td><td class="px-3 py-3 text-right" :class="line.disponible < 0 ? 'text-red-700' : ''">{{ currency(line.disponible) }}</td><td class="px-3 py-3 text-right">{{ line.taux_execution == null ? 'Non disponible' : `${line.taux_execution} %` }}</td><td class="px-3 py-3"><span class="rounded-full px-2 py-1 text-xs" :class="line.disponible < 0 ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-700'">{{ line.disponible < 0 ? 'Dépassement' : '—' }}</span></td><td class="px-3 py-3"><RouterLink :to="`/chef-projet/finances/${line.projet_id}`" class="text-xs font-semibold text-bleu-nuit hover:underline">Voir projet</RouterLink></td></tr><tr v-if="!visibleLines.length"><td colspan="8" class="px-3 py-8 text-center text-slate-500">Aucune ligne budgétaire ne correspond aux filtres.</td></tr></tbody></table></div>
      </section>
    </template>
  </main>
</template>

<script setup>
import { computed, defineComponent, h, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { Activity, ArrowUpDown, CircleCheck, Eye, HandCoins, PiggyBank, Receipt, RotateCcw, Search, TriangleAlert, Wallet } from 'lucide-vue-next'
import DashboardChart from '@/components/ui/DashboardChart.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import api from '@/services/api.js'

const KpiCard = defineComponent({
  props: { title: String, value: String, detail: String, icon: [Object, Function], tone: { type: String, default: 'neutral' } },
  setup(props) { return () => h('article', { class: 'glass-surface w-full min-w-0 rounded-2xl p-4 transition duration-200 hover:-translate-y-0.5 hover:shadow-lg' }, [
    h('div', { class: 'flex items-start justify-between gap-2' }, [h('div', [h('p', { class: 'text-xs font-semibold uppercase tracking-wide text-slate-500' }, props.title), h('p', { class: 'mt-3 break-words text-xl font-bold text-bleu-nuit' }, props.value), ...(props.detail ? [h('p', { class: 'mt-1 text-xs text-slate-500' }, props.detail)] : [])]), h(props.icon, { size: 21, class: props.tone === 'danger' ? 'shrink-0 text-red-600' : 'shrink-0 text-[#D20C4F]' })]),
  ]) }
})

const data = ref({ resume: {}, projets: [], projets_accessibles: [], campagnes: [], depenses_par_mois: [], lignes_budgetaires: [], top_postes: [] })
const filters = reactive({ project_id: '', campaign_id: '', budget_status: '' })
const search = ref('')
const lineSearch = ref('')
const lineSort = ref({ key: 'libelle', direction: 1 })
const loading = ref(true)
const error = ref('')
const page = ref(1)
let requestId = 0
let searchTimer

const summary = computed(() => {
  const projects = visibleProjects.value
  const budget_total = projects.reduce((sum, p) => sum + Number(p.budget || 0), 0)
  const total_depenses = projects.reduce((sum, p) => sum + Number(p.depenses || 0), 0)
  return {
    budget_total,
    total_depenses,
    financements_recus: projects.reduce((sum, p) => sum + Number(p.financements_recus || 0), 0),
    budget_disponible: projects.reduce((sum, p) => sum + Number(p.disponible || 0), 0),
    taux_execution: budget_total ? Math.round(total_depenses / budget_total * 1000) / 10 : null,
  }
})
const visibleCampaigns = computed(() => data.value.campagnes.filter(c => !filters.project_id || c.projet_id === String(filters.project_id)))
const visibleProjects = computed(() => {
  const q = search.value.trim().toLocaleLowerCase('fr')
  return data.value.projets.filter(p => !q || `${p.nom} ${p.code}`.toLocaleLowerCase('fr').includes(q))
})
const projectsWithBudget = computed(() => visibleProjects.value.filter(p => p.taux_execution != null))
const pagedProjects = computed(() => visibleProjects.value.slice((page.value - 1) * 10, page.value * 10))
const projectPages = computed(() => Math.max(1, Math.ceil(visibleProjects.value.length / 10)))
const topLines = computed(() => [...(data.value.lignes_budgetaires || [])]
  .filter(line => Number(line.depenses) > 0)
  .sort((a, b) => b.depenses - a.depenses)
  .slice(0, 10)
  .map(line => ({ poste: line.libelle, total: line.depenses })))
const receivedByProject = computed(() => visibleProjects.value.filter(p => Number(p.financements_recus) > 0))
const visibleLines = computed(() => {
  const q = lineSearch.value.trim().toLocaleLowerCase('fr')
  const projectIds = new Set(visibleProjects.value.map(p => p.id))
  return [...(data.value.lignes_budgetaires || [])].filter(l => projectIds.has(l.projet_id) && (!q || `${l.libelle} ${l.categorie} ${l.projet}`.toLocaleLowerCase('fr').includes(q))).sort((a, b) => {
    const left = a[lineSort.value.key]; const right = b[lineSort.value.key]
    return (typeof left === 'number' ? left - right : String(left || '').localeCompare(String(right || ''), 'fr')) * lineSort.value.direction
  })
})
const projectChart = computed(() => ({ labels: visibleProjects.value.map(p => p.nom), datasets: [
  { label: 'Budget alloué', data: visibleProjects.value.map(p => p.budget), backgroundColor: '#00313C' },
  { label: 'Dépenses approuvées', data: visibleProjects.value.map(p => p.depenses), backgroundColor: '#D20C4F' },
  { label: 'Disponible après engagements', data: visibleProjects.value.map(p => p.disponible), backgroundColor: '#94a3b8' },
]}))
const executionChart = computed(() => ({ labels: projectsWithBudget.value.map(p => p.nom), datasets: [{ label: 'Exécution', data: projectsWithBudget.value.map(p => p.taux_execution), backgroundColor: projectsWithBudget.value.map(p => p.taux_execution > 100 ? '#dc2626' : '#D20C4F') }] }))
const monthlyChart = computed(() => ({ labels: data.value.depenses_par_mois.map(x => x.mois), datasets: [{ label: 'Dépenses approuvées', data: data.value.depenses_par_mois.map(x => x.montant), borderColor: '#D20C4F', backgroundColor: 'rgba(210,12,79,.12)', fill: true }] }))
const lineChart = computed(() => ({ labels: topLines.value.map(x => x.poste), datasets: [{ label: 'Dépenses approuvées', data: topLines.value.map(x => x.total), backgroundColor: '#00313C' }] }))
const fundingChart = computed(() => ({ labels: receivedByProject.value.map(p => p.nom), datasets: [{ label: 'Financements reçus', data: receivedByProject.value.map(p => p.financements_recus), backgroundColor: '#00313C' }] }))

function currency(value) { return `${new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(Number(value) || 0)} FCFA` }
function toggleLineSort(key) { lineSort.value = { key, direction: lineSort.value.key === key ? -lineSort.value.direction : 1 } }
function resetFilters() { Object.assign(filters, { project_id: '', campaign_id: '', budget_status: '' }); search.value = ''; lineSearch.value = ''; page.value = 1 }
watch([search, visibleProjects], () => { page.value = 1 })
watch(() => filters.project_id, () => { if (filters.campaign_id && !visibleCampaigns.value.some(c => c.id === filters.campaign_id)) filters.campaign_id = '' })
watch(filters, loadData)
watch(search, () => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(loadData, 250)
})
onMounted(loadData)
onBeforeUnmount(() => window.clearTimeout(searchTimer))

async function loadData() {
  const currentRequest = ++requestId
  loading.value = true
  error.value = ''
  try {
    const params = { ...Object.fromEntries(Object.entries(filters).filter(([, value]) => value)), ...(search.value.trim() ? { search: search.value.trim() } : {}) }
    const response = await api.get('/api/reports/finance/', { params })
    if (currentRequest === requestId) data.value = { ...data.value, ...response.data }
  } catch (err) {
    if (currentRequest === requestId) error.value = err.response?.data?.detail || 'Impossible de charger les données financières.'
  } finally {
    if (currentRequest === requestId) loading.value = false
  }
}
</script>

<style scoped>
.glass-surface { @apply border border-white/80 bg-white/75 shadow-[0_8px_30px_rgba(15,23,42,0.06)] backdrop-blur-xl; }
.filter-input { @apply w-full rounded-lg border border-slate-200/90 bg-white/75 px-3 py-2 text-sm text-slate-800 outline-none backdrop-blur-sm focus:border-bleu-nuit focus:ring-2 focus:ring-bleu-nuit/10; }
.panel { @apply glass-surface min-w-0 rounded-2xl p-4; }
.panel-title { @apply text-base font-semibold text-bleu-nuit; }
.page-button { @apply rounded border border-slate-300 px-3 py-2 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40; }
</style>
