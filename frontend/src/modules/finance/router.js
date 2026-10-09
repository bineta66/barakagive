import DashboardLayout from "@/components/layout/DashboardLayout.vue"
import FinanceDashboard from "@/modules/finance/views/FinanceDashboard.vue"
import Budgets from "@/modules/finance/views/Budgets.vue"
import Dons from "@/modules/finance/views/Dons.vue"
import Depenses from "@/modules/finance/views/Depenses.vue"
import Justifications from "@/modules/finance/views/Justifications.vue"
import FinanceReports from "@/modules/finance/views/FinanceReports.vue"
import FinanceLines from "@/modules/finance/views/FinanceLines.vue"
import Financements from "@/modules/finance/views/Financements.vue"
import BudgetDetail from "@/modules/finance/views/BudgetDetail.vue"

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
        path: "budgets/:id",
        name: "finance-budget-detail",
        component: BudgetDetail,
      },
      {
        path: "lignes-budgetaires",
        name: "finance-lignes-budgetaires",
        component: FinanceLines,
      },
      {
        path: "financements",
        name: "finance-financements",
        component: Financements,
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
        path: "justificatifs",
        name: "finance-justificatifs",
        component: Justifications,
      },
      {
        path: "rapports",
        name: "finance-rapports",
        component: FinanceReports,
      },
    ],
  },
]

export default routes
