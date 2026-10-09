<template>
  <aside class="w-full shrink-0 xl:sticky xl:top-6 xl:w-[360px] rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
    <div class="mb-5 border-b border-slate-100 pb-4"><p class="text-xs font-semibold uppercase tracking-wide text-[#D20C4F]">Aperçu terrain</p><h3 class="mt-1 text-lg font-bold text-[#00313C]">{{ title || 'Formulaire de collecte' }}</h3><p class="mt-1 text-xs text-slate-500">Rendu tel que présenté à l’agent.</p></div>
    <div v-if="!questions.length" class="rounded-xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">Les questions apparaîtront ici.</div>
    <div v-else class="max-h-[70vh] space-y-4 overflow-y-auto pr-1">
      <label v-for="q in questions" :key="q.id" class="block rounded-xl border border-slate-100 bg-slate-50 p-3">
        <span class="mb-2 block text-sm font-medium text-slate-800">{{ q.libelle }} <b v-if="q.obligatoire" class="text-[#D20C4F]">*</b></span>
        <textarea v-if="['texte-long'].includes(q.type) || (q.type === 'photo' && q.backendType === 'TEXTAREA')" rows="3" placeholder="Votre réponse" class="w-full rounded-lg border border-slate-200 bg-white p-2 text-sm" />
        <input v-else-if="['texte','email','nombre','date','telephone'].includes(q.type)" :type="({ texte:'text', email:'email', nombre:'number', date:'date', telephone:'tel' })[q.type]" :placeholder="q.placeholder || 'Votre réponse'" class="w-full rounded-lg border border-slate-200 bg-white p-2 text-sm" />
        <select v-else-if="q.type === 'liste'" class="w-full rounded-lg border border-slate-200 bg-white p-2 text-sm"><option value="">Choisir une option</option><option v-for="opt in q.options" :key="opt">{{ opt }}</option></select>
        <fieldset v-else-if="['choix-unique','selection-multiple'].includes(q.type)" class="space-y-2"><label v-for="opt in q.options" :key="opt" class="flex items-center gap-2 text-sm text-slate-700"><input :type="q.type === 'choix-unique' ? 'radio' : 'checkbox'" :name="String(q.id)" :value="opt">{{ opt }}</label></fieldset>
        <div v-else-if="q.type === 'oui-non'" class="flex gap-2"><label v-for="option in ['Oui','Non']" :key="option" class="flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-center text-sm"><input type="radio" :name="String(q.id)" class="mr-2">{{ option }}</label></div>
        <div v-else-if="q.type === 'photo' || q.type === 'fichier'" class="rounded-lg border border-dashed border-slate-300 bg-white p-3"><input :type="q.type === 'photo' ? 'file' : 'file'" :accept="q.type === 'photo' ? 'image/*' : undefined" class="w-full text-xs" /></div>
        <div v-else-if="q.type === 'gps'" class="rounded-lg border border-slate-200 bg-white p-3 text-xs text-slate-500">Coordonnées GPS · position de l’appareil</div>
        <div v-else-if="q.type === 'echelle'" class="flex justify-between gap-1"><label v-for="n in 5" :key="n" class="flex flex-col items-center gap-1 text-xs text-slate-500"><input type="radio" :name="String(q.id)">{{ n }}</label></div>
        <p v-if="q.aide" class="mt-2 text-xs text-slate-500">{{ q.aide }}</p>
      </label>
    </div>
  </aside>
</template>

<script setup>
defineProps({ questions: { type: Array, required: true }, title: { type: String, default: "" } })
</script>
