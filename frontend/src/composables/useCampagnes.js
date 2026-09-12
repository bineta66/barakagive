import { ref, computed } from "vue"
import { campagnesMock } from "@/data/campagnesMock.js"

export function useCampagnes() {
  const recherche = ref("")
  const filtreStatut = ref("Tous les statuts")
  const filtreProjet = ref("Tous les projets")
  const filtreZone = ref("Toutes les zones")
  const pageCourante = ref(1)
  const parPage = 5

  const campagnesFiltrees = computed(() => {
    return campagnesMock.value.filter((c) => {
      const okRecherche =
        c.nom.toLowerCase().includes(recherche.value.toLowerCase()) ||
        c.code.toLowerCase().includes(recherche.value.toLowerCase())

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
    return Math.max(1, Math.ceil(campagnesFiltrees.value.length / parPage))
  })

  const campagnesPage = computed(() => {
    const start = (pageCourante.value - 1) * parPage
    return campagnesFiltrees.value.slice(start, start + parPage)
  })

  const statistiques = computed(() => {
    const total = campagnesMock.value.length
    const actives = campagnesMock.value.filter((c) => c.statut === "En cours").length
    const planifiees = campagnesMock.value.filter((c) => c.statut === "Planifiée").length
    const terminees = campagnesMock.value.filter((c) => c.statut === "Terminée").length
    return { total, actives, planifiees, terminees }
  })

  const reinitialiserFiltres = () => {
    recherche.value = ""
    filtreStatut.value = "Tous les statuts"
    filtreProjet.value = "Tous les projets"
    filtreZone.value = "Toutes les zones"
    pageCourante.value = 1
  }

  return {
    recherche,
    filtreStatut,
    filtreProjet,
    filtreZone,
    pageCourante,
    campagnesFiltrees,
    campagnesPage,
    totalPages,
    statistiques,
    reinitialiserFiltres,
  }
}
