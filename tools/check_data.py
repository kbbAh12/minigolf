#!/usr/bin/env python3
"""Prüft data.json und img/ auf typische Eintragsfehler.

Läuft lokal mit `python3 tools/check_data.py` und in der GitHub Action.
Fehler brechen ab (Exit-Code 1), Hinweise werden nur ausgegeben.
"""
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


try:
    with open(os.path.join(ROOT, 'data.json'), encoding='utf-8') as f:
        data = json.load(f)
except (OSError, json.JSONDecodeError) as e:
    print(f'FEHLER: data.json nicht lesbar: {e}')
    sys.exit(1)

players = data.get('players', {})
matches = data.get('matches', [])
img_dir = os.path.join(ROOT, 'img')
images = {f.rsplit('.', 1)[0] for f in os.listdir(img_dir) if f.lower().endswith('.jpg')}
# Morgen gilt noch als gültig, damit Runden nach Mitternacht und Zeitzonen nicht stören.
latest_ok = datetime.date.today() + datetime.timedelta(days=1)

if data.get('me') not in players:
    err(f'"me" ({data.get("me")!r}) steht nicht in "players"')

shots_seen = {}
prev_date = None
for i, m in enumerate(matches):
    where = f'Runde {i + 1} ({m.get("date", "?")}, {m.get("map", "?")})'

    date = m.get('date', '')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
        err(f'{where}: Datum muss JJJJ-MM-TT sein, ist {date!r}')
    else:
        d = datetime.date.fromisoformat(date)
        if d > latest_ok:
            err(f'{where}: Datum liegt in der Zukunft')
        if prev_date and d < prev_date:
            err(f'{where}: Datum früher als die Runde davor ({prev_date}), Reihenfolge prüfen')
        prev_date = d

    if not m.get('map'):
        err(f'{where}: "map" fehlt')
    if m.get('type') not in ('community', 'offiziell'):
        err(f'{where}: "type" muss "community" oder "offiziell" sein, ist {m.get("type")!r}')

    par, scores = m.get('par'), m.get('scores') or {}
    if scores and not par:
        err(f'{where}: "scores" ohne "par"')
    if par:
        if len(par) != 18:
            warn(f'{where}: Par hat {len(par)} statt 18 Löcher')
        for p, s in scores.items():
            if len(s) != len(par):
                err(f'{where}: {p} hat {len(s)} Lochwerte, Par hat {len(par)}')
            if any(not isinstance(x, int) or x < 0 for x in s):
                err(f'{where}: {p} hat ungültige Lochwerte')

    named = set(scores) | set(m.get('totals') or {}) | set(m.get('adjust') or {})
    for group in m.get('order') or []:
        named |= set(group)
    if m.get('winner'):
        named.add(m['winner'])
    if not named:
        err(f'{where}: keine Spieler (weder scores, totals noch order)')
    for p in sorted(named - set(players)):
        err(f'{where}: Spieler {p!r} fehlt in "players"')
    in_match = set(scores) | set(m.get('totals') or {}) | {p for g in m.get('order') or [] for p in g}
    for p in m.get('adjust') or {}:
        if p not in in_match:
            err(f'{where}: "adjust" für {p!r}, der in der Runde nicht vorkommt')

    shot = m.get('shot')
    if shot:
        if shot not in images:
            err(f'{where}: Screenshot img/{shot}.jpg fehlt')
        if shot in shots_seen:
            err(f'{where}: Screenshot {shot!r} schon bei Runde {shots_seen[shot]} verwendet')
        shots_seen[shot] = i + 1
    elif scores:
        warn(f'{where}: Lochwerte ohne Screenshot')

for img in sorted(images - set(shots_seen)):
    warn(f'img/{img}.jpg wird von keiner Runde verwendet')

for w in warnings:
    print(f'Hinweis: {w}')
for e in errors:
    print(f'FEHLER: {e}')
print(f'{len(matches)} Runden, {len(shots_seen)} Screenshots, '
      f'{len(errors)} Fehler, {len(warnings)} Hinweise')
sys.exit(1 if errors else 0)
