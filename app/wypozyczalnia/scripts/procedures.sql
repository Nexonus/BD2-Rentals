--- Procedura składowa obliczająca łączny koszt z utargu zbuforowanego (SQL) + koszt zakupu sprzętu
--- Generalnie dzięki temu w zakładce Zamówienia poprawnie wyświetla się kwota do zapłaty uwzględniając
--- czas wynajmu / h
DELIMITER //

CREATE PROCEDURE przelicz_utarg_transakcji(p_transakcja_id INT)
BEGIN
    DECLARE v_suma_wynajmy DECIMAL(12,2);
    DECLARE v_suma_sprzedaz DECIMAL(12,2);

    SELECT IFNULL(SUM(
        CASE 
            WHEN termin_zwrotu IS NULL THEN cena_za_godzine
            ELSE CEIL(TIMESTAMPDIFF(SECOND, data_wypozyczenia, termin_zwrotu) / 3600.0) * cena_za_godzine
        END --- Ważne aby był CEIL bo inaczej będziemy zaokrąglać w dół różnicę godzinową (znikający koszt z wynajmu)
    ), 0) INTO v_suma_wynajmy
    FROM wypozyczalnia_wypozyczenie WHERE transakcja_id = p_transakcja_id;

    SELECT IFNULL(SUM(cena_sprzedazy), 0) INTO v_suma_sprzedaz
    FROM wypozyczalnia_zakupsprzetu WHERE transakcja_id = p_transakcja_id;

    UPDATE wypozyczalnia_transakcja
    SET utarg_calkowity_zbuforowany = v_suma_wynajmy + v_suma_sprzedaz
    WHERE id = p_transakcja_id;
END //

DELIMITER ;