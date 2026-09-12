<template>
  <div class="min-h-screen bg-white flex justify-center items-start py-12 px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-4xl">
      <div class="p-6">
        <!-- Titre -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-amber-800">Créer projet</h1>
          <p class="text-sm text-gray-600 mt-1">
            Configurez les paramètres opérationnels, la cible de bénéficiaires et les zones de déploiement.
          </p>
        </div>

        <FormulaireProjet mode="creation" @submit="creerProjet" />
      </div>

      <!-- CHS -->
      <div class="mt-6 bg-white rounded-2xl border border-slate-200/60 p-6 flex gap-4 items-start">
      <div class="w-12 h-12 rounded-full bg-amber-800 flex items-center justify-center">
        <ShieldCheck class="text-white" :size="24" />
      </div>

      <div>
        <h3 class="text-sm font-bold uppercase text-amber-800">
          Standard de Responsabilité Humanitaire (CHS)
        </h3>

        <p class="text-xs text-gray-600 mt-1 leading-5">
          Toutes les campagnes créées sont soumises à l'audit de transparence des bénéficiaires
          et aux protocoles de sécurité des données sensibles de BarakaGive360.
        </p>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ShieldCheck } from "lucide-vue-next"
import FormulaireProjet from "@/modules/chef-projet/components/projets/FormulaireProjet.vue"

const creerProjet = (form) => {
  console.log(form)
  alert("Projet créé avec succès !")
}
</script>
