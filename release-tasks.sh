#!/usr/bin/env bash

# Update Database
python manage.py migrate

# Sync recipe categories
python manage.py sync_recipe_categories
