@echo off
REM Run Django tests with --keepdb flag
REM This reuses the test database instead of recreating it

echo Running Django tests...
python manage.py test --keepdb %*
