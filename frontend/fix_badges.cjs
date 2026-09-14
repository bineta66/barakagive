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
let stats = { replaced: 0, filesUpdated: [] };

function escapeHtml(str) {
  return str.replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

allFiles.forEach(f => {
  let content = fs.readFileSync(f, 'utf8');
  const original = content;
  const relPath = path.relative(path.join(process.cwd(), 'frontend/src'), f);
  let fileChanged = false;

  // Pattern 1: Multi-line span with :class="badgeClass(...)"
  // <span
  //   class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium"
  //   :class="badgeClass(item.statut)"
  // >
  //   {{ item.statut }}
  // </span>
  content = content.replace(
    /<span\s*\n\s*class="inline-flex items-center px-2\.5 py-1 rounded-full text-xs font-medium"?\s*\n\s*:class="badgeClass\(([^)]+)"\s*\n\s*>\s*\n\s*{{\s*\1\s*}}\s*\n\s*<\/span>/g,
    (match, expr) => {
      stats.replaced++;
      fileChanged = true;
      return `<StatusBadge :statut="${expr}">\n              {{ ${expr} }}\n            </StatusBadge>`;
    }
  );

  // Pattern 2: Single-line span with :class="badgeClass(...)"
  content = content.replace(
    /<span\s+class="inline-flex items-center px-2\.5 py-1 rounded-full text-xs font-medium"\s+:class="badgeClass\(([^)]+)\)"\s*>\s*{{\s*\1\s*}}\s*<\/span>/g,
    (match, expr) => {
      stats.replaced++;
      fileChanged = true;
      return `<StatusBadge :statut="${expr}">{{ ${expr} }}</StatusBadge>`;
    }
  );

  // Pattern 3: Inline badge with hardcoded class (RapportsGerant line 71)
  // <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-XXX-100 text-XXX-700">
  //   {{ ... }}
  // </span>
  content = content.replace(
    /<span\s+class="inline-flex items-center px-2\.5 py-1 rounded-full text-xs font-medium bg-[\w-]+\s+text-[\w-]+">\s*{{\s*(\S+)\s*}}\s*<\/span>/g,
    (match, expr) => {
      stats.replaced++;
      fileChanged = true;
      return `<StatusBadge :statut="${expr}">{{ ${expr} }}</StatusBadge>`;
    }
  );

  // Pattern 4: Conditional :class with ternary for badges (not badgeClass function)
  // These are harder to replace automatically, mark them for manual review
  // :class="zone.statut === 'X' ? 'bg-Y text-Z' : 'bg-A text-B'"
  // We'll leave these for now - they're in component files like CarteInfoZone.vue

  if (fileChanged) {
    // Add StatusBadge import if not present
    if (!content.includes('StatusBadge')) {
      // Find the last import statement
      const importMatch = content.match(/import\s+[^;]+;\n/g);
      if (importMatch) {
        const lastImport = importMatch[importMatch.length - 1];
        const importLine = "import StatusBadge from \"@/components/ui/StatusBadge.vue\"\n";
        content = content.replace(lastImport, lastImport + importLine);
      } else {
        // Find script setup and add import
        const scriptMatch = content.match(/<script setup>[\s\S]*?<\/script>/);
        if (scriptMatch) {
          content = content.replace(
            '<script setup>',
            '<script setup>\nimport StatusBadge from "@/components/ui/StatusBadge.vue"'
          );
        }
      }
    }

    if (content.charCodeAt(0) === 0xFEFF) {
      content = content.slice(1);
    }
    fs.writeFileSync(f, content, 'utf8');
    stats.filesUpdated.push(relPath);
  }
});

console.log('Badge replacements:', stats.replaced);
console.log('Files updated:', stats.filesUpdated);
