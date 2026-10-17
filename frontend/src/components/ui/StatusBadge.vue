<template>
  <span
    class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium font-poppins whitespace-nowrap"
    :class="badgeClass"
  >
    <slot />
  </span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  statut: {
    type: String,
    required: true,
  },
});

const badgeClass = computed(() => {
  const s = props.statut;
  switch (s) {
    case "Actif":
    case "ACTIF":
    case "ACTIVE":
    case "Reçu":
      return "bg-bleu-accent/15 text-bleu-accent border border-bleu-accent/30";
    case "TRIAL":
    case "Essai":
    case "En essai":
    case "BROUILLON":
    case "Brouillon":
    case "EN_ATTENTE":
    case "En attente":
    case "À budgétiser":
    case "INVITED":
    case "Invitation envoyée":
      return "bg-bleu-nuit/10 text-bleu-nuit border border-slate-200";
    case "EXPIRED":
    case "Expiré":
    case "Expirée":
    case "ANNULEE":
    case "Annulée":
    case "CANCELLED":
    case "Annulé":
    case "Critique":
    case "CRITIQUE":
    case "REJETEE":
    case "Rejetée":
      return "bg-rose-baraka/15 text-rose-baraka border border-rose-baraka/30";
    case "En cours":
    case "EN COURS":
    case "EN_COURS":
    case "Budgété":
    case "Budgétisé":
    case "Planifié":
    case "PLANIFIÉ":
    case "Planifiée":
    case "PLANIFIÉE":
    case "PLANIFIER":
    case "Élevé":
    case "Élevée":
      return "bg-bleu-nuit text-white";
    case "Terminé":
    case "TERMINÉ":
    case "Terminée":
    case "TERMINÉE":
    case "TERMINE":
    case "Archivé":
    case "Archivée":
    case "ARCHIVE":
    case "Inactif":
    case "INACTIF":
    case "SUSPENDED":
    case "Suspendu":
    case "Modéré":
    case "Modérée":
      return "bg-slate-100 text-slate-700 border border-slate-200";
    default:
      return "bg-slate-100 text-slate-700 border border-slate-200";
  }
});
</script>
