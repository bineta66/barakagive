<template>
  <main class="min-h-screen space-y-6 bg-white p-6">
    <RouterLink :to="{ name: 'finance-budgets' }" class="text-sm font-medium text-bleu-nuit hover:underline">← Retour aux budgets</RouterLink>

    <LoadingSpinner v-if="store.loading" message="Chargement du budget..." />
    <section v-else-if="budget" class="space-y-6">
      <header class="flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-bold text-bleu-nuit">{{ budget.projet_nom }}</h1>
          <p class="mt-1 text-sm text-slate-500">Détail du budget du projet</p>
        </div>
        <BoutonPrimary @click="showChoices = true"><Plus class="h-4 w-4" /> Ajouter</BoutonPrimary>
      </header>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <article v-for="item in details" :key="item.label" class="rounded-xl border border-slate-200/60 bg-white p-4 shadow-xs">
          <p class="text-xs font-bold uppercase text-slate-500">{{ item.label }}</p>
          <p class="mt-2 font-semibold text-slate-900">{{ item.value }}</p>
        </article>
      </div>

      <section class="rounded-xl border border-slate-200/60 p-5">
        <h2 class="font-bold text-slate-900">Ajouter au budget</h2>
        <p class="mt-1 text-sm text-slate-500">Choisissez le type d’opération à enregistrer.</p>
        <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <button v-for="choice in choices" :key="choice.label" class="rounded-lg border border-slate-200 p-4 text-left transition hover:border-bleu-nuit hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30" @click="goTo(choice.route)">
            <component :is="choice.icon" class="mb-2 h-5 w-5 text-bleu-nuit" />
            <span class="block font-semibold text-slate-900">{{ choice.label }}</span>
            <span class="mt-1 block text-xs text-slate-500">{{ choice.description }}</span>
          </button>
        </div>
      </section>
    </section>
    <p v-else class="rounded-lg border border-slate-200 p-5 text-sm text-slate-600">Ce budget est introuvable. <RouterLink :to="{ name: 'finance-budgets' }" class="text-bleu-nuit underline">Revenir à la liste</RouterLink></p>

    <Teleport to="body">
      <div v-if="showChoices" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showChoices = false">
        <section class="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl" role="dialog" aria-modal="true" aria-labelledby="add-choice-title">
          <div class="flex items-start justify-between gap-4">
            <div><h2 id="add-choice-title" class="text-lg font-bold text-slate-900">Que souhaitez-vous ajouter ?</h2><p class="mt-1 text-sm text-slate-500">Choisissez une opération pour ce budget.</p></div>
            <button class="rounded-lg p-2 text-slate-500 hover:bg-slate-100" aria-label="Fermer" @click="showChoices = false">×</button>
          </div>
          <div class="mt-5 grid gap-2 sm:grid-cols-2">
            <button v-for="choice in choices" :key="choice.label" class="flex items-center gap-3 rounded-lg border border-slate-200 p-3 text-left hover:bg-slate-50" @click="goTo(choice.route)"><component :is="choice.icon" class="h-5 w-5 text-bleu-nuit" /><span class="font-medium text-slate-800">{{ choice.label }}</span></button>
          </div>
        </section>
      </div>
    </Teleport>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, HandCoins, Landmark, Receipt, ListChecks } from 'lucide-vue-next'
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const store = useFinanceStore()
const showChoices = ref(false)
const budget = computed(() => store.budgets.find((item) => String(item.id) === String(route.params.id)))
const money = (value) => `${Number(value || 0).toLocaleString('fr-FR')} FCFA`
const details = computed(() => budget.value ? [
  { label: 'Montant du budget', value: money(budget.value.montant) },
  { label: 'Solde disponible', value: money(budget.value.solde) },
  { label: 'Source', value: budget.value.source_financement || '—' },
  { label: 'Taux d’exécution', value: `${budget.value.taux_execution || 0}%` },
  { label: 'Statut', value: budget.value.statut || '—' },
] : [])
const choices = [
  { label: 'Don', description: 'Enregistrer un don reçu', icon: HandCoins, route: 'finance-dons' },
  { label: 'Financement', description: 'Consulter les financements', icon: Landmark, route: 'finance-financements' },
  { label: 'Dépense', description: 'Enregistrer une dépense', icon: Receipt, route: 'finance-depenses' },
  { label: 'Ligne budgétaire', description: 'Consulter les lignes du budget', icon: ListChecks, route: 'finance-lignes-budgetaires' },
]
function goTo(name) {
  showChoices.value = false
  router.push({ name, query: { budget: String(route.params.id) } })
}
onMounted(async () => {
  if (!store.budgets.length) await store.fetchBudgets()
})
</script>
