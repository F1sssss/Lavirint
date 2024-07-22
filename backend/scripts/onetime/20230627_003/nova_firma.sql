SET @magacin_id = '1275';
SET @naplatni_uredjaj_id = '1299';
SET @firma_id = '1232';
SET @firma_pib = '03372804';

SET @operater_kodoperatera = 'jp205ge720';
SET @operater_ime = 'RUSLAN FAIZMATOV';
SET @operater_korisnicko_ime = 'ruslan';
SET @operater_lozinka = '$pbkdf2-sha256$29000$6p0TwphzLiWk9J6T0hpDiA$cMEwl2D9sOtPduf5wMPDPh.3I8cVk8R7WcwUv0LqIWA';
SET @operater_pib = @firma_pib;
SET @operater_kljuc = '4AVDH4TTKWRRM5KYGYHBCUNTPG7KWEXJ';  -- Deprecated
SET @operater_admin = 0;
SET @operater_aktivan = 1;

INSERT INTO megas.operater (
    ime, 
    lozinka, 
    email, 
    pib, 
    kljuc, 
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
    @operater_pib, 
    @operater_kljuc, 
    @operater_kodoperatera, 
    @operater_admin, 
    @operater_aktivan, 
    @magacin_id, 
    @naplatni_uredjaj_id, 
    @firma_id
);
SET @operater_id = LAST_INSERT_ID();

SET @podesavanje_pocetna_stranica = '/prodaja/racun/unos';
-- SET @podesavanje_pocetna_stranica = '/faktura/grupe/unos';
-- SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';


-- @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'po_artiklu';

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