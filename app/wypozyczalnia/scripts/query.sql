--- Terminal PS: Get-Content query.sql | python manage.py dbshell
--- Albo uruchamiamy runquery.ps1

--- Query Sandbox, to do testowania danych i funkcjonalności...

SELECT * FROM wypozyczalnia_transakcja AS TR WHERE TR.kaucja_pobrana LIKE 300;

USE WypozyczalniaDB;

SELECT * FROM wypozyczalnia_wypozyczenie;
UPDATE wypozyczalnia_wypozyczenie
SET data_wypozyczenia = DATE_SUB(data_wypozyczenia, INTERVAL 3 HOUR)
WHERE id = 12;

SHOW TABLES;