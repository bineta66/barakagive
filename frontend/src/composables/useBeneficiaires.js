import { ref, computed, onMounted } from "vue"
import { useBeneficiaryStore } from "@/stores/beneficiary.js"
import { useZoneStore } from "@/stores/zone.js"

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
    beneficiaryStore.fetchBeneficiaries().catch(() => {})
    zoneStore.fetchZones().catch(() => {})
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
    return {
      id: b.id,
      nom: b.full_name || b.nom || "Anonyme",
      prenom: "",
      phone: b.phone,
      nin: b.nin,
      region: b.zone?.region || b.region || "Dakar",
      zone: b.zone?.nom || b.zone || "Zone générale",
      statut: (b.ai_score || 0) >= 80 ? "Critique" : (b.ai_score || 0) >= 50 ? "Élevé" : "Normal",
      scoreIA: b.ai_score || 50,
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
      total: parZone.length,
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
    return [...liste].sort((a, b) => b.scoreIA - a.scoreIA).slice(0, 5)
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

  const totalPages = computed(() => Math.max(1, Math.ceil(beneficiairesFiltres.value.length / parPage)))

  const beneficiairesPage = computed(() => {
    const start = (pageCourante.value - 1) * parPage
    return beneficiairesFiltres.value.slice(start, start + parPage)
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

