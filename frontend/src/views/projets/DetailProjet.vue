<template>
  <div class="p-6 bg-white min-h-screen">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-amber-800">Détail du projet</h1>
      <p class="text-sm text-gray-600 mt-1">
        Consultez les informations complètes du projet.
      </p>
    </div>

    <CarteProjet :projet="projet" />

    <div class="mt-6 bg-white rounded-2xl border border-slate-200/60 p-6">
      <h3 class="text-sm font-bold uppercase text-amber-800 mb-4">
        Informations complémentaires
      </h3>
      <p class="text-sm text-gray-700 leading-6">
        Cette vue sera enrichie prochainement avec les bénéficiaires, les zones de déploiement,
        les rapports d'exécution et les documents joints.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import CarteProjet from "@/components/projets/CarteProjet.vue"

const projet = ref({
  nom: "Secours Alimentaire & Nutrition d'Urgence",
  code: "PRJ-2025-089",
  responsable: "Marie Dupont",
  zone: "Dakar, Sénégal",
  budget: "340 000 €",
  debut: "15 Jan 2025",
  fin: "30 Nov 2025",
  statut: "En cours",
  description:
    "Projet de distribution alimentaire et de nutrition pour les familles vulnérables dans la région de Dakar.",
})
</script>
