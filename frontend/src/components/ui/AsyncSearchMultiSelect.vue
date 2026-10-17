<template>
  <div>
    <div class="mb-2 flex flex-wrap gap-2" v-if="selectedIds.length">
      <span v-for="id in selectedIds" :key="String(id)" class="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs text-blue-900">
        {{ labelFor(id) }}
        <button type="button" class="font-bold" :aria-label="`Retirer ${labelFor(id)}`" @click="toggle(id)">×</button>
      </span>
    </div>
    <input
      v-model="query"
      type="search"
      autocomplete="off"
      :placeholder="placeholder"
      class="mb-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-bleu-nuit/30"
      @input="scheduleSearch"
    />
    <div class="max-h-56 overflow-y-auto rounded-lg border border-slate-200 bg-slate-50 p-2">
      <label v-for="item in items" :key="String(item[valueKey])" class="flex cursor-pointer items-center gap-2 rounded px-2 py-1.5 text-sm hover:bg-white">
        <input
          type="checkbox"
          :checked="has(item[valueKey])"
          class="rounded text-bleu-nuit focus:ring-bleu-nuit/30"
          @change="toggle(item[valueKey])"
        />
        <span>{{ item[labelKey] }}</span>
        <span v-if="secondaryKey && item[secondaryKey]" class="text-xs text-slate-500">— {{ item[secondaryKey] }}</span>
      </label>
      <p v-if="loading" class="px-2 py-2 text-sm text-slate-500">Recherche…</p>
      <p v-else-if="!items.length" class="px-2 py-2 text-sm text-slate-500">Aucune zone trouvée.</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import api from "@/services/api.js";

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  endpoint: { type: String, required: true },
  labelKey: { type: String, default: "nom" },
  valueKey: { type: String, default: "id" },
  secondaryKey: { type: String, default: "" },
  placeholder: { type: String, default: "Rechercher…" },
  initialOptions: { type: Array, default: () => [] },
});
const emit = defineEmits(["update:modelValue", "selected-options", "resolved-ids", "available"]);
const query = ref("");
const items = ref([]);
const loading = ref(false);
const knownOptions = new Map();
for (const option of props.initialOptions) knownOptions.set(String(option[props.valueKey]), option);
const selectedIds = computed(() => (props.modelValue || []).map((value) => String(value)));
let searchTimer;
let searchSequence = 0;
let resolveSequence = 0;

const has = (id) => selectedIds.value.includes(String(id));
const labelFor = (id) => {
  const item = knownOptions.get(String(id));
  return item ? [item[props.labelKey], props.secondaryKey && item[props.secondaryKey]].filter(Boolean).join(" — ") : `Zone ${String(id).slice(0, 8)}`;
};
const emitSelected = () => {
  emit("selected-options", selectedIds.value.map((id) => knownOptions.get(id)).filter(Boolean));
};
const remember = (rows) => {
  for (const row of rows || []) knownOptions.set(String(row[props.valueKey]), row);
  emitSelected();
};

const search = async (term) => {
  const sequence = ++searchSequence;
  loading.value = true;
  try {
    const { data } = await api.get(props.endpoint, { params: { search: term, page: 1, page_size: 20 } });
    if (sequence === searchSequence) {
      items.value = Array.isArray(data) ? data : (data?.results || []);
      if (!term) emit("available", data?.count ?? items.value.length);
      remember(items.value);
    }
  } catch {
    if (sequence === searchSequence) items.value = [];
  } finally {
    if (sequence === searchSequence) loading.value = false;
  }
};
const scheduleSearch = () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => search(query.value.trim()), 250);
};
const toggle = (id) => {
  const next = [...selectedIds.value];
  const index = next.indexOf(String(id));
  if (index < 0) next.push(String(id));
  else next.splice(index, 1);
  emit("update:modelValue", next);
  emitSelected();
};

watch(() => props.modelValue, async (values) => {
  const missing = (values || []).map(String).filter((id) => !knownOptions.has(id));
  if (!missing.length) {
    emitSelected();
    return;
  }
  const sequence = ++resolveSequence;
  try {
    const { data } = await api.get(props.endpoint, { params: { ids: missing.join(","), page: 1, page_size: 100 } });
    if (sequence === resolveSequence) {
      const rows = Array.isArray(data) ? data : (data?.results || []);
      remember(rows);
      emit("resolved-ids", rows.map((row) => String(row[props.valueKey])));
    }
  } catch {
    if (sequence === resolveSequence) emitSelected();
  }
}, { immediate: true });

onMounted(() => search(""));
onBeforeUnmount(() => clearTimeout(searchTimer));
</script>
