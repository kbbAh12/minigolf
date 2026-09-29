# Minigolf-Buch

Statistik-Website für unsere Runden in *Golf With Your Friends*.

**Live:** [kbbah12.github.io/minigolf](https://kbbah12.github.io/minigolf)

Die Seite ist eine einzelne HTML-Datei ohne Build-Schritt und ohne Framework. GitHub Pages veröffentlicht den Stand von `main` direkt.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `index.html` | Die ganze Seite. Lädt `data.json` und zeigt vier Tabs: Runden, Duelle, Maps, Spieler. |
| `data.json` | Alle Runden, Spieler und Map-Bewertungen. |
| `img/` | Screenshots der Bestenliste am Rundenende, ein Bild pro Runde. |
| `tools/check_data.py` | Prüft `data.json` und `img/` auf Eintragsfehler. |
| `_archiv/` | Nicht mehr benutzte Dateien. Bleibt im Repo einsehbar, wird aber nicht veröffentlicht. |

## Neue Runde eintragen

Runden werden meist über eine Claude-Session eingetragen: Screenshot und Infos zur Runde geben, die Session trägt ein und committet.

- Screenshot nach `img/<map-name>.jpg`, bei einer weiteren Runde auf derselben Map `-2`, `-3` usw.
- Das Datum ist der Tag, an dem gespielt wurde, nicht der Tag des Eintragens. Auf dem Screenshot steht kein Datum, deshalb der Session den Spieltag immer dazusagen, sonst muss sie raten.
- Vor dem Commit `python3 tools/check_data.py` laufen lassen. Die Prüfung läuft zusätzlich bei jedem Push als GitHub Action.

### Felder einer Runde

`data.json` = `{ me, players, matches[], maps }`

| Feld | Bedeutung |
|---|---|
| `date`, `map` | Datum (`JJJJ-MM-TT`) und Map-Name |
| `type` | `"community"` oder `"offiziell"` |
| `shot` | Name des Screenshots in `img/`, ohne `.jpg` |
| `par` | Par pro Loch |
| `scores` | Schläge pro Loch und Spieler |
| `totals` | Gesamtschläge, nur wenn keine Lochwerte vorliegen |
| `order` | Platzierung, wenn gar keine Zahlen da sind. Gleichstand als gemeinsame Gruppe, z. B. `[["Max"], ["Ich", "Henry"]]` |
| `adjust` | Korrektur auf den Gesamtwert, z. B. `{"Max": -3}`, wenn unklar ist, auf welchem Loch sie anfällt |
| `note` | Freitext, v. a. für Korrekturen und Besonderheiten |

## Wertung

### 14 Schläge und Bugs

14 ist die Höchstzahl an Schlägen pro Loch. Eine 14 ist deshalb nicht automatisch ein Fehler: Man bekommt sie auch regulär, wenn man das Zeitlimit überschreitet, das Loch aufgibt oder nach dem 12. Schlag nicht eingelocht hat.

Manchmal treten auf einem Loch aber Bugs auf. Dann hat ein Spieler mehr Schläge, als er ohne den Bug gebraucht hätte, oder er kann das Loch gar nicht weiterspielen und bekommt die 14. Ob und wie das korrigiert wird, entscheiden die Spieler der jeweiligen Runde. Eine Korrektur wird eingetragen, indem der Lochwert geändert wird oder, falls das Loch unklar ist, per `adjust`. In beiden Fällen steht in der Notiz, was geändert wurde und welche Werte der Screenshot zeigt.

### Sonstiges

- Wer während einer Runde rausfliegt, wird normalerweise nicht gewertet. Ausnahmen stehen in der Notiz.
- Runden ohne Schlagzahlen zählen für Siege und Platzierungen, aber nicht für Schlagdifferenzen.

## Spieler

| Name im Buch | Ingame |
|---|---|
| Ich | kbb[AH] |
| Max | Diktator Mbappe |
| Henry | Jakob Schwarz |
| Florian | spUUkz |
| Robin | Jaray4r |
| Sencesless | Sencesless |
| Lauser (BOT) | Lauser |
| Mysli | mysli |
| ShiN | ShiN |

## Stärke-Wert

Die Spielerliste und die Duellmatrix sind nach einem Stärke-Wert sortiert. Er beruht auf dem Bradley-Terry-Modell: Jede Runde wird in direkte Vergleiche zerlegt (wer lag vor wem), und daraus wird für jeden Spieler ein Wert geschätzt, der diese Ergebnisse am besten erklärt. Ein Sieg gegen einen starken Gegner zählt dabei mehr als einer gegen einen schwachen.

Das passt hier, weil nicht jeder gleich oft gegen jeden spielt und die Runden unterschiedlich groß sind. Ein einfacher Schnitt aus Platzierungen oder Siegen hängt stark davon ab, gegen wen man zufällig gespielt hat. Der Stärke-Wert gleicht das aus.

Technisch: MM-Algorithmus mit 400 Iterationen, ein halber virtueller Sieg pro Spieler als Dämpfung (damit wenige Runden keine Extremwerte erzeugen), normiert auf das geometrische Mittel 1. Werte über 1 heißen stärker als der Durchschnitt.

## Commit-Nachrichten

Kurz sagen, was sich geändert hat, statt „Add files via upload“:

- `Runde 28.09.: Lozza 2`
- `Runden 23.–28.09. eintragen`
- `Screenshot Moonpine ergänzen`
- `Bug-Korrektur Sky Castles (Henry Loch 17)`
