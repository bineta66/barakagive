<template>
  <div class="self-stretch p-8 inline-flex flex-col justify-start items-start gap-8">
    <div class="self-stretch inline-flex justify-between items-end">
      <div class="size- inline-flex flex-col justify-start items-start gap-2">
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="justify-center text-yellow-800 text-4xl font-bold font-['Inter'] leading-9">Justifications</div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="justify-center text-gray-800 text-sm font-normal font-['Inter'] leading-5 tracking-tight">Gestion des pièces justificatives des dépenses.</div>
        </div>
      </div>
    </div>

    <div class="self-stretch bg-white rounded-xl shadow-[0px_4px_20px_0px_rgba(0,0,0,0.05)] flex flex-col justify-start items-start overflow-hidden">
      <div class="self-stretch p-6 border-b border-indigo-50 inline-flex justify-between items-center">
        <div class="size- inline-flex flex-col justify-start items-start">
          <div class="w-52 justify-center text-yellow-800 text-lg font-semibold font-['Inter'] leading-7 tracking-wide">PIÈCES JUSTIFICATIVES</div>
        </div>
      </div>
      <div class="self-stretch flex flex-col justify-start items-start">
        <div class="self-stretch bg-white shadow-[0px_1px_4px_0px_rgba(0,0,0,0.05)] flex flex-col justify-start items-start">
          <div class="self-stretch inline-flex justify-center items-start">
            <div class="w-48 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-12 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Dépense</div>
            </div>
            <div class="w-40 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-20 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Type</div>
            </div>
            <div class="w-32 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-16 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Statut</div>
            </div>
            <div class="w-32 px-5 py-3 inline-flex flex-col justify-start items-start">
              <div class="w-16 justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Date</div>
            </div>
            <div class="w-32 px-5 py-3 inline-flex flex-col justify-end items-start">
              <div class="w-14 text-right justify-center text-gray-800 text-xs font-medium font-['Inter'] uppercase leading-4 tracking-wide">Actions</div>
            </div>
          </div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div v-for="depense in store.depenses" :key="depense.id" class="self-stretch border-t border-indigo-50 inline-flex justify-center items-center">
            <div class="w-48 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="self-stretch justify-center text-gray-800 text-xs font-semibold font-['Inter'] leading-5">{{ depense.reference }}</div>
            </div>
            <div class="w-40 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="justify-center text-gray-800 text-xs font-medium font-['Inter'] leading-5">{{ depense.justifications?.[0]?.type_fichier || '-' }}</div>
            </div>
            <div class="w-32 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="size- px-2 py-[2.50px] bg-white rounded-md outline outline-1 outline-offset-[-1px] outline-emerald-800/10 inline-flex justify-start items-start">
                <div class="justify-center text-emerald-800 text-[10px] font-bold font-['Inter'] leading-4 tracking-tight">{{ depense.justifications?.[0]?.statut || 'Aucun' }}</div>
              </div>
            </div>
            <div class="w-32 px-5 py-6 inline-flex flex-col justify-start items-start">
              <div class="justify-center text-gray-800 text-xs font-medium font-['Inter'] leading-5">{{ depense.justifications?.[0]?.created_at || '-' }}</div>
            </div>
            <div class="w-24 pl-5 flex justify-end items-start gap-1">
              <div v-if="depense.justifications && depense.justifications.length > 0" class="size-8 bg-blue-600 rounded-md shadow-[0px_1px_2px_0px_rgba(0,0,0,0.05)] flex justify-center items-center" @click="uploadJustification(depense)">
                <div class="size- pt-0.5 pb-[2.75px] inline-flex flex-col justify-start items-start">
                  <div class="w-2 h-2.5 relative">
                    <div class="w-2 h-2.5 left-0 top-0 absolute bg-white"></div>
                  </div>
                </div>
              </div>
              <div v-else class="size-8 bg-green-600 rounded-md shadow-[0px_1px_2px_0px_rgba(0,0,0,0.05)] flex justify-center items-center" @click="uploadJustification(depense)">
                <div class="size- pt-0.5 pb-[2.75px] inline-flex flex-col justify-start items-start">
                  <div class="w-2 h-2.5 relative">
                    <div class="w-2 h-2.5 left-0 top-0 absolute bg-white"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <JustificationModal
      v-if="modalOpen"
      :ouvert="modalOpen"
      :depense="selectedDepense"
      @fermer="modalOpen = false"
      @save="saveJustification"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'
import JustificationModal from '@/modules/finance/components/justifications/JustificationModal.vue'

const store = useFinanceStore()
const modalOpen = ref(false)
const selectedDepense = ref(null)

const uploadJustification = (depense) => {
  selectedDepense.value = depense
  modalOpen.value = true
}

const saveJustification = async (data) => {
  try {
    await store.uploadJustification(data.depenseId, data.file)
    modalOpen.value = false
  } catch (error) {
    console.error('Erreur:', error)
  }
}

onMounted(() => {
  store.fetchExpenses()
})
</script>