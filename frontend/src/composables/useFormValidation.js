/**
 * useFormValidation.js — Composable central de validation BarakaGive360
 *
 * Usage :
 *   const { errors, validate, validateField, isFormValid, resetErrors } = useFormValidation()
 *   const ok = validate(schema, values)
 */
import { reactive, computed } from 'vue'

// ─── Expressions régulières ───────────────────────────────────────────────────
export const REGEX = {
  nom:        /^[\p{L}]+(?:[ '\u2019-][\p{L}]+)*$/u,
  nomLong:    /^.{3,120}$/,
  email:      /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/,
  phone:      /^(\+221\s?)?(70|75|76|77|78)[0-9]{7}$/,
  phoneLocal: /^(70|75|76|77|78)[0-9]{7}$/,
  password:   /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_\-#^])[A-Za-z\d@$!%*?&_\-#^]{8,}$/,
}

// ─── Messages d'erreur centralisés ───────────────────────────────────────────
export const MESSAGES = {
  required:        'Ce champ est obligatoire.',
  nom:             'Le nom doit contenir entre 2 et 50 caractères (lettres, espaces, tiret, apostrophe).',
  prenom:          'Le prénom doit contenir entre 2 et 50 caractères.',
  nomLong:         'Ce champ doit contenir entre 3 et 120 caractères.',
  email:           'Veuillez saisir une adresse email valide (ex: contact@ong.sn).',
  emailMax:        "L'email ne peut pas dépasser 100 caractères.",
  phone:           'Numéro invalide. Format Sénégal : 70, 75, 76, 77 ou 78 + 7 chiffres.',
  password:        'Minimum 8 caractères dont 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial.',
  passwordMin:     'Le mot de passe doit contenir au moins 8 caractères.',
  passwordConfirm: 'Les mots de passe ne correspondent pas.',
  montantMin:      'Le montant doit être supérieur à 0 FCFA.',
  montantMax:      'Le montant ne peut pas dépasser 999 999 999 FCFA.',
  montantRequired: 'Veuillez saisir un montant.',
  pourcentage:     'La valeur doit être un entier entre 0 et 100.',
  dateRequired:    'La date est obligatoire.',
  dateFinMin:      'La date de fin doit être égale ou postérieure à la date de début.',
  descMax:         'La description ne peut pas dépasser 500 caractères.',
  adresseMax:      "L'adresse ne peut pas dépasser 255 caractères.",
  selectRequired:  'Veuillez faire une sélection.',
}

// ─── Règles de validation réutilisables ──────────────────────────────────────
export const rules = {
  /** Valide un nom (prénom, nom de famille) */
  nom: (value) => {
    if (typeof value !== 'string') return MESSAGES.nom
    const v = value.trim().replace(/\s+/g, ' ')
    if (!v) return MESSAGES.required
    if (v.length < 2 || v.length > 50 || !REGEX.nom.test(v)) return MESSAGES.nom
    return null
  },

  /** Valide un prénom */
  prenom: (value) => {
    if (typeof value !== 'string') return MESSAGES.prenom
    const v = value.trim().replace(/\s+/g, ' ')
    if (!v) return MESSAGES.required
    if (v.length < 2 || v.length > 50 || !REGEX.nom.test(v)) return MESSAGES.prenom
    return null
  },

  /** Valide un nom long (ONG, projet, campagne) */
  nomLong: (value) => {
    if (typeof value !== 'string') return MESSAGES.nomLong
    const v = value.trim().replace(/\s+/g, ' ')
    if (!v) return MESSAGES.required
    if (v.length < 3 || v.length > 120) return MESSAGES.nomLong
    return null
  },

  /** Nom de campagne : le backend autorise jusqu'à 200 caractères. */
  nomCampagne: (value) => {
    if (typeof value !== 'string') return 'Le nom de la campagne doit contenir entre 3 et 200 caractères.'
    const v = value.trim().replace(/\s+/g, ' ')
    if (!v) return MESSAGES.required
    if (v.length < 3 || v.length > 200) return 'Le nom de la campagne doit contenir entre 3 et 200 caractères.'
    return null
  },

  /** Valide un email */
  email: (value) => {
    const v = (value || '').trim()
    if (!v) return MESSAGES.required
    if (v.length > 100) return MESSAGES.emailMax
    if (!REGEX.email.test(v)) return MESSAGES.email
    return null
  },

  /** Valide un téléphone sénégalais (avec ou sans +221) */
  phone: (value) => {
    const v = (value || '').trim().replace(/\s/g, '')
    if (!v) return MESSAGES.required
    // Normaliser : enlever +221 ou 221 au début
    const local = v.replace(/^(\+221|221)/, '')
    if (!REGEX.phoneLocal.test(local)) return MESSAGES.phone
    return null
  },

  /** Valide un mot de passe fort */
  password: (value) => {
    const v = value || ''
    if (!v) return MESSAGES.required
    if (v.length < 8) return MESSAGES.passwordMin
    if (!REGEX.password.test(v)) return MESSAGES.password
    return null
  },

  /** Valide un mot de passe minimal (activation) */
  passwordMin: (value) => {
    const v = value || ''
    if (!v) return MESSAGES.required
    if (v.length < 8) return MESSAGES.passwordMin
    return null
  },

  /** Valide la confirmation du mot de passe */
  passwordConfirm: (value, ref) => {
    if (!value) return MESSAGES.required
    if (value !== ref) return MESSAGES.passwordConfirm
    return null
  },

  /** Valide un montant FCFA */
  montant: (value) => {
    if (value === '' || value === null || value === undefined) return MESSAGES.montantRequired
    if (typeof value !== 'number' && typeof value !== 'string') return MESSAGES.montantMin
    if (typeof value === 'string' && !value.trim()) return MESSAGES.montantRequired
    const n = Number(value)
    if (!Number.isFinite(n)) return 'Veuillez saisir un montant valide.'
    if (n <= 0) return MESSAGES.montantMin
    if (n > 999999999) return MESSAGES.montantMax
    return null
  },

  /** Valide un budget facultatif, zéro étant autorisé. */
  montantNonNegatif: (value) => {
    if (value === '' || value === null || value === undefined) return null
    if (typeof value !== 'number' && typeof value !== 'string') return 'Veuillez saisir un nombre valide.'
    if (typeof value === 'string' && !value.trim()) return null
    const n = Number(value)
    if (!Number.isFinite(n)) return 'Veuillez saisir un nombre valide.'
    if (n < 0) return 'Le budget doit être supérieur ou égal à 0.'
    if (n > 9999999999999.99) return 'Le budget dépasse le montant maximal autorisé.'
    return null
  },

  /** Valide un pourcentage (0–100 entier) */
  pourcentage: (value) => {
    if (value === '' || value === null || value === undefined) return MESSAGES.required
    if (typeof value !== 'number' && typeof value !== 'string') return MESSAGES.pourcentage
    if (typeof value === 'string' && !value.trim()) return MESSAGES.required
    const n = Number(value)
    if (!Number.isFinite(n) || !Number.isInteger(n) || n < 0 || n > 100) return MESSAGES.pourcentage
    return null
  },

  /** Valide une date obligatoire */
  date: (value) => {
    if (!value) return MESSAGES.dateRequired
    return null
  },

  /** Valide que la date de fin >= date de début */
  dateFin: (value, dateDebut) => {
    if (!value) return MESSAGES.dateRequired
    if (dateDebut && value < dateDebut) return MESSAGES.dateFinMin
    return null
  },

  /** Valide une description (optionnel mais max 500) */
  description: (value) => {
    const v = (value || '').trim()
    if (v.length > 500) return MESSAGES.descMax
    return null
  },

  /** Limite la longueur d'un texte optionnel ou requis par une autre règle. */
  maxLength: (max) => (value) => {
    if (typeof value === 'string' && value.trim().length > max) {
      return `Ce champ ne peut pas dépasser ${max} caractères.`
    }
    return null
  },

  /** Valide une adresse (optionnel mais max 255) */
  adresse: (value) => {
    const v = (value || '').trim()
    if (v.length > 255) return MESSAGES.adresseMax
    return null
  },

  /** Valide un select obligatoire */
  select: (value) => {
    if (!value && value !== 0) return MESSAGES.selectRequired
    return null
  },

  /** Valide un champ obligatoire générique */
  required: (value) => {
    const v = typeof value === 'string' ? value.trim() : value
    if (!v && v !== 0) return MESSAGES.required
    return null
  },
}

// ─── Composable principal ─────────────────────────────────────────────────────
export function useFormValidation() {
  // Dictionnaire réactif : fieldName → message d'erreur (null = OK)
  const errors = reactive({})

  // Retourne true si aucune erreur
  const isFormValid = computed(() =>
    Object.values(errors).every((e) => !e)
  )

  /** Efface toutes les erreurs */
  const resetErrors = () => {
    Object.keys(errors).forEach((k) => { errors[k] = null })
  }

  /**
   * Valide un seul champ et stocke l'erreur
   * @param {string} field  - nom du champ
   * @param {Function} rule - fonction rule(value, ...extra) → string|null
   * @param {*} value       - valeur à valider
   * @param {...*} extra    - arguments supplémentaires (ex: passwordConfirm)
   * @returns {boolean}     - true si valide
   */
  const validateField = (field, rule, value, ...extra) => {
    const error = rule(value, ...extra)
    errors[field] = error
    return !error
  }

  /**
   * Valide un schéma complet : { fieldName: [rule, value, ...extra] }
   * @param {Object} schema - ex: { nom: [rules.nom, form.nom] }
   * @returns {boolean} - true si tout est valide
   */
  const validate = (schema) => {
    let allValid = true
    for (const [field, args] of Object.entries(schema)) {
      const [rule, value, ...extra] = args
      const error = rule(value, ...extra)
      errors[field] = error
      if (error) allValid = false
    }
    return allValid
  }

  /**
   * Classe CSS pour un champ selon son état
   * @param {string} field
   * @param {boolean} touched - si le champ a été touché
   * @returns {string}
   */
  const fieldClass = (field, touched = true) => {
    if (!touched) return 'border-slate-200'
    if (errors[field]) return 'border-red-500 focus:ring-red-500/30'
    return 'border-slate-200 focus:ring-bleu-nuit/30'
  }

  return {
    errors,
    isFormValid,
    resetErrors,
    validate,
    validateField,
    fieldClass,
  }
}

// ─── Export des règles pour usage direct ─────────────────────────────────────
export default useFormValidation
