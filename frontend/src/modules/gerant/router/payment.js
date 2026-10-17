import { createRouter, createWebHistory } from "vue-router"
import SubscriptionDashboard from "@/views/payment/SubscriptionDashboard.vue"
import Subscribe from "@/views/payment/Subscribe.vue"
import PaymentExpired from "@/views/payment/PaymentExpired.vue"
import PaymentHistory from "@/views/payment/PaymentHistory.vue"

const routes = [
  {
    path: "payment",
    name: "payment-dashboard",
    component: SubscriptionDashboard,
    meta: { requiresAuth: true, roles: ["GERANT"] },
  },
  {
    path: "payment/subscribe",
    name: "payment-subscribe",
    component: Subscribe,
    meta: { requiresAuth: true, roles: ["GERANT"] },
  },
  {
    path: "payment/expired",
    name: "payment-expired",
    component: PaymentExpired,
    meta: { requiresAuth: true, roles: ["GERANT"] },
  },
  {
    path: "payment/history",
    name: "payment-history",
    component: PaymentHistory,
    meta: { requiresAuth: true, roles: ["GERANT"] },
  },
]

export default routes