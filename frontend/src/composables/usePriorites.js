import { ref, computed } from "vue";
import api from "@/services/api.js";

/**
 * Composable pour la Carte des Priorités.
 * Gère le chargement des données régionales depuis Django.
 * Aucun calcul n'est effectué ici — tout vient du backend.
 */
export function usePriorites() {
  // ── État ──────────────────────────────────────────────────────────────────
  const projetSelectionne = ref(null);
  const regions = ref([]); // [{region, score, total_beneficiaires, niveau, couleur}]
  const regionSelectionnee = ref(null); // nom de la région cliquée
  const detailRegion = ref(null); // données complètes de la région sélectionnée
  const drawerOuvert = ref(false);
  const chargementCarte = ref(false);
  const chargementRegion = ref(false);
  const erreur = ref(null);
  const projets = ref([]); // liste des projets disponibles
  const chargementProjets = ref(false);
  const derniereMaj = ref(null);

  // ── Computed ──────────────────────────────────────────────────────────────
  const totalBeneficiaires = computed(() => {
    return regions.value.reduce((sum, r) => sum + (r.total_beneficiaires || 0), 0);
  });

  const regionsParNom = computed(() => {
    const map = {};
    regions.value.forEach((r) => {
      map[r.region.toLowerCase()] = r;
    });
    return map;
  });

  // ── Actions ───────────────────────────────────────────────────────────────

  /**
   * Charge la liste des projets du chef de projet
   */
  async function chargerProjets() {
    chargementProjets.value = true;
    try {
      const response = await api.get("/api/projects/");
      projets.value = response.data || [];
      if (projets.value.length > 0 && !projetSelectionne.value) {
        projetSelectionne.value = projets.value[0];
        await chargerRegions(projetSelectionne.value.id);
      }
    } catch (e) {
      erreur.value = "Impossible de charger les projets.";
    } finally {
      chargementProjets.value = false;
    }
  }

  /**
   * Charge les scores de toutes les régions pour coloriser la carte SVG
   * @param {number} projetId
   */
  async function chargerRegions(projetId) {
    chargementCarte.value = true;
    erreur.value = null;
    try {
      const response = await api.get(`/api/projets/${projetId}/regions/`);
      regions.value = response.data || [];
      derniereMaj.value = new Date().toLocaleString("fr-FR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (e) {
      erreur.value = "Impossible de charger les scores des régions.";
      regions.value = [];
    } finally {
      chargementCarte.value = false;
    }
  }

  /**
   * Charge le détail complet d'une région (zones + bénéficiaires + critères)
   * @param {number} projetId
   * @param {string} regionName
   */
  async function chargerDetailRegion(projetId, regionName) {
    chargementRegion.value = true;
    erreur.value = null;
    try {
      const encoded = encodeURIComponent(regionName);
      const response = await api.get(
        `/api/projets/${projetId}/regions/${encoded}/priorites/`
      );
      detailRegion.value = response.data;
    } catch (e) {
      erreur.value = `Impossible de charger les données de ${regionName}.`;
      detailRegion.value = null;
    } finally {
      chargementRegion.value = false;
    }
  }

  /**
   * Sélectionne une région et charge son détail
   * @param {string} regionName
   */
  async function selectionnerRegion(regionName) {
    if (!projetSelectionne.value) return;
    regionSelectionnee.value = regionName;
    drawerOuvert.value = true;
    await chargerDetailRegion(projetSelectionne.value.id, regionName);
  }

  /**
   * Ferme le drawer et réinitialise la sélection
   */
  function fermerDrawer() {
    drawerOuvert.value = false;
    regionSelectionnee.value = null;
    detailRegion.value = null;
  }

  /**
   * Change le projet sélectionné et recharge les données
   * @param {object} projet
   */
  async function changerProjet(projet) {
    projetSelectionne.value = projet;
    fermerDrawer();
    await chargerRegions(projet.id);
  }

  return {
    // État
    projets,
    projetSelectionne,
    regions,
    regionSelectionnee,
    detailRegion,
    drawerOuvert,
    chargementCarte,
    chargementRegion,
    chargementProjets,
    erreur,
    derniereMaj,
    // Computed
    totalBeneficiaires,
    regionsParNom,
    // Actions
    chargerProjets,
    chargerRegions,
    chargerDetailRegion,
    selectionnerRegion,
    fermerDrawer,
    changerProjet,
  };
}

