# nexdex.space — sources

это открытая версия исходников (для гита) — читаемый python/flask код без
скомпилированных бинарей. если нужен готовый инструмент — смотри релиз
`nexdex.space-setup.exe`, который разворачивает всё сам (portable python +
ffmpeg внутри, ничего ставить не надо). лицензия — MIT, см. `LICENSE`.

---

## структура

```
app/          — flask-приложение (см. app/README.md — там всё подробно)
  app.py
  backend/     — downloader, converter, metadata, scripts_format, search, history
  templates/
  static/
installer/    — исходники установщика (реальный, рабочий C++)
  installer.cpp   — консольный лаунчер: при первом запуске достаёт из себя
                    зашитый ресурс (payload.zip — portable python + весь
                    app/ + ffmpeg), распаковывает в %LOCALAPPDATA%\nexdex.space,
                    создаёт ярлык на рабочем столе, дальше просто запускает
  installer.rc    — иконка + payload как RCDATA-ресурс + версия файла
                    (CompanyName/LegalCopyright = savsis)
  icon.ico

LICENSE       — MIT, savsis
```

## как собрать установщик самому

1. поставь python 3.11 embeddable (`python-3.11.9-embed-amd64.zip` с python.org),
   включи `import site` в `python311._pth`, добавь строку `Lib\site-packages`,
   поставь pip (`get-pip.py`), затем `pip install -r app/requirements.txt`
   этим же python'ом.
2. положи скачанный/собранный `ffmpeg.exe`+`ffprobe.exe` в `app/ffmpeg/`.
3. запакуй `python\` и `app\` (портативный питон + приложение) в `payload.zip`
   рядом с папкой `installer\`.
4. собери через MSVC:
   ```
   rc.exe /fo installer.res installer.rc
   cl.exe /std:c++17 /EHsc /O2 installer.cpp installer.res /Fe:nexdex.space-setup.exe /link shell32.lib ole32.lib
   ```
   `installer.rc` ссылается на `..\payload.zip` и зашивает его прямо в exe
   как ресурс (RCDATA) — поэтому результат остаётся нормальным PE-файлом
   (в отличие от "приклеивания" zip после exe, что ломает Authenticode-подпись).

---

made by savsis with <3
