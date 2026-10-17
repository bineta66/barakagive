<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Titre -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Campagnes</h1>
        <p class="text-xs text-gray-500 mt-1">
          Gérez et suivez les campagnes humanitaires.
        </p>
      </div>

      <BoutonPrimary to="/chef-projet/campagnes/creer">
        <Plus :size="18" />
        Nouvelle campagne
      </BoutonPrimary>
    </div>

    <LoadingSpinner
      v-if="campaignStore.loading && !campaignStore.campaigns.length"
      message="Chargement des campagnes..."
    />
    <AlertMessage
      v-if="feedback.message"
      :type="feedback.type"
      :message="feedback.message"
      class="mb-4"
    />

    <!-- Cartes statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">
            Total campagnes
          </p>
          <h3 class="text-xl font-bold text-bleu-nuit mt-2">
            {{ statistiques.total }}
          </h3>
        </div>
        <ClipboardList class="text-bleu-nuit" :size="28" />
      </div>

      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Actives</p>
          <h3 class="text-xl font-bold text-bleu-nuit mt-2">
            {{ statistiques.actives }}
          </h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>

      <div
        class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Terminées</p>
          <h3 class="text-xl font-bold text-bleu-nuit mt-2">
            {{ statistiques.terminees }}
          </h3>
        </div>
        <CheckCircle class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div
      class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 grid md:grid-cols-3 gap-3"
    >
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="recherche"
          type="text"
          placeholder="Rechercher une campagne..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm outline-none focus:ring-2 focus:ring-bleu-nuit/30"
        />
      </div>

      <select
        v-model="filtreStatut"
        class="border rounded-lg px-3 py-2 text-sm bg-white"
      >
        <option value="Tous les statuts">Tous les statuts</option>
        <option value="Brouillon">Brouillon</option>
        <option value="Planifiée">Planifiée</option>
        <option value="En cours">En cours</option>
        <option value="Terminée">Terminée</option>
        <option value="Annulée">Annulée</option>
      </select>

      <select
        v-model="filtreProjet"
        class="border rounded-lg px-3 py-2 text-sm bg-white"
      >
        <option value="Tous les projets">Tous les projets</option>
        <option
          v-for="proj in projectStore.projects"
          :key="proj.id"
          :value="proj.name"
        >
          {{ proj.name }}
        </option>
      </select>
    </div>

    <div class="flex justify-end gap-2">
      <button
        type="button"
        @click="modeAffichage = 'cartes'"
        :aria-pressed="modeAffichage === 'cartes'"
        class="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold transition"
        :class="modeAffichage === 'cartes' ? 'border-bleu-nuit bg-bleu-nuit text-white' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'"
      >
        <LayoutGrid :size="16" /> Cartes
      </button>
      <button
        type="button"
        @click="modeAffichage = 'tableau'"
        :aria-pressed="modeAffichage === 'tableau'"
        class="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold transition"
        :class="modeAffichage === 'tableau' ? 'border-bleu-nuit bg-bleu-nuit text-white' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'"
      >
        <List :size="16" /> Tableau
      </button>
    </div>

    <!-- Vue tableau -->
    <div v-if="modeAffichage === 'tableau'" class="bg-white rounded-xl border border-slate-200/60 overflow-x-auto">
      <table class="w-full min-w-[640px]">
        <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
          <tr>
            <th class="text-left px-4 py-4">Campagne</th>
            <th class="text-left px-4">Projet</th>
            <th class="text-left px-4">Zones</th>
            <th class="text-left px-4">Statut</th>
            <th class="text-right px-4">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="campagne in campagnesPage"
            :key="campagne.id"
            class="border-t hover:bg-slate-50"
          >
            <td class="px-4 py-4">
              <h3 class="font-semibold text-sm text-slate-800">
                {{ campagne.nom }}
              </h3>
              <p class="text-xs text-gray-500">{{ campagne.code }}</p>
            </td>

            <td class="px-4 text-sm text-slate-600">
              {{ campagne.projet }}
            </td>

            <td class="px-4 text-sm text-slate-600">
              {{ campagne.zone }}
            </td>

            <td class="px-4">
              <StatusBadge :statut="campagne.statut">{{
                campagne.statut
              }}</StatusBadge>
            </td>

            <td class="px-4">
              <div class="flex justify-end gap-2">
                <RouterLink
                  :to="`/chef-projet/campagnes/${campagne.id}`"
                  class="text-slate-500 hover:text-bleu-nuit p-1"
                  title="Voir détails"
                >
                  <Eye :size="18" />
                </RouterLink>

                <RouterLink
                  :to="`/chef-projet/campagnes/modifier/${campagne.id}`"
                  class="text-slate-500 hover:text-bleu-nuit p-1"
                  title="Modifier"
                >
                  <Pencil :size="18" />
                </RouterLink>

                <RouterLink
                  :to="`/chef-projet/campagnes/${campagne.id}/formulaire`"
                  class="text-slate-500 hover:text-bleu-nuit p-1"
                  title="Formulaire dynamique"
                >
                  <FileText :size="18" />
                </RouterLink>

                <button
                  @click="confirmerSupprimer(campagne)"
                  class="text-slate-500 hover:text-red-600 p-1.5 rounded-lg hover:bg-red-50 transition"
                  title="Supprimer"
                >
                  <Trash2 :size="16" />
                </button>
              </div>
            </td>
          </tr>

          <tr v-if="!campagnesPage.length">
            <td colspan="5" class="py-8 text-center text-sm text-slate-500">
              Aucune campagne trouvée.
            </td>
          </tr>
        </tbody>
      </table>

    </div>

    <!-- Vue cartes -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <article v-for="campagne in campagnesPage" :key="campagne.id" class="overflow-hidden rounded-xl border border-slate-200/70 bg-white/75 text-slate-800 backdrop-blur-xl">
        <div class="border-b border-slate-200/70 p-5">
          <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <h2 class="text-lg font-bold text-slate-900 truncate">{{ campagne.nom }}</h2>
            <p class="text-xs text-slate-500 mt-1">{{ campagne.code }}</p>
          </div>
          <StatusBadge :statut="campagne.statut">{{ campagne.statut }}</StatusBadge>
          </div>

          <div class="mt-5 grid grid-cols-2 gap-3 text-xs">
          <div class="rounded-lg border border-slate-200/70 bg-slate-100/70 p-3">
            <p class="text-slate-500">Projet</p>
            <p class="mt-1 truncate text-sm font-semibold text-slate-800">{{ campagne.projet }}</p>
          </div>
          <div class="rounded-lg border border-slate-200/70 bg-slate-100/70 p-3">
            <p class="text-slate-500">Zones</p>
            <p class="mt-1 text-sm font-semibold text-slate-800">{{ campagne.zone }}</p>
          </div>
          <div class="rounded-lg border border-slate-200/70 bg-slate-100/70 p-3">
            <p class="text-slate-500">Début</p>
            <p class="mt-1 text-sm font-semibold text-slate-800">{{ formatDate(campagne.dateDebut) }}</p>
          </div>
          <div class="rounded-lg border border-slate-200/70 bg-slate-100/70 p-3">
            <p class="text-slate-500">Fin</p>
            <p class="mt-1 text-sm font-semibold text-slate-800">{{ formatDate(campagne.dateFin) }}</p>
          </div>
        </div>
        </div>

        <div class="flex items-center justify-between gap-3 bg-slate-100/70 p-4">
          <div class="flex items-center gap-1">
            <RouterLink :to="`/chef-projet/campagnes/${campagne.id}`" class="inline-flex items-center gap-1.5 rounded-lg bg-white px-3 py-2 text-xs font-semibold text-bleu-nuit hover:bg-slate-100" title="Voir les détails" aria-label="Voir les détails"><Eye :size="15" />Détails</RouterLink>
            <RouterLink :to="`/chef-projet/campagnes/modifier/${campagne.id}`" class="rounded-lg p-2 text-slate-600 hover:bg-bleu-nuit/5 hover:text-bleu-nuit" title="Modifier" aria-label="Modifier"><Pencil :size="17" /></RouterLink>
            <RouterLink :to="`/chef-projet/campagnes/${campagne.id}/formulaire`" class="rounded-lg p-2 text-slate-600 hover:bg-bleu-nuit/5 hover:text-bleu-nuit" title="Formulaire dynamique" aria-label="Formulaire dynamique"><FileText :size="17" /></RouterLink>
          </div>
          <button @click="confirmerSupprimer(campagne)" class="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-semibold text-rose-baraka hover:bg-rose-baraka/10 transition"><Trash2 :size="15" />Supprimer</button>
        </div>
      </article>
      <div v-if="!campagnesPage.length" class="lg:col-span-2 rounded-xl border border-slate-200 bg-white py-10 text-center text-sm text-slate-500">Aucune campagne trouvée.</div>
    </div>

    <!-- Pagination commune aux deux modes -->
    <div v-if="campagnesFiltrees.length > 0" class="flex flex-col sm:flex-row items-center justify-between gap-3 px-1 text-xs">
      <p class="text-slate-500">Affichage de {{ campagnesPage.length }} sur {{ campaignStore.totalCampaigns }} campagnes</p>
      <div class="flex gap-1" v-if="totalPages > 1">
        <button class="px-3 py-2 border rounded bg-white text-bleu-nuit disabled:opacity-40" :disabled="pageCourante === 1" @click="pageCourante = pageCourante - 1">Précédent</button>
        <button v-for="page in pagesVisibles" :key="page" class="w-8 h-8 border rounded" :class="page === pageCourante ? 'bg-bleu-nuit text-white' : 'bg-white text-bleu-nuit'" @click="pageCourante = page">{{ page }}</button>
        <button class="px-3 py-2 border rounded bg-white text-bleu-nuit disabled:opacity-40" :disabled="pageCourante === totalPages" @click="pageCourante = pageCourante + 1">Suivant</button>
      </div>
    </div>

    <!-- ── Modale confirmation suppression ─────────────────── -->
    <Teleport to="body">
      <div
        v-if="campagneASupprimer"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
        @click.self="campagneASupprimer = null"
      >
        <div class="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full">
          <div
            class="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center mx-auto mb-4"
          >
            <Trash2 :size="22" class="text-red-600" />
          </div>
          <h3 class="text-center font-bold text-slate-900 mb-2">
            Supprimer la campagne
          </h3>
          <p class="text-center text-sm text-slate-500 mb-6">
            Voulez-vous vraiment supprimer
            <strong>{{ campagneASupprimer.nom }}</strong> ? Cette action est
            irréversible.
          </p>
          <div class="flex gap-3">
            <button
              @click="campagneASupprimer = null"
              class="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              Annuler
            </button>
            <button
              @click="executerSuppression"
              :disabled="suppression"
              class="flex-1 px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm font-semibold transition disabled:opacity-60"
            >
              {{ suppression ? "Suppression..." : "Supprimer" }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { RouterLink } from "vue-router";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import AlertMessage from "@/components/ui/AlertMessage.vue";
import { useCampagnes } from "@/composables/useCampagnes.js";
import { useProjectStore } from "@/stores/project.js";
import {
  Plus,
  ClipboardList,
  Activity,
  CheckCircle,
  Search,
  Eye,
  Pencil,
  FileText,
  Trash2,
  LayoutGrid,
  List,
} from "lucide-vue-next";
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue";

const projectStore = useProjectStore();
const feedback = reactive({ type: "success", message: "" });
const campagneASupprimer = ref(null);
const suppression = ref(false);
const modeAffichage = ref("cartes");

const {
  recherche,
  filtreStatut,
  filtreProjet,
  filtreZone,
  pageCourante,
  campagnesPage,
  totalPages,
  pagesVisibles,
  campagnesFiltrees,
  statistiques,
  campaignStore,
} = useCampagnes();

onMounted(async () => {
  try {
    await projectStore.fetchProjects();
  } catch (e) {}
});

const confirmerSupprimer = (campagne) => {
  campagneASupprimer.value = campagne;
};

const formatDate = (date) => {
  if (!date) return "Non définie";
  return new Intl.DateTimeFormat("fr-FR").format(new Date(date));
};

const executerSuppression = async () => {
  if (!campagneASupprimer.value) return;
  suppression.value = true;
  feedback.message = "";
  try {
    await campaignStore.deleteCampaign(campagneASupprimer.value.id);
    campagneASupprimer.value = null;
    feedback.type = "success";
    feedback.message = "Campagne supprimée avec succès.";
  } catch (err) {
    campagneASupprimer.value = null;
    feedback.type = "error";
    feedback.message = campaignStore.error || "Erreur lors de la suppression.";
  } finally {
    suppression.value = false;
  }
};
</script>

