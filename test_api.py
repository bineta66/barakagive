import os, json, urllib.request, urllib.error
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg5Mzc3NDMwLCJpYXQiOjE3ODkzNzAyMzAsImp0aSI6IjI4ODVkNzkxYjc4YjQ5MGViZjI1NWIzZWUyNWE0ZTk3IiwidXNlcl9pZCI6IjEzIn0.cJa_vaGqo6Trrg2PnB2nmBDhuolNf2fWAO0enI7iKz4"
headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
base = "http://localhost:8000"

def request(method, path, data=None):
    url = f"{base}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode()
            print(f"{method} {path} -> {resp.status}")
            if content:
                print(json.dumps(json.loads(content), indent=2, ensure_ascii=False))
            return resp.status, json.loads(content) if content else None
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"{method} {path} -> {e.code}")
        if body:
            print(body)
        return e.code, None

print("=== GET /api/project-criteria/ ===")
request("GET", "/api/project-criteria/")

print("\n=== POST /api/project-criteria/ ===")
request("POST", "/api/project-criteria/", {"name": "Environnement"})

print("\n=== POST /api/projects/ ===")
request("POST", "/api/projects/", {
    "name": "Projet Nutrition Touba",
    "description": "Distribution alimentaire",
    "chef_projet": 15,
    "responsable_finance": 14,
    "region": "Diourbel",
    "objectif": "Réduire la malnutrition",
    "start_date": "2026-10-01",
    "end_date": "2027-03-31",
    "criteria_ids": [1, 2, 3],
})

print("\n=== GET /api/projects/ ===")
request("GET", "/api/projects/")

print("\n=== GET /api/projects/1/ ===")
request("GET", "/api/projects/1/")

print("\n=== PATCH /api/projects/1/ ===")
request("PATCH", "/api/projects/1/", {"description": "Mis à jour"})

print("\n=== PATCH /api/projects/1/budget/ ===")
request("PATCH", "/api/projects/1/budget/", {"budget": 15000.50})

print("\n=== DELETE /api/projects/1/ (archive) ===")
request("DELETE", "/api/projects/1/")

print("\n=== GET /api/projects/ (after archive) ===")
request("GET", "/api/projects/")
