# Flower
Game to train people with amblyopia.

## How to run app from sources
Create virtual environment

`python -m venv venv`

Activate it

`source venv/bin/activate`

Install dependencies

`pip install -r requirements.txt`

Run the app

`python main.py`

## Translation to other languages

To work with translation you need `gettext` package.

Use `update_po.sh` to update strings to be translated. After translation, update translations using `update_mo.sh`

## Thanks for media files

All sounds: http://gcompris.net/