--- Terminal PS: Get-Content query.sql | python manage.py dbshell
--- Albo uruchamiamy runquery.ps1

SELECT * FROM wypozyczalnia_transakcja AS TR WHERE TR.kaucja_pobrana LIKE 300;