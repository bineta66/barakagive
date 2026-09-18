import { computed, ref } from "vue"
import { defineStore } from "pinia"
import { getErrorMessage } from "@/services/api.js"
import { financeService } from "@/modules/finance/services/financeService.js"

const asNumber = (value) => Number(value || 0)

export const useFinanceStore = defineStore("finance", () => {
  const finances = ref([])
  const projetsAssignes = ref([])
  const budgets = ref([])
  const donsFinancements = ref([])
  const depenses = ref([])
  const justificatifs = ref([])
  const bailleurs = ref([])
  const bailleurRecords = ref([])
  const postes = ref([])
  const statistiques = ref({ budgetTotal: 0, depensesRealisees: 0, soldeDisponible: 0, tauxExecution: 0 })
  const budgetsStatistiques = ref({ budgetTotal: 0, budgetConsomme: 0, soldeDisponible: 0, projetsBudgétises: 0 })
  const donsStatistiques = ref({ totalFinancements: 0, nombreBailleurs: 0, financementDuMois: 0, projetsFinances: 0 })
  const depensesStatistiques = ref({ depensesTotales: 0, depensesDuMois: 0, nombreOperations: 0, budgetRestant: 0 })
  const justificatifsStatistiques = ref({ valides: 0, enAttente: 0, montantJustifie: 0, depensesSansJustificatif: 0 })
  const depensesParCategorie = ref([])
  const dernieresOperations = ref([])
  const categoriesDepense = ref(["Alimentation", "Logistique", "Santé", "Éducation", "Transport", "Personnel", "Équipement"])
  const modesPaiement = ref(["Virement", "Chèque", "Espèces", "Mobile money"])
  const typesDocument = ref(["PDF", "JPG", "JPEG", "PNG"])
  const typesFinancement = ref(["Subvention", "Don", "Prêt", "Investissement"])
  const loading = ref(false)
  const error = ref(null)

  const formatMontant = (value) => asNumber(value).toLocaleString("fr-FR")
  const tauxExecutionValue = computed(() => statistiques.value.tauxExecution || 0)

  const refresh = async () => {
    loading.value = true
    error.value = null
    try {
      const [dashboard, projects, rawBudgets, rawDons, rawBailleurs, rawDepenses] = await Promise.all([
        financeService.fetchDashboard(),
        financeService.fetchProjects(),
        financeService.fetchBudgets(),
        financeService.fetchDonations(),
        financeService.fetchFunders(),
        financeService.fetchExpenses(),
      ])

      const projectMap = new Map(projects.map((project) => [String(project.id), project]))
      const funderMap = new Map(rawBailleurs.map((funder) => [String(funder.id), funder]))

      projetsAssignes.value = projects.map((project) => ({
        ...project,
        nom: project.name,
        chefProjet: project.chef_projet || "",
        budget: asNumber(project.budget),
        statut: project.archived ? "Archivé" : "En cours",
      }))
      finances.value = projetsAssignes.value
      bailleurRecords.value = rawBailleurs
      bailleurs.value = rawBailleurs.map((funder) => funder.nom)
      postes.value = []

      budgets.value = rawBudgets.map((budget) => {
        const project = projectMap.get(String(budget.projet))
        const posts = budget.postes || []
        const consumed = posts.reduce((sum, post) => sum + asNumber(post.montant_depense), 0)
        postes.value.push(...posts.map((post) => ({ ...post, budgetProjetId: budget.projet })))
        return {
          ...budget,
          projetId: budget.projet,
          projet: project?.name || budget.projet,
          chefProjet: project?.chef_projet || "",
          budgetTotal: asNumber(budget.montant_total),
          consomme: consumed,
          solde: asNumber(budget.montant_total) - consumed,
        }
      })

      donsFinancements.value = rawDons.map((don) => ({
        ...don,
        projetId: don.projet,
        projet: projectMap.get(String(don.projet))?.name || don.projet || "",
        bailleurId: don.bailleur,
        bailleur: funderMap.get(String(don.bailleur))?.nom || don.bailleur,
        date: don.date_reception,
        typeFinancement: don.statut,
      }))

      depenses.value = rawDepenses.map((expense) => {
        const project = projectMap.get(String(expense.projet))
        const attached = expense.justificatifs || []
        return {
          ...expense,
          projetId: expense.projet,
          projet: project?.name || expense.projet,
          categorie: expense.libelle,
          date: expense.date_depense,
          fournisseur: "",
          justificatif: attached.length ? attached[0].id : null,
        }
      })

      justificatifs.value = rawDepenses.flatMap((expense) => (expense.justificatifs || []).map((file) => ({
        ...file,
        depenseId: expense.id,
        depense: expense.libelle,
        projet: projectMap.get(String(expense.projet))?.name || expense.projet,
        typeDocument: file.type_fichier,
        numeroDocument: file.nom_original,
        dateDocument: file.created_at,
        nom: file.nom_original,
      })))

      statistiques.value = {
        budgetTotal: asNumber(dashboard.budget_total),
        depensesRealisees: asNumber(dashboard.montant_depense),
        soldeDisponible: asNumber(dashboard.solde),
        tauxExecution: dashboard.budget_total ? Math.round((dashboard.montant_depense / dashboard.budget_total) * 100) : 0,
      }
      budgetsStatistiques.value = {
        budgetTotal: asNumber(dashboard.budget_total),
        budgetConsomme: asNumber(dashboard.montant_depense),
        soldeDisponible: asNumber(dashboard.solde),
        projetsBudgétises: budgets.value.length,
      }
      donsStatistiques.value = {
        totalFinancements: donsFinancements.value.reduce((sum, don) => sum + asNumber(don.montant), 0),
        nombreBailleurs: new Set(donsFinancements.value.map((don) => don.bailleurId)).size,
        financementDuMois: 0,
        projetsFinances: new Set(donsFinancements.value.map((don) => don.projetId)).size,
      }
      depensesStatistiques.value = {
        depensesTotales: depenses.value.reduce((sum, expense) => sum + asNumber(expense.montant), 0),
        depensesDuMois: 0,
        nombreOperations: depenses.value.length,
        budgetRestant: asNumber(dashboard.solde),
      }
      justificatifsStatistiques.value = {
        valides: justificatifs.value.length,
        enAttente: 0,
        montantJustifie: 0,
        depensesSansJustificatif: depenses.value.filter((expense) => !expense.justificatif).length,
      }
      dernieresOperations.value = depenses.value.slice(0, 5).map((expense) => ({
        id: expense.id,
        date: expense.date,
        libelle: expense.libelle,
        montant: asNumber(expense.montant),
        type: "depense",
      }))
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const createBudget = async (data) => {
    await financeService.createBudget({ projet: data.projetId, don: data.donId, montant_total: data.budgetTotal, statut: "BROUILLON" })
    return refresh()
  }

  const createDonation = async (data) => {
    let bailleurId = data.bailleurId
    if (!bailleurId && data.bailleur) {
      const response = await financeService.createFunder({ nom: data.bailleur, actif: true })
      bailleurId = response.data.id
    }
    await financeService.createDonation({ bailleur: bailleurId, projet: data.projetId || null, montant: data.montant, devise: "XOF", date_reception: data.date, description: data.commentaire || "", statut: "RECU" })
    return refresh()
  }

  const createExpense = async (data) => {
    const post = postes.value.find((item) => String(item.id) === String(data.posteBudgetaireId))
      || postes.value.find((item) => String(item.budgetProjetId) === String(data.projetId))
    if (!post) throw new Error("Aucun poste budgétaire n'est disponible pour ce projet.")
    const response = await financeService.createExpense({ projet: data.projetId, poste_budgetaire: post.id, libelle: data.libelle, montant: data.montant, date_depense: data.date })
    await refresh()
    return response.data
  }

  const uploadJustification = async (expenseId, file) => {
    await financeService.uploadJustification(expenseId, file)
    return refresh()
  }

  refresh()

  return {
    finances, projetsAssignes, budgets, donsFinancements, depenses, justificatifs, bailleurs, bailleurRecords, postes,
    statistiques, budgetsStatistiques, donsStatistiques, depensesStatistiques, justificatifsStatistiques,
    depensesParCategorie, dernieresOperations, categoriesDepense, modesPaiement, typesDocument, typesFinancement,
    loading, error, formatMontant, tauxExecutionValue, fetchAll: refresh, refresh, createBudget, createDonation,
    createExpense, uploadJustification,
  }
})

