# django-admin-tui
A terminal UI for Django written in Python.

Adds a TUI that brings the admin dashboard (save for Admin Actions) to the terminal.  

## Installation and running
1. Install `django_admin_tui` and go to your Django project 
2. Add `'django_admin_tui'` to `INSTALLED_APPS`
3. Register your models with the default admin (TODO: support custom `AdminSite`s)
4. Run the TUI with `./manage.py admin-tui` 

## Controls:
\# TODO 

## Actions
Since regular django Admin Actions require an HTTP request, actions in the TUI are different. 
