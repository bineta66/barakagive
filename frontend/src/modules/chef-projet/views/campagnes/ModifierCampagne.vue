<template>
  <div
    class="min-h-screen bg-white flex justify-center items-start py-8 px-4 sm:px-6 lg:px-8"
  >
    <div
      class="w-full max-w-4xl bg-white rounded-2xl border border-slate-200/60 p-8 shadow-xs-sm"
    >
      <!-- En-tête -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-6 mb-6 border-b border-slate-100 gap-4">
        <div>
          <h1 class="text-3xl font-bold text-bleu-nuit">Modifier la campagne</h1>
          <p class="text-sm text-gray-500 mt-1">
            Mettez à jour les informations, zones d'intervention et calendrier de la campagne.
          </p>
        </div>

        <div class="flex items-center gap-3">
          <BoutonSecondary to="/chef-projet/campagnes">
            <List :size="18" />
            Liste des campagnes
          </BoutonSecondary>
        </div>
      </div>

      <LoadingSpinner
        v-if="loading"
        message="Chargement des données de la campagne..."
      />
      <AlertMessage
        v-if="feedback.message"
        :type="feedback.type"
        :message="feedback.message"
        class="mb-6"
      />

      <!-- Formulaire -->
      <form
        v-if="!loading && form.nom !== undefined"
        @submit.prevent="modifierCampagne"
        class="space-y-8"
      >
        <!-- Section 1 : Identification & Projet -->
        <div>
          <h3 class="text-xl font-bold text-bleu-nuit mb-4 pb-2 border-b">
            1. Identification & Projet
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Nom de la campagne -->
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Nom de la campagne *
              </label>
              <input
                v-model="form.nom"
                type="text"
                placeholder="Ex : Distribution Alimentaire d'Urgence Hivernage 2026"
                class="w-full rounded-lg border bg-slate-50 px-4 py-2.5 focus:ring-2 outline-none text-sm transition"
                maxlength="200"
                :class="
                  fErr.nom
                    ? 'border-red-500 focus:ring-red-500/20'
                    : 'border-gray-300 focus:ring-bleu-nuit/30'
                "
              />
              <p v-if="fErr.nom" class="mt-1 text-xs text-red-600">{{ fErr.nom }}</p>
            </div>

            <!-- Projet associé (affichage informatif car lié immuablement au backend) -->
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Projet humanitaire rattaché
              </label>
              <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between text-sm">
                <span class="font-medium text-slate-800">
                  {{ campagneProjetNom || "Projet associé" }}
                </span>
                <span class="text-xs px-2 py-0.5 bg-bleu-nuit/10 text-bleu-nuit rounded font-semibold">
                  Rattaché
                </span>
              </div>
            </div>

            <!-- Description -->
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Description
              </label>
              <textarea
                v-model="form.description"
                rows="3"
                maxlength="500"
                placeholder="Décrivez succinctement l'objectif de la campagne..."
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-bleu-nuit/30 outline-none text-sm"
              ></textarea>
              <p v-if="fErr.description" class="mt-1 text-xs text-red-600">{{ fErr.description }}</p>
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Type d'opération *</label>
              <select v-model="form.type" required class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm focus:ring-2 focus:ring-bleu-nuit/30">
                <option value="" disabled>Sélectionner le type de campagne...</option>
                <option value="COLLECTE">Collecte de fonds (ancien type)</option>
                <option value="COLLECTE_BESOINS">Collecte des besoins</option>
                <option value="DISTRIBUTION">Distribution</option>
                <option value="SANTE">Santé</option>
                <option value="ALIMENTATION">Alimentation</option>
                <option value="URGENCE">Urgence</option>
                <option value="SENSIBILISATION">Sensibilisation</option>
                <option value="SUIVI_EVALUATION">Suivi et évaluation</option>
              </select>
              <p v-if="form.type === 'COLLECTE'" class="text-xs text-amber-700 mt-1">Ancien type conservé pour cette campagne ; sélectionnez un type opérationnel pour le remplacer.</p>
            </div>
          </div>
        </div>

        <!-- Section 2 : Zones d'intervention -->
        <div>
          <h3 class="text-xl font-bold text-bleu-nuit mb-4 pb-2 border-b">
            2. Zones d'intervention
          </h3>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Sélectionnez les zones d'intervention * (au moins une zone)
            </label>

            <div :class="fErr.zone_ids ? 'rounded border border-red-500 p-2' : ''">
              <AsyncSearchMultiSelect
                v-model="form.zone_ids"
                :initial-options="zoneOptions"
                endpoint="/api/zones/"
                label-key="nom"
                value-key="id"
                secondary-key="region_nom"
                placeholder="Rechercher des zones par nom…"
                @selected-options="zoneOptions = $event"
              />
            </div>
            <p v-if="fErr.zone_ids" class="mt-1 text-xs text-red-600">{{ fErr.zone_ids }}</p>
            <p v-else class="text-xs text-slate-500 mt-1.5">
              {{ form.zone_ids.length }} zone(s) sélectionnée(s).
            </p>
          </div>
        </div>

        <!-- Section 3 : Calendrier & Statut -->
        <div>
          <h3 class="text-xl font-bold text-bleu-nuit mb-4 pb-2 border-b">
            3. Calendrier & Statut
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Date de début *
              </label>
              <input
                v-model="form.date_debut"
                type="date"
                class="w-full rounded-lg border bg-slate-50 px-4 py-2.5 text-sm transition outline-none focus:ring-2"
                :class="
                  fErr.date_debut
                    ? 'border-red-500 focus:ring-red-500/20'
                    : 'border-gray-300 focus:ring-bleu-nuit/30'
                "
              />
              <p v-if="fErr.date_debut" class="mt-1 text-xs text-red-600">
                {{ fErr.date_debut }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Date de fin *
              </label>
              <input
                v-model="form.date_fin"
                type="date"
                class="w-full rounded-lg border bg-slate-50 px-4 py-2.5 text-sm transition outline-none focus:ring-2"
                :class="
                  fErr.date_fin
                    ? 'border-red-500 focus:ring-red-500/20'
                    : 'border-gray-300 focus:ring-bleu-nuit/30'
                "
              />
              <p v-if="fErr.date_fin" class="mt-1 text-xs text-red-600">
                {{ fErr.date_fin }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Statut *
              </label>
              <select
                v-model="form.statut"
                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-bleu-nuit/30"
              >
                <option value="BROUILLON">Brouillon</option>
                <option value="PLANIFIER">Planifiée</option>
                <option value="EN_COURS">En cours</option>
                <option value="TERMINE">Terminée</option>
                <option value="ANNULEE">Annulée</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Boutons d'action -->
        <div class="pt-6 border-t flex flex-col sm:flex-row items-center justify-between gap-4">
          <button
            type="button"
            @click="confirmerSuppression = true"
            class="inline-flex items-center gap-2 px-5 py-2.5 border border-red-200 text-red-600 rounded-lg text-sm font-semibold hover:bg-red-50 transition w-full sm:w-auto justify-center"
          >
            <Trash2 :size="16" />
            Supprimer la campagne
          </button>

          <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
            <BoutonSecondary to="/chef-projet/campagnes" type="button">
              Annuler
            </BoutonSecondary>

            <button
              type="submit"
              :disabled="submitting"
              class="px-6 py-2.5 bg-bleu-nuit text-white font-semibold text-sm rounded-lg hover:bg-[#01111eff] transition shadow-xs disabled:opacity-50 flex items-center gap-2"
            >
              <span
                v-if="submitting"
                class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
              ></span>
              {{ submitting ? "Enregistrement..." : "Enregistrer les modifications" }}
            </button>
          </div>
        </div>
      </form>
    </div>

    <!-- Modale confirmation suppression -->
    <Teleport to="body">
      <div
        v-if="confirmerSuppression"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
        @click.self="confirmerSuppression = false"
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
            Voulez-vous vraiment supprimer <strong>{{ form.nom }}</strong> ?
            Cette action est irréversible.
          </p>
          <div class="flex gap-3">
            <button
              @click="confirmerSuppression = false"
              class="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              Annuler
            </button>
            <button
              @click="supprimerCampagne"
              :disabled="deleting"
              class="flex-1 px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm font-semibold transition disabled:opacity-60"
            >
              {{ deleting ? "Suppression..." : "Supprimer" }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { List, Trash2 } from "lucide-vue-next";
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import AlertMessage from "@/components/ui/AlertMessage.vue";
import AsyncSearchMultiSelect from "@/components/ui/AsyncSearchMultiSelect.vue";
import { useCampaignStore } from "@/stores/campaign.js";
import { useFormValidation, rules } from "@/composables/useFormValidation.js";

const route = useRoute();
const router = useRouter();
const campaignStore = useCampaignStore();
const { errors: fErr, validate: fValidate } = useFormValidation();

const loading = ref(true);
const submitting = ref(false);
const confirmerSuppression = ref(false);
const deleting = ref(false);
const feedback = reactive({ type: "success", message: "" });
const campagneProjetNom = ref("");
const zoneOptions = ref([]);

const form = reactive({
  nom: "",
  type: "DISTRIBUTION",
  description: "",
  zone_ids: [],
  date_debut: "",
  date_fin: "",
  statut: "PLANIFIER",
});

onMounted(async () => {
  loading.value = true;
  try {
    const data = await campaignStore.fetchCampaign(route.params.id);
    form.nom = data.nom || "";
    form.type = data.type || "DISTRIBUTION";
    form.description = data.description || "";
    form.date_debut = data.date_debut || "";
    form.date_fin = data.date_fin || "";
    form.statut = data.statut || "PLANIFIER";
    zoneOptions.value = data.zones || [];
    form.zone_ids = zoneOptions.value.map((z) => String(z.id));
    campagneProjetNom.value = data.projet?.name || data.projet_nom || "";
  } catch (err) {
    feedback.type = "error";
    feedback.message = "Erreur lors du chargement de la campagne.";
  } finally {
    loading.value = false;
  }
});

const modifierCampagne = async () => {
  feedback.message = "";

  // Validation complète avec useFormValidation
  const ok = fValidate({
    nom: [rules.nomCampagne, form.nom],
    description: [rules.description, form.description],
    date_debut: [rules.date, form.date_debut],
    date_fin: [rules.dateFin, form.date_fin, form.date_debut],
    statut: [rules.required, form.statut],
    type: [rules.required, form.type],
  });

  if (!ok) {
    feedback.type = "error";
    feedback.message = "Veuillez corriger les champs en rouge.";
    return;
  }

  if (!form.zone_ids.length) {
    fErr.zone_ids = "Veuillez sélectionner au moins une zone d'intervention.";
    feedback.type = "error";
    feedback.message = "Veuillez sélectionner au moins une zone d'intervention (section 2).";
    return;
  } else {
    delete fErr.zone_ids;
  }

  submitting.value = true;
  try {
    await campaignStore.updateCampaign(route.params.id, {
      nom: form.nom.trim(),
      type: form.type === "COLLECTE" ? undefined : form.type,
      description: form.description ? form.description.trim() : "",
      date_debut: form.date_debut,
      date_fin: form.date_fin,
      zone_ids: form.zone_ids,
      statut: form.statut,
    });
    feedback.type = "success";
    feedback.message = "Campagne modifiée avec succès !";
    setTimeout(() => {
      router.push("/chef-projet/campagnes");
    }, 800);
  } catch (err) {
    feedback.type = "error";
    feedback.message =
      campaignStore.error || "Erreur lors de la modification de la campagne.";
  } finally {
    submitting.value = false;
  }
};

const supprimerCampagne = async () => {
  deleting.value = true;
  feedback.message = "";
  try {
    await campaignStore.deleteCampaign(route.params.id);
    confirmerSuppression.value = false;
    feedback.type = "success";
    feedback.message = "Campagne supprimée avec succès !";
    setTimeout(() => {
      router.push("/chef-projet/campagnes");
    }, 800);
  } catch (err) {
    feedback.type = "error";
    feedback.message =
      campaignStore.error || "Erreur lors de la suppression de la campagne.";
  } finally {
    deleting.value = false;
  }
};
</script>
