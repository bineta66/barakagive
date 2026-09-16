import { ref, computed } from "vue"

export function useFormBuilder() {
  const questions = ref([])
  const currentFormId = ref(null)

  const typeMapFrontendToBackend = {
    texte: "TEXT",
    nombre: "NUMBER",
    liste: "SELECT",
    "selection-multiple": "CHECKBOX",
    "oui-non": "YES_NO",
    date: "DATE",
    telephone: "PHONE",
    photo: "TEXTAREA",
    gps: "GPS",
  }

  const typeMapBackendToFrontend = {
    TEXT: "texte",
    NUMBER: "nombre",
    SELECT: "liste",
    CHECKBOX: "selection-multiple",
    YES_NO: "oui-non",
    DATE: "date",
    PHONE: "telephone",
    TEXTAREA: "photo",
    GPS: "gps",
  }

  const typesQuestions = [
    {
      id: "texte",
      label: "Texte",
      iconPath: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    },
    {
      id: "nombre",
      label: "Nombre",
      iconPath: "M7 7h10M7 12h10M7 17h10",
    },
    {
      id: "liste",
      label: "Liste déroulante",
      iconPath: "M19 9l-7 7-7-7",
    },
    {
      id: "selection-multiple",
      label: "Sélection multiple",
      iconPath: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4",
    },
    {
      id: "oui-non",
      label: "Oui/Non",
      iconPath: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
    },
    {
      id: "date",
      label: "Date",
      iconPath: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z",
    },
    {
      id: "telephone",
      label: "Téléphone",
      iconPath: "M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.504 1.205l-1.996.998A11.25 11.25 0 005.25 19.5a1 1 0 01-1 0v-2.25a1 1 0 01.817-.985A11.25 11.25 0 0013.5 17.25a1 1 0 011 0v2.25a1 1 0 01-1 0A13.25 13.25 0 013 12.5z",
    },
    {
      id: "photo",
      label: "Texte long / Photo",
      iconPath: "M3 9a2 2 0 012-2h2.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.504 1.205l-1.996.998A11.25 11.25 0 005.25 19.5a1 1 0 01-1 0v-2.25a1 1 0 01.817-.985A11.25 11.25 0 0013.5 17.25a1 1 0 011 0v2.25a1 1 0 01-1 0A13.25 13.25 0 013 12.5z",
    },
    {
      id: "gps",
      label: "GPS",
      iconPath: "M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z",
    },
  ]

  const loadFromBackendFields = (fields = [], formId = null) => {
    currentFormId.value = formId
    questions.value = fields.map((f, index) => ({
      id: f.id,
      libelle: f.label,
      label: f.label,
      type: typeMapBackendToFrontend[f.type] || "texte",
      backendType: f.type,
      obligatoire: !!f.obligatoire,
      ordre: f.ordre !== undefined ? f.ordre : index,
      placeholder: f.placeholder || "",
      options: Array.isArray(f.options) ? [...f.options] : [],
    }))
  }

  const prepareForBackend = (q, index = 0) => {
    const backendType = typeMapFrontendToBackend[q.type] || "TEXT"
    const payload = {
      label: q.libelle || q.label || "Question sans titre",
      type: backendType,
      obligatoire: !!q.obligatoire,
      ordre: index,
      placeholder: q.placeholder || "",
    }
    if (backendType === "SELECT" || backendType === "CHECKBOX") {
      payload.options = q.options?.length ? q.options : ["Option 1", "Option 2"]
    }
    return payload
  }

  const ajouterOption = (idQuestion, option) => {
    const question = questions.value.find((q) => q.id === idQuestion)
    if (question) {
      if (!question.options) question.options = []
      question.options.push(option)
    }
  }

  const supprimerOption = (idQuestion, indexOption) => {
    const question = questions.value.find((q) => q.id === idQuestion)
    if (question && question.options) {
      question.options.splice(indexOption, 1)
    }
  }

  const statistiques = computed(() => {
    const total = questions.value.length
    const obligatoires = questions.value.filter((q) => q.obligatoire).length
    const typesUtilises = new Set(questions.value.map((q) => q.type)).size
    return {
      total,
      obligatoires,
      typesUtilises,
    }
  })

  return {
    questions,
    typesQuestions,
    statistiques,
    loadFromBackendFields,
    prepareForBackend,
    typeMapFrontendToBackend,
    typeMapBackendToFrontend,
    ajouterOption,
    supprimerOption,
  }
}
