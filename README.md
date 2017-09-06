# mOffWiki

Downloads Wiki pages from https://the-morpheus.de/wiki and keep them up to date.
Other wikimedia wiki's should work too.
Für Einstellungen ist die config.json .

```
{
    "changes_src": "/wiki/?title=Spezial:Letzte_%C3%84nderungen", die Seite auf der Änderungen an Artikeln gezeigt werden
    "path": "wiki/", der Pfad an dem die Artikel gespeichert werden
    "domain": "https://the-morpheus.de", die Domain der Wiki
    "pages": [ Die Artikel die heruntergeladen/aktualisiert werden
        "python",
        "java",
        "perl"
    ],
    "last_update": "20170905190115" Datum + Zeit in UTC der letzen Aktualisierung
}
```