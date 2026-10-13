#!/usr/bin/env python3
"""Check catalog.json before it is published, then write version.json.

Usage:  python3 scripts/validate.py            # check against the last commit, write version.json
        python3 scripts/validate.py --check    # check only

Rules (the app depends on these):
  - schemaVersion 1; version is a whole number that goes up by 1 whenever the catalog changes
  - every flavour has a unique, lowercase-hyphenated id and a name
  - an id that was published is never removed or reused for a different name
  - status is "current", "limited", "retired" or null; discontinued == (status == "retired")
  - released flavours only: no upcoming, rumoured or cancelled entries, and no alcoholic products
  - count matches the number of flavours
"""
import json, re, subprocess, sys

ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent
STATUSES = {"current", "limited", "retired", None}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BANNED = re.compile(r"\bhard mountain dew\b|dewgarita", re.I)

def fail(msg):
    print("INVALID:", msg); sys.exit(1)

def previous():
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "show", "HEAD:catalog.json"], capture_output=True, text=True, check=True).stdout
        return json.loads(out)
    except Exception:
        return None

cat = json.loads((ROOT / "catalog.json").read_text())
if cat.get("schemaVersion") != 1: fail("schemaVersion must be 1")
if not isinstance(cat.get("version"), int) or cat["version"] < 1: fail("version must be a positive integer")
if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(cat.get("generated", ""))): fail("generated must be YYYY-MM-DD")
fl = cat.get("flavours")
if not isinstance(fl, list) or not fl: fail("flavours must be a non-empty list")
if cat.get("count") != len(fl): fail(f"count is {cat.get('count')} but there are {len(fl)} flavours")

seen = {}
for f in fl:
    fid, name = f.get("id"), f.get("name")
    if not isinstance(fid, str) or not ID_RE.match(fid): fail(f"bad id {fid!r}")
    if fid in seen: fail(f"duplicate id {fid}")
    if not isinstance(name, str) or not name.strip(): fail(f"{fid}: missing name")
    if f.get("status") not in STATUSES: fail(f"{fid}: bad status {f.get('status')!r}")
    if f.get("discontinued") != (f.get("status") == "retired"): fail(f"{fid}: discontinued must equal status == 'retired'")
    if BANNED.search(name): fail(f"{fid}: alcoholic products are not included")
    if f.get("markets") is not None and not (isinstance(f["markets"], list) and all(isinstance(m, str) for m in f["markets"])): fail(f"{fid}: markets must be a list of strings")
    if f.get("zeroSugar") not in (True, False, None): fail(f"{fid}: zeroSugar must be true, false or null")
    for k in ("notes", "availability", "since", "update", "sourceURL"):
        if f.get(k) is not None and not isinstance(f[k], str): fail(f"{fid}: {k} must be text or null")
    if f.get("sourceURL") and not f["sourceURL"].startswith("https://"): fail(f"{fid}: sourceURL must be https")
    seen[fid] = name

prev = previous()
if prev:
    old = {f["id"]: f["name"] for f in prev["flavours"]}
    missing = sorted(set(old) - set(seen))
    if missing: fail("published ids removed: " + ", ".join(missing))
    changed = json.dumps(prev["flavours"], sort_keys=True) != json.dumps(fl, sort_keys=True)
    if changed and cat["version"] != prev["version"] + 1:
        fail(f"catalog changed, so version must be {prev['version'] + 1} (it is {cat['version']})")
    if not changed and cat["version"] != prev["version"]:
        fail(f"flavours unchanged, so version must stay {prev['version']}")

print(f"OK: version {cat['version']}, {len(fl)} flavours")
if "--check" not in sys.argv:
    ver = {"schemaVersion": 1, "version": cat["version"], "generated": cat["generated"], "count": len(fl)}
    (ROOT / "version.json").write_text(json.dumps(ver, indent=1) + "\n")
    print("wrote version.json")
