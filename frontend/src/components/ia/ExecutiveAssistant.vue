<template>
  <div v-if="authStore.isGerant">
    <!-- Simple bouton flottant qui redirige vers la page dédiée -->
    <AssistantFloatingButton @click="navigateToAssistant" />
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.js";
import AssistantFloatingButton from "@/components/ia/AssistantFloatingButton.vue";

const router = useRouter();
const authStore = useAuthStore();

const navigateToAssistant = () => {
  router.push({ name: "gerant-assistant" });
};
</script>
