import DashboardLayout from "@/components/layout/DashboardLayout.vue";
import FinanceDashboard from "@/module/finance/FinanceDashboard.vue";
import BudgetList from "@/module/finance/BudgetList.vue";
import DonationList from "@/module/finance/DonationList.vue";
import ExpenseList from "@/module/finance/ExpenseList.vue";
import JustificationList from "@/module/finance/JustificationList.vue";
import FinanceAIAssistant from "@/module/finance/FinanceAIAssistant.vue";
import FinanceReports from "@/module/finance/FinanceReports.vue";

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
        path: "projets",
        name: "finance-projets",
        component: BudgetList,
      },
      {
        path: "budgets",
        name: "finance-budgets",
        component: BudgetList,
      },
      {
        path: "dons",
        name: "finance-dons",
        component: DonationList,
      },
      {
        path: "depenses",
        name: "finance-depenses",
        component: ExpenseList,
      },
      {
        path: "justifications",
        name: "finance-justifications",
        component: JustificationList,
      },
      {
        path: "justificatifs",
        name: "finance-justificatifs",
        component: JustificationList,
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