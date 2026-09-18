const DB_NAME = "BarakaGiveOffline"
const DB_VERSION = 1
const STORE_NAME = "pending_beneficiaries"

const openDatabase = () => {
  return new Promise((resolve, reject) => {
    if (typeof window === "undefined" || !window.indexedDB) {
      return reject(new Error("IndexedDB n'est pas supporté par ce navigateur."))
    }

    const request = window.indexedDB.open(DB_NAME, DB_VERSION)

    request.onupgradeneeded = (event) => {
      const db = event.target.result
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: "local_id" })
        store.createIndex("sync_status", "sync_status", { unique: false })
        store.createIndex("campagne_id", "campagne_id", { unique: false })
        store.createIndex("created_at", "created_at", { unique: false })
      }
    }

    request.onsuccess = (event) => resolve(event.target.result)
    request.onerror = (event) => reject(event.target.error)
  })
}

export const offlineStorage = {
  async saveBeneficiary(item) {
    const db = await openDatabase()
    return new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_NAME], "readwrite")
      const store = tx.objectStore(STORE_NAME)

      const record = {
        ...item,
        sync_status: item.sync_status || "PENDING",
        created_at: item.created_at || new Date().toISOString(),
      }

      const request = store.put(record)
      request.onsuccess = () => resolve(record)
      request.onerror = (e) => reject(e.target.error)
    })
  },

  async getPendingBeneficiaries() {
    const db = await openDatabase()
    return new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_NAME], "readonly")
      const store = tx.objectStore(STORE_NAME)
      const request = store.getAll()

      request.onsuccess = () => {
        const all = request.result || []
        const pending = all.filter((i) => i.sync_status === "PENDING")
        resolve(pending)
      }
      request.onerror = (e) => reject(e.target.error)
    })
  },

  async getAllBeneficiaries() {
    const db = await openDatabase()
    return new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_NAME], "readonly")
      const store = tx.objectStore(STORE_NAME)
      const request = store.getAll()

      request.onsuccess = () => resolve(request.result || [])
      request.onerror = (e) => reject(e.target.error)
    })
  },

  async markSynced(localId, serverId = null) {
    const db = await openDatabase()
    return new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_NAME], "readwrite")
      const store = tx.objectStore(STORE_NAME)
      const getReq = store.get(localId)

      getReq.onsuccess = () => {
        const record = getReq.result
        if (record) {
          record.sync_status = "SYNCED"
          if (serverId) record.server_id = serverId
          record.synced_at = new Date().toISOString()
          store.put(record)
        }
        resolve(record)
      }
      getReq.onerror = (e) => reject(e.target.error)
    })
  },

  async markConflict(localId, message = "Doublon détecté") {
    const db = await openDatabase()
    return new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_NAME], "readwrite")
      const store = tx.objectStore(STORE_NAME)
      const getReq = store.get(localId)

      getReq.onsuccess = () => {
        const record = getReq.result
        if (record) {
          record.sync_status = "CONFLICT"
          record.error_message = message
          store.put(record)
        }
        resolve(record)
      }
      getReq.onerror = (e) => reject(e.target.error)
    })
  },

  async deleteBeneficiary(localId) {
    const db = await openDatabase()
    return new Promise((resolve, reject) => {
      const tx = db.transaction([STORE_NAME], "readwrite")
      const store = tx.objectStore(STORE_NAME)
      const request = store.delete(localId)

      request.onsuccess = () => resolve(true)
      request.onerror = (e) => reject(e.target.error)
    })
  },

  async getCounts() {
    try {
      const all = await this.getAllBeneficiaries()
      const pending = all.filter((i) => i.sync_status === "PENDING").length
      const synced = all.filter((i) => i.sync_status === "SYNCED").length
      const conflict = all.filter((i) => i.sync_status === "CONFLICT").length
      return { total: all.length, pending, synced, conflict }
    } catch {
      return { total: 0, pending: 0, synced: 0, conflict: 0 }
    }
  },
}

