<template>
  <div v-if="ouvert" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="fermer">
    <div class="bg-white border border-slate-200 rounded-2xl shadow-xs-sm max-w-md w-full">
      <div class="p-6">
        <h2 class="text-2xl font-bold" style="color: #744D03">Ajouter justificatif</h2>
        <p class="text-sm text-gray-500 mt-1">Joindre une pièce justificative (PDF, JPG, PNG)</p>
      </div>

      <form @submit.prevent="submit" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fichier *</label>
          <input 
            type="file" 
            @change="handleFileChange" 
            class="w-full border rounded-lg px-3 py-2" 
            accept=".pdf,.jpg,.jpeg,.png"
            required
          >
        </div>
        <div v-if="selectedFile" class="text-sm text-gray-600 mt-1">
          {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
        </div>
      </form>

      <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
        <button @click="fermer" class="px-4 py-2 border rounded-lg">Annuler</button>
        <button @click="submit" class="px-4 py-2 bg-orange-600 text-white rounded-lg">Téléverser</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  ouvert: Boolean,
  depense: { type: Object, default: null },
})

const emit = defineEmits(['fermer', 'save'])

const selectedFile = ref(null)

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0]
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const submit = () => {
  if (!selectedFile.value) {
    alert('Veuillez sélectionner un fichier')
    return
  }
  emit('save', {
    depenseId: props.depense.id,
    file: selectedFile.value
  })
  fermer()
}

const fermer = () => emit('fermer')
</script>