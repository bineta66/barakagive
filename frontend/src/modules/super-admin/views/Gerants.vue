<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Liste des Gérants</h1>
        <p class="text-sm text-slate-500 mt-1">
          Tous les gérunts des ONG enregistrées sur la plateforme
        </p>
      </div>
    </div>

    <!-- Alert Error -->
    <AlertMessage
      v-if="error"
      type="error"
      :message="error"
      :dismissible="true"
      @dismiss="error = null"
    />

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Chargement des gérunts..." />

    <!-- Table -->
    <div
      v-else
      class="bg-white border border-slate-200/60 rounded-xl overflow-hidden"
    >
      <table class="w-full">
        <thead class="bg-slate-50 border-b border-slate-200">
          <tr>
            <th
              class="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase"
            >
              Gérant
            </th>
            <th
              class="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase"
            >
              Contact
            </th>
            <th
              class="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase"
            >
              ONG
            </th>
            <th
              class="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase"
            >
              Région
            </th>
            <th
              class="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase"
            >
              Statut ONG
            </th>
            <th
              class="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase"
            >
              Statut Compte
            </th>
            <th
              class="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase"
            >
              Inscrit le
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="gerant in store.gerants"
            :key="gerant.id"
            class="hover:bg-slate-50/50"
          >
            <!-- Gérant -->
            <td class="px-4 py-3">
              <div class="text-sm font-medium text-slate-900">
                {{ gerant.first_name || "-" }} {{ gerant.last_name || "-" }}
              </div>
            </td>
            <!-- Contact -->
            <td class="px-4 py-3">
              <div class="text-sm text-slate-600">{{ gerant.email }}</div>
              <div class="text-xs text-slate-400">
                {{ gerant.phone || "-" }}
              </div>
            </td>
            <!-- ONG -->
            <td class="px-4 py-3">
              <div class="text-sm font-medium text-slate-900">
                {{ gerant.organization?.name || "-" }}
              </div>
              <div v-if="gerant.organization?.acronym" class="text-xs text-bleu-nuit">
                {{ gerant.organization.acronym }}
              </div>
            </td>
            <!-- Région -->
            <td class="px-4 py-3 text-sm text-slate-600">
              {{ gerant.region || "-" }}
            </td>
            <!-- Statut ONG -->
            <td class="px-4 py-3">
              <span
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                :class="getOngStatusClass(gerant.status_ong)"
              >
                {{ getOngStatusLabel(gerant.status_ong) }}
              </span>
            </td>
            <!-- Statut Compte -->
            <td class="px-4 py-3">
              <span
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                :class="getStatusClass(gerant.status)"
              >
                {{ getStatusLabel(gerant.status) }}
              </span>
            </td>
            <!-- Date inscription -->
            <td class="px-4 py-3 text-sm text-slate-600">
              {{ formatDate(gerant.date_joined) }}
            </td>
          </tr>
          <tr v-if="store.gerants.length === 0">
            <td colspan="7" class="px-4 py-8 text-center text-slate-500">
              Aucun gérant trouvé
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import AlertMessage from "@/components/ui/AlertMessage.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import { useSuperAdminStore } from "../stores/superAdminStore.js";

const store = useSuperAdminStore();

const loading = store.loading;
const error = store.error;

const getStatusClass = (status) => {
  switch (status) {
    case "ACTIVE":
      return "bg-bleu-accent/15 text-bleu-accent border border-bleu-accent/25";
    case "INACTIVE":
      return "bg-slate-100 text-slate-600 border border-slate-200";
    case "PENDING":
      return "bg-bleu-nuit/10 text-bleu-nuit border border-slate-200";
    default:
      return "bg-slate-100 text-slate-600 border border-slate-200";
  }
};

const getStatusLabel = (status) => {
  switch (status) {
    case "ACTIVE":
      return "Actif";
    case "INACTIVE":
      return "Inactif";
    case "PENDING":
      return "En attente";
    default:
      return status;
  }
};

const getOngStatusClass = (status) => {
  switch (status) {
    case "ACTIVE":
      return "bg-bleu-accent/15 text-bleu-accent border border-bleu-accent/25";
    case "EN_ATTENTE":
      return "bg-bleu-nuit/10 text-bleu-nuit border border-slate-200";
    case "REJETEE":
      return "bg-rose-baraka/15 text-rose-baraka border border-rose-baraka/30";
    case "SUSPENDED":
      return "bg-slate-100 text-slate-600 border border-slate-200";
    default:
      return "bg-slate-100 text-slate-600 border border-slate-200";
  }
};

const getOngStatusLabel = (status) => {
  switch (status) {
    case "ACTIVE":
      return "Active";
    case "EN_ATTENTE":
      return "En attente";
    case "REJETEE":
      return "Rejetée";
    case "SUSPENDED":
      return "Suspendue";
    default:
      return status;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
};

onMounted(() => {
  store.fetchGerants();
});
</script>