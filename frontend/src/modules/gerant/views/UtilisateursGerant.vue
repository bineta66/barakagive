<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100"
    >
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">
          Collaborateurs & Rôles
        </h1>
        <p class="text-sm text-slate-500 mt-1">
          Gérez les membres de votre organisation (Chefs de projet, Finance,
          Agents terrain).
        </p>
      </div>
      <div class="flex items-center gap-3">
        <BoutonPrimary to="/gerant/utilisateurs/creer">
          <Plus class="w-4 h-4" />
          <span>Nouvel utilisateur</span>
        </BoutonPrimary>
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

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div
        class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Total équipe</p>
          <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
            {{ usersPagination.count }}
          </h3>
        </div>
        <Users class="text-bleu-nuit" :size="28" />
      </div>

      <div
        class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Chefs de projet
          </p>
          <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
            {{ chefsProjet.length }}
          </h3>
        </div>
        <UserCheck class="text-bleu-nuit" :size="28" />
      </div>

      <div
        class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Resp. Finance
          </p>
          <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
            {{ responsablesFinance.length }}
          </h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>

      <div
        class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center"
      >
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">
            Agents Terrain
          </p>
          <h3 class="text-2xl font-bold text-bleu-nuit mt-1">
            {{ agents.length }}
          </h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div
      class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex flex-col sm:flex-row gap-3"
    >
      <div class="relative flex-1">
        <Search
          class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          :size="16"
        />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher par nom, prénom ou email..."
          class="w-full border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
        />
      </div>

      <select
        v-model="filtreRole"
        class="border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
      >
        <option value="tous">Tous les rôles</option>
        <option value="CHEF_PROJET">Chef de projet</option>
        <option value="FINANCE">Responsable Finance</option>
        <option value="AGENT">Agent Terrain</option>
        <option value="GERANT">Gérant</option>
      </select>

      <select
        v-model="filtreStatut"
        class="border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 bg-white"
      >
        <option value="tous">Tous les statuts</option>
        <option value="ACTIVE">Actif</option>
        <option value="INVITED">Invitation envoyée</option>
        <option value="SUSPENDED">Suspendu</option>
      </select>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Chargement des collaborateurs..." />

    <!-- Tableau -->
    <div
      v-else
      class="bg-white rounded-xl border border-slate-200/60 overflow-hidden shadow-xs-sm"
    >
      <EmptyState
        v-if="utilisateursFiltres.length === 0"
        titre="Aucun collaborateur trouvé"
        description="Aucun utilisateur ne correspond à vos filtres actuels."
      />

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead
            class="bg-slate-50 text-xs font-semibold uppercase text-bleu-nuit border-b border-slate-100"
          >
            <tr>
              <th class="text-left px-4 py-3">Nom & Prénom</th>
              <th class="text-left px-4 py-3">Email & Téléphone</th>
              <th class="text-left px-4 py-3">Rôle</th>
              <th class="text-left px-4 py-3">Statut</th>
              <th class="text-right px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr
              v-for="u in utilisateursFiltres"
              :key="u.id"
              class="hover:bg-slate-50/70 transition"
            >
              <td class="px-4 py-3.5">
                <div class="font-semibold text-slate-900">
                  {{ u.first_name }} {{ u.last_name }}
                </div>
              </td>
              <td class="px-4 py-3.5">
                <div class="text-slate-700">{{ u.email }}</div>
                <div class="text-xs text-slate-400">{{ u.phone || "-" }}</div>
              </td>
              <td class="px-4 py-3.5">
                <span
                  class="inline-block px-2.5 py-1 text-xs font-semibold rounded-full"
                  :class="getRoleBadgeClass(u.role)"
                >
                  {{ formatRole(u.role) }}
                </span>
              </td>
              <td class="px-4 py-3.5">
                <StatusBadge :statut="u.status">
                  {{
                    u.status === "ACTIVE"
                      ? "Actif"
                      : u.status === "INVITED"
                      ? "Invitation envoyée"
                      : "Suspendu"
                  }}
                </StatusBadge>
              </td>
              <td class="px-4 py-3.5 text-right">
                <div class="flex items-center justify-end gap-1">
                  <!-- Modifier -->
                  <button
                    v-if="u.role !== 'GERANT'"
                    @click="ouvrirModification(u)"
                    class="p-1.5 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition"
                    title="Modifier"
                  >
                    <Pencil :size="16" />
                  </button>

                  <!-- Voir Détails -->
                  <button
                    @click="ouvrirDetails(u)"
                    class="p-1.5 text-bleu-nuit hover:bg-slate-100 rounded-lg transition"
                    title="Voir les détails"
                  >
                    <Eye :size="16" />
                  </button>

                  <!-- Activer / Désactiver -->
                  <button
                    v-if="u.role !== 'GERANT'"
                    @click="basculerStatut(u)"
                    class="p-1.5 rounded-lg transition"
                    :class="
                      u.status === 'ACTIVE'
                        ? 'text-rose-600 hover:bg-rose-50'
                        : 'text-emerald-600 hover:bg-emerald-50'
                    "
                    :title="
                      u.status === 'ACTIVE'
                        ? 'Désactiver ce collaborateur'
                        : 'Activer ce collaborateur'
                    "
                  >
                    <Power :size="16" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm">
      <span>Page {{ currentPage }} sur {{ pageCount }} · {{ usersPagination.count }} utilisateur(s)</span>
      <div class="flex gap-2">
        <button class="rounded border px-3 py-2 disabled:opacity-40" :disabled="currentPage <= 1" @click="currentPage--">Précédent</button>
        <button class="rounded border px-3 py-2 disabled:opacity-40" :disabled="currentPage >= pageCount" @click="currentPage++">Suivant</button>
      </div>
    </div>

    <!-- Modal Détails Collaborateur -->
    <div
      v-if="utilisateurSelectionne"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      @click.self="utilisateurSelectionne = null"
    >
      <div
        class="bg-white rounded-2xl shadow-xs-sm max-w-lg w-full border border-slate-200 overflow-hidden"
      >
        <!-- Modal Header -->
        <div
          class="p-6 border-b border-slate-100 flex items-center justify-between"
        >
          <div class="flex items-center gap-3">
            <div
              class="w-12 h-12 rounded-xl bg-bleu-nuit/10 border border-bleu-nuit/30 text-bleu-nuit font-bold text-lg flex items-center justify-center"
            >
              {{ utilisateurSelectionne.first_name?.[0]
              }}{{ utilisateurSelectionne.last_name?.[0] }}
            </div>
            <div>
              <h3 class="text-xl font-bold text-slate-900">
                {{ utilisateurSelectionne.first_name }}
                {{ utilisateurSelectionne.last_name }}
              </h3>
              <p class="text-xs text-slate-500">
                {{ utilisateurSelectionne.email }}
              </p>
            </div>
          </div>
          <button
            @click="utilisateurSelectionne = null"
            class="p-2 text-slate-400 hover:text-slate-600 rounded-lg transition"
          >
            <X :size="20" />
          </button>
        </div>

        <!-- Modal Body -->
        <div class="p-6 space-y-4 text-sm">
          <div class="grid grid-cols-2 gap-4">
            <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
              <span class="text-xs font-semibold text-slate-400 block mb-1"
                >ROLE OPERATIONNEL</span
              >
              <span
                class="inline-block px-2.5 py-1 text-xs font-semibold rounded-full"
                :class="getRoleBadgeClass(utilisateurSelectionne.role)"
              >
                {{ formatRole(utilisateurSelectionne.role) }}
              </span>
            </div>

            <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
              <span class="text-xs font-semibold text-slate-400 block mb-1"
                >STATUT DU COMPTE</span
              >
              <StatusBadge :statut="utilisateurSelectionne.status">
                {{
                  utilisateurSelectionne.status === "ACTIVE"
                    ? "Actif"
                    : utilisateurSelectionne.status === "INVITED"
                    ? "Invitation envoyée"
                    : "Suspendu"
                }}
              </StatusBadge>
            </div>
          </div>

          <div class="space-y-3 pt-2">
            <div
              class="flex items-center justify-between py-2 border-b border-slate-100"
            >
              <span class="text-slate-500 text-xs font-medium"
                >Téléphone / WhatsApp</span
              >
              <span class="text-slate-900 font-semibold text-xs">{{
                utilisateurSelectionne.phone || "Non renseigné"
              }}</span>
            </div>
            <div
              class="flex items-center justify-between py-2 border-b border-slate-100"
            >
              <span class="text-slate-500 text-xs font-medium"
                >Connexion autorisée</span
              >
              <span
                class="font-semibold text-xs"
                :class="
                  utilisateurSelectionne.is_active
                    ? 'text-emerald-600'
                    : 'text-slate-500'
                "
              >
                {{
                  utilisateurSelectionne.is_active
                    ? "Oui (Actif)"
                    : "Non (Bloqué)"
                }}
              </span>
            </div>
            <div
              class="flex items-center justify-between py-2 border-b border-slate-100"
            >
              <span class="text-slate-500 text-xs font-medium"
                >Date d'inscription</span
              >
              <span class="text-slate-700 text-xs">{{
                formatDate(utilisateurSelectionne.date_joined)
              }}</span>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div
          class="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between"
        >
          <BoutonSecondary @click="utilisateurSelectionne = null">
            Fermer
          </BoutonSecondary>

          <button
            v-if="utilisateurSelectionne.role !== 'GERANT'"
            @click="basculerStatut(utilisateurSelectionne)"
            class="p-2 rounded-lg transition"
            :class="
              utilisateurSelectionne.status === 'ACTIVE'
                ? 'text-rose-600 hover:bg-rose-50'
                : 'text-emerald-600 hover:bg-emerald-50'
            "
            :title="
              utilisateurSelectionne.status === 'ACTIVE'
                ? 'Désactiver le compte'
                : 'Activer le compte'
            "
          >
            <Power :size="18" />
          </button>
        </div>
      </div>
    </div>
    <!-- Modal Modification Collaborateur -->
    <UtilisateurFormModal
      :ouvert="modalModifOuvert"
      :utilisateur="utilisateurAModifier"
      :saving="loading"
      @fermer="modalModifOuvert = false; utilisateurAModifier = null"
      @save="sauvegarderModification"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { storeToRefs } from "pinia";
import {
  Users,
  UserCheck,
  Wallet,
  Activity,
  Search,
  Plus,
  Eye,
  Power,
  X,
  Pencil,
} from "lucide-vue-next";
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js";
import { useAutoRefresh } from "@/composables/useAutoRefresh.js";
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue";
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import AlertMessage from "@/components/ui/AlertMessage.vue";
import UtilisateurFormModal from "@/modules/gerant/components/utilisateurs/UtilisateurFormModal.vue";

const store = useGerantStore();
const { users, usersPagination, chefsProjet, responsablesFinance, agents, loading, error } =
  storeToRefs(store);

const search = ref("");
const filtreRole = ref("tous");
const filtreStatut = ref("tous");
const utilisateurSelectionne = ref(null);
const modalModifOuvert = ref(false);
const utilisateurAModifier = ref(null);
const currentPage = ref(1);
const pageCount = computed(() => Math.max(1, Math.ceil(usersPagination.value.count / 20)));

watch([currentPage, search, filtreRole, filtreStatut], () => {
  store.fetchUsers({
    page: currentPage.value,
    page_size: 20,
    search: search.value.trim(),
    role: filtreRole.value === "tous" ? "" : filtreRole.value,
    status: filtreStatut.value === "tous" ? "" : filtreStatut.value,
  }).catch(() => {});
}, { immediate: true });

watch([search, filtreRole, filtreStatut], () => {
  if (currentPage.value !== 1) currentPage.value = 1;
});

useAutoRefresh(() => store.fetchUsers());

const ouvrirDetails = (user) => {
  utilisateurSelectionne.value = { ...user };
};

const ouvrirModification = (user) => {
  utilisateurAModifier.value = { ...user };
  modalModifOuvert.value = true;
};

const sauvegarderModification = async (data) => {
  try {
    await store.updateUser(utilisateurAModifier.value.id, data);
    modalModifOuvert.value = false;
    utilisateurAModifier.value = null;
  } catch (err) {
    alert("Erreur lors de la modification : " + (err?.response?.data?.detail || err.message));
  }
};

const basculerStatut = async (user) => {
  const isCurrentlyActive = user.status === "ACTIVE";
  const actionName = isCurrentlyActive ? "désactiver" : "activer";
  if (
    !confirm(
      `Voulez-vous vraiment ${actionName} le compte de ${user.first_name} ${user.last_name} ?`
    )
  ) {
    return;
  }
  try {
    const updated = await store.toggleUserStatus(user.id, isCurrentlyActive);
    if (
      utilisateurSelectionne.value &&
      utilisateurSelectionne.value.id === user.id
    ) {
      utilisateurSelectionne.value = {
        ...utilisateurSelectionne.value,
        ...updated,
      };
    }
  } catch (err) {
    alert(
      "Erreur lors de la modification du statut : " +
        (err?.response?.data?.detail || err.message)
    );
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return "Non précisée";
  try {
    return new Date(dateStr).toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
};

const utilisateursFiltres = computed(() => {
  let result = users.value;

  if (search.value) {
    const q = search.value.toLowerCase();
    result = result.filter(
      (u) =>
        (u.first_name && u.first_name.toLowerCase().includes(q)) ||
        (u.last_name && u.last_name.toLowerCase().includes(q)) ||
        (u.email && u.email.toLowerCase().includes(q))
    );
  }

  if (filtreRole.value !== "tous") {
    result = result.filter((u) => u.role === filtreRole.value);
  }

  if (filtreStatut.value !== "tous") {
    result = result.filter((u) => u.status === filtreStatut.value);
  }

  return result;
});

const formatRole = (role) => {
  switch (role) {
    case "CHEF_PROJET":
      return "Chef de projet";
    case "FINANCE":
      return "Responsable Finance";
    case "AGENT":
      return "Agent Terrain";
    case "GERANT":
      return "Gérant";
    default:
      return role;
  }
};

const getRoleBadgeClass = (role) => {
  switch (role) {
    case "CHEF_PROJET":
      return "bg-bleu-accent/10 text-or border border-bleu-accent/20";
    case "FINANCE":
      return "bg-amber-50 text-amber-800 border border-amber-200";
    case "AGENT":
      return "bg-emerald-50 text-emerald-800 border border-emerald-200";
    default:
      return "bg-slate-100 text-slate-800";
  }
};
</script>
