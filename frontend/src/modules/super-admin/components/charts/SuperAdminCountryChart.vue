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

      <!-- ONG par pays line -->
      <polyline
        fill="none"
        stroke="#7C3AED"
        stroke-width="3"
        stroke-linejoin="round"
        stroke-linecap="round"
        points="50,100 100,80 150,90 200,60 250,70 300,40 350,60 400,50 450,30"
      />
      <circle cx="100" cy="80" r="5" fill="#7C3AED" />
      <circle cx="200" cy="60" r="5" fill="#7C3AED" />
      <circle cx="300" cy="40" r="5" fill="#7C3AED" />
      <circle cx="400" cy="50" r="5" fill="#7C3AED" />
    </svg>
  </div>
</template>

<script setup>
</script>





