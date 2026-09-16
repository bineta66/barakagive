<template>
  <div class="mx-auto max-w-3xl space-y-6 px-4 py-5 md:px-6">
    <div><p class="text-xs font-bold uppercase tracking-[0.18em] text-amber-700">Mon espace</p><h1 class="mt-1 text-2xl font-bold text-slate-900">Mon profil</h1></div>
    <section class="rounded-2xl border border-gray-200 bg-white p-6"><div class="flex flex-col items-center gap-5 sm:flex-row"><div class="flex h-24 w-24 items-center justify-center rounded-full bg-amber-100 text-3xl font-bold text-amber-800">{{ initials }}</div><div><h2 class="text-xl font-bold text-slate-900">{{ user?.full_name || `${user?.first_name || "Agent"} ${user?.last_name || ""}` }}</h2><p class="mt-1 text-sm text-amber-700">Agent Terrain</p></div></div><dl class="mt-8 grid gap-5 border-t border-slate-100 pt-6 sm:grid-cols-2"><div><dt class="text-xs font-bold uppercase text-slate-400">Email</dt><dd class="mt-1 text-sm font-medium text-slate-800">{{ user?.email || "-" }}</dd></div><div><dt class="text-xs font-bold uppercase text-slate-400">Téléphone</dt><dd class="mt-1 text-sm font-medium text-slate-800">{{ user?.phone || "-" }}</dd></div><div><dt class="text-xs font-bold uppercase text-slate-400">ONG</dt><dd class="mt-1 text-sm font-medium text-slate-800">{{ user?.organization?.name || user?.organization_name || "-" }}</dd></div><div><dt class="text-xs font-bold uppercase text-slate-400">Région</dt><dd class="mt-1 text-sm font-medium text-slate-800">{{ user?.organization?.region || "-" }}</dd></div><div><dt class="text-xs font-bold uppercase text-slate-400">Rôle</dt><dd class="mt-1 text-sm font-medium text-slate-800">Agent Terrain</dd></div></dl><div class="mt-8 grid gap-3 sm:grid-cols-2"><button type="button" class="h-11 rounded-xl border border-slate-300 font-semibold text-slate-700">Modifier profil</button><button type="button" class="h-11 rounded-xl border border-slate-300 font-semibold text-slate-700">Changer photo</button></div></section>
  </div>
</template>
<script setup>
import { computed } from "vue"
import { useAuthStore } from "@/stores/auth.js"
const authStore = useAuthStore()
const user = computed(() => authStore.user)
const initials = computed(() => `${user.value?.first_name?.[0] || "A"}${user.value?.last_name?.[0] || "G"}`.toUpperCase())
</script>

