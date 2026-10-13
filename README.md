# MDFlavours

The flavour catalog for the Dew Tracker app, published so the app can download updates.

- `catalog.json`: the full catalog (released flavours only)
- `version.json`: a small file the app checks first, so it only downloads the catalog when it changed
- `scripts/validate.py`: run before every commit; checks the rules below and writes `version.json`

The app reads these through raw GitHub links:

```
https://raw.githubusercontent.com/OldGafferSoftware/MDFlavours/main/version.json
https://raw.githubusercontent.com/OldGafferSoftware/MDFlavours/main/catalog.json
```

The catalog is refreshed each morning by a scheduled task. Each update is one commit, so the history is a record of every change.

## Format

```json
{
  "schemaVersion": 1,
  "version": 2,
  "generated": "2026-10-14",
  "count": 141,
  "license": "CC BY-SA 4.0",
  "attribution": "https://github.com/OldGafferSoftware/MDFlavours#attribution",
  "flavours": [
    {
      "id": "mountain-dew-baja-blast",
      "name": "Baja Blast",
      "notes": "Description shown at the top of the flavour screen",
      "status": "current",
      "markets": ["US", "UK"],
      "availability": "Where to find it, if not ordinary stores",
      "zeroSugar": true,
      "since": "2004",
      "update": "Short note on the latest status",
      "sourceURL": "https://…",
      "discontinued": false
    }
  ]
}
```

`status` is `current`, `limited` (on sale for a limited time), `retired`, or `null` when the current status isn't known. `discontinued` repeats `status == "retired"` for app version 0.1, which only reads that field. Every field except `id` and `name` may be `null`.

## Rules

1. Released flavours only. No upcoming, rumoured or cancelled flavours, and no alcoholic products.
2. An `id` is permanent. Never remove or rename one: people's tastings are stored against it. A flavour that ends is marked `retired`.
3. Any change to `flavours` raises `version` by exactly 1.
4. Run `python3 scripts/validate.py` before committing. It refuses a catalog that breaks these rules.

## Attribution

Many entries, and most `notes` text, are adapted from the Wikipedia article [List of Mountain Dew flavors and varieties](https://en.wikipedia.org/wiki/List_of_Mountain_Dew_flavors_and_varieties) by its contributors ([history](https://en.wikipedia.org/w/index.php?title=List_of_Mountain_Dew_flavors_and_varieties&action=history)), snapshot of 2026-10-10. Status, market and availability details also draw on the news sources linked in each entry's `sourceURL`, written in our own words.

Changes from the article: kept each entry's name and the first sentence of its notes; removed citation markers; combined the tables into one list; removed a leading "Mountain Dew" from names; added "(Energy)" to four energy drink names; left out alcoholic products and two repeated entries; added `id`, `status`, `markets`, `availability`, `zeroSugar`, `since`, `update` and `sourceURL`; added entries for flavours released after the snapshot.

The catalog is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). This license covers the catalog data only, not the names, which may be trademarks of their owners. This is an unofficial fan project, not affiliated with or endorsed by any brand owner or by Wikipedia.
