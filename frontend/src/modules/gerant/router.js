import DashboardLayout from "@/components/layout/DashboardLayout.vue";
import DashboardGerant from "./views/DashboardGerant.vue";
import MonONG from "./views/MonONG.vue";
import ProjetsGerant from "./views/ProjetsGerant.vue";
import CreerProjetGerant from "./views/CreerProjetGerant.vue";
import UtilisateursGerant from "./views/UtilisateursGerant.vue";
import CreerUtilisateurGerant from "./views/CreerUtilisateurGerant.vue";
import PartenairesGerant from "./views/PartenairesGerant.vue";
import BailleursGerant from "./views/BailleursGerant.vue";
import FinancesGerant from "./views/FinancesGerant.vue";
import RapportsGerant from "./views/RapportsGerant.vue";

const routes = [
  {
    path: "/gerant",
     component: DashboardLayout,
    redirect: { name: "gerant-dashboard" },
    children: [
      {
        path: "dashboard",
        name: "gerant-dashboard",
        component: DashboardGerant,
      },
      {
        path: "mon-ong",
        name: "gerant-mon-ong",
        component: MonONG,
      },
      {
        path: "projets",
        name: "gerant-projets",
        component: ProjetsGerant,
      },
      {
        path: "projets/creer",
        name: "gerant-projets-creer",
        component: CreerProjetGerant,
      },
      {
        path: "utilisateurs",
        name: "gerant-utilisateurs",
        component: UtilisateursGerant,
      },
      {
        path: "utilisateurs/creer",
        name: "gerant-utilisateurs-creer",
        component: CreerUtilisateurGerant,
      },
      {
        path: "partenaires",
        name: "gerant-partenaires",
        component: PartenairesGerant,
      },
      {
        path: "bailleurs",
        name: "gerant-bailleurs",
        component: BailleursGerant,
      },
      {
        path: "finances",
        name: "gerant-finances",
        component: FinancesGerant,
      },
      {
        path: "rapports",
        name: "gerant-rapports",
        component: RapportsGerant,
      },
    ],
  },
];

export default routes;

