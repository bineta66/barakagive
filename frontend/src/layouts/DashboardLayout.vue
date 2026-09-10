<template>
  <div class="flex min-h-screen bg-white">
    <Sidebar />

    <div class="flex-1 flex flex-col">
      <Navbar />

      <main class="flex-1 p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import Sidebar from "@/components/Sidebar.vue"
import Navbar from "@/components/Navbar.vue"
</script>