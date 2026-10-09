import { ref, computed, onMounted } from "vue"
import { useBeneficiaryStore } from "@/stores/beneficiary.js"
import { useZoneStore } from "@/stores/zone.js"
import { watch } from "vue"

export function useBeneficiaires() {
  const beneficiaryStore = useBeneficiaryStore()
  const zoneStore = useZoneStore()

  const regionSelectionnee = ref("")
  const zoneSelectionnee = ref("")
  const recherche = ref("")
  const filtreStatut = ref("")
  const pageCourante = ref(1)
  const parPage = 10

  const defaultRegions = [
    "Dakar", "Thiès", "Diourbel", "Fatick", "Kaolack", "Kaffrine",
    "Saint-Louis", "Louga", "Matam", "Tambacounda", "Kédougou",
    "Kolda", "Sédhiou", "Ziguinchor"
  ]

  onMounted(() => {
    zoneStore.fetchZones().catch(() => {})
  })

  watch([pageCourante, regionSelectionnee, zoneSelectionnee, recherche, filtreStatut], () => {
    const params = {
      page: pageCourante.value,
      page_size: parPage,
      search: recherche.value.trim(),
    }
    if (regionSelectionnee.value) params.region = regionSelectionnee.value
    if (zoneSelectionnee.value) {
      const selectedZone = zoneStore.zones.find((zone) => zone.nom === zoneSelectionnee.value)
      if (selectedZone?.id) params.zone_id = selectedZone.id
    }
    if (filtreStatut.value) params.statut = filtreStatut.value
    beneficiaryStore.fetchBeneficiaries(params).catch(() => {})
  }, { immediate: true })
  watch([regionSelectionnee, zoneSelectionnee, recherche, filtreStatut], () => {
    if (pageCourante.value !== 1) pageCourante.value = 1
  })

  const regions = computed(() => {
    const fromZones = zoneStore.zones.map((z) => z.region).filter(Boolean)
    return Array.from(new Set([...fromZones, ...defaultRegions]))
  })

  const zones = computed(() => {
    if (!regionSelectionnee.value) return zoneStore.zones.map((z) => z.nom)
    return zoneStore.zones
      .filter((z) => (z.region || "").toLowerCase() === regionSelectionnee.value.toLowerCase())
      .map((z) => z.nom)
  })

  const normaliser = (b) => {
    const score = Number(b.score_vulnerabilite)
    const scoreValide = Number.isFinite(score) ? score : null
    return {
      id: b.id,
      nom: b.full_name || b.nom || "Anonyme",
      prenom: "",
      phone: b.phone,
      nin: b.nin,
      region: b.zone?.region || b.region || "Dakar",
      zone: b.zone?.nom || b.zone || "Zone générale",
      statut: scoreValide === null ? "Non évalué" : scoreValide >= 80 ? "Critique" : scoreValide >= 50 ? "Élevé" : "Normal",
      scoreVulnerabilite: scoreValide,
      vulnerabilite: b.vulnerability_criteria || "Non spécifié",
    }
  }

  const beneficiaires = computed(() => {
    return beneficiaryStore.beneficiaries.map(normaliser)
  })

  const statistiques = computed(() => {
    const base = regionSelectionnee.value
      ? beneficiaires.value.filter((b) => b.region.toLowerCase() === regionSelectionnee.value.toLowerCase())
      : beneficiaires.value
    const parZone = zoneSelectionnee.value ? base.filter((b) => b.zone === zoneSelectionnee.value) : base

    return {
      total: beneficiaryStore.pagination.count,
      critiques: parZone.filter((b) => b.statut === "Critique").length,
      eleves: parZone.filter((b) => b.statut === "Élevé").length,
      zones: new Set(parZone.map((b) => b.zone)).size,
    }
  })

  const beneficiairesUrgents = computed(() => {
    let liste = beneficiaires.value
    if (regionSelectionnee.value) {
      liste = liste.filter((b) => b.region.toLowerCase() === regionSelectionnee.value.toLowerCase())
    }
    if (zoneSelectionnee.value) {
      liste = liste.filter((b) => b.zone === zoneSelectionnee.value)
    }
    return [...liste].sort((a, b) => (b.scoreVulnerabilite ?? -1) - (a.scoreVulnerabilite ?? -1)).slice(0, 5)
  })

  const synthese = computed(() => {
    return {
      region: regionSelectionnee.value || "Toutes les régions",
      zone: zoneSelectionnee.value || "Toutes les zones",
      totalBeneficiaires: statistiques.value.total,
      campagnesActives: 1,
      projetPrincipal: "Distribution d'Urgence",
      urgencesElevees: statistiques.value.critiques + statistiques.value.eleves,
    }
  })

  const beneficiairesFiltres = computed(() => {
    let liste = beneficiaires.value
    if (regionSelectionnee.value) {
      liste = liste.filter((b) => b.region.toLowerCase() === regionSelectionnee.value.toLowerCase())
    }
    if (zoneSelectionnee.value) {
      liste = liste.filter((b) => b.zone === zoneSelectionnee.value)
    }
    if (recherche.value) {
      const q = recherche.value.toLowerCase()
      liste = liste.filter((b) => b.nom.toLowerCase().includes(q) || String(b.id).toLowerCase().includes(q))
    }
    if (filtreStatut.value) {
      liste = liste.filter((b) => b.statut === filtreStatut.value)
    }
    return liste
  })

  const totalPages = computed(() => Math.max(1, Math.ceil(beneficiaryStore.pagination.count / parPage)))

  const beneficiairesPage = computed(() => {
    return beneficiairesFiltres.value
  })

  const selectionnerRegion = (region) => {
    regionSelectionnee.value = region
    zoneSelectionnee.value = ""
    pageCourante.value = 1
  }

  const selectionnerZone = (zone) => {
    zoneSelectionnee.value = zone
    pageCourante.value = 1
  }

  const reinitialiserFiltres = () => {
    regionSelectionnee.value = ""
    zoneSelectionnee.value = ""
    recherche.value = ""
    filtreStatut.value = ""
    pageCourante.value = 1
  }

  return {
    beneficiaires,
    regions,
    zones,
    regionSelectionnee,
    zoneSelectionnee,
    recherche,
    filtreStatut,
    pageCourante,
    parPage,
    beneficiairesFiltres,
    beneficiairesPage,
    totalPages,
    statistiques,
    beneficiairesUrgents,
    synthese,
    selectionnerRegion,
    selectionnerZone,
    reinitialiserFiltres,
  }
}

