SET @obrada_id = 4;

INSERT INTO csv_obrada ( id, naziv, lokacija_ulaznih_csv_datoteka, lokacija_neuspjelih_csv_datoteka, lokacija_uspjelih_csv_datoteka, lokacija_izlaznih_csv_datoteka, lokacija_debug_datoteka, format_datoteke) 
VALUES (@obrada_id, 'Perfekt', '/home/boca/csv/elavirint/input/', '/home/boca/csv/elavirint/fail/', '/home/boca/csv/elavirint/success/', '/home/boca/csv/elavirint/output/', '/home/boca/csv/elavirint/debug/', 'elavirint');

SET @firma_id = 241;

INSERT INTO csv_obrada_ovlascenje (csv_obrada_id, firma_id) VALUES (@obrada_id, @firma_id);

UPDATE naplatni_uredjaj SET podrazumijevani_iznos_depozita=0 WHERE id IN (513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540);

INSERT INTO organizaciona_jedinica (efi_kod, firma_id, adresa, grad, drzava_id) VALUES ('sa426ks811', @firma_id, 'MOJSIJA ZEČEVIĆA 7', 'Berane', 39);
SET @organizaciona_jedinica_id = LAST_INSERT_ID();

INSERT INTO naplatni_uredjaj (efi_kod, organizaciona_jedinica_id, tip_naplatnog_uredjaja_id, podrazumijevani_iznos_depozita) VALUES ('uq506fv728', 536, 1, 0);
SET @naplatni_uredjaj_id = LAST_INSERT_ID();

SET @magacin_id = 536;
SET @operater_kodoperatera = 'zt151nz802';
SET @operater_ime = 'Test Test';
SET @operater_korisnicko_ime = 'test';
SET @operater_lozinka = '';
SET @operater_pib = @firma_pib;
SET @operater_kljuc = '4AVDH4TTKWRRM5KYGYHBCUNTPG7KWEXJ';
SET @operater_admin = 0;
SET @operater_aktivan = 1;

INSERT INTO megas.operater (ime, lozinka, email, pib, kljuc, kodoperatera, admin, aktivan, magacin_id, naplatni_uredjaj_id, firma_id) 
VALUES (@operater_ime, @operater_lozinka, @operater_korisnicko_ime, @operater_pib, @operater_kljuc, @operater_kodoperatera, @operater_admin, @operater_aktivan, @magacin_id, @naplatni_uredjaj_id, @firma_id);
SET @operater_id = LAST_INSERT_ID();

SET @podesavanje_pocetna_stranica = 'prodaja/racun/unos';
-- SET @podesavanje_pocetna_stranica = 'racun/opsti_unos';

SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
-- SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'po_artiklu';

SET @podrazumijevani_tip_stampe = '58mm';
-- SET @podrazumijevani_tip_stampe = 'A4';

INSERT INTO `podesavanja_aplikacije` (pocetna_stranica, podrazumijevani_tip_unosa_stavke_fakture, podrazumijevani_tip_stampe, operater_id) 
VALUES (@podesavanje_pocetna_stranica, @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, @podrazumijevani_tip_stampe, @operater_id);