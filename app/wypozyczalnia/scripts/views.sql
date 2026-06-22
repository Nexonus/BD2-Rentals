--- Analiza sprzedaży, produkty jakiej kategorii są sprzedawane najczęściej w jakiej kwocie
--- When zrobiony na sztywno ale trzeba by było robić podmiankę w logice BD...

CREATE OR REPLACE VIEW view_analiza_sprzedazy AS
SELECT 
    CASE s.kategoria
        WHEN 'A1' THEN 'Oświetlenie'
        WHEN 'A2' THEN 'Błotniki'
        WHEN 'A3' THEN 'Hamulce'
        WHEN 'A4' THEN 'Dzwonki'
        WHEN 'A5' THEN 'Uchwyty'
        WHEN 'A6' THEN 'Siodełka'
        WHEN 'A7' THEN 'Opony'
        WHEN 'A8' THEN 'Bagażniki'
        WHEN 'A9' THEN 'Przyczepki'
        WHEN 'A10' THEN 'Lusterka'
        WHEN 'B1' THEN 'Kaski'
        WHEN 'B2' THEN 'Zapięcia'
        WHEN 'B3' THEN 'Kamizelki'
        WHEN 'B4' THEN 'Ochraniacze'
        WHEN 'C1' THEN 'Pompki'
        WHEN 'C2' THEN 'Dętki'
        WHEN 'C3' THEN 'Liczniki'
        WHEN 'C4' THEN 'Koszyki'
        ELSE 'Inne'
    END AS 'Kategoria',
    SUM(zakup.ilosc) AS 'Liczba Sztuk', 
    SUM(zakup.cena_sprzedazy) AS 'Przychód (PLN)'
FROM wypozyczalnia_zakupsprzetu zakup
JOIN wypozyczalnia_akcesoria s ON zakup.akcesoria_id = s.id
GROUP BY `Kategoria`;

SELECT * FROM view_analiza_sprzedazy;

--- Analiza czasu wypożyczenia rowerów (ktory model najczęściej i jak długo wypożyczany)

CREATE OR REPLACE VIEW view_statystyki AS
SELECT 
    r.marka, 
    r.typ_roweru AS 'Typ',
    COUNT(w.id) AS 'Liczba wypożyczeń',
    SUM(TIMESTAMPDIFF(SECOND, w.data_wypozyczenia, w.termin_zwrotu) / 3600.0) AS 'Suma godzin'
FROM wypozyczalnia_rower r
LEFT JOIN wypozyczalnia_wypozyczenie w ON r.id = w.rower_id
GROUP BY r.id;

SELECT * FROM view_statystyki;

--- Przychód z wypożyczeń rowerów:

CREATE OR REPLACE VIEW view_przychod_rowery AS
SELECT 
    r.marka AS 'Marka/Model',
    r.typ_roweru AS 'Typ',
    COUNT(w.id) AS 'Liczba Wypożyczeń',
    SUM(
        CASE 
            WHEN w.termin_zwrotu IS NULL THEN w.cena_za_godzine
            ELSE CEIL(TIMESTAMPDIFF(SECOND, w.data_wypozyczenia, w.termin_zwrotu) / 3600.0) * w.cena_za_godzine
        END
    ) AS 'Przychód z wypożyczeń (PLN)'
FROM wypozyczalnia_rower r
JOIN wypozyczalnia_wypozyczenie w ON r.id = w.rower_id
GROUP BY r.id
ORDER BY `Przychód z wypożyczeń (PLN)` DESC;

SELECT * FROM view_przychod_rowery;

--- Liczba obsłużonych transakcji przez pracowników:

CREATE OR REPLACE VIEW view_statystyki_pracownikow AS
SELECT 
    p.imie AS 'Imię', 
    p.nazwisko AS 'Nazwisko', 
    COUNT(t.id) AS 'Liczba obsłużonych transakcji'
FROM wypozyczalnia_pracownik p
LEFT JOIN wypozyczalnia_transakcja t ON p.id = t.pracownik_id
GROUP BY p.id
ORDER BY `Liczba obsłużonych transakcji` DESC;

SELECT * FROM view_statystyki_pracownikow;

--- Lista asortymentu w danej wypożyczalni/sklepie:

CREATE OR REPLACE VIEW view_asortyment_sklep AS
SELECT 
    s.miasto AS 'Miasto',
    s.adres AS 'Adres',
    r.marka AS 'Marka',
    r.typ_roweru AS 'Typ',
    r.nr_seryjny AS 'Nr Seryjny',
    IF(r.dostepnosc = 1, 'Dostępny', 'Wypożyczony') AS 'Status'
FROM wypozyczalnia_rower r
JOIN wypozyczalnia_sklep s ON r.sklep_id = s.id
ORDER BY s.miasto, r.marka;

SELECT * FROM view_asortyment_sklep;

--- Przychód z miast w których znajdują się wypożyczalnie/sklepy:
--- Chodzi konkretnie o przychód z [wypożyczeń]

CREATE OR REPLACE VIEW view_przychody_miasta AS
SELECT 
    s.miasto AS 'Miasto',
    SUM(
        CASE 
            WHEN w.termin_zwrotu IS NULL THEN w.cena_za_godzine
            ELSE CEIL(TIMESTAMPDIFF(SECOND, w.data_wypozyczenia, w.termin_zwrotu) / 3600.0) * w.cena_za_godzine
        END
    ) AS 'Przychód całkowity'
FROM wypozyczalnia_sklep s
JOIN wypozyczalnia_rower r ON s.id = r.sklep_id
JOIN wypozyczalnia_wypozyczenie w ON r.id = w.rower_id
GROUP BY s.miasto
ORDER BY `Przychód całkowity` DESC;

SELECT * FROM view_przychody_miasta;