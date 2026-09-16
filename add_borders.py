import os, re
ROOT = "C:/Users/dell/Desktop/barakagive/frontend/src"
changed = []
for dirpath, _, filenames in os.walk(ROOT):
    for fn in filenames:
        if not fn.endswith(".vue"):
            continue
        path = os.path.join(dirpath, fn)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            original = f.read()
        cleaned = original
        # Add border to shadow-sm white rounded containers missing border
        def add_border(m):
            cls = m.group(1)
            if "border" in cls or "shadow-sm" not in cls:
                return m.group(0)
            if "bg-white" in cls and "rounded" in cls:
                return 'class="' + cls.replace("rounded", "border border-slate-200 rounded") + '"'
            return m.group(0)
        cleaned = re.sub(r'class="([^"]*)"', add_border, cleaned)
        if cleaned != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            changed.append(path.replace("C:/Users/dell/Desktop/barakagive/frontend/src/", ""))
print("Changed:", len(changed))
for c in changed:
    print(" -", c)
