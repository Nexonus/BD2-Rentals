DELIMITER //

CREATE TRIGGER trig_sprzedaz_after_insert AFTER INSERT ON wypozyczalnia_zakupsprzetu
FOR EACH ROW CALL przelicz_utarg_transakcji(NEW.transakcja_id); //

CREATE TRIGGER trig_sprzedaz_after_update AFTER UPDATE ON wypozyczalnia_zakupsprzetu
FOR EACH ROW CALL przelicz_utarg_transakcji(NEW.transakcja_id); //

CREATE TRIGGER trig_sprzedaz_after_delete AFTER DELETE ON wypozyczalnia_zakupsprzetu
FOR EACH ROW CALL przelicz_utarg_transakcji(OLD.transakcja_id); //

CREATE TRIGGER trig_wynajem_after_insert AFTER INSERT ON wypozyczalnia_wypozyczenie
FOR EACH ROW CALL przelicz_utarg_transakcji(NEW.transakcja_id); //

CREATE TRIGGER trig_wynajem_after_update AFTER UPDATE ON wypozyczalnia_wypozyczenie
FOR EACH ROW CALL przelicz_utarg_transakcji(NEW.transakcja_id); //

CREATE TRIGGER trig_wynajem_after_delete AFTER DELETE ON wypozyczalnia_wypozyczenie
FOR EACH ROW CALL przelicz_utarg_transakcji(OLD.transakcja_id); //

DELIMITER ;

--- Trigery obsługujące procedurę składową dla sprzedaży i wynajmu.

