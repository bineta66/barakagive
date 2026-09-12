import { ref, computed } from "vue"
import { formulaireMock } from "@/data/formulaireMock.js"

export function useFormBuilder(initialFormulaire = formulaireMock) {
  const questions = ref([])
  const suivantId = ref(1)

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
      label: "Photo",
      iconPath: "M3 9a2 2 0 012-2h2.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.504 1.205l-1.996.998A11.25 11.25 0 005.25 19.5a1 1 0 01-1 0v-2.25a1 1 0 01.817-.985A11.25 11.25 0 0013.5 17.25a1 1 0 011 0v2.25a1 1 0 01-1 0A13.25 13.25 0 013 12.5z",
    },
    {
      id: "gps",
      label: "GPS",
      iconPath: "M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z",
    },
  ]

  const initialiser = () => {
    questions.value = JSON.parse(JSON.stringify(initialFormulaire.questions || []))
    if (questions.value.length > 0) {
      suivantId.value = Math.max(...questions.value.map((q) => q.id)) + 1
    }
  }

  const ajouterQuestion = (type) => {
    const typeConfig = typesQuestions.find((t) => t.id === type)
    const nouvelleQuestion = {
      id: suivantId.value++,
      type: type,
      libelle: typeConfig ? typeConfig.label : "Nouvelle question",
      obligatoire: false,
      options: type === "liste" ? [] : [],
    }
    questions.value.push(nouvelleQuestion)
    return nouvelleQuestion.id
  }

  const supprimerQuestion = (id) => {
    const index = questions.value.findIndex((q) => q.id === id)
    if (index !== -1) {
      questions.value.splice(index, 1)
    }
  }

  const dupliquerQuestion = (id) => {
    const originale = questions.value.find((q) => q.id === id)
    if (originale) {
      const copie = JSON.parse(JSON.stringify(originale))
      copie.id = suivantId.value++
      copie.libelle = copie.libelle + " (copie)"
      const index = questions.value.findIndex((q) => q.id === id)
      questions.value.splice(index + 1, 0, copie)
      return copie.id
    }
    return null
  }

  const mettreAJourQuestion = (id, champ, valeur) => {
    const question = questions.value.find((q) => q.id === id)
    if (question) {
      question[champ] = valeur
    }
  }

  const ajouterOption = (idQuestion, option) => {
    const question = questions.value.find((q) => q.id === idQuestion)
    if (question && question.type === "liste") {
      if (!question.options) {
        question.options = []
      }
      question.options.push(option)
    }
  }

  const supprimerOption = (idQuestion, indexOption) => {
    const question = questions.value.find((q) => q.id === idQuestion)
    if (question && question.options) {
      question.options.splice(indexOption, 1)
    }
  }

  const modifierOption = (idQuestion, indexOption, nouvelleValeur) => {
    const question = questions.value.find((q) => q.id === idQuestion)
    if (question && question.options) {
      question.options[indexOption] = nouvelleValeur
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

  const reinitialiser = () => {
    initialiser()
  }

  initialiser()

  return {
    questions,
    typesQuestions,
    ajouterQuestion,
    supprimerQuestion,
    dupliquerQuestion,
    mettreAJourQuestion,
    ajouterOption,
    supprimerOption,
    modifierOption,
    statistiques,
    reinitialiser,
  }
}