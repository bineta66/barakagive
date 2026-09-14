import { ref, computed } from "vue"
import { defineStore } from "pinia"
import { superAdminService } from "@/modules/super-admin/services/superAdminService.js"

export const useSuperAdminStore = defineStore("superAdmin", () => {
  const demandesONG = ref([])
  const ongs = ref([])
  const abonnements = ref([])
  const statistiques = ref({
    totalONG: 0,
    ongActives: 0,
    totalUtilisateurs: 0,
    totalProjets: 0,
    revenuMensuel: 0,
    tauxActivation: 0,
    abonnementsActifs: 0,
    abonnementsExpires: 0,
  })
  const listeDemandes = ref([])
  const loading = ref(false)
  const error = ref(null)

  const formatMontant = (montant) => {
    if (!montant) return "0"
    return montant.toLocaleString("fr-FR")
  }

  const fetchAll = async () => {
    loading.value = true
    error.value = null
    try {
      demandesONG.value = superAdminService.getDemandesONG().value
      ongs.value = superAdminService.getONGs().value
      abonnements.value = superAdminService.getAbonnements().value
      statistiques.value = superAdminService.getStatistiques()
      listeDemandes.value = superAdminService.getDemandeStatistiques()
    } catch (e) {
      error.value = e.message || "Erreur lors du chargement des données"
    } finally {
      loading.value = false
    }
  }

  fetchAll()

  return {
    demandesONG,
    ongs,
    abonnements,
    statistiques,
    listeDemandes,
    loading,
    error,
    formatMontant,
    fetchAll,
  }
})

