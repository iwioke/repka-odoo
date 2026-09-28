# Repka AI Automation — business presentation

Готовый файл: `Repka_AI_Automation.pptx` (14 слайдов, 16:9, русский язык). Основана на четырёх протестированных DEMO с детерминированными правилами и синтетическими примерами; остальные направления явно помечены FUTURE. Не заявляет о внедрённой ML-модели, OCR или production-интеграции.

Для показа достаточно открыть PPTX в PowerPoint/Keynote. Для пересборки нужен Python 3.9+ и пакет `python-pptx==1.0.2` (только build-зависимость; сценарии не зависят от него):

```sh
python3 -m pip install 'python-pptx==1.0.2'
python3 ai_automations/.internal/build_presentation.py
```

Проверена целостность PPTX-архива, наличие 14 слайдов, границы всех объектов и Quick Look thumbnail титульного слайда. Полную визуальную проверку остальных слайдов в PowerPoint/Keynote стоит сделать перед внешним показом; PDF не создан (в среде нет LibreOffice/PDF-конвертера).
