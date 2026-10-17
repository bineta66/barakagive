import Dexie, { liveQuery } from 'dexie'

// Base de données IndexedDB pour la synchronisation hors ligne
const databases = new Map()

const getScopedDatabase = () => {
  let user = null
  try {
    user = JSON.parse(localStorage.getItem('user') || 'null')
  } catch {
    user = null
  }
  if (!user?.id) {
    throw new Error('Une session utilisateur est requise pour le stockage hors ligne.')
  }
  const organization = user.organization
  const organizationId = user.organization_id ??
    (organization && typeof organization === 'object' ? organization.id : organization) ??
    'no-organization'
  const scope = `org_${encodeURIComponent(String(organizationId))}_user_${encodeURIComponent(String(user.id))}`
  if (!databases.has(scope)) {
    const scopedDb = new Dexie(`BarakaGiveSyncDB_${scope}`)
    scopedDb.version(1).stores({
      beneficiaires: 'uuid, statut, campagne, created_at',
      photos: 'uuid, beneficiaire_uuid, type, created_at',
      signatures: 'uuid, beneficiaire_uuid, created_at',
      gps: 'uuid, beneficiaire_uuid, created_at',
    })
    databases.set(scope, scopedDb)
  }
  return databases.get(scope)
}

const db = new Proxy({}, {
  get(_target, property) {
    return getScopedDatabase()[property]
  },
})

// Classe pour gérer les opérations de synchronisation
export class SyncStore {
  // Créer un nouveau bénéficiaire en attente de synchronisation
  static async createBeneficiaire(data) {
    const uuid = crypto.randomUUID()
    const beneficiaire = {
      uuid,
      ...data,
      statut: 'EN_ATTENTE',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    
    await db.beneficiaires.add(beneficiaire)
    return beneficiaire
  }
  
  // Créer une photo
  static async createPhoto(beneficiaireUuid, photoData, type = 'profil') {
    const uuid = crypto.randomUUID()
    const photo = {
      uuid,
      beneficiaire_uuid: beneficiaireUuid,
      data: photoData,
      type,
      created_at: new Date().toISOString()
    }
    
    await db.photos.add(photo)
    return photo
  }
  
  // Créer une signature
  static async createSignature(beneficiaireUuid, signatureData) {
    const uuid = crypto.randomUUID()
    const signature = {
      uuid,
      beneficiaire_uuid: beneficiaireUuid,
      data: signatureData,
      created_at: new Date().toISOString()
    }
    
    await db.signatures.add(signature)
    return signature
  }
  
  // Créer des données GPS
  static async createGPS(beneficiaireUuid, coordinates) {
    const uuid = crypto.randomUUID()
    const gps = {
      uuid,
      beneficiaire_uuid: beneficiaireUuid,
      latitude: coordinates.latitude,
      longitude: coordinates.longitude,
      accuracy: coordinates.accuracy,
      created_at: new Date().toISOString()
    }
    
    await db.gps.add(gps)
    return gps
  }
  
  // Récupérer tous les bénéficiaires en attente de synchronisation
  static async getPendingBeneficiaires() {
    return await db.beneficiaires
      .where('statut')
      .equals('EN_ATTENTE')
      .sortBy('created_at')
  }
  
  // Mettre à jour le statut d'un bénéficiaire
  static async updateStatut(uuid, statut) {
    await db.beneficiaires.update(uuid, {
      statut,
      updated_at: new Date().toISOString()
    })
  }
  
  // Récupérer un bénéficiaire complet avec ses données associées
  static async getBeneficiaireComplet(uuid) {
    const beneficiaire = await db.beneficiaires.get(uuid)
    if (!beneficiaire) return null
    
    const photos = await db.photos.where('beneficiaire_uuid').equals(uuid).toArray()
    const signature = await db.signatures.where('beneficiaire_uuid').equals(uuid).first()
    const gps = await db.gps.where('beneficiaire_uuid').equals(uuid).first()
    
    return {
      ...beneficiaire,
      photos,
      signature,
      gps
    }
  }
  
  // Supprimer un bénéficiaire et ses données associées
  static async deleteBeneficiaire(uuid) {
    await db.photos.where('beneficiaire_uuid').equals(uuid).delete()
    await db.signatures.where('beneficiaire_uuid').equals(uuid).delete()
    await db.gps.where('beneficiaire_uuid').equals(uuid).delete()
    await db.beneficiaires.delete(uuid)
  }
  
  // Récupérer les statistiques de synchronisation
  static async getSyncStats() {
    const enAttente = await db.beneficiaires.where('statut').equals('EN_ATTENTE').count()
    const enCours = await db.beneficiaires.where('statut').equals('SYNCHRONISATION').count()
    const synchronises = await db.beneficiaires.where('statut').equals('SYNCHRONISE').count()
    const echecs = await db.beneficiaires.where('statut').equals('ECHEC').count()
    
    return {
      enAttente,
      enCours,
      synchronises,
      echecs,
      total: enAttente + enCours + synchronises + echecs
    }
  }
  
  // Observer les changements en temps réel
  static observeBeneficiaires() {
    return liveQuery(() => db.beneficiaires.toArray())
  }
  
  // Vider toutes les données (pour le développement)
  static async clearAll() {
    await db.beneficiaires.clear()
    await db.photos.clear()
    await db.signatures.clear()
    await db.gps.clear()
  }
}

export default db
