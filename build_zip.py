# -*- coding: utf-8 -*-
"""Build cite_helpdesk_production.zip: strip demo + __pycache__/.pyc."""
import os
import re
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "cite_helpdesk")
OUT = os.path.join(ROOT, "cite_helpdesk_production.zip")

with open(os.path.join(SRC, "__manifest__.py"), encoding="utf-8") as fh:
    manifest = fh.read()
# Strip demo list to [] for production build.
manifest_prod = re.sub(r'"demo"\s*:\s*\[[^\]]*\]', '"demo": []', manifest)

count = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
    for base, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", "demo")]
        for name in files:
            if name.endswith((".pyc", ".pyo")):
                continue
            full = os.path.join(base, name)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            if rel.endswith("cite_helpdesk/__manifest__.py"):
                zf.writestr(rel, manifest_prod)
            else:
                zf.write(full, rel)
            count += 1

print("entries=%d" % count)
print("demo_stripped=%s" % ('"demo": []' in manifest_prod))
with zipfile.ZipFile(OUT) as zf:
    bad = [n for n in zf.namelist()
           if "__pycache__" in n or n.endswith(".pyc") or "/demo/" in n]
print("bad_entries=%d" % len(bad))
print("size_kb=%d" % (os.path.getsize(OUT) // 1024))
