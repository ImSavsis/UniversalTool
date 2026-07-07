# nexdex.space

локальный веб-инструмент — качает музыку/видео, конвертирует файлы, редактирует
метаданные треков, форматирует py/lua скрипты. открывается сам в браузере на
`localhost`, тёмная тема, гугл-минимализм.

---

## что внутри

**загрузчик** — вставляешь ссылку (youtube / soundcloud / apple music / spotify /
yandex music) или ищешь по названию (видно обложку+автора перед скачиванием),
выбираешь формат — качает и вшивает обложку+теги. для spotify/apple music метаданные
берутся с официальных публичных api, а само аудио ищется и качается с youtube —
без взлома drm. история последних скачиваний сохраняется локально.

**конвертер** — картинки (webp, png, jpg, ico и генерация иконок из любой картинки),
pdf, pptx, аудио (flac/wav/mp3/m4a/ogg/opus/aac), видео (mp4/avi/mov/mkv/webm/gif).
честно: pptx → картинка/pdf не поддерживается (нужен libreoffice/powerpoint для
рендера слайдов — тяжёлая внешняя зависимость, спорит с идеей лёгкого инструмента).

**метаданные** — редактор тегов для mp3/flac/wav/m4a/ogg/opus: название, исполнитель,
альбом, год, номер трека, обложка. есть массовый режим — применить одного исполнителя/
альбом/обложку сразу на несколько файлов.

**скрипты** — форматирование `.py` (black) и `.lua` (stylua, качается сам при первом
использовании), подсветка синтаксических ошибок.

---

## что нужно

- python 3.10+
- ffmpeg — уже лежит в `ffmpeg\`, ничего доп. качать не надо

## установка

```
pip install -r requirements.txt
```

## запуск

```
python app.py
```

или просто дважды кликнуть `start.bat`. браузер откроется сам на
`http://127.0.0.1:5000`. порт меняется через `PORT=8080 python app.py`.

---

## форматы загрузчика

| # | формат | качество |
|---|--------|----------|
| 1 | MP3 | 320 / 256 / 192 / 128 kbps |
| 2 | FLAC | lossless |
| 3 | WAV | lossless |
| 4 | M4A | best |
| 5 | ALAC | lossless |
| 6 | OGG | best |
| 7 | OPUS | best |
| 8 | MP4 | видео + аудио |

---

## структура

```
app.py                    — flask entrypoint, сам открывает браузер
backend/
  downloader.py            — detect_platform, download_track (youtube/spotify/apple/yandex/vk)
  jobs.py                  — фоновые задачи скачивания + прогресс
  search.py                — поиск по youtube/soundcloud/apple music
  history.py                — история скачанных треков (data/history.json)
  converter.py               — картинки/pdf/pptx/аудио/видео
  metadata.py                 — чтение/запись тегов+обложки
  scripts_format.py            — black + stylua
templates/index.html
static/css/style.css
static/js/app.js
ffmpeg/                    — ffmpeg.exe, ffprobe.exe
bin/                       — сюда качается stylua.exe при первом форматировании lua
data/history.json
downloads/ uploads/ outputs/
```

---

UDP: часть про поиск/скачивание работает через публичные api и youtube — если
ссылка "не режимного" сервиса не отдаёт данные без логина, так и напишет в ошибке.
pptx рендер слайдов — эксперимент на будущее, если приспичит тащить libreoffice.
made by savsis with ♥
