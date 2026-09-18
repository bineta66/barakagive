<template>
  <div class="mx-auto max-w-3xl space-y-6 px-4 py-5 md:px-6">
    <RouterLink :to="`/agent/campagnes/${beneficiary?.campagne?.id || ''}/beneficiaires`" class="text-sm font-semibold text-amber-700">Retour aux bénéficiaires</RouterLink>
    <section v-if="beneficiary" class="rounded-2xl border border-gray-200 bg-white p-6">
      <div class="flex items-start justify-between gap-4"><div><p class="text-xs font-bold uppercase tracking-wide text-slate-400">Bénéficiaire</p><h1 class="mt-1 text-2xl font-bold text-slate-900">{{ beneficiary.prenom }} {{ beneficiary.nom }}</h1></div><span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">{{ beneficiary.sync_status || "Synchronisé" }}</span></div>
      <dl class="mt-8 grid gap-5 border-t border-slate-100 pt-6 sm:grid-cols-2"><div><dt class="text-xs font-bold uppercase text-slate-400">Téléphone</dt><dd class="mt-1 text-sm">{{ beneficiary.telephone || "-" }}</dd></div><div><dt class="text-xs font-bold uppercase text-slate-400">Sexe</dt><dd class="mt-1 text-sm">{{ beneficiary.sexe || "-" }}</dd></div><div><dt class="text-xs font-bold uppercase text-slate-400">Date de naissance</dt><dd class="mt-1 text-sm">{{ beneficiary.date_naissance || "-" }}</dd></div><div><dt class="text-xs font-bold uppercase text-slate-400">Localité</dt><dd class="mt-1 text-sm">{{ beneficiary.zone?.nom || "-" }}</dd></div><div><dt class="text-xs font-bold uppercase text-slate-400">Latitude</dt><dd class="mt-1 text-sm">{{ beneficiary.latitude || "-" }}</dd></div><div><dt class="text-xs font-bold uppercase text-slate-400">Longitude</dt><dd class="mt-1 text-sm">{{ beneficiary.longitude || "-" }}</dd></div></dl>
      <div v-if="beneficiary.responses?.length" class="mt-8 border-t border-slate-100 pt-6"><h2 class="font-bold text-slate-900">Réponses du formulaire</h2><dl class="mt-4 space-y-3"><div v-for="response in beneficiary.responses" :key="response.id" class="flex justify-between gap-4 text-sm"><dt class="text-slate-500">{{ response.question?.label }}</dt><dd class="font-medium text-slate-900">{{ response.value_text || response.value_number || response.value_boolean || response.value_date || "-" }}</dd></div></dl></div>
    </section>
    <div v-else-if="!loading" class="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-slate-500">Bénéficiaire introuvable.</div>
  </div>
</template>
<script setup>
import { onMounted, ref } from "vue"
import { RouterLink, useRoute } from "vue-router"
import { useBeneficiaryStore } from "@/stores/beneficiary.js"
const route = useRoute()
const store = useBeneficiaryStore()
const beneficiary = ref(null)
const loading = ref(true)
onMounted(async () => { try { beneficiary.value = await store.fetchBeneficiary(route.params.id) } finally { loading.value = false } })
</script>

