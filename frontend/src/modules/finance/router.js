import FinanceLayout from "./layout/FinanceLayout.vue";
import DashboardFinance from "./views/DashboardFinance.vue";
import AssignedProjects from "./views/AssignedProjects.vue";

const routes = [
  {
    path: "/finance",
    component: FinanceLayout,
    redirect: { name: "finance-dashboard" },
    children: [
      {
        path: "dashboard",
        name: "finance-dashboard",
        component: DashboardFinance,
      },
      {
        path: "projets",
        name: "finance-projets",
        component: AssignedProjects,
      },
    ],
  },
];

export default routes;
