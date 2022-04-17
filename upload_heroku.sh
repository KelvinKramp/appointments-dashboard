#!/bin/sh
pip freeze > requirements.txt
git add .
git commit -m "update"
git push origin main
git push heroku main
