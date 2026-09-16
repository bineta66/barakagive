<template>
  <div class="flex-1 min-w-0">
    <div class="self-stretch h-[626px] min-h-[580px] relative bg-white">
      <div class="w-[608.66px] pb-3 left-[16px] top-[16px] absolute bg-white rounded-xl shadow-xs-[0px_4px_20px_0px_rgba(0,0,0,0.05)] inline-flex justify-between items-center">
        <div class="size- flex justify-start items-center gap-2">
          <div class="size-3 bg-bleu-nuit"></div>
          <div class="size- inline-flex flex-col justify-start items-start">
            <div class="justify-center text-slate-900 text-base font-semibold font-['Poppins'] leading-6">Cartographie Opérationnelle // Sénégal</div>
          </div>
        </div>
        <div class="size- inline-flex flex-col justify-start items-start">
          <div class="justify-center text-gray-800 text-xs font-normal font-['Poppins'] leading-4">COORDS : WGS84 EPSG:4326</div>
        </div>
      </div>
      <div class="w-[608.66px] pt-3 left-[16px] top-[512px] absolute inline-flex flex-col justify-start items-start">
        <div class="self-stretch h-11 pt-3 bg-white flex flex-col justify-center items-start gap-3">
          <div class="w-[646.66px] h-11 relative">
            <div class="size-3 left-[167.08px] top-[1px] absolute"></div>
            <div class="size- left-0 top-[30px] absolute inline-flex justify-start items-center gap-1">
              <div class="size-3 bg-neutral-300"></div>
              <div class="size- inline-flex flex-col justify-start items-start">
                <div class="justify-center text-gray-800 text-xs font-normal font-['Poppins'] leading-4 tracking-wide">Zone sans bénéficiaire</div>
              </div>
            </div>
          </div>
          <div class="size- flex flex-col justify-start items-start">
            <div class="justify-center text-gray-800 text-xs font-normal font-['Poppins'] leading-4">Dernière synchro GPS : 10:42:19 UTC</div>
          </div>
        </div>
      </div>
      <div class="w-[608.66px] h-[460px] p-2 left-[16px] top-[52px] absolute bg-neutral-200 inline-flex justify-center items-center overflow-hidden">
        <img class="w-[607px] h-96" src="https://placehold.co/607x436" />
        <div class="size- px-3 py-1 left-[12px] top-[12px] absolute bg-white/90 flex justify-start items-center gap-1">
          <div class="size-2 bg-bleu-nuit"></div>
          <div class="size- inline-flex flex-col justify-start items-start">
            <div class="justify-center text-gray-800 text-xs font-normal font-['Poppins'] leading-4 tracking-wide">FLUX EN DIRECT // SENEGAL OPERATIONS</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  regionSelectionnee: String,
  zoneSelectionnee: String,
  regions: Array,
})

const emit = defineEmits(["update:regionSelectionnee", "update:zoneSelectionnee"])

const selectRegion = (region) => {
  if (props.regionSelectionnee === region) {
    emit("update:regionSelectionnee", "")
    emit("update:zoneSelectionnee", "")
  } else {
    emit("update:regionSelectionnee", region)
    emit("update:zoneSelectionnee", "")
  }
}

const clearRegion = () => {
  emit("update:regionSelectionnee", "")
  emit("update:zoneSelectionnee", "")
}
</script>


