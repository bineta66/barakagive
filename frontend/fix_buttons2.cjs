const fs = require('fs');
const path = require('path');

function findVueFiles(dir, files = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      findVueFiles(fullPath, files);
    } else if (entry.name.endsWith('.vue')) {
      files.push(fullPath);
    }
  }
  return files;
}

const allFiles = findVueFiles(path.join(process.cwd(), 'frontend/src'));
let fixed = 0;

allFiles.forEach(f => {
  let content = fs.readFileSync(f, 'utf8');
  const original = content;

  // Fix raw "Retour" buttons that use hover:bg-slate-50 (white-ish on hover)
  // Replace with BoutonSecondary component usage
  // Pattern: <RouterLink to="..." class="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 transition flex items-center gap-2">
  // <ArrowLeft :size="16" />\n  Retour
  // </RouterLink>
  
  const retourRegex = /<RouterLink\s+to="([^"]+)"\s+class="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 transition flex items-center gap-2">\s*<ArrowLeft :size="16" \/>\s*Retour\s*<\/RouterLink>/g;
  if (retourRegex.test(content)) {
    content = content.replace(retourRegex, (match, to) => {
      fixed++;
      return `<BoutonSecondary to="${to}">\n        <ArrowLeft :size="16" />\n        Retour\n      </BoutonSecondary>`;
    });
    
    // Add BoutonSecondary import if needed
    if (!content.includes('BoutonSecondary')) {
      const importMatch = content.match(/import BoutonPrimary/g);
      if (importMatch) {
        content = content.replace(
          'import BoutonPrimary',
          'import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"\nimport BoutonPrimary'
        );
      } else {
        content = content.replace(
          '<script setup>',
          '<script setup>\nimport BoutonSecondary from "@/components/ui/BoutonSecondary.vue"'
        );
      }
    }
  }

  // Also fix: <button @click="annuler" class="px-4 py-2 bg-amber-700 ..."> Annuler </button>
  // Change to BoutonSecondary
  // Pattern: <button\s+type="button"\s+@click="annuler"\s+class="px-4 py-2 text-amber-800 font-semibold hover:bg-amber-50 rounded-lg transition">\s*Annuler\s*</button>
  const annulerRegex = /<button\s+type="button"\s+@click="(?:annuler|cancel)"\s+class="px-4 py-2 text-[\w-]+ font-semibold hover:bg-[\w-]+\/10 rounded-lg transition">\s*Annuler\s*<\/button>/g;
  if (annulerRegex.test(content)) {
    content = content.replace(annulerRegex, (match) => {
      fixed++;
      return '<BoutonSecondary @click="annuler">\n          Annuler\n        </BoutonSecondary>';
    });
    
    if (!content.includes('import BoutonSecondary')) {
      content = content.replace(
        '<script setup>',
        '<script setup>\nimport BoutonSecondary from "@/components/ui/BoutonSecondary.vue"'
      );
    }
  }

  if (content !== original) {
    if (content.charCodeAt(0) === 0xFEFF) {
      content = content.slice(1);
    }
    fs.writeFileSync(f, content, 'utf8');
    const relPath = path.relative(path.join(process.cwd(), 'frontend/src'), f);
    console.log('Fixed buttons in: ' + relPath);
  }
});

console.log('Total buttons fixed:', fixed);
