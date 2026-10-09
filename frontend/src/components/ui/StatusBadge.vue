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
      return "bg-emerald-600 text-white";
    case "TRIAL":
    case "Essai":
    case "En essai":
      return "bg-amber-100 text-amber-800";
    case "EXPIRED":
    case "Expiré":
    case "Expirée":
      return "bg-red-50 text-red-700";
    case "ANNULEE":
    case "Annulée":
    case "CANCELLED":
    case "Annulé":
      return "bg-red-100 text-red-800";
    case "En cours":
    case "EN COURS":
    case "EN_COURS":
    case "Budgété":
    case "Budgétisé":
    case "Élevé":
    case "Élevée":
      return "bg-bleu-nuit text-white";
    case "Planifié":
    case "PLANIFIÉ":
    case "Planifiée":
    case "PLANIFIÉE":
    case "PLANIFIER":
    case "EN_ATTENTE":
    case "À budgétiser":
      return "bg-bleu-nuit text-white";
    case "Terminé":
    case "TERMINÉ":
    case "Terminée":
    case "TERMINÉE":
    case "TERMINE":
    case "Archivé":
    case "Archivée":
    case "ARCHIVE":
      return "bg-gray-500 text-white";
    case "BROUILLON":
    case "Brouillon":
      return "bg-amber-100 text-amber-800";
    case "Inactif":
    case "INACTIF":
    case "SUSPENDED":
    case "Suspendu":
    case "En attente":
    case "INVITED":
    case "Invitation envoyée":
    case "Modéré":
    case "Modérée":
      return "bg-gray-400 text-white";
    case "Critique":
    case "CRITIQUE":
      return "bg-red-600 text-white";
    default:
      return "bg-gray-400 text-white";
  }
});
</script>
