import { ref, computed, onMounted } from "vue"
import { useProjectStore } from "@/stores/project.js"

export function useFinances() {
  const projectStore = useProjectStore()

  const recherche = ref("")
  const filtreStatut = ref("Tous les statuts")
  const filtreProjet = ref("Tous les projets")
  const filtreRegion = ref("Toutes les régions")
  const pageCourante = ref(1)
  const parPage = 10

  onMounted(() => {
    projectStore.fetchProjects().catch(() => {})
  })

  const projetsFinance = computed(() => {
    return projectStore.projects.map((p) => {
      const budget = parseFloat(p.budget) || 0
      const montantEngage = Math.round(budget * 0.45)
      const montantRestant = budget - montantEngage
      const taux = budget > 0 ? Math.round((montantEngage / budget) * 100) : 0

      return {
        id: p.id,
        code: p.code,
        nom: p.name || p.nom,
        region: p.region || "Générale",
        budgetAllocation: budget,
        montantEngage,
        montantRestant,
        tauxExecution: taux,
        statut: p.archived ? "Clôturé" : "En cours",
        dateDebut: p.start_date || "-",
        dateFin: p.end_date || "-",
      }
    })
  })

  const financesFiltrees = computed(() => {
    return projetsFinance.value.filter((f) => {
      const q = recherche.value.toLowerCase()
      const okRecherche =
        !q ||
        (f.nom || "").toLowerCase().includes(q) ||
        (f.code || "").toLowerCase().includes(q)

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
    const budgetTotal = projetsFinance.value.reduce((sum, f) => sum + f.budgetAllocation, 0)
    const totalEngage = projetsFinance.value.reduce((sum, f) => sum + f.montantEngage, 0)
    const totalRestant = budgetTotal - totalEngage
    const tauxExecution = budgetTotal > 0 ? Math.round((totalEngage / budgetTotal) * 100) : 0

    return {
      budgetTotal,
      totalEngage,
      totalRestant,
      tauxExecution,
    }
  })

  const regionsFinance = computed(() => {
    const set = new Set(projectStore.projects.map((p) => p.region).filter(Boolean))
    return Array.from(set)
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
    regionsFinance,
    reinitialiserFiltres,
    projetsDetail: projetsFinance,
    projectStore,
  }
}

