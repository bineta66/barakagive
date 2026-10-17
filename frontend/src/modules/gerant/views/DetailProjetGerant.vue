<template>
  <div class="min-w-0 space-y-5 bg-slate-50 p-4 sm:space-y-6 sm:p-6 min-h-screen">
    <!-- En-tête -->
    <div class="flex flex-col gap-4 border-b border-slate-200 pb-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Détail du projet</h1>
        <p class="text-sm text-slate-500 mt-1">
          Informations et suivi du projet humanitaire.
        </p>
      </div>
      <div class="flex w-full gap-2 sm:w-auto sm:gap-3">
        <RouterLink
          to="/gerant/projets"
          class="inline-flex flex-1 items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 sm:flex-none sm:px-4"
        >
          <ArrowLeft :size="16" />
          Retour
        </RouterLink>
        <RouterLink
          :to="`/gerant/projets/modifier/${projet?.id}`"
          class="inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-bleu-nuit px-3 py-2.5 text-sm font-semibold text-white transition hover:bg-[#0a2540] sm:flex-none sm:px-4"
        >
          <Pencil :size="16" />
          Modifier
        </RouterLink>
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement du projet..." />

    <div v-else-if="projet" class="space-y-6">
      <!-- KPI Cards -->
      <div class="grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div class="flex min-w-0 items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Budget</p>
            <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
              {{ formatMontant(projet.budget) }} FCFA
            </h3>
          </div>
          <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700"><Wallet :size="22" /></span>
        </div>
        <div class="flex min-w-0 items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Statut</p>
            <h3 class="text-xl font-bold mt-1" :class="projet.archived ? 'text-slate-600' : 'text-bleu-accent'">
              {{ projet.archived ? "Archivé" : "En cours" }}
            </h3>
          </div>
          <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-700"><Activity :size="22" /></span>
        </div>
        <div class="flex min-w-0 items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Région</p>
            <h3 class="text-xl font-bold text-bleu-nuit mt-1">
              {{ projet.region || "-" }}
            </h3>
          </div>
          <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-sky-50 text-sky-700"><MapPin :size="22" /></span>
        </div>
        <div class="flex min-w-0 items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div>
            <p class="text-xs font-bold uppercase text-slate-500">Bénéficiaires</p>
            <h3 class="text-2xl font-bold text-bleu-nuit mt-1">{{ beneficiaryStats?.total ?? 0 }}</h3>
          </div>
          <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-rose-50 text-rose-700"><Users :size="22" /></span>
        </div>
      </div>

      <div class="grid min-w-0 grid-cols-1 items-start gap-4 xl:grid-cols-2 sm:gap-6">
        <section class="min-w-0 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          <div class="mb-5">
            <h2 class="text-lg font-bold text-bleu-nuit">Suivi des bénéficiaires</h2>
            <p class="mt-1 text-sm text-slate-500">Répartition des bénéficiaires prioritaires, pris en charge, en attente et sortis.</p>
          </div>
          <div v-if="beneficiaryStatsLoading" class="py-8 text-center text-sm text-slate-500">Chargement des bénéficiaires…</div>
          <p v-else-if="beneficiaryStatsError" role="alert" class="rounded-lg bg-amber-50 p-4 text-sm text-amber-800">{{ beneficiaryStatsError }}</p>
          <p v-else-if="!beneficiaryStats?.total" class="py-8 text-center text-sm text-slate-500">Aucun bénéficiaire enregistré pour ce projet.</p>
          <div v-else class="space-y-4">
            <ChartDonut :items="beneficiaryBreakdown" :size="156" :thickness="24" :center-value="beneficiaryTrackedTotal" center-label="suivis" :center-font-size="18" />
            <div class="flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3 text-xs text-slate-500">
              <span>{{ beneficiaryStats.total }} bénéficiaires au total</span>
            </div>
          </div>
        </section>

        <!-- Informations générales -->
        <section class="min-w-0 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          <h2 class="text-xl font-bold text-bleu-nuit mb-4 pb-2 border-b border-slate-100">
            Informations générales
          </h2>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-5">
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Nom du projet</label>
            <p class="text-sm font-semibold text-slate-900">{{ projet.name }}</p>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Code projet</label>
            <p class="text-sm font-mono text-bleu-nuit">{{ projet.code || "PRJ" }}</p>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Chef de projet</label>
            <p class="text-sm text-slate-900">{{ projet.chef_projet || "Non assigné" }}</p>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Responsable Finance</label>
            <p class="text-sm text-slate-900">{{ projet.responsable_finance || "Non assigné" }}</p>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Date de début</label>
            <p class="text-sm text-slate-900">{{ projet.start_date || "-" }}</p>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Date de fin</label>
            <p class="text-sm text-slate-900">{{ projet.end_date || "-" }}</p>
          </div>
          <div class="sm:col-span-2">
            <label class="block text-xs font-semibold text-slate-500 mb-1">Description</label>
            <p class="text-sm text-slate-700">{{ projet.description || "Aucune description" }}</p>
          </div>
          <div class="sm:col-span-2">
            <label class="block text-xs font-semibold text-slate-500 mb-1">Objectif humanitaire</label>
            <p class="text-sm text-slate-700">{{ projet.objectif || "Non défini" }}</p>
          </div>
          </div>
        </section>
      </div>

      <!-- Critères de vulnérabilité -->
      <div v-if="projet.criteres && projet.criteres.length" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
        <h2 class="text-xl font-bold text-bleu-nuit mb-4 pb-2 border-b border-slate-100">
          Critères de vulnérabilité
        </h2>
        <div class="space-y-3">
          <div
            v-for="critere in projet.criteres"
            :key="critere.id"
            class="flex items-center justify-between gap-3 rounded-xl border border-slate-100 bg-slate-50/80 p-3"
          >
            <span class="text-sm font-medium text-slate-900">{{ critere.nom }}</span>
            <span class="text-sm font-bold text-bleu-nuit">{{ critere.poids }}%</span>
          </div>
        </div>
      </div>
    </div>

    <EmptyState
      v-else
      titre="Projet introuvable"
      description="Le projet demandé n'existe pas ou a été supprimé."
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { ArrowLeft, Pencil, Wallet, Activity, MapPin, Users } from "lucide-vue-next";
import { useProjectStore } from "@/stores/project.js";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ChartDonut from "@/components/ui/ChartDonut.vue";
import api from "@/services/api.js";

const route = useRoute();
const projectStore = useProjectStore();
const loading = ref(true);
const projet = ref(null);
const beneficiaryStats = ref(null);
const beneficiaryStatsLoading = ref(false);
const beneficiaryStatsError = ref("");
const beneficiaryTrackedTotal = computed(() => beneficiaryBreakdown.value.reduce((sum, item) => sum + item.value, 0));
const beneficiaryBreakdown = computed(() => {
  const levels = beneficiaryStats.value?.levels || {};
  return [
    { label: "Prioritaires", value: Number(levels.prioritaires || 0), color: "#dc2626" },
    { label: "Pris en charge", value: Number(levels.pris_en_charge || 0), color: "#16a34a" },
    { label: "En attente", value: Number(levels.en_attente || 0), color: "#eab308" },
    { label: "Sortis", value: Number(levels.sortis || 0), color: "#f97316" },
  ];
});

const formatMontant = (v) => Number(v || 0).toLocaleString("fr-FR");

onMounted(async () => {
  loading.value = true;
  try {
    const data = await projectStore.fetchProject(route.params.id);
    projet.value = data;
    beneficiaryStatsLoading.value = true;
    try {
      const response = await api.get("/api/projects/dashboard/", { params: { project_id: data.id } });
      const levels = response.data?.beneficiaires_par_niveau || {};
      beneficiaryStats.value = {
        total: Number(levels.total ?? response.data?.operationnel?.beneficiaires ?? 0),
        levels,
      };
    } catch (error) {
      beneficiaryStatsError.value = error.response?.data?.detail || "Impossible de charger la répartition des bénéficiaires.";
    } finally {
      beneficiaryStatsLoading.value = false;
    }
  } catch (err) {
    console.error("Erreur chargement projet:", err);
  } finally {
    loading.value = false;
  }
});
</script>
