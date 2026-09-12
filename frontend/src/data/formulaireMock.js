export const typesQuestionsMock = [
  { id: "texte", label: "Texte", icon: "Type" },
  { id: "nombre", label: "Nombre", icon: "Hash" },
  { id: "liste", label: "Liste déroulante", icon: "ChevronDown" },
  { id: "oui-non", label: "Oui/Non", icon: "ToggleLeft" },
  { id: "date", label: "Date", icon: "Calendar" },
  { id: "telephone", label: "Téléphone", icon: "Phone" },
  { id: "photo", label: "Photo", icon: "Camera" },
  { id: "gps", label: "GPS", icon: "MapPin" },
]

export const formulaireMock = {
  id: 1,
  nom: "Formulaire de collecte",
  questions: [
    {
      id: 1,
      type: "texte",
      libelle: "Nom du bénéficiaire",
      obligatoire: true,
      options: [],
    },
    {
      id: 2,
      type: "telephone",
      libelle: "Numéro de téléphone",
      obligatoire: true,
      options: [],
    },
    {
      id: 3,
      type: "liste",
      libelle: "Type d'aide demandée",
      obligatoire: false,
      options: ["Alimentaire", "Sanitaire", "Éducative", "Autre"],
    },
    {
      id: 4,
      type: "oui-non",
      libelle: "Bénéficiaire déplacé ?",
      obligatoire: true,
      options: [],
    },
    {
      id: 5,
      type: "gps",
      libelle: "Coordonnées GPS",
      obligatoire: true,
      options: [],
    },
  ],
}