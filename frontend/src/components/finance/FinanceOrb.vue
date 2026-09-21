<template>
  <button
    type="button"
    @click="openAssistant"
    class="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-full backdrop-blur-md transition-all duration-300 shadow-2xl cursor-pointer group"
    :class="orbContainerClasses"
  >
    <!-- Icon Container -->
    <div class="relative flex items-center justify-center">
      <!-- Golden Coin Icon -->
      <Coins class="w-6 h-6 text-[#D97706] group-hover:rotate-12 transition-transform duration-300" />
      
      <!-- AI Sparkle overlay -->
      <Sparkles class="w-3.5 h-3.5 text-amber-300 absolute -top-1 -right-1 animate-spin-slow" />
    </div>

    <!-- Text / Status Badge -->
    <div class="flex flex-col text-left">
      <span class="text-xs font-extrabold tracking-wide uppercase text-amber-200">
        Assistant IA
      </span>
      <span class="text-[11px] font-medium text-slate-200 flex items-center gap-1.5">
        <span class="w-2 h-2 rounded-full" :class="alertDotClass"></span>
        {{ alertText }}
      </span>
    </div>

    <!-- Alert Indicator Pill if Warning/Critical -->
    <span
      v-if="isAlertActive"
      class="w-3 h-3 rounded-full bg-rose-500 animate-ping absolute -top-1 -right-1"
    ></span>
  </button>
</template>

<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
import { Coins, Sparkles } from "lucide-vue-next"

const props = defineProps({
  alertLevel: {
    type: String,
    default: "Vert", // 'Vert' | 'Jaune' | 'Orange' | 'Rouge'
  },
})

const router = useRouter()

const isAlertActive = computed(() => {
  const lvl = String(props.alertLevel || "").toLowerCase()
  return lvl === "orange" || lvl === "rouge"
})

const orbContainerClasses = computed(() => {
  if (isAlertActive.value) {
    return "bg-[#021427]/90 border-2 border-rose-500/80 text-white shadow-rose-950/50 animate-pulse hover:animate-none hover:scale-105"
  }
  return "bg-[#021427]/85 hover:bg-[#021427] border border-[#744D03]/60 text-white shadow-[#021427]/40 hover:scale-105"
})

const alertDotClass = computed(() => {
  const lvl = String(props.alertLevel || "").toLowerCase()
  if (lvl === "rouge") return "bg-rose-500 animate-ping"
  if (lvl === "orange") return "bg-amber-500 animate-pulse"
  if (lvl === "jaune") return "bg-yellow-400"
  return "bg-emerald-400"
})

const alertText = computed(() => {
  const lvl = String(props.alertLevel || "").toLowerCase()
  if (lvl === "rouge") return "Alerte critique"
  if (lvl === "orange") return "Attention requise"
  if (lvl === "jaune") return "Suivi recommandé"
  return "Budget sous contrôle"
})

const openAssistant = () => {
  router.push("/finance/ai-assistant")
}
</script>

<style scoped>
@keyframes spinSlow {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.animate-spin-slow {
  animation: spinSlow 8s linear infinite;
}
</style>
