<template>
  <div class="p-4 sm:p-6 lg:p-8 space-y-6 bg-[#F8FAFC] min-h-screen">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-[#021427] tracking-tight">
          Pièces Justificatives
        </h1>
        <p class="text-xs sm:text-sm text-slate-600 mt-1">
          Centralisation, vérification et archivage des factures, reçus et pièces comptables.
        </p>
      </div>

      <button
        type="button"
        @click="openAddModal"
        class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#744D03] text-white text-xs sm:text-sm font-semibold hover:bg-[#5c3c02] shadow-md transition cursor-pointer self-start sm:self-auto"
      >
        <Plus class="w-4 h-4" />
        <span>Ajouter une nouvelle pièce</span>
      </button>
    </div>

    <!-- Search & Filter bar -->
    <div class="rounded-2xl bg-white p-4 border border-[#E5E7EB] shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
      <div class="relative w-full md:w-80">
        <Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Nom du fichier, référence dépense..."
          class="w-full pl-10 pr-4 py-2 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
        />
      </div>

      <div class="flex items-center gap-3 w-full md:w-auto">
        <label class="text-xs font-semibold text-slate-600 whitespace-nowrap">Statut :</label>
        <select
          v-model="selectedStatus"
          class="w-full md:w-64 py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-[#E5E7EB] rounded-xl focus:outline-none focus:border-[#021427]"
        >
          <option value="">Tous les statuts</option>
          <option value="CONFORME">Conforme (Vert)</option>
          <option value="A_VERIFIER">À vérifier (Jaune)</option>
          <option value="NON_CONFORME">Non conforme (Rouge)</option>
        </select>
      </div>
    </div>

    <!-- Main Content List -->
    <div class="rounded-2xl bg-white border border-[#E5E7EB] shadow-sm overflow-hidden">
      <!-- Loading -->
      <div v-if="financeStore.loading" class="p-12 text-center text-slate-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#021427] border-t-transparent mb-2"></div>
        <p class="text-sm">Chargement des pièces justificatives...</p>
      </div>

      <!-- Empty -->
      <div v-else-if="filteredJustifications.length === 0" class="p-12 text-center text-slate-400">
        <FileText class="w-12 h-12 mx-auto mb-3 opacity-40 text-[#021427]" />
        <p class="text-base font-semibold text-[#021427]">Aucune pièce justificative disponible</p>
        <p class="text-xs text-slate-500 mt-1">Ajoutez des documents PDF ou images liés à vos dépenses.</p>
      </div>

      <div v-else>
        <!-- Mobile View -->
        <div class="block lg:hidden divide-y divide-[#E5E7EB]">
          <div
            v-for="j in filteredJustifications"
            :key="j.id"
            class="p-4 space-y-3"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <FileCode class="w-5 h-5 text-[#744D03]" />
                <span class="text-xs font-bold text-[#021427] truncate max-w-[180px]">
                  {{ getFileName(j) }}
                </span>
              </div>
              <AlertBadge :status="j.statut" />
            </div>

            <div class="text-xs text-slate-600 space-y-1">
              <p>Dépense liée : <span class="font-mono font-semibold text-slate-800">{{ j.depense_reference || 'DEP' }}</span></p>
              <p>Catégorie : {{ j.depense_categorie || 'Non spécifiée' }}</p>
              <p>Ajouté le : {{ formatDate(j.created_at) }}</p>
            </div>

            <div class="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
              <button
                @click="previewFile(j)"
                class="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-semibold hover:bg-slate-200"
              >
                Aperçu
              </button>
              <a
                :href="getFileUrl(j)"
                target="_blank"
                download
                class="px-3 py-1.5 rounded-lg bg-amber-50 text-[#744D03] text-xs font-semibold hover:bg-amber-100"
              >
                Télécharger
              </a>
              <button
                @click="deleteFile(j.id)"
                class="px-3 py-1.5 rounded-lg bg-rose-50 text-rose-700 text-xs font-semibold hover:bg-rose-100"
              >
                Supprimer
              </button>
            </div>
          </div>
        </div>

        <!-- Desktop View Table -->
        <div class="hidden lg:block overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-[#F8FAFC] border-b border-[#E5E7EB] text-xs font-semibold uppercase tracking-wider text-slate-600">
                <th class="py-3.5 px-5">Aperçu</th>
                <th class="py-3.5 px-5">Nom du fichier</th>
                <th class="py-3.5 px-5">Dépense liée</th>
                <th class="py-3.5 px-5">Date d'envoi</th>
                <th class="py-3.5 px-5">Statut</th>
                <th class="py-3.5 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E5E7EB] text-sm">
              <tr
                v-for="j in filteredJustifications"
                :key="j.id"
                class="hover:bg-slate-50/80 transition-colors"
              >
                <td class="py-4 px-5">
                  <button
                    @click="previewFile(j)"
                    class="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-[#021427] hover:scale-105 transition"
                  >
                    <Image v-if="isImage(j)" class="w-5 h-5 text-emerald-600" />
                    <FileText v-else class="w-5 h-5 text-rose-600" />
                  </button>
                </td>
                <td class="py-4 px-5 font-semibold text-[#021427]">
                  {{ getFileName(j) }}
                </td>
                <td class="py-4 px-5 text-slate-700">
                  <div class="font-mono text-xs font-bold text-slate-900">{{ j.depense_reference || 'DEP' }}</div>
                  <div class="text-xs text-slate-500">{{ j.depense_categorie }}</div>
                </td>
                <td class="py-4 px-5 text-slate-600 text-xs">
                  {{ formatDate(j.created_at) }}
                </td>
                <td class="py-4 px-5">
                  <AlertBadge :status="j.statut" />
                </td>
                <td class="py-4 px-5 text-right space-x-2">
                  <button
                    @click="previewFile(j)"
                    title="Aperçu"
                    class="p-1.5 rounded-lg text-slate-600 hover:text-[#021427] hover:bg-slate-100"
                  >
                    <Eye class="w-4 h-4" />
                  </button>
                  <a
                    :href="getFileUrl(j)"
                    target="_blank"
                    download
                    title="Télécharger"
                    class="p-1.5 inline-block rounded-lg text-[#744D03] hover:bg-amber-50"
                  >
                    <Download class="w-4 h-4" />
                  </a>
                  <button
                    @click="deleteFile(j.id)"
                    title="Supprimer"
                    class="p-1.5 rounded-lg text-rose-600 hover:bg-rose-50"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal: Ajouter une nouvelle pièce -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 z-50 bg-[#021427]/60 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 border border-[#E5E7EB]">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-lg font-bold text-[#021427]">Ajouter une pièce justificative</h3>
          <button @click="showAddModal = false" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="submitNewPiece" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Dépense associée</label>
            <select
              v-model="newPieceForm.depenseId"
              required
              class="w-full p-2.5 text-xs sm:text-sm bg-slate-50 border rounded-xl focus:border-[#021427] focus:outline-none"
            >
              <option value="" disabled>Sélectionner une dépense</option>
              <option
                v-for="d in financeStore.depenses"
                :key="d.id"
                :value="d.id"
              >
                {{ d.reference }} - {{ d.categorie }} ({{ formatCurrency(d.montant) }})
              </option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Fichier (PDF ou Image, Max 10Mo)</label>
            <input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              required
              @change="handleNewFileSelected"
              class="w-full text-xs text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-[#021427] file:text-white hover:file:bg-slate-800"
            />
          </div>

          <div class="pt-4 flex items-center justify-end gap-3 border-t">
            <button
              type="button"
              @click="showAddModal = false"
              class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 text-xs font-semibold"
            >
              Annuler
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="px-5 py-2 rounded-xl bg-[#744D03] text-white text-xs font-semibold hover:bg-[#5c3c02]"
            >
              {{ submitting ? "Envoi..." : "Téléverser la pièce" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Aperçu Document -->
    <div
      v-if="previewDoc"
      class="fixed inset-0 z-50 bg-[#021427]/80 backdrop-blur-md flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-2xl max-w-3xl w-full h-[80vh] p-6 shadow-2xl flex flex-col justify-between border border-[#E5E7EB]">
        <div class="flex items-center justify-between border-b pb-3">
          <div>
            <h3 class="text-base font-bold text-[#021427]">{{ getFileName(previewDoc) }}</h3>
            <p class="text-xs text-slate-500">Dépense : {{ previewDoc.depense_reference }}</p>
          </div>
          <button @click="previewDoc = null" class="text-slate-400 hover:text-slate-600">
            <X class="w-6 h-6" />
          </button>
        </div>

        <div class="flex-1 my-4 bg-slate-100 rounded-xl overflow-hidden flex items-center justify-center p-2">
          <img
            v-if="isImage(previewDoc)"
            :src="getFileUrl(previewDoc)"
            alt="Aperçu"
            class="max-h-full max-w-full object-contain rounded-lg"
          />
          <iframe
            v-else
            :src="getFileUrl(previewDoc)"
            class="w-full h-full rounded-lg"
          ></iframe>
        </div>

        <div class="flex items-center justify-between pt-2 border-t text-xs">
          <AlertBadge :status="previewDoc.statut" />
          <a
            :href="getFileUrl(previewDoc)"
            target="_blank"
            download
            class="px-4 py-2 bg-[#744D03] text-white rounded-xl font-semibold hover:bg-[#5c3c02]"
          >
            Télécharger le fichier original
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { Plus, Search, FileText, FileCode, Image, Eye, Download, Trash2, X } from "lucide-vue-next"
import { useFinanceStore } from "@/stores/finance.js"
import AlertBadge from "@/components/finance/AlertBadge.vue"

const financeStore = useFinanceStore()

const searchQuery = ref("")
const selectedStatus = ref("")

const showAddModal = ref(false)
const submitting = ref(false)
const previewDoc = ref(null)

const newPieceForm = ref({
  depenseId: "",
  file: null,
})

onMounted(async () => {
  await financeStore.fetchAllJustifications()
  await financeStore.fetchExpenses()
})

const filteredJustifications = computed(() => {
  return (financeStore.justifications || []).filter((j) => {
    const fn = getFileName(j).toLowerCase()
    const depRef = String(j.depense_reference || "").toLowerCase()
    const q = searchQuery.value.toLowerCase()

    const matchesSearch = !q || fn.includes(q) || depRef.includes(q)
    const matchesStat = !selectedStatus.value || String(j.statut).toUpperCase() === String(selectedStatus.value).toUpperCase()

    return matchesSearch && matchesStat
  })
})

const getFileName = (j) => {
  if (j.fichier) {
    const parts = j.fichier.split("/")
    return parts[parts.length - 1]
  }
  return `Justificatif_${j.id?.substring(0, 6) || 'Doc'}.pdf`
}

const getFileUrl = (j) => {
  return j.url || j.fichier || "#"
}

const isImage = (j) => {
  const url = getFileUrl(j).toLowerCase()
  return url.endsWith(".png") || url.endsWith(".jpg") || url.endsWith(".jpeg") || j.type_fichier?.includes("image")
}

const formatCurrency = (val) => {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "XOF",
    maximumFractionDigits: 0,
  }).format(val || 0).replace("XOF", "FCFA")
}

const formatDate = (d) => {
  if (!d) return "N/A"
  return new Date(d).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" })
}

const openAddModal = () => {
  newPieceForm.value = {
    depenseId: financeStore.depenses[0]?.id || "",
    file: null,
  }
  showAddModal.value = true
}

const handleNewFileSelected = (e) => {
  if (e.target.files?.length > 0) {
    newPieceForm.value.file = e.target.files[0]
  }
}

const submitNewPiece = async () => {
  if (!newPieceForm.value.depenseId || !newPieceForm.value.file) return
  submitting.value = true
  try {
    await financeStore.addJustification(newPieceForm.value.depenseId, newPieceForm.value.file)
    showAddModal.value = false
    alert("Pièce justificative téléversée avec succès.")
  } catch {
    alert("Erreur lors de l'envoi de la pièce justificative.")
  } finally {
    submitting.value = false
  }
}

const previewFile = (j) => {
  previewDoc.value = j
}

const deleteFile = async (id) => {
  if (confirm("Êtes-vous sûr de vouloir supprimer cette pièce justificative ?")) {
    await financeStore.removeJustification(id)
  }
}
</script>
