<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex items-center justify-between pb-4 border-b border-slate-100">
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Modifier le projet</h1>
        <p class="text-sm text-slate-500 mt-1">
          Mettez à jour les informations du projet.
        </p>
      </div>
      <div class="flex items-center gap-3">
        <RouterLink
          to="/gerant/projets"
          class="inline-flex items-center gap-2 px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
        >
          <ArrowLeft :size="16" />
          Retour
        </RouterLink>
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement du projet..." />
    <AlertMessage
      v-if="feedback.message"
      :type="feedback.type"
      :message="feedback.message"
      class="mb-4"
    />

    <div v-if="!loading && projet" class="max-w-4xl">
      <ProjetFormModal
        :ouvert="true"
        :projet="projet"
        :saving="projectStore.loading"
        @fermer="router.push('/gerant/projets')"
        @save="sauvegarder"
        @delete="supprimerProjet"
      />
    </div>

    <EmptyState
      v-else-if="!loading"
      titre="Projet introuvable"
      description="Le projet demandé n'existe pas ou a été supprimé."
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import { ArrowLeft } from "lucide-vue-next";
import { useProjectStore } from "@/stores/project.js";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import AlertMessage from "@/components/ui/AlertMessage.vue";
import ProjetFormModal from "@/modules/gerant/components/projets/ProjetFormModal.vue";

const route = useRoute();
const router = useRouter();
const projectStore = useProjectStore();

const loading = ref(true);
const projet = ref(null);
const feedback = reactive({ type: "success", message: "" });

onMounted(async () => {
  loading.value = true;
  try {
    await projectStore.fetchProject(route.params.id);
    projet.value = projectStore.currentProject;
  } catch (err) {
    feedback.type = "error";
    feedback.message = "Erreur lors du chargement du projet.";
  } finally {
    loading.value = false;
  }
});

const sauvegarder = async (data) => {
  feedback.message = "";
  try {
    await projectStore.updateProject(route.params.id, data);
    feedback.type = "success";
    feedback.message = "Projet modifié avec succès !";
    setTimeout(() => {
      router.push("/gerant/projets");
    }, 800);
  } catch (err) {
    feedback.type = "error";
    feedback.message = projectStore.error || "Erreur lors de la modification du projet.";
  }
};

const supprimerProjet = async () => {
  feedback.message = "";
  try {
    await projectStore.deleteProject(route.params.id);
    feedback.type = "success";
    feedback.message = "Projet supprimé avec succès !";
    setTimeout(() => {
      router.push("/gerant/projets");
    }, 800);
  } catch (err) {
    feedback.type = "error";
    feedback.message = projectStore.error || "Erreur lors de la suppression du projet.";
  }
};
</script>
