<template>
  <div class="min-h-screen bg-white flex justify-center items-start py-12 px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-4xl">
      <div class="p-6">
        <div class="mb-6">
          <h1 class="text-3xl font-bold text-or">Détail de la zone</h1>
          <p class="text-sm text-gray-600 mt-1">
            Synthèse et bénéficiaires de la zone sélectionnée.
          </p>
        </div>

        <ZoneSummaryCard :synthese="synthese" />

        <div class="mt-6">
          <UrgentBeneficiaries :beneficiaires="beneficiairesUrgents" />
        </div>
      </div>
    </div>
  </div>

  <OperationalOrbitalIA />
</template>

<script setup>
import { useBeneficiaires } from "@/composables/useBeneficiaires.js"
import ZoneSummaryCard from "@/modules/chef-projet/components/beneficiaires/ZoneSummaryCard.vue"
import UrgentBeneficiaries from "@/modules/chef-projet/components/beneficiaires/UrgentBeneficiaries.vue"
import OperationalOrbitalIA from "@/components/ia/OperationalOrbitalIA.vue"

const {
  zoneSelectionnee,
  regionSelectionnee,
  synthese,
  beneficiairesUrgents,
} = useBeneficiaires()
</script>


