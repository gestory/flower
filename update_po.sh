#!/usr/bin/env sh
xgettext -Lpython --output=messages.pot main.py flower.kv
msgmerge --update --no-fuzzy-matching --backup=off po/en.po messages.pot
msgmerge --update --no-fuzzy-matching --backup=off po/ru.po messages.pot
