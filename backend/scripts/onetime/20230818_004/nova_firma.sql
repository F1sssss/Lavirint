------------------------------------------------------------------------------------------------------------------------
-- Varijable

SET @magacin_id = 751;
SET @naplatni_uredjaj_id = 762;
SET @firma_id = 710;

------------------------------------------------------------------------------------------------------------------------
-- Dodavanje operater

SET @operater_kodoperatera = 'bu184gl964';
SET @operater_ime = 'Dragan Bošković';
SET @operater_korisnicko_ime = 'dragan';
SET @operater_lozinka = '$pbkdf2-sha256$29000$wdibc6619p7TOgfgnBPCOA$bRaLPlz.9yCwZYxtnWqgDPK6JpGWcWS.m6AKG7KrsBg';
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
    @firma_id as 'ID',
    @firma_pib as 'PIB',
    @firma_naziv as 'Naziv',
    CASE
        WHEN @firma_je_aktivna=1 THEN 'Da'
        WHEN @firma_je_aktivna=0 THEN 'Ne'
    END as 'Aktivna',
    CASE
        WHEN @firma_je_poreski_obaveznik=1 THEN 'Da'
        WHEN @firma_je_poreski_obaveznik=0 THEN 'Ne'
    END as 'PDV',
    '' as 'Dobavljač';

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;