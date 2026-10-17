/**
 * offlineStorage.js — Stockage IndexedDB pour les agents terrain BarakaGive360
 *
 * Statuts de synchronisation :
 *   PENDING   → sauvegardé localement, pas encore envoyé
 *   SYNCING   → envoi en cours vers le serveur
 *   SYNCED    → envoyé et confirmé par le serveur
 *   FAILED    → échec d'envoi (erreur réseau / serveur)
 *   CONFLICT  → doublon détecté côté serveur
 *
 * Version DB : 3 (migration depuis versions précédentes)
 */

const DB_NAME = 'BarakaGiveOffline'
const DB_VERSION = 3
const STORE_BENEFICIAIRES = 'beneficiaires'

const LEGACY_CACHE_KEYS = ['bg_cached_campaigns', 'bg_cached_zones', 'bg_cached_forms']

const getScopedCacheKey = (name) => {
  try {
    const identity = JSON.parse(localStorage.getItem('user') || 'null')
    const userId = identity?.id
    const organization = identity?.organization
    const organizationId = identity?.organization_id ??
      (organization && typeof organization === 'object' ? organization.id : organization) ??
      'no-organization'
    if (!userId) return null
    return `bg_cached_${name}_org_${encodeURIComponent(String(organizationId))}_user_${encodeURIComponent(String(userId))}`
  } catch {
    return null
  }
}

const clearLegacyCacheKeys = () => {
  try {
    if (typeof localStorage !== 'undefined') {
      LEGACY_CACHE_KEYS.forEach((key) => localStorage.removeItem(key))
    }
  } catch { }
}

const getScopedDatabaseName = () => {
  let identity
  try {
    identity = JSON.parse(localStorage.getItem('user') || 'null')
  } catch {
    identity = null
  }
  if (!identity?.id) {
    throw new Error('Une session utilisateur est requise pour le stockage hors ligne.')
  }
  const organization = identity.organization
  const organizationId = identity.organization_id ??
    (organization && typeof organization === 'object' ? organization.id : organization) ??
    'no-organization'
  return `${DB_NAME}_org_${encodeURIComponent(String(organizationId))}_user_${encodeURIComponent(String(identity.id))}`
}

// ── Ouverture et migration de la base ─────────────────────────────────────────
const openDB = () => new Promise((resolve, reject) => {
  if (typeof window === 'undefined' || !window.indexedDB) {
    return reject(new Error('IndexedDB non disponible sur ce navigateur.'))
  }

  let scopedDatabaseName
  try {
    scopedDatabaseName = getScopedDatabaseName()
  } catch (error) {
    return reject(error)
  }

  const req = window.indexedDB.open(scopedDatabaseName, DB_VERSION)

  req.onupgradeneeded = (e) => {
    const db = e.target.result
    const oldVersion = e.oldVersion

    // Nettoyer les anciens stores (v1, v2)
    const obsoletes = ['pending_beneficiaries']
    obsoletes.forEach(name => {
      if (db.objectStoreNames.contains(name)) {
        db.deleteObjectStore(name)
      }
    })

    if (!db.objectStoreNames.contains(STORE_BENEFICIAIRES)) {
      const store = db.createObjectStore(STORE_BENEFICIAIRES, { keyPath: 'local_id' })
      store.createIndex('sync_status', 'sync_status', { unique: false })
      store.createIndex('campagne_id', 'campagne_id', { unique: false })
      store.createIndex('timestamp', 'timestamp', { unique: false })
    } else if (oldVersion < 3) {
      // Migration v2 → v3 : normaliser les statuts français vers anglais
      // (géré après ouverture, voir migrateLegacyStatuses)
    }
  }

  req.onsuccess = (e) => {
    const db = e.target.result
    // Migration asynchrone des anciens statuts français
    migrateLegacyStatuses(db).then(() => resolve(db)).catch(() => resolve(db))
  }

  req.onerror = (e) => reject(e.target.error)
})

// ── Migration des anciens statuts français (v2 → v3) ─────────────────────────
const migrateLegacyStatuses = (db) => new Promise((resolve) => {
  try {
    const tx = db.transaction([STORE_BENEFICIAIRES], 'readwrite')
    const store = tx.objectStore(STORE_BENEFICIAIRES)
    const req = store.getAll()

    req.onsuccess = () => {
      const items = req.result || []
      const needsMigration = items.filter(
        item => item.statut && !item.sync_status
      )

      const statusMap = {
        'EN_ATTENTE': 'PENDING',
        'SYNCHRONISE': 'SYNCED',
        'SYNCHRONISATION': 'SYNCING',
        'ECHEC': 'FAILED',
        'CONFLIT': 'CONFLICT',
      }

      for (const item of needsMigration) {
        item.sync_status = statusMap[item.statut] || 'PENDING'
        delete item.statut
        store.put(item)
      }

      tx.oncomplete = () => resolve()
      tx.onerror = () => resolve()
    }

    req.onerror = () => resolve()
  } catch {
    resolve()
  }
})

// ── API publique ──────────────────────────────────────────────────────────────
export const offlineStorage = {

  /**
   * Sauvegarder un bénéficiaire en attente de synchronisation.
   * Toujours créé avec sync_status = PENDING.
   */
  async saveBeneficiary(payload) {
    const db = await openDB()
    return new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_BENEFICIAIRES], 'readwrite')
      const store = tx.objectStore(STORE_BENEFICIAIRES)

      const record = {
        local_id: payload.local_id || crypto.randomUUID(),
        campagne_id: payload.campagne_id,
        campagne_nom: payload.campagne_nom || '',
        zone_id: payload.zone_id,
        zone_nom: payload.zone_nom || '',
        formulaire_id: payload.formulaire_id || null,
        beneficiary: payload.beneficiary || {},
        responses: payload.responses || [],
        sync_status: 'PENDING',
        timestamp: payload.timestamp || new Date().toISOString(),
        synced_at: null,
        server_id: null,
        error_message: null,
      }

      const req = store.put(record)
      req.onsuccess = () => resolve(record)
      req.onerror = (e) => reject(e.target.error)
    })
  },

  /**
   * Mettre à jour le statut de synchronisation d'un enregistrement.
   * @param {string} localId
   * @param {'PENDING'|'SYNCING'|'SYNCED'|'FAILED'|'CONFLICT'} status
   * @param {object} meta — champs supplémentaires (server_id, error_message…)
   */
  async updateStatus(localId, status, meta = {}) {
    const db = await openDB()
    return new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_BENEFICIAIRES], 'readwrite')
      const store = tx.objectStore(STORE_BENEFICIAIRES)
      const getReq = store.get(localId)

      getReq.onsuccess = () => {
        const record = getReq.result
        if (!record) return resolve(null)

        record.sync_status = status
        if (status === 'SYNCED' || status === 'CONFLICT') {
          record.synced_at = new Date().toISOString()
        }
        if (meta.server_id !== undefined) record.server_id = meta.server_id
        if (meta.error_message !== undefined) record.error_message = meta.error_message

        store.put(record)
        resolve(record)
      }
      getReq.onerror = (e) => reject(e.target.error)
    })
  },

  /**
   * Récupérer tous les enregistrements à synchroniser (PENDING, SYNCING, et optionnellement FAILED).
   * @param {boolean} includeFailed - inclure les enregistrements ayant échoué pour réessai
   */
  async getPendingBeneficiaries(includeFailed = true) {
    const db = await openDB()
    return new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_BENEFICIAIRES], 'readonly')
      const store = tx.objectStore(STORE_BENEFICIAIRES)
      const req = store.getAll()

      req.onsuccess = () => {
        const all = req.result || []
        const validStatuses = includeFailed
          ? ['PENDING', 'SYNCING', 'FAILED']
          : ['PENDING', 'SYNCING']
        resolve(all.filter(i => validStatuses.includes(i.sync_status)))
      }
      req.onerror = (e) => reject(e.target.error)
    })
  },

  /**
   * Récupérer tous les enregistrements (tous statuts).
   */
  async getAll() {
    const db = await openDB()
    return new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_BENEFICIAIRES], 'readonly')
      const req = tx.objectStore(STORE_BENEFICIAIRES).getAll()
      req.onsuccess = () => resolve(req.result || [])
      req.onerror = (e) => reject(e.target.error)
    })
  },

  /**
   * Récupérer les enregistrements d'une campagne spécifique.
   */
  async getByCampagne(campagneId) {
    const all = await this.getAll()
    return all.filter(i => String(i.campagne_id) === String(campagneId))
  },

  /**
   * Supprimer un enregistrement local.
   */
  async delete(localId) {
    const db = await openDB()
    return new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_BENEFICIAIRES], 'readwrite')
      const req = tx.objectStore(STORE_BENEFICIAIRES).delete(localId)
      req.onsuccess = () => resolve(true)
      req.onerror = (e) => reject(e.target.error)
    })
  },

  /**
   * Statistiques par statut.
   * @returns {{ pending, syncing, synced, failed, conflict, total }}
   */
  async getStats() {
    try {
      const all = await this.getAll()
      return {
        pending: all.filter(i => i.sync_status === 'PENDING').length,
        syncing: all.filter(i => i.sync_status === 'SYNCING').length,
        synced: all.filter(i => i.sync_status === 'SYNCED').length,
        failed: all.filter(i => i.sync_status === 'FAILED').length,
        conflict: all.filter(i => i.sync_status === 'CONFLICT').length,
        total: all.length,
      }
    } catch {
      return { pending: 0, syncing: 0, synced: 0, failed: 0, conflict: 0, total: 0 }
    }
  },

  // ── Rétro-compatibilité ───────────────────────────────────────────────────
  async getAllBeneficiaries() { return this.getAll() },
  async getPending() { return this.getPendingBeneficiaries() },
  async markSynchronise(localId, serverId = null) {
    return this.updateStatus(localId, 'SYNCED', { server_id: serverId })
  },
  async markSynced(localId, serverId) {
    return this.updateStatus(localId, 'SYNCED', { server_id: serverId })
  },
  async getCounts() {
    const stats = await this.getStats()
    return {
      total: stats.total,
      enAttente: stats.pending,
      synchronise: stats.synced,
    }
  },

  // ── Cache des campagnes & zones pour le mode hors connexion ───────────────
  saveCachedCampaigns(campaigns) {
    try {
      clearLegacyCacheKeys()
      const key = getScopedCacheKey('campaigns')
      if (typeof localStorage !== 'undefined' && key && Array.isArray(campaigns) && campaigns.length) {
        localStorage.setItem(key, JSON.stringify(campaigns))
      }
    } catch { }
  },
  getCachedCampaigns() {
    try {
      clearLegacyCacheKeys()
      const key = getScopedCacheKey('campaigns')
      if (typeof localStorage !== 'undefined' && key) {
        const raw = localStorage.getItem(key)
        return raw ? JSON.parse(raw) : []
      }
    } catch { }
    return []
  },
  saveCachedZones(zones) {
    try {
      clearLegacyCacheKeys()
      const key = getScopedCacheKey('zones')
      if (typeof localStorage !== 'undefined' && key && Array.isArray(zones) && zones.length) {
        localStorage.setItem(key, JSON.stringify(zones))
      }
    } catch { }
  },
  getCachedZones() {
    try {
      clearLegacyCacheKeys()
      const key = getScopedCacheKey('zones')
      if (typeof localStorage !== 'undefined' && key) {
        const raw = localStorage.getItem(key)
        return raw ? JSON.parse(raw) : []
      }
    } catch { }
    return []
  },
  saveCachedForm(campaignId, form) {
    try {
      clearLegacyCacheKeys()
      const key = getScopedCacheKey('forms')
      if (typeof localStorage !== 'undefined' && key && campaignId && form?.id) {
        const cached = JSON.parse(localStorage.getItem(key) || '{}')
        cached[String(campaignId)] = form
        localStorage.setItem(key, JSON.stringify(cached))
      }
    } catch { }
  },
  getCachedForm(campaignId) {
    try {
      clearLegacyCacheKeys()
      const key = getScopedCacheKey('forms')
      if (typeof localStorage !== 'undefined' && key) {
        const cached = JSON.parse(localStorage.getItem(key) || '{}')
        return cached[String(campaignId)] || null
      }
    } catch { }
    return null
  },
}
