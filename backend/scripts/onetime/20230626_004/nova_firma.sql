------------------------------------------------------------------------------------------------------------------------
-- Dodavanje firme

SET @firma_pib = '03411974';
SET @firma_je_poreski_obaveznik = 0;
SET @firma_naziv = 'D.O.O. "BLUE LIFE COMPANY"';
SET @firma_pdvbroj = '';
SET @firma_adresa = 'ULICA MASLINA BR. 20, LOKAL BR. 2';
SET @firma_grad = 'BUDVA';
SET @firma_drzava = 39;
SET @firma_telefon = '';
SET @firma_email = '';
SET @firma_ziroracun = '';
SET @firma_kodorganizacionejedinice = 'aj014mb503';  -- Deprecated
SET @firma_tcrkod = 'av764if608';  -- Deprecated
SET @firma_kodsoftvera = 'gg387fl042';  -- Deprecated
SET @firma_tip_naplatnog_uredjaja = 1;
SET @firma_je_aktivna=1;
SET @firma_cert_pass = 'gAAAAABkmeaqc1guqQE7pfnzNpTEG6JP5AF0As6hYLYJQwJ_RB_od0IbvaVcowUOh4lDBlBy3_3YH69EST_WG41dpKiQrbqjVw==';

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
    kodorganizacionejedinice, 
    tcrkod, 
    kodsoftvera, 
    je_poreski_obaveznik, 
    tip_naplatnog_uredjaja_id, 
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
    @firma_kodorganizacionejedinice, 
    @firma_tcrkod, 
    @firma_kodsoftvera, 
    @firma_je_poreski_obaveznik, 
    @firma_tip_naplatnog_uredjaja, 
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

SET @organizaciona_jedinica_efi_kod = 'mn420hr275';
SET @organizaciona_jedinica_adresa = 'MASLINA BB';
SET @organizaciona_jedinica_grad = 'BUDVA';
SET @organizaciona_jedinica_drzava = 39;
SET @organizaciona_jedinica_naziv = '';

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

SET @naplatni_uredjaj_id = 'jw112qh562';

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
-- Dodavanje operater i podešavanja

SET @operater_kodoperatera = 'ed014pk100';
SET @operater_ime = 'DIMEN ESER';
SET @operater_korisnicko_ime = 'dimen';
SET @operater_lozinka = '$pbkdf2-sha256$29000$YqxVao2x1ppzjhGidM65dw$97.0atJc8Z5cj2AjDoWGzjPShgU5iSheuhIUpE7t7KI';
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

-- SET @podesavanje_pocetna_stranica = '/prodaja/racun/unos';
-- SET @podesavanje_pocetna_stranica = '/faktura/grupe/unos';
SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';


@podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
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