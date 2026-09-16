<template>
  <div class="self-stretch p-6 bg-white inline-flex flex-col justify-between items-start">
    <!-- En-tête -->
    <div class="self-stretch flex flex-col justify-start items-start gap-4">
      <div class="self-stretch pb-3 inline-flex justify-between items-center">
        <div class="text-slate-700 text-sm font-bold uppercase leading-5 tracking-wide">
          ACTIVITE RECENTE
        </div>
        <div class="text-slate-400 text-xs font-medium leading-4">
          Temps réel
        </div>
      </div>

      <!-- Activités -->
      <div class="self-stretch flex flex-col justify-start items-start gap-4">
        <div
          v-for="activite in activites"
          :key="activite.id"
          class="self-stretch inline-flex justify-start items-start"
        >
          <div class="w-2 h-3.5 pt-1.5 flex justify-start items-start">
            <div class="size-2 rounded-full" :class="activite.couleur"></div>
          </div>
          <div class="pl-3 inline-flex flex-col justify-start items-start">
            <div class="flex flex-col gap-0.5">
              <div class="text-slate-800 text-xs font-medium">
                {{ activite.titre }}
                <span class="text-slate-900 font-medium">{{ activite.titreGras }}</span>
              </div>
              <div class="text-slate-400 text-xs">
                {{ activite.meta }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="self-stretch pt-8 flex flex-col justify-start items-start">
      <div class="self-stretch inline-flex justify-between items-center">
        <div class="text-bleu-nuit text-xs font-semibold leading-4">
          Voir tout l'historique d'audit
        </div>
        <div class="w-2 h-0.5 bg-bleu-nuit"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
const activites = [
  {
    id: 1,
    couleur: "bg-bleu-nuit",
    titre: "Déploiement du projet ",
    titreGras: "Eau & Santé Sahel",
    meta: "Par Dr. Ousmane Kane • Il y a 25 min",
  },
  {
    id: 2,
    couleur: "bg-emerald-600",
    titre: "Enregistrement de ",
    titreGras: "320 bénéficiaires",
    meta: "validé • Zone Sud-Mali • Il y a 1h 10",
  },
  {
    id: 3,
    couleur: "bg-bleu-nuit",
    titre: "Nouvel utilisateur accrédité : ",
    titreGras: "Sarah B. (Coordinatrice)",
    meta: "Rôle : Gestionnaire de camp • Il y a 3h",
  },
  {
    id: 4,
    couleur: "bg-slate-200",
    titre: "Clôture administrative : ",
    titreGras: "Mission Urgence Famine Tchad",
    meta: "Rapport d'audit archivé • Hier à 17:40",
  },
  {
    id: 5,
    couleur: "bg-bleu-nuit",
    titre: "Subvention bailleur ",
    titreGras: "USAID/BHA réceptionnée",
    meta: "Finances • Hier à 11:15",
  },
]
</script>