@echo off
REM Setup test database for Django tests
REM Run this ONCE to set up the test database

echo Setting up test database...
psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS test_fusionlab;"
psql -U postgres -d postgres -c "CREATE DATABASE test_fusionlab TEMPLATE fusionlab;"

echo.
echo Test database created successfully!
echo.
echo Now run tests with: python manage.py test --keepdb
echo.
pause
