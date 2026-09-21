<template>
  <div
    class="relative overflow-hidden rounded-2xl bg-white p-5 border border-[#E5E7EB] shadow-sm hover:shadow-md transition-all duration-200 group"
  >
    <!-- Top Row: Icon + Indicator -->
    <div class="flex items-center justify-between">
      <div
        class="w-12 h-12 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110"
        :class="bgIconClass"
      >
        <component :is="icon" class="w-6 h-6" :class="iconColorClass" />
      </div>

      <span
        v-if="badgeText"
        class="text-xs font-semibold px-2.5 py-1 rounded-full border"
        :class="badgeClass"
      >
        {{ badgeText }}
      </span>
    </div>

    <!-- Title & Value -->
    <div class="mt-4">
      <p class="text-xs font-medium uppercase tracking-wider text-slate-500">
        {{ title }}
      </p>
      <h3 class="text-2xl lg:text-3xl font-bold text-[#021427] mt-1 tracking-tight">
        {{ formattedValue }}
      </h3>
    </div>

    <!-- Bottom Subtext / Trend -->
    <div v-if="subtext" class="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
      <span>{{ subtext }}</span>
      <span v-if="trend" :class="trendClass" class="font-semibold flex items-center gap-1">
        {{ trend }}
      </span>
    </div>

    <!-- Subtle accent glow line -->
    <div
      class="absolute bottom-0 left-0 right-0 h-1"
      :class="barColorClass"
    ></div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: [Number, String],
    required: true,
    default: 0,
  },
  isCurrency: {
    type: Boolean,
    default: true,
  },
  suffix: {
    type: String,
    default: "",
  },
  subtext: {
    type: String,
    default: "",
  },
  trend: {
    type: String,
    default: "",
  },
  icon: {
    type: Object,
    required: true,
  },
  variant: {
    type: String,
    default: "blue", // 'blue', 'ocre', 'green', 'amber', 'purple'
  },
  badgeText: {
    type: String,
    default: "",
  },
})

const formattedValue = computed(() => {
  if (props.suffix) {
    return `${props.value}${props.suffix}`
  }
  if (props.isCurrency && typeof props.value === "number") {
    return new Intl.NumberFormat("fr-FR", {
      style: "currency",
      currency: "XOF",
      maximumFractionDigits: 0,
    }).format(props.value).replace("XOF", "FCFA")
  }
  return props.value
})

const bgIconClass = computed(() => {
  const map = {
    blue: "bg-[#021427]/10",
    ocre: "bg-[#744D03]/10",
    green: "bg-emerald-50",
    amber: "bg-amber-50",
    purple: "bg-purple-50",
  }
  return map[props.variant] || "bg-[#021427]/10"
})

const iconColorClass = computed(() => {
  const map = {
    blue: "text-[#021427]",
    ocre: "text-[#744D03]",
    green: "text-emerald-600",
    amber: "text-amber-600",
    purple: "text-purple-600",
  }
  return map[props.variant] || "text-[#021427]"
})

const barColorClass = computed(() => {
  const map = {
    blue: "bg-[#021427]",
    ocre: "bg-[#744D03]",
    green: "bg-emerald-500",
    amber: "bg-amber-500",
    purple: "bg-purple-500",
  }
  return map[props.variant] || "bg-[#021427]"
})

const badgeClass = computed(() => {
  return "bg-slate-100 text-slate-700 border-slate-200"
})

const trendClass = computed(() => {
  if (props.trend?.startsWith("+")) return "text-emerald-600"
  if (props.trend?.startsWith("-")) return "text-rose-600"
  return "text-slate-600"
})
</script>
