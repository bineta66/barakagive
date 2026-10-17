/**
 * useAutoRefresh — Actualisation intelligente sans polling permanent
 *
 * Stratégie :
 * 1. Chargement initial au montage — seulement si l'utilisateur est authentifié
 * 2. Re-chargement au retour sur l'onglet si les données sont périmées (> staleAfter)
 * 3. Zéro polling périodique — aucune requête inutile en fond
 * 4. Jamais de requête si pas de token (évite les 401 après déconnexion)
 */
import { onMounted, onUnmounted } from 'vue'

/**
 * @param {Function} fetchFn     — fonction async pour recharger les données
 * @param {number}  staleAfter   — délai ms après lequel les données sont périmées
 *                                 au retour sur l'onglet (défaut : 5 minutes)
 */
export function useAutoRefresh(fetchFn, staleAfter = 5 * 60_000) {
  let lastFetch = 0

  const isAuthenticated = () => !!localStorage.getItem('accessToken')

  const doFetch = () => {
    if (!isAuthenticated()) return
    fetchFn()
      .then(() => { lastFetch = Date.now() })
      .catch(() => { })
  }

  const onVisible = () => {
    if (document.visibilityState !== 'visible') return
    if (!isAuthenticated()) return
    const elapsed = Date.now() - lastFetch
    if (elapsed >= staleAfter) doFetch()
  }

  onMounted(() => {
    doFetch()
    document.addEventListener('visibilitychange', onVisible)
  })

  onUnmounted(() => {
    document.removeEventListener('visibilitychange', onVisible)
  })
}
