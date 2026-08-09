"""Quick end-to-end smoke test using Django's test client.

Run with:  ./venv/bin/python smoke_test.py
This is a helper script (not part of the app) to verify key pages load.
"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth.models import User  # noqa: E402
from django.test import Client  # noqa: E402

# django.test.Client sends HTTP_HOST=testserver, which is not in ALLOWED_HOSTS.
settings.ALLOWED_HOSTS.append("testserver")

u, _ = User.objects.get_or_create(
    username="smoke_tester", defaults={"email": "smoke@example.com"}
)
u.set_password("SmokePass123!")
u.is_active = True
u.save()

c = Client()
print("home:", c.get("/").status_code)
print("login page:", c.get("/login/").status_code)
print("register page:", c.get("/register/").status_code)
assert c.login(username="smoke_tester", password="SmokePass123!"), "login failed"

paths = [
    "/dashboard/", "/tasks/", "/tasks/add/", "/notes/", "/notes/add/",
    "/resources/", "/resources/add/", "/profile/", "/profile/password/",
    "/ai-chat/", "/notes/export/pdf/",
]
for path in paths:
    r = c.get(path)
    ctype = r.get("Content-Type", "")[:30]
    print(f"{path}: {r.status_code} ({ctype})")

# Exercise an AI chat send (uses offline fallback when AI_API_KEY is empty).
r = c.post("/ai-chat/send/", {"message": "Explain Django MVT in one line."},
           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
print("ai send:", r.status_code, r.get("Content-Type", "")[:30])

print("ALL SMOKE CHECKS DONE")
