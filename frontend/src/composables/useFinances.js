import { ref, computed, watch } from "vue"
import { financesMock, projetsFinanceMock, regionsFinanceMock, projetsDetailFinanceMock } from "@/data/financesMock.js"

export function useFinances() {
  const recherche = ref("")
  const filtreStatut = ref("Tous les statuts")
  const filtreProjet = ref("Tous les projets")
  const filtreRegion = ref("Toutes les régions")
  const pageCourante = ref(1)
  const parPage = 5

  const financesFiltrees = computed(() => {
    return financesMock.value.filter((f) => {
      const okRecherche =
        f.nom.toLowerCase().includes(recherche.value.toLowerCase()) ||
        f.code.toLowerCase().includes(recherche.value.toLowerCase())

      const okStatut =
        filtreStatut.value === "Tous les statuts" ||
        f.statut === filtreStatut.value

      const okProjet =
        filtreProjet.value === "Tous les projets" ||
        f.nom === filtreProjet.value

      const okRegion =
        filtreRegion.value === "Toutes les régions" ||
        f.region === filtreRegion.value

      return okRecherche && okStatut && okProjet && okRegion
    })
  })

  const totalPages = computed(() => {
    return Math.max(1, Math.ceil(financesFiltrees.value.length / parPage))
  })

  const financesPage = computed(() => {
    const start = (pageCourante.value - 1) * parPage
    return financesFiltrees.value.slice(start, start + parPage)
  })

  const statistiques = computed(() => {
    const budgetTotal = financesMock.value.reduce((sum, f) => sum + f.budgetAllocation, 0)
    const totalEngage = financesMock.value.reduce((sum, f) => sum + f.montantEngage, 0)
    const totalRestant = budgetTotal - totalEngage
    const tauxExecution = budgetTotal > 0 ? Math.round((totalEngage / budgetTotal) * 100) : 0

    return {
      budgetTotal,
      totalEngage,
      totalRestant,
      tauxExecution,
    }
  })

  const reinitialiserFiltres = () => {
    recherche.value = ""
    filtreStatut.value = "Tous les statuts"
    filtreProjet.value = "Tous les projets"
    filtreRegion.value = "Toutes les régions"
    pageCourante.value = 1
  }

  return {
    recherche,
    filtreStatut,
    filtreProjet,
    filtreRegion,
    pageCourante,
    financesFiltrees,
    financesPage,
    totalPages,
    statistiques,
    projets: projetsFinanceMock,
    regions: regionsFinanceMock,
    projetsDetail: projetsDetailFinanceMock,
    reinitialiserFiltres,
  }
}
