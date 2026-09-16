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
        cleaned = re.sub(r"\bshadow-xl\b", "shadow-sm", original)
        cleaned = re.sub(r"\bshadow-2xl\b", "shadow-sm", cleaned)
        cleaned = re.sub(r"\bshadow-lg\b", "shadow-sm", cleaned)
        if cleaned != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            changed.append(path.replace("C:/Users/dell/Desktop/barakagive/frontend/src/", ""))
print("Changed:", len(changed))
for c in changed:
    print(" -", c)
