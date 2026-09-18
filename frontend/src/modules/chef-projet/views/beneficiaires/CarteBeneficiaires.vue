<template>
  <div class="min-h-screen bg-white flex justify-center items-start py-12 px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-4xl">
      <div class="p-6">
        <BeneficiaireHeader />
        <div class="mt-6">
          <SenegalMap
            :region-selectionnee="regionSelectionnee"
            :zone-selectionnee="zoneSelectionnee"
            :regions="regions"
            @update:regionSelectionnee="selectionnerRegion"
            @update:zoneSelectionnee="selectionnerZone"
          />
        </div>
        <div class="mt-6">
          <ZoneSummaryCard :synthese="synthese" />
        </div>
      </div>
    </div>
  </div>

  <OperationalOrbitalIA />
</template>

<script setup>
import { useBeneficiaires } from "@/composables/useBeneficiaires.js"
import BeneficiaireHeader from "@/modules/chef-projet/components/beneficiaires/BeneficiaireHeader.vue"
import SenegalMap from "@/modules/chef-projet/components/beneficiaires/SenegalMap.vue"
import ZoneSummaryCard from "@/modules/chef-projet/components/beneficiaires/ZoneSummaryCard.vue"
import OperationalOrbitalIA from "@/components/ia/OperationalOrbitalIA.vue"

const {
  regions,
  regionSelectionnee,
  zoneSelectionnee,
  synthese,
  selectionnerRegion,
  selectionnerZone,
} = useBeneficiaires()
</script>

