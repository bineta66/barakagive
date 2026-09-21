<template>
  <div class="self-stretch p-8 inline-flex flex-col justify-start items-start gap-8">
    <div class="self-stretch inline-flex justify-between items-end">
      <div class="size- inline-flex flex-col justify-start items-start gap-2">
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="justify-center text-yellow-800 text-4xl font-bold font-['Inter'] leading-9">Dépenses</div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="justify-center text-gray-800 text-sm font-normal font-['Inter'] leading-5 tracking-tight">Gestion des dépenses et justificatifs.</div>
        </div>
      </div>
      <div class="h-11 px-6 bg-slate-900 rounded-md shadow-[0px_1px_2px_0px_rgba(0,0,0,0.05)] flex justify-start items-center gap-2" @click="modalOpen = true">
        <div class="size- pt-[2.50px] pb-1 inline-flex flex-col justify-start items-start">
          <div class="w-2.5 h-3 relative">
            <div class="size-2.5 left-[0.38px] top-[1.13px] absolute bg-white"></div>
          </div>
        </div>
        <div class="text-center justify-center text-white text-sm font-semibold font-['Inter'] leading-5 tracking-tight">Ajouter dépense</div>
      </div>
    </div>

    <div class="self-stretch bg-white rounded-xl shadow-[0px_4px_20px_0px_rgba(0,0,0,0.05)] flex flex-col justify-start items-start overflow-hidden">
      <div class="self-stretch p-6 border-b border-indigo-50 inline-flex justify-between items-center">
        <div class="size- inline-flex flex-col justify-start items-start">
          <div class="w-52 justify-center text-yellow-800 text-lg font-semibold font-['Inter'] leading-7 tracking-wide">LISTE DES DÉPENSES</div>
        </div>
        <div class="size- flex justify-start items-center gap-4">
          <div class="w-36 h-5 relative">
            <div class="left-0 top-[-1px] absolute justify-center text-gray-800 text-xs font-normal font-['Inter'] leading-5">{{ store.depenses.length }} dépenses répertoriées</div>
          </div>
        </div>
      </div>
      <div class="self-stretch flex flex-col justify-start items-start">
        <div class="self-stretch bg-white shadow-[0px_1px_4px_0px_rgba(0,0,0,0.05)] flex flex-col justify-start items-start">
          <div class="self-stretch inline-flex justify-center items-start">
            <div class="w-32 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-12 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Référence</div>
            </div>
            <div class="w-48 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-24 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Projet</div>
            </div>
            <div class="w-40 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-20 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Catégorie</div>
            </div>
            <div class="w-40 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-20 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Montant</div>
            </div>
            <div class="w-32 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-16 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Date</div>
            </div>
            <div class="w-32 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-16 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Statut</div>
            </div>
            <div class="w-40 px-5 py-3 inline-flex flex-col justify-end items-start">
              <div class="w-20 text-right justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Justificatif</div>
            </div>
          </div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div v-for="depense in store.depenses" :key="depense.id" class="self-stretch border-t border-indigo-50 inline-flex justify-center items-center">
            <div class="w-32 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="self-stretch justify-center text-gray-800 text-xs font-semibold font-['Inter'] leading-5">{{ depense.reference }}</div>
            </div>
            <div class="w-48 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="justify-center text-gray-800 text-xs font-medium font-['Inter'] leading-5">{{ depense.projet_nom }}</div>
            </div>
            <div class="w-40 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="justify-center text-gray-800 text-xs font-medium font-['Inter'] leading-5">{{ depense.categorie }}</div>
            </div>
            <div class="w-40 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="justify-center text-red-700 text-xs font-medium font-['Inter'] leading-5">{{ formatMontant(depense.montant) }}</div>
            </div>
            <div class="w-32 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="justify-center text-gray-800 text-xs font-medium font-['Inter'] leading-5">{{ depense.date }}</div>
            </div>
            <div class="w-32 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="size- px-2 py-[2.50px] bg-white rounded-md outline outline-1 outline-offset-[-1px] outline-emerald-800/10 inline-flex justify-start items-start">
                <div class="justify-center text-emerald-800 text-[10px] font-bold font-['Inter'] leading-4 tracking-tight">{{ depense.statut }}</div>
              </div>
            </div>
            <div class="w-40 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div v-if="depense.justifications && depense.justifications.length > 0" class="justify-center text-emerald-800 text-xs font-medium font-['Inter'] leading-5">Oui</div>
              <div v-else class="justify-center text-red-700 text-xs font-medium font-['Inter'] leading-5">Non</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <DepenseFormModal
      v-if="modalOpen"
      :ouvert="modalOpen"
      @fermer="modalOpen = false"
      @save="saveDepense"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'
import DepenseFormModal from '@/modules/finance/components/depenses/DepenseFormModal.vue'

const store = useFinanceStore()
const modalOpen = ref(false)

const formatMontant = (value) => {
  return Number(value || 0).toLocaleString('fr-FR')
}

const saveDepense = async (data) => {
  try {
    await store.createExpense(data)
    modalOpen.value = false
  } catch (error) {
    console.error('Erreur:', error)
  }
}

onMounted(() => {
  store.fetchExpenses()
})
</script>