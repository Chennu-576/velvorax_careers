import requests
import sys

routes = [
    "/",
    "/about",
    "/jobs",
    "/it-jobs",
    "/non-it-jobs",
    "/job-categories",
    "/global-jobs",
    "/login",
    "/register"
]

all_passed = True
for path in routes:
    url = f"http://localhost:3001{path}"
    try:
        r = requests.get(url, timeout=5)
        print(f"[OK] {path} -> {r.status_code}")
        if r.status_code != 200:
            all_passed = False
    except Exception as e:
        print(f"[FAIL] {path} -> {e}")
        all_passed = False

if not all_passed:
    sys.exit(1)
print("\nALL 9 REQUIRED PUBLIC PAGES VERIFIED RETURNING HTTP 200 OK!")
