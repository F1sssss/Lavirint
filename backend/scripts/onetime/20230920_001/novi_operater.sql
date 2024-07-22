------------------------------------------------------------------------------------------------------------------------
-- Varijable

SET @firma_id = 935;
SET @magacin_id = 976;
SET @naplatni_uredjaj_id = 994;

------------------------------------------------------------------------------------------------------------------------
-- Dodavanje operater

SET @operater_kodoperatera = 'mk099zt826';
SET @operater_ime = 'ANĐELA JAĆIMOVIĆ';
SET @operater_korisnicko_ime = 'andjela';
SET @operater_lozinka = '$pbkdf2-sha256$29000$nZNyLkWIMUaIkbLWGsMYgw$qcpHb58GTkFj6FJU1.BnnPly3q/KVcuiKJkZCUoXWeA';
SET @operater_admin = 0;
SET @operater_aktivan = 1;

INSERT INTO megas.operater (
    ime, 
    lozinka, 
    email, 
    kodoperatera, 
    admin, 
    aktivan, 
    magacin_id, 
    naplatni_uredjaj_id, 
    firma_id
) VALUES (
    @operater_ime, 
    @operater_lozinka, 
    @operater_korisnicko_ime, 
    @operater_kodoperatera, 
    @operater_admin, 
    @operater_aktivan, 
    @magacin_id, 
    @naplatni_uredjaj_id, 
    @firma_id
);
SET @operater_id = LAST_INSERT_ID();

------------------------------------------------------------------------------------------------------------------------
-- Dodavanje podešavanja operatera

-- SET @podesavanje_pocetna_stranica = '/prodaja/racun/unos';
-- SET @podesavanje_pocetna_stranica = '/faktura/grupe/unos';
SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';


SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
-- SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'po_artiklu';

SET @podrazumijevani_tip_stampe = '58mm';
-- SET @podrazumijevani_tip_stampe = 'A4';

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id
);

------------------------------------------------------------------------------------------------------------------------
-- Selekcija za Excel

SELECT
    @firma_id,
    @operater_id,
    @operater_korisnicko_ime,
    @naplatni_uredjaj_id;