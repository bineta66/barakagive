import DashboardLayout from "@/components/layout/DashboardLayout.vue";
import DashboardFinance from "./views/DashboardFinance.vue";
import AssignedProjects from "./views/AssignedProjects.vue";
import FinanceProjectDetail from "./views/FinanceProjectDetail.vue";
import Budgets from "./views/Budgets.vue";
import DonsFinancements from "./views/DonsFinancements.vue";
import Depenses from "./views/Depenses.vue";
import Justificatifs from "./views/Justificatifs.vue";
import RapportsFinances from "./views/RapportsFinances.vue";

const routes = [
  {
    path: "/finance",
     component: DashboardLayout,
    redirect: { name: "finance-dashboard" },
    children: [
      {
        path: "dashboard",
        name: "finance-dashboard",
        component: DashboardFinance,
      },
      {
        path: "projets",
        name: "finance-assigned-projects",
        component: AssignedProjects,
      },
      {
        path: "budgets",
        name: "finance-budgets",
        component: Budgets,
      },
      {
        path: "projets/:id",
        name: "finance-project-detail",
        component: FinanceProjectDetail,
      },
      {
        path: "dons",
        name: "finance-dons",
        component: DonsFinancements,
      },
      {
        path: "depenses",
        name: "finance-depenses",
        component: Depenses,
      },
      {
        path: "justificatifs",
        name: "finance-justificatifs",
        component: Justificatifs,
      },
      {
        path: "rapports",
        name: "finance-rapports",
        component: RapportsFinances,
      },
    ],
  },
];

export default routes;
