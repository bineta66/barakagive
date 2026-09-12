import { ref, computed } from "vue"
import { beneficiairesMock, regionsMock, zonesMock, syntheseMock } from "@/data/beneficiairesMock.js"

export function useBeneficiaires() {
  const beneficiaires = ref([])
  const regionSelectionnee = ref("")
  const zoneSelectionnee = ref("")
  const recherche = ref("")
  const filtreStatut = ref("")
  const pageCourante = ref(1)
  const parPage = 10

  const regions = regionsMock
  const zones = computed(() => {
    if (!regionSelectionnee.value) return []
    return zonesMock[regionSelectionnee.value] || []
  })

  const statistiques = computed(() => {
    const base = regionSelectionnee.value ? beneficiaires.value.filter((b) => b.region === regionSelectionnee.value) : beneficiaires.value
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
      liste = liste.filter((b) => b.region === regionSelectionnee.value)
    }
    if (zoneSelectionnee.value) {
      liste = liste.filter((b) => b.zone === zoneSelectionnee.value)
    }
    return [...liste]
      .sort((a, b) => b.scoreIA - a.scoreIA)
      .slice(0, 5)
  })

  const synthese = computed(() => {
    return {
      region: regionSelectionnee.value || syntheseMock.region,
      zone: zoneSelectionnee.value || syntheseMock.zone,
      totalBeneficiaires: statistiques.value.total,
      campagnesActives: regionSelectionnee.value ? Math.floor(Math.random() * 5) + 1 : syntheseMock.campagnesActives,
      projetPrincipal: syntheseMock.projetPrincipal,
      urgencesElevees: statistiques.value.critiques + statistiques.value.eleves,
    }
  })

  const beneficiairesFiltres = computed(() => {
    let liste = beneficiaires.value
    if (regionSelectionnee.value) {
      liste = liste.filter((b) => b.region === regionSelectionnee.value)
    }
    if (zoneSelectionnee.value) {
      liste = liste.filter((b) => b.zone === zoneSelectionnee.value)
    }
    if (recherche.value) {
      const search = recherche.value.toLowerCase()
      liste = liste.filter((b) => b.nom.toLowerCase().includes(search) || b.prenom.toLowerCase().includes(search) || b.id.toLowerCase().includes(search))
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

  const initialiser = () => {
    beneficiaires.value = JSON.parse(JSON.stringify(beneficiairesMock))
    regionSelectionnee.value = ""
    zoneSelectionnee.value = ""
    recherche.value = ""
    filtreStatut.value = ""
    pageCourante.value = 1
  }

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

  initialiser()

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
