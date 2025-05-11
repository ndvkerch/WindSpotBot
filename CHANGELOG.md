Changelog
All notable changes to WindSpotBot will be documented in this file.
[Unreleased]
Added

Миграция Alembic для создания таблицы users с полями id, name, username, timezone, created_at.
Реализован хендлер /start с сохранением пользователя в базу данных и запросом геолокации для часового пояса.
Добавлен GeoService.get_timezone для определения часового пояса с использованием timezonefinder.
Создан src/database/init.py для инициализации базы данных.
Обновлены UserRepository и модель User для поддержки новой таблицы.
Расширено главное меню в MainKeyboards для соответствия ТЗ.

Changed

Обновлен bot.py для поддержки UserRepository и GeoService в хендлере /start.
Уточнена документация в architecture.md.

