<template>
  <main class="min-h-screen space-y-5 bg-slate-50 p-4 sm:p-6">
    <header class="flex flex-col gap-4 border-b border-slate-200 pb-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Gestion des Projets</h1>
        <p class="mt-1 text-sm text-slate-600">Créez, suivez et administrez les projets humanitaires de votre organisation.</p>
      </div>
      <RouterLink to="/gerant/projets/creer" class="inline-flex items-center justify-center gap-2 rounded-lg bg-bleu-nuit px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#01111e]">
        <Plus :size="18" /> Nouveau projet
      </RouterLink>
    </header>

    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" />
    <p v-if="loadError" role="alert" class="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{{ loadError }}</p>

    <LoadingSpinner v-if="loading && !projets.length" message="Chargement des projets…" />

    <template v-else>
      <section class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4" aria-label="Indicateurs des projets">
        <KpiCard title="Total des projets" :value="String(projetsFiltres.length)" :icon="FolderKanban" />
        <KpiCard title="Projets en cours" :value="String(projetsActifsFiltres.length)" :icon="Activity" />
        <KpiCard title="Projets à surveiller" :value="String(projetsSurveiller.length)" :icon="TriangleAlert" :tone="projetsSurveiller.length ? 'warning' : 'neutral'" />
        <KpiCard title="Budget alloué / approuvé" :value="budgetsDisponibles ? `${formatMontant(budgetTotal)} FCFA` : 'Non disponible'" :icon="Wallet" />
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm" aria-label="Filtres des projets">
        <div class="grid gap-3 lg:grid-cols-[minmax(250px,2fr)_minmax(180px,1fr)_auto]">
          <label class="relative">
            <span class="sr-only">Rechercher un projet</span><Search class="absolute left-3 top-3 text-slate-400" :size="16" />
            <input v-model="filters.search" type="search" placeholder="Rechercher par nom, code ou région…" class="filter-input pl-9" />
          </label>
          <label><span class="sr-only">Région</span>
            <select v-model="filters.region" class="filter-input"><option value="">Toutes les régions</option><option v-for="region in regionsListe" :key="region" :value="region">{{ region }}</option></select>
          </label>
          <button v-if="hasFilters" class="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" @click="resetFilters"><RotateCcw :size="15" /> Réinitialiser</button>
        </div>
        <details class="mt-3">
          <summary class="cursor-pointer text-xs font-semibold text-bleu-nuit">Filtres avancés</summary>
          <div class="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <label><span class="mb-1 block text-xs text-slate-500">Statut</span><select v-model="filters.status" class="filter-input"><option value="">Tous les statuts</option><option v-for="status in statusOptions" :key="status" :value="status">{{ status }}</option></select></label>
            <label><span class="mb-1 block text-xs text-slate-500">Chef de projet</span><select v-model="filters.chef" class="filter-input"><option value="">Tous les chefs</option><option v-for="chef in chefsListe" :key="chef" :value="chef">{{ chef }}</option></select></label>
            <label><span class="mb-1 block text-xs text-slate-500">Début au plus tôt</span><input v-model="filters.start_from" type="date" class="filter-input" /></label>
            <label><span class="mb-1 block text-xs text-slate-500">Échéance au plus tard</span><input v-model="filters.end_to" type="date" class="filter-input" /></label>
          </div>
        </details>
      </section>

      <section class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3">
          <h2 class="font-semibold text-bleu-nuit">Liste des projets</h2><span class="text-xs text-slate-500">{{ projetsFiltres.length }} résultat(s)</span>
        </div>
        <EmptyState v-if="!projetsFiltres.length" titre="Aucun projet trouvé" description="Aucun projet ne correspond aux filtres actuels. Vous pouvez modifier les filtres ou créer un projet." container-class="min-h-[180px]" />
        <div v-else class="overflow-x-auto">
          <table class="w-full min-w-[920px]">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-bleu-nuit"><tr><th class="px-4 py-3">Code & projet</th><th class="px-4 py-3">Chef de projet</th><th class="px-4 py-3">Région</th><th class="px-4 py-3 text-right">Budget alloué</th><th class="px-4 py-3">Période</th><th class="px-4 py-3">Statut / échéance</th><th class="px-4 py-3 text-right">Actions</th></tr></thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              <tr v-for="p in projetsFiltres" :key="p.id" class="hover:bg-slate-50/70">
                <td class="px-4 py-3"><RouterLink :to="`/gerant/projets/${p.id}`" class="font-semibold text-slate-900 hover:text-bleu-accent">{{ p.name }}</RouterLink><span class="mt-0.5 block text-xs font-medium text-slate-500">{{ p.code || 'Code indisponible' }}</span></td>
                <td class="px-4 py-3 text-slate-700">{{ p.chef_projet || 'Non assigné' }}</td>
                <td class="px-4 py-3 text-slate-600">{{ p.region || '—' }}</td>
                <td class="px-4 py-3 text-right font-semibold text-slate-800">{{ budgetForProject(p.id) == null ? 'Non disponible' : `${formatMontant(budgetForProject(p.id))} FCFA` }}</td>
                <td class="px-4 py-3 text-xs text-slate-600"><time :datetime="p.start_date">{{ formatDate(p.start_date) }}</time> – <time :datetime="p.end_date">{{ formatDate(p.end_date) }}</time></td>
                <td class="px-4 py-3"><span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold" :class="statusClass(p)"><component :is="statusIcon(p)" :size="13" />{{ projectStatus(p) }}</span><p v-if="deadlineHint(p)" class="mt-1 text-xs" :class="deadlineHint(p).tone">{{ deadlineHint(p).text }}</p><p v-if="budgetExceeded(p.id)" class="mt-1 inline-flex items-center gap-1 text-xs font-medium text-red-700"><TriangleAlert :size="13" />Budget engagé dépassé</p></td>
                <td class="px-4 py-3 text-right"><div class="inline-flex items-center gap-1"><RouterLink :to="`/gerant/projets/${p.id}`" class="action-button" title="Voir les détails" aria-label="Voir les détails"><Eye :size="18" class="text-indigo-600" /></RouterLink><RouterLink v-if="!p.archived" :to="`/gerant/projets/modifier/${p.id}`" class="action-button" title="Modifier" aria-label="Modifier"><Pencil :size="18" class="text-sky-700" /></RouterLink><button v-if="!p.archived" class="action-button hover:text-amber-700" title="Archiver" aria-label="Archiver le projet" @click="projetAArchiver = p"><Archive :size="18" class="text-amber-600" /></button></div></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <Teleport to="body"><div v-if="projetAArchiver" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="projetAArchiver = null"><div class="w-full max-w-sm rounded-xl bg-white p-6 shadow-xl"><div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-red-50 text-red-600"><Archive :size="22" /></div><h2 class="mb-2 text-center font-bold text-slate-900">Archiver le projet</h2><p class="mb-6 text-center text-sm text-slate-600">Le projet « {{ projetAArchiver.name }} » sera conservé et marqué comme archivé.</p><div class="flex gap-3"><button class="flex-1 rounded-lg border border-slate-200 px-4 py-2.5 text-sm" @click="projetAArchiver = null">Annuler</button><button class="flex-1 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50" :disabled="archivage" @click="executerArchivage">{{ archivage ? 'Archivage…' : 'Archiver' }}</button></div></div></div></Teleport>
  </main>
</template>

<script setup>
import { computed, defineComponent, h, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Activity, Archive, CalendarClock, CircleCheck, Eye, FolderKanban, Pencil, Plus, RotateCcw, Search, TriangleAlert, Wallet } from 'lucide-vue-next'
import EmptyState from '@/components/ui/EmptyState.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import AlertMessage from '@/components/ui/AlertMessage.vue'
import { useAutoRefresh } from '@/composables/useAutoRefresh.js'
import { useGerantStore } from '@/modules/gerant/stores/gerantStore.js'
import api from '@/services/api.js'

const KpiCard = defineComponent({
  props: { title: String, value: String, icon: [Object, Function], tone: { type: String, default: 'neutral' } },
  setup(props) { return () => h('article', { class: 'flex min-h-[112px] items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm' }, [h('div', [h('p', { class: 'text-xs font-bold uppercase tracking-wide text-slate-500' }, props.title), h('p', { class: `mt-2 text-2xl font-bold ${props.tone === 'warning' ? 'text-amber-700' : 'text-bleu-nuit'}` }, props.value)]), h(props.icon, { size: 24, class: props.tone === 'warning' ? 'shrink-0 text-amber-600' : 'shrink-0 text-[#D20C4F]' })]) }
})

const store = useGerantStore()
const filters = reactive({ search: '', region: '', status: '', chef: '', start_from: '', end_to: '' })
const budgets = ref([])
const budgetsDisponibles = ref(false)
const loading = ref(true)
const loadError = ref('')
const feedback = reactive({ type: 'success', message: '' })
const projetAArchiver = ref(null)
const archivage = ref(false)
const projets = computed(() => store.projets)
const todayParts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Africa/Dakar', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date())
const todayIso = `${todayParts.find(part => part.type === 'year').value}-${todayParts.find(part => part.type === 'month').value}-${todayParts.find(part => part.type === 'day').value}`
const today = new Date(`${todayIso}T00:00:00`)
const statusOptions = ['Planifié', 'En cours', 'Échéance dépassée', 'Archivé']
const deadlineHorizonDays = 30

const regionsListe = computed(() => [...new Set(projets.value.map(p => p.region).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'fr')))
const chefsListe = computed(() => [...new Set(projets.value.map(p => p.chef_projet).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'fr')))
const projectBudgetMap = computed(() => {
  const totals = new Map()
  for (const budget of budgets.value) {
    if (!isAllocatedBudget(budget)) continue
    const id = String(budget.projet)
    const current = totals.get(id) || { amount: 0, balance: 0 }
    current.amount += Number(budget.montant) || 0
    current.balance += Number(budget.solde ?? budget.montant) || 0
    totals.set(id, current)
  }
  return totals
})
const projetsFiltres = computed(() => {
  const q = filters.search.trim().toLocaleLowerCase('fr')
  return projets.value.filter(project => {
    const matchesText = !q || `${project.name} ${project.code} ${project.region}`.toLocaleLowerCase('fr').includes(q)
    const matchesRegion = !filters.region || project.region === filters.region
    const matchesStatus = !filters.status || projectStatus(project) === filters.status
    const matchesChef = !filters.chef || project.chef_projet === filters.chef
    const matchesStart = !filters.start_from || project.start_date >= filters.start_from
    const matchesEnd = !filters.end_to || project.end_date <= filters.end_to
    return matchesText && matchesRegion && matchesStatus && matchesChef && matchesStart && matchesEnd
  })
})
const projetsActifsFiltres = computed(() => projetsFiltres.value.filter(isProjectActive))
const projetsSurveiller = computed(() => projetsFiltres.value.filter(project => isDeadlineOverdue(project) || budgetExceeded(project.id)))
const budgetTotal = computed(() => projetsFiltres.value.reduce((sum, project) => sum + (budgetForProject(project.id) || 0), 0))
const hasFilters = computed(() => Object.values(filters).some(Boolean))

function isAllocatedBudget(budget) { return budget.statut !== 'BROUILLON' || budget.source_financement === 'Allocation projet' }
function budgetForProject(id) { return budgetsDisponibles.value ? projectBudgetMap.value.get(String(id))?.amount ?? 0 : null }
function budgetExceeded(id) { return Number(projectBudgetMap.value.get(String(id))?.balance) < 0 }
function parseDate(value) { if (!value) return null; const date = new Date(`${value}T00:00:00`); return Number.isNaN(date.getTime()) ? null : date }
function isDeadlineOverdue(project) { return !project.archived && Boolean(project.end_date && project.end_date < todayIso) }
function isProjectActive(project) { return !project.archived && project.start_date <= todayIso && project.end_date >= todayIso }
function projectStatus(project) {
  if (project.archived) return 'Archivé'
  if (project.start_date > todayIso) return 'Planifié'
  if (project.end_date < todayIso) return 'Échéance dépassée'
  return 'En cours'
}
function statusClass(project) {
  if (project.archived) return 'bg-slate-100 text-slate-600'
  if (isDeadlineOverdue(project)) return 'bg-red-50 text-red-700'
  if (projectStatus(project) === 'Planifié') return 'bg-amber-50 text-amber-800'
  return 'bg-emerald-50 text-emerald-700'
}
function statusIcon(project) { return isDeadlineOverdue(project) ? TriangleAlert : project.archived ? Archive : projectStatus(project) === 'Planifié' ? CalendarClock : CircleCheck }
function deadlineHint(project) {
  const end = parseDate(project.end_date)
  if (!end || project.archived) return null
  const days = Math.ceil((end.getTime() - today.getTime()) / 86400000)
  if (days < 0) return { text: `Échéance dépassée de ${Math.abs(days)} jour(s)`, tone: 'text-red-700' }
  if (days <= deadlineHorizonDays) return { text: `Échéance dans ${days} jour(s)`, tone: 'text-amber-700' }
  return null
}
function formatDate(value) { const date = parseDate(value); return date ? date.toLocaleDateString('fr-FR') : '—' }
function formatMontant(value) { return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(Number(value) || 0) }
function resetFilters() { Object.keys(filters).forEach(key => { filters[key] = '' }) }

async function loadDashboard() {
  loading.value = true
  loadError.value = ''
  const outcomes = await Promise.allSettled([store.fetchProjets(), fetchAllBudgets()])
  if (outcomes[0].status === 'rejected' || store.error) loadError.value = store.error || 'Impossible de charger les projets.'
  if (outcomes[1].status === 'fulfilled') {
    budgets.value = outcomes[1].value
    budgetsDisponibles.value = true
  } else {
    budgetsDisponibles.value = false
    loadError.value ||= 'Impossible de charger les budgets; les montants ne sont pas affichés.'
  }
  loading.value = false
}
async function fetchAllBudgets() {
  const all = []
  let page = 1
  let next = true
  while (next) {
    const response = await api.get('/api/finance/budgets/', { params: { page, page_size: 100 } })
    const body = response.data
    all.push(...(body?.results ?? (Array.isArray(body) ? body : [])))
    next = Boolean(body?.next)
    page += 1
  }
  return all
}
async function executerArchivage() {
  if (!projetAArchiver.value || archivage.value) return
  archivage.value = true
  feedback.message = ''
  try {
    await store.deleteProject(projetAArchiver.value.id)
    projetAArchiver.value = null
    feedback.type = 'success'
    feedback.message = 'Projet archivé avec succès.'
  } catch {
    feedback.type = 'error'
    feedback.message = store.error || 'Erreur lors de l’archivage du projet.'
  } finally {
    archivage.value = false
  }
}

useAutoRefresh(loadDashboard)
</script>

<style scoped>
.filter-input { @apply w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 outline-none focus:border-bleu-nuit focus:ring-2 focus:ring-bleu-nuit/20; }
.action-button { @apply rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-bleu-nuit; }
</style>
