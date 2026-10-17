# Plugin Figma local ? BarakaGive

## Importer les pages en calques editables
1. Connecte-toi a BarakaGive et ouvre la page a exporter.
2. Ouvre la console du navigateur (F12 ? Console) et execute `import('/export-page-to-figma.js')`. Un JSON de la page rendue est telecharge. Fais cette operation pour chaque page a importer.
3. Dans Figma Desktop, importe le plugin via **Plugins ? Development ? Import plugin from manifest?** et choisis `manifest.json`.
4. Lance le plugin, selectionne un ou plusieurs fichiers JSON dans ? Import editable depuis l?application ?, puis clique ? Creer les calques editables ?.

Les textes, champs, boutons, fonds, SVG, illustrations raster et graphiques Chart.js sont reconstruits en calques Figma. Les graphiques sont redessines en barres, courbes, secteurs, axes et libelles distincts. Les illustrations non photographiques sont vectorisees. Seules les photos reelles restent des images.

Le JSON contient les valeurs textuelles visibles dans ta session. Utilise des donnees de test ou retire les informations sensibles avant partage. Les positions et dimensions viennent du navigateur. Les polices peuvent varier si elles ne sont pas installees dans Figma ; les effets CSS complexes peuvent demander un ajustement. Les SVG et les formes restent editables, mais les images vectorisees peuvent etre simplifiees.

## Graphiques
Le composant `DashboardChart.vue` expose les donnees du graphique au moment de l?export. Redemarre/actualise l?application apres installation de cette version avant d?exporter une page avec graphique.

Le dossier inclut aussi `export-page-to-figma.js`, deja copie dans `frontend/public/` pour le servir par Vite ou le serveur frontend.
