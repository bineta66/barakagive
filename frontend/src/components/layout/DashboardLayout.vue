<template>
  <div class="flex min-h-screen bg-white">
    <aside class="fixed top-0 left-0 z-40 h-screen w-64 overflow-y-auto">
      <Sidebar />
    </aside>

    <div class="flex-1 flex flex-col ml-64">
      <header class="fixed top-0 left-64 z-30 h-16 w-[calc(100%-16rem)] border-b border-slate-200 bg-white">
        <Navbar />
      </header>

      <main class="flex-1 pt-16 p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import Sidebar from "@/components/layout/Sidebar.vue"
import Navbar from "@/components/layout/Navbar.vue"
</script>
