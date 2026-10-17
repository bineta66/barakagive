<template>
  <div class="space-y-6 pb-6">
    <header class="flex flex-col gap-1 border-b border-slate-200/70 pb-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Vue globale de votre ONG</p>
        <h1 class="mt-1 text-2xl font-bold text-bleu-nuit sm:text-3xl">Tableau de bord Gérant</h1>
        <p class="mt-1 text-sm text-slate-500">Suivez les projets, les ressources et les actions de votre organisation.</p>
      </div>
      <RouterLink to="/gerant/utilisateurs" class="inline-flex w-fit items-center gap-2 rounded-xl bg-bleu-nuit px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-bleu-nuit/90">
        <Users :size="17" /> Gérer les utilisateurs
      </RouterLink>
    </header>

    <AlertMessage v-if="error" type="error" :message="error" :dismissible="true" @dismiss="error = null" />
    <LoadingSpinner v-if="loading && !decisionDashboard" message="Chargement des données de l'organisation..." />

    <template v-else-if="decisionDashboard">
      <section aria-label="Indicateurs principaux" class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard titre="Projets actifs" :valeur="operationnel.projets_actifs ?? 0" :icone="FolderKanban" />
        <KpiCard titre="Campagnes actives" :valeur="operationnel.campagnes_en_cours ?? 0" :icone="ClipboardList" />
        <KpiCard titre="Bénéficiaires suivis" :valeur="formatNombre(operationnel.beneficiaires ?? 0)" :icone="Users" />
        <KpiCard titre="Budget total" :valeur="montant(finance.budget_total) + ' FCFA'" :icone="Wallet" />
      </section>

      <section class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <article class="glass-surface min-w-0 p-5">
          <div class="mb-4 flex items-center justify-between gap-3">
            <div>
              <h2 class="text-base font-bold text-slate-900">Synthèse financière</h2>
              <p class="mt-1 text-xs text-slate-500">Montants calculés à partir des données financières de l’ONG.</p>
            </div>
            <Wallet class="shrink-0 text-bleu-nuit" :size="21" />
          </div>
          <dl class="divide-y divide-slate-200/70">
            <div class="flex items-center justify-between gap-4 py-3 text-sm">
              <dt class="text-slate-600">Financements reçus</dt><dd class="text-right font-semibold text-slate-900">{{ montant(finance.financements_recus) }} FCFA</dd>
            </div>
            <div class="flex items-center justify-between gap-4 py-3 text-sm">
              <dt class="text-slate-600">Dons reçus</dt><dd class="text-right font-semibold text-slate-900">{{ montant(finance.dons_recus) }} FCFA</dd>
            </div>
            <div class="flex items-center justify-between gap-4 py-3 text-sm">
              <dt class="text-slate-600">Dépenses validées</dt><dd class="text-right font-semibold text-slate-900">{{ montant(finance.depenses_validees) }} FCFA</dd>
            </div>
            <div class="flex items-center justify-between gap-4 py-3 text-sm">
              <dt class="font-semibold text-slate-700">Solde disponible</dt>
              <dd class="text-right text-base font-bold" :class="Number(finance.solde) < 0 ? 'text-rose-baraka' : 'text-bleu-nuit'">{{ montant(finance.solde) }} FCFA</dd>
            </div>
          </dl>
        </article>

        <article class="glass-surface min-w-0 p-5">
          <div class="mb-3">
            <h2 class="text-base font-bold text-slate-900">État des projets</h2>
            <p class="mt-1 text-xs text-slate-500">Répartition selon les dates de début et de fin enregistrées.</p>
          </div>
          <DashboardChart v-if="projectStatusChart.labels.length" type="bar" :data="projectStatusChart" :height="230" />
          <p v-else class="py-12 text-center text-sm text-slate-500">Aucun projet enregistré.</p>
        </article>
      </section>

      <section class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <article class="glass-surface min-w-0 p-5">
          <div class="mb-3">
            <h2 class="text-base font-bold text-slate-900">Évolution des bénéficiaires</h2>
            <p class="mt-1 text-xs text-slate-500">Enregistrements et prises en charge mensuels.</p>
          </div>
          <DashboardChart v-if="beneficiaryTrend.labels.length" type="line" :data="beneficiaryTrend" :height="260" />
          <p v-else class="py-12 text-center text-sm text-slate-500">Aucune donnée mensuelle disponible.</p>
        </article>

        <article class="glass-surface min-w-0 p-5">
          <div class="mb-3">
            <h2 class="text-base font-bold text-slate-900">Répartition géographique</h2>
            <p class="mt-1 text-xs text-slate-500">Bénéficiaires par zone et part dans le total suivi.</p>
          </div>
          <DashboardChart v-if="geographyChart.labels.length" type="bar" horizontal :data="geographyChart" :height="260" series-color="#00313C" />
          <p v-else class="py-12 text-center text-sm text-slate-500">Aucune répartition géographique disponible.</p>
          <div v-if="geographySummary.length" class="mt-3 flex flex-wrap gap-2">
            <span v-for="zone in geographySummary" :key="zone.nom" class="rounded-full border border-bleu-nuit/10 bg-white/60 px-2.5 py-1 text-xs text-slate-600">
              {{ zone.nom }} · {{ zone.pourcentage }} %
            </span>
          </div>
        </article>
      </section>

      <section class="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.4fr)]">
        <article class="glass-surface min-w-0 p-5">
          <div class="mb-4">
            <h2 class="text-base font-bold text-slate-900">Indicateurs de progression</h2>
            <p class="mt-1 text-xs text-slate-500">Taux fournis par les indicateurs métier Django.</p>
          </div>
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-3 xl:grid-cols-1">
            <div v-for="item in progressIndicators" :key="item.label" class="flex min-w-0 items-center gap-3 rounded-xl border border-bleu-nuit/10 bg-white/45 p-3">
              <div class="h-[92px] w-24 shrink-0">
                <DashboardChart v-if="item.available" type="doughnut" :data="progressData(item.value, item.color)" :height="92" :center-value="clampPercent(item.value)" center-label="réalisé" :series-color="item.color" />
                <div v-else class="flex h-full w-full items-center justify-center rounded-full border-[12px]" :style="{ borderColor: `${item.color}35` }"><span class="text-sm font-bold text-slate-500">—</span></div>
              </div>
              <div class="min-w-0">
                <p class="text-sm font-semibold text-slate-800">{{ item.label }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ item.available ? `${clampPercent(item.value)} %` : item.unavailableLabel }}</p>
              </div>
            </div>
          </div>
        </article>

        <article class="glass-surface min-w-0 p-5">
          <div class="mb-4 flex items-start justify-between gap-3">
            <div>
              <div class="flex items-center gap-2">
                <Sparkles class="text-bleu-nuit" :size="19" />
                <h2 class="text-base font-bold text-slate-900">Analyse IA de l’ONG</h2>
              </div>
              <p class="mt-1 text-xs text-slate-500">Synthèse fondée sur les données réelles du périmètre de votre organisation.</p>
            </div>
            <button type="button" :disabled="aiLoading" class="shrink-0 rounded-lg border border-bleu-nuit/15 bg-white/60 px-3 py-2 text-xs font-semibold text-bleu-nuit transition hover:bg-white disabled:opacity-50" @click="chargerAnalyseIa">
              {{ aiLoading ? 'Analyse…' : 'Actualiser' }}
            </button>
          </div>
          <div v-if="aiLoading && !aiInsight" class="flex min-h-20 items-center gap-3 text-sm text-slate-500">
            <span class="h-5 w-5 animate-spin rounded-full border-2 border-slate-200 border-t-bleu-nuit"></span> Analyse des indicateurs en cours…
          </div>
          <div v-else-if="aiInsight" class="grid grid-cols-1 gap-4 border-t border-slate-200/70 pt-4 md:grid-cols-3">
            <section class="min-w-0" aria-labelledby="ai-general-title">
              <h3 id="ai-general-title" class="mb-2 text-xs font-bold uppercase tracking-wide text-slate-500">Situation générale</h3>
              <p class="text-sm leading-6 text-slate-700">{{ aiInsight.summary }}</p>
            </section>
            <section class="min-w-0" aria-labelledby="ai-attention-title">
              <h3 id="ai-attention-title" class="mb-2 text-xs font-bold uppercase tracking-wide text-slate-500">⚠ À surveiller</h3>
              <ul v-if="aiInsight.attentionPoints.length" class="space-y-2">
                <li v-for="(point, index) in aiInsight.attentionPoints" :key="`${point.title}-${index}`" class="rounded-lg border border-slate-200/70 bg-white/40 p-2.5">
                  <div class="flex items-start gap-2">
                    <span class="mt-1 h-2 w-2 shrink-0 rounded-full" :class="severityClass(point.severity)" aria-hidden="true"></span>
                    <div class="min-w-0">
                      <p class="text-xs font-semibold leading-5 text-slate-800">{{ point.title }}</p>
                      <p class="text-xs leading-5 text-slate-600">{{ point.description }}</p>
                    </div>
                  </div>
                </li>
              </ul>
              <p v-else class="text-xs leading-5 text-slate-500">Aucun risque majeur détecté avec les données disponibles.</p>
            </section>
            <section class="min-w-0" aria-labelledby="ai-priority-title">
              <h3 id="ai-priority-title" class="mb-2 text-xs font-bold uppercase tracking-wide text-slate-500">💡 Priorité recommandée</h3>
              <ol v-if="aiInsight.recommendations.length" class="list-inside list-decimal space-y-2 text-xs leading-5 text-slate-700">
                <li v-for="(recommendation, index) in aiInsight.recommendations" :key="index">{{ recommendation }}</li>
              </ol>
              <p v-else class="text-xs leading-5 text-slate-500">Aucune action prioritaire n’est justifiée pour le moment.</p>
            </section>
          </div>
          <p v-else class="text-sm text-slate-500">{{ aiError || 'Les données disponibles ne permettent pas encore d’identifier une priorité fiable.' }}</p>
          <p v-if="aiInsight?.generatedAt" class="mt-4 border-t border-slate-200/70 pt-3 text-[11px] text-slate-400">Dernière analyse : {{ formatAnalysisDate(aiInsight.generatedAt) }}</p>
        </article>
      </section>

      <section class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <article class="glass-surface min-w-0 overflow-hidden">
          <div class="flex items-center justify-between gap-3 border-b border-slate-200/70 px-5 py-4">
            <div>
              <h2 class="text-base font-bold text-slate-900">Utilisateurs</h2>
              <p class="mt-1 text-xs text-slate-500">{{ team.total ?? 0 }} compte(s) dans l’ONG</p>
            </div>
            <RouterLink to="/gerant/utilisateurs" class="text-xs font-semibold text-bleu-nuit hover:underline">Voir tous</RouterLink>
          </div>
          <div class="grid grid-cols-2 gap-2 px-5 py-3 sm:grid-cols-4">
            <div v-for="role in teamRoles" :key="role.key" class="rounded-xl border border-bleu-nuit/10 bg-white/45 px-3 py-2.5">
              <p class="text-lg font-bold text-bleu-nuit">{{ team.par_role?.[role.key] ?? 0 }}</p>
              <p class="text-[11px] leading-4 text-slate-500">{{ role.label }}</p>
            </div>
          </div>
          <div v-if="team.recents?.length" class="divide-y divide-slate-200/60 px-5">
            <div v-for="person in team.recents.slice(0, 5)" :key="person.id" class="flex items-center gap-3 py-3">
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-bleu-nuit/10 text-xs font-bold text-bleu-nuit">{{ initials(person) }}</div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-semibold text-slate-800">{{ person.first_name }} {{ person.last_name }}</p>
                <p class="text-xs text-slate-500">{{ roleLabel(person.role) }}</p>
              </div>
              <span class="rounded-full px-2 py-1 text-[10px] font-semibold" :class="person.status === 'ACTIVE' ? 'bg-bleu-accent/15 text-bleu-accent border border-bleu-accent/25' : 'bg-slate-100 text-slate-600'">{{ statusLabel(person.status) }}</span>
            </div>
          </div>
          <p v-else class="px-5 pb-5 text-sm text-slate-500">Aucun utilisateur enregistré.</p>
        </article>

        <article class="glass-surface min-w-0 overflow-hidden">
          <div class="border-b border-slate-200/70 px-5 py-4">
            <h2 class="text-base font-bold text-slate-900">Activités récentes</h2>
            <p class="mt-1 text-xs text-slate-500">Dernières opérations enregistrées dans l’ONG.</p>
          </div>
          <div v-if="activities.length" class="divide-y divide-slate-200/60 px-5">
            <div v-for="activity in activities.slice(0, 6)" :key="activity.id" class="flex items-start gap-3 py-3">
              <span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-bleu-nuit"></span>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-semibold text-slate-800">{{ activityLabel(activity.label) }}</p>
                <p class="mt-0.5 break-words text-xs text-slate-500">{{ activity.detail }}</p>
                <p v-if="activity.actor" class="mt-1 text-[11px] text-slate-400">{{ activity.actor }}</p>
              </div>
              <time class="shrink-0 text-[11px] text-slate-400">{{ formatDate(activity.at) }}</time>
            </div>
          </div>
          <p v-else class="px-5 py-6 text-sm text-slate-500">Aucune activité récente enregistrée.</p>
        </article>
      </section>
    </template>
    <div v-else-if="!loading" class="glass-surface p-6 text-center text-sm text-slate-600">
      Les indicateurs du dashboard ne sont pas disponibles pour le moment.
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { RouterLink } from 'vue-router'
import { FolderKanban, ClipboardList, Users, Wallet, Sparkles } from 'lucide-vue-next'
import api from '@/services/api.js'
import { useGerantStore } from '@/modules/gerant/stores/gerantStore.js'
import { useAutoRefresh } from '@/composables/useAutoRefresh.js'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import AlertMessage from '@/components/ui/AlertMessage.vue'
import KpiCard from '@/components/ui/KpiCard.vue'
import DashboardChart from '@/components/ui/DashboardChart.vue'

const store = useGerantStore()
const { decisionDashboard, loading, error } = storeToRefs(store)
const { formatMontant } = store
const aiInsight = ref(null)
const aiError = ref('')
const aiLoading = ref(false)

const finance = computed(() => decisionDashboard.value?.finance || {})
const operationnel = computed(() => decisionDashboard.value?.operationnel || {})
const graphs = computed(() => decisionDashboard.value?.graphiques || {})
const team = computed(() => decisionDashboard.value?.utilisateurs || {})
const activities = computed(() => decisionDashboard.value?.activites_recentes || [])

const formatNombre = value => new Intl.NumberFormat('fr-FR').format(Number(value) || 0)
const montant = value => formatMontant(value ?? 0)
const clampPercent = value => Math.max(0, Math.min(100, Number(value) || 0))
const severityClass = severity => ({ high: 'bg-rose-baraka', medium: 'bg-amber-500', low: 'bg-slate-400' }[severity] || 'bg-slate-400')
const formatAnalysisDate = value => {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '—' : new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}

const normalizeAiInsight = (raw, generatedAt) => {
  const cleaned = String(raw || '').trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '')
  const parsed = JSON.parse(cleaned)
  const summary = typeof parsed.summary === 'string' ? parsed.summary.trim() : ''
  if (!summary) throw new Error('Résumé manquant')

  const attentionPoints = Array.isArray(parsed.attentionPoints)
    ? parsed.attentionPoints.slice(0, 3).flatMap(point => {
      if (!point || typeof point.title !== 'string' || typeof point.description !== 'string') return []
      return [{
        title: point.title.trim().slice(0, 100),
        description: point.description.trim().slice(0, 220),
        severity: ['high', 'medium', 'low'].includes(point.severity) ? point.severity : 'medium',
      }]
    })
    : []
  const recommendations = Array.isArray(parsed.recommendations)
    ? parsed.recommendations.filter(item => typeof item === 'string' && item.trim()).slice(0, 2).map(item => item.trim().slice(0, 220))
    : []

  return { summary: summary.slice(0, 600), attentionPoints, recommendations, generatedAt }
}

const projectStatusChart = computed(() => ({
  labels: (graphs.value.projets_statuts || []).map(row => row.label),
  datasets: [{
    label: 'Projets',
    data: (graphs.value.projets_statuts || []).map(row => row.total),
    backgroundColor: ['#94a3b8', '#00313C', '#D20C4F'],
    borderRadius: 6,
    maxBarThickness: 38,
  }],
}))

const beneficiaryTrend = computed(() => {
  const rows = graphs.value.beneficiaires_mensuels || []
  return {
    labels: rows.map(row => new Date(`${row.month}-01T00:00:00`).toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' })),
    datasets: [
      { label: 'Enregistrés', data: rows.map(row => row.identified), borderColor: '#00313C', backgroundColor: 'rgb(0 49 60 / 10%)', fill: true },
      { label: 'Prioritaires', data: rows.map(row => row.priority), borderColor: '#D20C4F', backgroundColor: 'transparent', fill: false },
      { label: 'Pris en charge', data: rows.map(row => row.aided), borderColor: '#16a34a', backgroundColor: 'transparent', fill: false },
    ],
  }
})

const zoneRows = computed(() => [...(graphs.value.beneficiaires_zones || [])].sort((a, b) => (b.total || 0) - (a.total || 0)).slice(0, 8))
const geographyChart = computed(() => ({
  labels: zoneRows.value.map(row => row.nom),
  datasets: [{ label: 'Bénéficiaires', data: zoneRows.value.map(row => row.total), backgroundColor: '#00313C', borderRadius: 5, maxBarThickness: 24 }],
}))
const geographySummary = computed(() => {
  const total = Number(operationnel.value.beneficiaires) || 0
  return zoneRows.value.slice(0, 4).map(row => ({
    nom: row.nom,
    pourcentage: total ? Math.round((Number(row.total || 0) / total) * 100) : 0,
  }))
})

const progressIndicators = computed(() => [
  {
    label: 'Prise en charge',
    value: operationnel.value.taux_prise_en_charge,
    available: Number(operationnel.value.beneficiaires) > 0,
    unavailableLabel: 'Aucun bénéficiaire',
    color: '#16a34a',
  },
  {
    label: 'Exécution budgétaire',
    value: finance.value.taux_execution,
    available: Number(finance.value.budget_total) > 0,
    unavailableLabel: 'Aucun budget',
    color: '#eab308',
  },
  {
    label: 'Progression des campagnes',
    value: operationnel.value.taux_realisation_campagnes,
    available: Number(operationnel.value.campagnes) > 0,
    unavailableLabel: 'Aucune campagne',
    color: '#f97316',
  },
])
const progressData = (value, color) => {
  const percent = clampPercent(value)
  return { labels: ['Réalisé', 'Restant'], datasets: [{ data: [percent, 100 - percent], backgroundColor: [color, `${color}35`], borderWidth: 0, hoverOffset: 0 }] }
}

const teamRoles = [
  { key: 'CHEF_PROJET', label: 'Chefs de projet' },
  { key: 'AGENT', label: 'Agents terrain' },
  { key: 'FINANCE', label: 'Finance' },
  { key: 'GERANT', label: 'Gérants' },
]
const roleLabel = role => ({ GERANT: 'Gérant', CHEF_PROJET: 'Chef de projet', AGENT: 'Agent terrain', FINANCE: 'Finance', SUPER_ADMIN: 'Super administrateur' }[role] || role || 'Rôle non défini')
const statusLabel = status => ({ ACTIVE: 'Actif', INVITED: 'Invité', EN_ATTENTE: 'En attente', EN_ATTENTE_ACTIVATION: 'À activer', SUSPENDED: 'Suspendu' }[status] || status || 'Inconnu')
const initials = person => `${person.first_name?.[0] || ''}${person.last_name?.[0] || ''}`.toUpperCase() || '?'
const activityLabel = label => ({
  'Beneficiaire enregistre': 'Nouveau bénéficiaire enregistré',
  'Campagne creee': 'Nouvelle campagne créée',
  'Aide humanitaire enregistree': 'Aide humanitaire enregistrée',
  'Depense validee': 'Dépense validée',
}[label] || label)
const formatDate = value => value ? new Intl.DateTimeFormat('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }).format(new Date(value)) : '—'

const chargerAnalyseIa = async () => {
  aiLoading.value = true
  aiError.value = ''
  try {
    const response = await api.post('/api/assistant/chat/', {
      question: `Produis une synthèse stratégique courte pour le gérant à partir uniquement des données réelles de son organisation présentes dans le contexte et les résultats d’outils Django. N’utilise aucune donnée d’une autre organisation et n’invente aucun fait. Ne répète pas les KPI simplement affichés dans le dashboard. Sélectionne uniquement les risques urgents, écarts importants ou actions utiles; ignore les informations sans impact décisionnel. Réponds uniquement en JSON valide, sans Markdown, au format exact : {"summary":"2 ou 3 phrases maximum sur la situation globale, sans liste brute de KPI","attentionPoints":[{"severity":"high|medium|low","title":"titre court","description":"fait vérifiable et concis"}],"recommendations":["action concrète liée à un point d’attention"]}. Maximum 3 attentionPoints, triés par priorité, et 2 recommandations. Si aucun risque important n’est établi, renvoie des tableaux vides et indique que la situation est stable. Si les données ne suffisent pas, indique exactement : Les données disponibles ne permettent pas encore d’identifier une priorité fiable. Dans ce cas, ne fabrique ni point d’attention ni recommandation. N’inclus aucune liste de projets, bénéficiaires, transactions ou moyens de paiement, aucun point fort, aucune source ni détail déjà visible ailleurs. Le gérant reste le décideur.`,
    })
    if ((response.data?.sources || []).some(source => String(source).includes('Système de secours'))) {
      throw new Error('L’analyse IA est indisponible pour le moment.')
    }
    aiInsight.value = normalizeAiInsight(response.data?.answer, response.data?.generated_at)
  } catch (err) {
    aiInsight.value = null
    aiError.value = err.response?.data?.detail || 'Analyse IA temporairement indisponible. Les indicateurs métier restent disponibles.'
  } finally {
    aiLoading.value = false
  }
}

useAutoRefresh(() => store.fetchAll())
onMounted(() => {
  if (localStorage.getItem('accessToken')) void chargerAnalyseIa()
})
</script>
