<template>
  <div class="h-64">
    <svg
      width="100%"
      height="100%"
      viewBox="0 0 500 200"
      preserveAspectRatio="xMidYMid meet"
    >
      <!-- Background grid lines -->
      <line x1="0" y1="25" x2="500" y2="25" stroke="#F1F5F9" />
      <line x1="0" y1="50" x2="500" y2="50" stroke="#F1F5F9" />
      <line x1="0" y1="75" x2="500" y2="75" stroke="#F1F5F9" />
      <line x1="0" y1="100" x2="500" y2="100" stroke="#F1F5F9" />
      <line x1="0" y1="125" x2="500" y2="125" stroke="#F1F5F9" />
      <line x1="0" y1="150" x2="500" y2="150" stroke="#F1F5F9" />
      <line x1="0" y1="175" x2="500" y2="175" stroke="#F1F5F9" />

      <!-- Revenue line (emerald) -->
      <polyline
        fill="none"
        stroke="#0D9488"
        stroke-width="3"
        stroke-linejoin="round"
        stroke-linecap="round"
        points="50,140 100,120 150,130 200,100 250,90 300,70 350,80 400,50 450,60"
      />

      <!-- Dots -->
      <circle cx="50" cy="140" r="5" fill="#0D9488" />
      <circle cx="150" cy="130" r="5" fill="#0D9488" />
      <circle cx="250" cy="90" r="5" fill="#0D9488" />
      <circle cx="350" cy="80" r="5" fill="#0D9488" />
      <circle cx="450" cy="60" r="5" fill="#0D9488" />
    </svg>
  </div>
</template>

<script setup>
</script>





