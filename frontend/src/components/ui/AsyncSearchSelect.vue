<template>
  <div class="relative">
    <input
      :value="query"
      :placeholder="modelValue ? String(modelValue) : placeholder"
      type="search"
      autocomplete="off"
      class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-bleu-nuit/30"
      @focus="openResults"
      @input="onInput"
      @keydown.esc="closeResults"
    />
    <div
      v-if="open"
      class="absolute z-30 mt-1 max-h-56 w-full overflow-auto rounded-lg border border-slate-200 bg-white py-1 shadow-lg"
    >
      <button
        v-for="item in items"
        :key="String(item[valueKey])"
        type="button"
        class="block w-full px-3 py-2 text-left text-sm hover:bg-slate-50"
        @click="choose(item[valueKey])"
      >
        <span>{{ item[labelKey] }}</span>
        <span v-if="secondaryKey && item[secondaryKey]" class="ml-1 text-xs text-slate-500">— {{ item[secondaryKey] }}</span>
      </button>
      <button
        v-if="manualOption"
        type="button"
        class="block w-full border-t border-slate-100 px-3 py-2 text-left text-sm font-medium text-bleu-nuit hover:bg-slate-50"
        @click="choose(manualValue)"
      >{{ manualOption }}</button>
      <p v-if="!items.length && !loading && !manualOption" class="px-3 py-2 text-sm text-slate-500">Aucun résultat.</p>
      <p v-if="loading" class="px-3 py-2 text-sm text-slate-500">Recherche…</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount } from "vue";
import api from "@/services/api.js";

const props = defineProps({
  modelValue: { type: [String, Number], default: "" },
  modelLabel: { type: String, default: "" },
  extraParams: { type: Object, default: () => ({}) },
  endpoint: { type: String, required: true },
  labelKey: { type: String, default: "nom" },
  valueKey: { type: String, default: "id" },
  secondaryKey: { type: String, default: "" },
  placeholder: { type: String, default: "Rechercher…" },
  manualOption: { type: String, default: "" },
  manualValue: { type: String, default: "__autre__" },
});
const emit = defineEmits(["update:modelValue", "select"]);
const query = ref("");
const items = ref([]);
const knownItems = new Map();
const open = ref(false);
const loading = ref(false);
let debounceTimer;
let requestSequence = 0;
let valueResolveSequence = 0;

const search = async (term) => {
  const sequence = ++requestSequence;
  loading.value = true;
  try {
    const { data } = await api.get(props.endpoint, {
      params: { ...props.extraParams, search: term, page: 1, page_size: 20 },
    });
    if (sequence === requestSequence) {
      items.value = Array.isArray(data) ? data : (data?.results || []);
      for (const item of items.value) knownItems.set(String(item[props.valueKey]), item);
    }
  } catch {
    if (sequence === requestSequence) items.value = [];
  } finally {
    if (sequence === requestSequence) loading.value = false;
  }
};

const openResults = () => {
  open.value = true;
  if (!items.value.length) search(query.value.trim());
};
const onInput = (event) => {
  query.value = event.target.value;
  open.value = true;
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => search(query.value.trim()), 250);
};
const closeResults = () => { open.value = false; };
const choose = (value) => {
  emit("update:modelValue", value);
  const item = items.value.find((entry) => String(entry[props.valueKey]) === String(value));
  if (item) knownItems.set(String(value), item);
  emit("select", item || null);
  query.value = item ? String(item[props.labelKey] || "") : "";
  open.value = false;
};

watch(() => [props.modelValue, props.modelLabel], async ([value, label]) => {
  if (!value) query.value = "";
  else if (props.manualOption && value === props.manualValue) query.value = "";
  else if (label) query.value = label;
  else if (knownItems.has(String(value))) query.value = String(knownItems.get(String(value))[props.labelKey] || value);
  else if (props.valueKey === "id") {
    const sequence = ++valueResolveSequence;
    try {
      const { data } = await api.get(props.endpoint, { params: { ...props.extraParams, ids: String(value), page: 1, page_size: 1 } });
      if (sequence !== valueResolveSequence) return;
      const rows = Array.isArray(data) ? data : (data?.results || []);
      for (const item of rows) knownItems.set(String(item[props.valueKey]), item);
      const selected = rows.find((item) => String(item[props.valueKey]) === String(value));
      query.value = selected ? String(selected[props.labelKey] || value) : String(value);
    } catch {
      query.value = String(value);
    }
  } else query.value = String(value);
}, { immediate: true });
watch(() => props.extraParams, () => {
  items.value = [];
  if (open.value) search(query.value.trim());
}, { deep: true });
onBeforeUnmount(() => clearTimeout(debounceTimer));
</script>
