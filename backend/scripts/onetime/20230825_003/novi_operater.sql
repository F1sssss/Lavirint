------------------------------------------------------------------------------------------------------------------------
-- Varijable

SET @magacin_id = 1345;
SET @naplatni_uredjaj_id = 1370;
SET @firma_id = 1299;

------------------------------------------------------------------------------------------------------------------------
-- Dodavanje operater

SET @operater_kodoperatera = 'uf734ol033';
SET @operater_ime = 'LEDJAN DAUTI';
SET @operater_korisnicko_ime = 'ledjan';
SET @operater_lozinka = '$pbkdf2-sha256$29000$.L.3dg6hlNL6H0OI0bp37g$SjOYiK3a3zf4pgYO4IFBpnh/MGF2NCIS1WFsdlExhj4';
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

-- SET @podrazumijevani_tip_stampe = '58mm';
SET @podrazumijevani_tip_stampe = 'A4';

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
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;