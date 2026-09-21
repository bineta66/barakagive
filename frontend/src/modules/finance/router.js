import DashboardLayout from "@/components/layout/DashboardLayout.vue";
import FinanceDashboard from "./views/FinanceDashboard.vue";
import Budgets from "./views/Budgets.vue";
import Dons from "./views/Dons.vue";
import Depenses from "./views/Depenses.vue";
import Justifications from "./views/Justifications.vue";
import FinanceAIAssistant from "./views/FinanceAIAssistant.vue";
import FinanceReports from "./views/FinanceReports.vue";

const routes = [
  {
    path: "/finance",
    component: DashboardLayout,
    redirect: { name: "finance-dashboard" },
    children: [
      {
        path: "dashboard",
        name: "finance-dashboard",
        component: FinanceDashboard,
      },
      {
        path: "budgets",
        name: "finance-budgets",
        component: Budgets,
      },
      {
        path: "dons",
        name: "finance-dons",
        component: Dons,
      },
      {
        path: "depenses",
        name: "finance-depenses",
        component: Depenses,
      },
      {
        path: "justifications",
        name: "finance-justifications",
        component: Justifications,
      },
      {
        path: "ai-assistant",
        name: "finance-ai-assistant",
        component: FinanceAIAssistant,
      },
      {
        path: "rapports",
        name: "finance-rapports",
        component: FinanceReports,
      },
    ],
  },
];

export default routes;