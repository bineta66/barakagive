import { ref, computed, onMounted } from "vue"
import { useCampaignStore } from "@/stores/campaign.js"
import { watch } from "vue"

export function useCampagnes() {
  const campaignStore = useCampaignStore()
  const recherche = ref("")
  const filtreStatut = ref("Tous les statuts")
  const filtreProjet = ref("Tous les projets")
  const filtreZone = ref("Toutes les zones")
  const pageCourante = ref(1)
  const parPage = 8

  const statutLabel = (statut) => {
    switch (statut) {
      case "BROUILLON":
        return "Brouillon"
      case "PLANIFIER":
        return "Planifiée"
      case "EN_COURS":
        return "En cours"
      case "TERMINE":
        return "Terminée"
      case "ANNULEE":
        return "Annulée"
      default:
        return statut || "-"
    }
  }

  const determineStatus = (c) => {
    if (c.statut) return statutLabel(c.statut)
    const today = new Date().toISOString().split("T")[0]
    if (c.date_debut && c.date_debut > today) return "Planifiée"
    if (c.date_fin && c.date_fin < today) return "Terminée"
    return "En cours"
  }

  const normaliserCampagne = (c) => {
    return {
      ...c,
      nom: c.nom,
      code: c.code_campagne || c.code || `CMP-${c.id?.substring ? c.id.substring(0, 6) : c.id}`,
      projet: c.projet?.name || (typeof c.projet === "string" ? c.projet : "-"),
      zone: c.zones_count ? `${c.zones_count} zone(s)` : (c.zone || "-"),
      statut: determineStatus(c),
      dateDebut: c.date_debut,
      dateFin: c.date_fin,
    }
  }

  const campagnesNormalisees = computed(() => {
    return campaignStore.campaigns.map(normaliserCampagne)
  })

  const campagnesFiltrees = computed(() => {
    return campagnesNormalisees.value.filter((c) => {
      const q = recherche.value.toLowerCase()
      const okRecherche =
        !q ||
        (c.nom || "").toLowerCase().includes(q) ||
        (c.code || "").toLowerCase().includes(q)

      const okStatut =
        filtreStatut.value === "Tous les statuts" ||
        c.statut === filtreStatut.value

      const okProjet =
        filtreProjet.value === "Tous les projets" ||
        c.projet === filtreProjet.value

      const okZone =
        filtreZone.value === "Toutes les zones" ||
        c.zone === filtreZone.value

      return okRecherche && okStatut && okProjet && okZone
    })
  })

  const totalPages = computed(() => {
    return Math.max(1, Math.ceil(campaignStore.totalCampaigns / parPage))
  })

  const campagnesPage = computed(() => {
    return campagnesFiltrees.value
  })
  const pagesVisibles = computed(() => {
    const start = Math.max(1, pageCourante.value - 2)
    const end = Math.min(totalPages.value, pageCourante.value + 2)
    return Array.from({ length: end - start + 1 }, (_value, index) => start + index)
  })

  const statistiques = computed(() => {
    const total = campaignStore.totalCampaigns
    const actives = campagnesNormalisees.value.filter((c) => c.statut === "En cours").length
    const planifiees = campagnesNormalisees.value.filter((c) => c.statut === "Planifiée").length
    const terminees = campagnesNormalisees.value.filter((c) => c.statut === "Terminée").length
    return { total, actives, planifiees, terminees }
  })

  const reinitialiserFiltres = () => {
    recherche.value = ""
    filtreStatut.value = "Tous les statuts"
    filtreProjet.value = "Tous les projets"
    filtreZone.value = "Toutes les zones"
    pageCourante.value = 1
  }

  watch([pageCourante, recherche, filtreStatut, filtreProjet], () => {
    const statutMap = {
      Brouillon: "BROUILLON",
      "Planifiée": "PLANIFIER",
      "En cours": "EN_COURS",
      "Terminée": "TERMINE",
      "Annulée": "ANNULEE",
    }
    campaignStore.fetchCampaigns({
      page: pageCourante.value,
      page_size: parPage,
      search: recherche.value.trim(),
      statut: statutMap[filtreStatut.value] || "",
      projet: filtreProjet.value === "Tous les projets" ? "" : filtreProjet.value,
    }).catch(() => {})
  }, { immediate: true })
  watch([recherche, filtreStatut, filtreProjet], () => {
    if (pageCourante.value !== 1) pageCourante.value = 1
  })
  watch(totalPages, (count) => {
    if (pageCourante.value > count) pageCourante.value = count
  })

  return {
    recherche,
    filtreStatut,
    filtreProjet,
    filtreZone,
    pageCourante,
    campagnesFiltrees,
    campagnesPage,
    totalPages,
    pagesVisibles,
    statistiques,
    reinitialiserFiltres,
    campaignStore,
  }
}


