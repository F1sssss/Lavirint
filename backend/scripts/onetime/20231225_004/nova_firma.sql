------------------------------------------------------------------------------------------------------------------------
-- Dodavanje firme

SET @firma_pib = '02790602';
SET @firma_je_poreski_obaveznik = 1;
SET @firma_naziv = 'D.O.O. "CILING"';
SET @firma_pdvbroj = '';
SET @firma_adresa = 'TOTOŠI BB';
SET @firma_grad = 'ULCINJ';
SET @firma_drzava = 39;
SET @firma_telefon = '';
SET @firma_email = '';
SET @firma_ziroracun = '';
SET @firma_je_aktivna = 1;
SET @firma_cert_pass = 'gAAAAABliZPNJ_EdifyoLMirTxBlnOpgylaz1YL5KbwVBWzYB4snDkzxvMm5AldH_-yz4ySmpdnM6fJX1CgePdh9d46TGvFBew==';

INSERT INTO megas.firma (
    naziv, 
    pib, 
    pdvbroj, 
    adresa, 
    telefon, 
    email, 
    ziroracun, 
    drzava, 
    grad, 
    je_poreski_obaveznik, 
    je_aktivna, 
    certificate_password
) VALUES (
    @firma_naziv, 
    @firma_pib, 
    @firma_pdvbroj, 
    @firma_adresa, 
    @firma_telefon, 
    @firma_email, 
    @firma_ziroracun, 
    @firma_drzava, 
    @firma_grad, 
    @firma_je_poreski_obaveznik, 
    @firma_je_aktivna, 
    @firma_cert_pass
);
SET @firma_id = LAST_INSERT_ID();

INSERT INTO megas.company_settings (
    company_id, 
    smtp_active, 
    smtp_host, 
    smtp_port, 
    smtp_mail, 
    smtp_username, 
    smtp_password
) values (
    @firma_id, 
    0, 
    NULL, 
    NULL, 
    NULL, 
    NULL, 
    NULL
);

INSERT INTO megas.jedinica_mjere (firma_id, naziv, opis, ui_default) VALUES (@firma_id, 'kom', 'komad', 1);
INSERT INTO megas.jedinica_mjere (firma_id, naziv, opis, ui_default) VALUES (@firma_id, 'l', 'litar', 0);
INSERT INTO megas.jedinica_mjere (firma_id, naziv, opis, ui_default) VALUES (@firma_id, 'kg', 'kilogram', 0);
INSERT INTO megas.jedinica_mjere (firma_id, naziv, opis, ui_default) VALUES (@firma_id, 'm', 'metar', 0);
INSERT INTO megas.jedinica_mjere (firma_id, naziv, opis, ui_default) VALUES (@firma_id, 'm2', 'kvadratni metar', 0);
INSERT INTO megas.jedinica_mjere (firma_id, naziv, opis, ui_default) VALUES (@firma_id, 'm3', 'kubni metar', 0);
INSERT INTO megas.jedinica_mjere (firma_id, naziv, opis, ui_default) VALUES (@firma_id, 'g', 'gram', 0);
INSERT INTO megas.jedinica_mjere (firma_id, naziv, opis, ui_default) VALUES (@firma_id, 't', 'tona', 0);
INSERT INTO megas.jedinica_mjere (firma_id, naziv, opis, ui_default) VALUES (@firma_id, 'par', 'par', 0);
INSERT INTO megas.jedinica_mjere (firma_id, naziv, opis, ui_default) VALUES (@firma_id, 'k', 'karat', 0);
INSERT INTO megas.jedinica_mjere (firma_id, naziv, opis, ui_default) VALUES (@firma_id, 'd', 'dan', 0);

------------------------------------------------------------------------------------------------------------------------
-- Dodavanje grupe artikala

INSERT INTO megas.grupa_artikala (
    naziv, 
    ui_default, 
    firma_id
) VALUES (
    'Bez grupe', 
    1, 
    @firma_id
);
SET @grupa_artikala_id = LAST_INSERT_ID();

INSERT INTO megas.magacin (naziv, firma_id) VALUES ('magacin01', @firma_id);
SET @magacin_id = LAST_INSERT_ID();

-----------------------------------------------------------------------------------------------------------------------
-- Dodavanje organizacione jedinice

SET @organizaciona_jedinica_efi_kod = 'au491cb876';
SET @organizaciona_jedinica_naziv = '';
SET @organizaciona_jedinica_adresa = 'MEHMET GJYLI BB';
SET @organizaciona_jedinica_grad = 'ULCINJ';
SET @organizaciona_jedinica_drzava = 39;

INSERT INTO `organizaciona_jedinica` (
    efi_kod, 
    adresa, 
    grad, 
    drzava_id, 
    firma_id, 
    naziv
) VALUES (
    @organizaciona_jedinica_efi_kod, 
    @organizaciona_jedinica_adresa, 
    @organizaciona_jedinica_grad, 
    @organizaciona_jedinica_drzava, 
    @firma_id, 
    @organizaciona_jedinica_naziv
);
SET @organizaciona_jedinica_id = LAST_INSERT_ID();

------------------------------------------------------------------------------------------------------------------------
-- Dodavanje podešavanja organizacione jedinice

SET @organizaciona_jedinica_settings_default_invoice_note = '';

INSERT INTO `organizational_unit_settings` (
    organizational_unit_id, 
    default_invoice_note
) VALUES (
    @organizaciona_jedinica_id, 
    @organizaciona_jedinica_settings_default_invoice_note
);
SET @organizational_unit_settings_id = LAST_INSERT_ID();

------------------------------------------------------------------------------------------------------------------------
-- Dodavanje naplatnog uređaja

SET @naplatni_uredjaj_id = 'ta066yc414';

SET @tip_naplatnog_uredjaja_id = 1;  -- Suunmi
-- SET @tip_naplatnog_uredjaja_id = 2;  -- Pipo
-- SET @tip_naplatnog_uredjaja_id = 3;  -- Z91

INSERT INTO `naplatni_uredjaj` (
    efi_kod,
    organizaciona_jedinica_id, 
    tip_naplatnog_uredjaja_id
) VALUES (
    @naplatni_uredjaj_id, 
    @organizaciona_jedinica_id, 
    @tip_naplatnog_uredjaja_id
);
SET @naplatni_uredjaj_id=LAST_INSERT_ID();

INSERT INTO `invoice_processing_lock` VALUES (@naplatni_uredjaj_id);
INSERT INTO `credit_note_processing_lock` VALUES (@naplatni_uredjaj_id);

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
    END as 'PDV';

------------------------------------------------------------------------------------------------------------------------
-- Dodavanje operatera

SET @operater_kodoperatera = 'lb426ec311';
SET @operater_ime = 'ISUF KALEZIC';
SET @operater_korisnicko_ime = 'isuf';
SET @operater_lozinka = '$pbkdf2-sha256$29000$0Pq/F0KIMWbMWWsNwfi/tw$i/.685gzvdzSq/oaqLSS4LOtOvf43VwLOYigxosiIhM';
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
-- Selekcija operatera

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    @naplatni_uredjaj_id;
