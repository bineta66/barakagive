<template>
  <div class="self-stretch p-8 inline-flex flex-col justify-start items-start gap-8">
    <div class="self-stretch inline-flex justify-between items-end">
      <div class="size- inline-flex flex-col justify-start items-start gap-2">
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="justify-center text-yellow-800 text-4xl font-bold font-['Inter'] leading-9">Tableau de Bord Financier</div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="justify-center text-gray-800 text-sm font-normal font-['Inter'] leading-5 tracking-tight">Indicateurs financiers en temps réel pour vos projets assignés.</div>
        </div>
      </div>
    </div>

    <div class="self-stretch inline-flex justify-center items-start gap-6">
      <div class="flex-1 p-6 bg-white rounded-xl shadow-[0px_4px_20px_0px_rgba(0,0,0,0.05)] border-l-4 border-white inline-flex flex-col justify-start items-start gap-1">
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="self-stretch justify-center text-gray-500 text-xs font-semibold font-['Inter'] uppercase leading-4 tracking-wide">Budget total</div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="self-stretch justify-center text-slate-900 text-2xl font-bold font-['Inter'] leading-9">{{ formatMontant(store.dashboard?.budget_total) }} FCFA</div>
        </div>
      </div>
      <div class="flex-1 p-6 bg-white rounded-xl shadow-[0px_4px_20px_0px_rgba(0,0,0,0.05)] border-l-4 border-white inline-flex flex-col justify-start items-start gap-1">
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="self-stretch justify-center text-gray-500 text-xs font-semibold font-['Inter'] uppercase leading-4 tracking-wide">Dons reçus</div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="self-stretch justify-center text-slate-900 text-2xl font-bold font-['Inter'] leading-9">{{ formatMontant(store.dashboard?.dons_reçus) }} FCFA</div>
        </div>
      </div>
      <div class="flex-1 p-6 bg-white rounded-xl shadow-[0px_4px_20px_0px_rgba(0,0,0,0.05)] border-l-4 border-white inline-flex flex-col justify-start items-start gap-1">
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="self-stretch justify-center text-gray-500 text-xs font-semibold font-['Inter'] uppercase leading-4 tracking-wide">Dépenses totales</div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="self-stretch justify-center text-slate-900 text-2xl font-bold font-['Inter'] leading-9">{{ formatMontant(store.dashboard?.depenses_totales) }} FCFA</div>
        </div>
      </div>
      <div class="flex-1 p-6 bg-white rounded-xl shadow-[0px_4px_20px_0px_rgba(0,0,0,0.05)] border-l-4 border-white inline-flex flex-col justify-start items-start gap-1">
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="self-stretch justify-center text-gray-500 text-xs font-semibold font-['Inter'] uppercase leading-4 tracking-wide">Solde disponible</div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="self-stretch justify-center text-slate-900 text-2xl font-bold font-['Inter'] leading-9">{{ formatMontant(store.dashboard?.solde_disponible) }} FCFA</div>
        </div>
      </div>
    </div>

    <div class="self-stretch inline-flex justify-center items-start gap-6">
      <div class="flex-1 p-6 bg-white rounded-xl shadow-[0px_4px_20px_0px_rgba(0,0,0,0.05)] border-l-4 border-white inline-flex flex-col justify-start items-start gap-1">
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="self-stretch justify-center text-gray-500 text-xs font-semibold font-['Inter'] uppercase leading-4 tracking-wide">Taux d'exécution</div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="self-stretch justify-center text-slate-900 text-2xl font-bold font-['Inter'] leading-9">{{ store.dashboard?.taux_execution }}%</div>
        </div>
      </div>
    </div>

    <div class="self-stretch bg-white rounded-xl shadow-[0px_4px_20px_0px_rgba(0,0,0,0.05)] flex flex-col justify-start items-start overflow-hidden">
      <div class="self-stretch p-6 border-b border-indigo-50 inline-flex justify-between items-center">
        <div class="size- inline-flex flex-col justify-start items-start">
          <div class="w-52 justify-center text-yellow-800 text-lg font-semibold font-['Inter'] leading-7 tracking-wide">DERNIÈRES TRANSACTIONS</div>
        </div>
      </div>
      <div class="self-stretch flex flex-col justify-start items-start">
        <div class="self-stretch bg-white shadow-[0px_1px_4px_0px_rgba(0,0,0,0.05)] flex flex-col justify-start items-start">
          <div class="self-stretch inline-flex justify-center items-start">
            <div class="w-32 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-12 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Type</div>
            </div>
            <div class="w-40 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-20 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Référence</div>
            </div>
            <div class="w-48 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-24 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Description</div>
            </div>
            <div class="w-40 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-20 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Montant</div>
            </div>
            <div class="w-32 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-16 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Date</div>
            </div>
          </div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div v-for="item in recentTransactions" :key="item.id" class="self-stretch border-t border-indigo-50 inline-flex justify-center items-center">
            <div class="w-32 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="justify-center text-gray-800 text-xs font-semibold font-['Inter'] leading-5">{{ item.type }}</div>
            </div>
            <div class="w-40 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="justify-center text-gray-800 text-xs font-medium font-['Inter'] leading-5">{{ item.reference }}</div>
            </div>
            <div class="w-48 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="justify-center text-gray-800 text-xs font-medium font-['Inter'] leading-5">{{ item.description }}</div>
            </div>
            <div class="w-40 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="justify-center" :class="item.type === 'Dépense' ? 'text-red-700' : 'text-emerald-800'">{{ formatMontant(item.montant) }}</div>
            </div>
            <div class="w-32 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="justify-center text-gray-800 text-xs font-medium font-['Inter'] leading-5">{{ item.date }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'

const store = useFinanceStore()

const recentTransactions = computed(() => {
  const transactions = []
  
  store.dons.slice(0, 5).forEach(don => {
    transactions.push({
      id: don.id,
      type: 'Don',
      reference: don.reference,
      description: don.bailleur,
      montant: don.montant,
      date: don.date,
    })
  })
  
  store.depenses.slice(0, 5).forEach(depense => {
    transactions.push({
      id: depense.id,
      type: 'Dépense',
      reference: depense.reference,
      description: depense.libelle || depense.categorie,
      montant: depense.montant,
      date: depense.date,
    })
  })
  
  return transactions.sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 10)
})

const formatMontant = (value) => {
  return Number(value || 0).toLocaleString('fr-FR')
}

onMounted(() => {
  store.refreshAll()
})
</script>