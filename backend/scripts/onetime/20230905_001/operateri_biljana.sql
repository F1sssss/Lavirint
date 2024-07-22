SET @magacin_id = 1234;
SET @naplatni_uredjaj_id = 1256;
SET @firma_id = 1191;

SET @operater_kodoperatera = 'ud404cs781';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1208;
SET @naplatni_uredjaj_id = 1230;
SET @firma_id = 1165;

SET @operater_kodoperatera = 'pc838do429';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1206;
SET @naplatni_uredjaj_id = 1228;
SET @firma_id = 1163;

SET @operater_kodoperatera = 'my745jk925';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1195;
SET @naplatni_uredjaj_id = 1217;
SET @firma_id = 1152;

SET @operater_kodoperatera = 'jg379xx962';
SET @operater_ime = 'OLIVERA TODOROVIC';
SET @operater_korisnicko_ime = 'olivera';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1098;
SET @naplatni_uredjaj_id = 1119;
SET @firma_id = 1057;

SET @operater_kodoperatera = 'yj607qg947';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1136;
SET @naplatni_uredjaj_id = 1159;
SET @firma_id = 1095;

SET @operater_kodoperatera = 'fr355ff855';
SET @operater_ime = 'OLIVERA TODOROVIC';
SET @operater_korisnicko_ime = 'olivera';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1135;
SET @naplatni_uredjaj_id = 1158;
SET @firma_id = 1094;

SET @operater_kodoperatera = 'il298py906';
SET @operater_ime = 'OLIVERA TODOROVIC';
SET @operater_korisnicko_ime = 'olivera';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1133;
SET @naplatni_uredjaj_id = 1156;
SET @firma_id = 1092;

SET @operater_kodoperatera = 'pp237yg591';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1085;
SET @naplatni_uredjaj_id = 1104;
SET @firma_id = 1044;

SET @operater_kodoperatera = 'sf776gf399';
SET @operater_ime = 'OLIVERA TODOROVIC';
SET @operater_korisnicko_ime = 'olivera';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1082;
SET @naplatni_uredjaj_id = 1101;
SET @firma_id = 1041;

SET @operater_kodoperatera = 'oy984vs642';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1052;
SET @naplatni_uredjaj_id = 1070;
SET @firma_id = 1011;

SET @operater_kodoperatera = 'al462lk429';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1036;
SET @naplatni_uredjaj_id = 1054;
SET @firma_id = 995;

SET @operater_kodoperatera = 'fd735hn312';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1035;
SET @naplatni_uredjaj_id = 1053;
SET @firma_id = 994;

SET @operater_kodoperatera = 'gr610ed769';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 989;
SET @naplatni_uredjaj_id = 1007;
SET @firma_id = 948;

SET @operater_kodoperatera = 'ov796qg939';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 990;
SET @naplatni_uredjaj_id = 1008;
SET @firma_id = 949;

SET @operater_kodoperatera = 'vx196ph615';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 981;
SET @naplatni_uredjaj_id = 999;
SET @firma_id = 940;

SET @operater_kodoperatera = 'hs587hh265';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 919;
SET @naplatni_uredjaj_id = 935;
SET @firma_id = 878;

SET @operater_kodoperatera = 'ai304or167';
SET @operater_ime = 'IVANA STANKOVIC';
SET @operater_korisnicko_ime = 'ivana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$jLE2hjAmBICwNgYAoJRybg$Wc9rswMZbSww52swxMEFfJTZMkXgcsYD.a0BFgGuSN4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 892;
SET @naplatni_uredjaj_id = 908;
SET @firma_id = 851;

SET @operater_kodoperatera = 'pd822ru948';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 893;
SET @naplatni_uredjaj_id = 909;
SET @firma_id = 852;

SET @operater_kodoperatera = 'tt570xa253';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 897;
SET @naplatni_uredjaj_id = 913;
SET @firma_id = 856;

SET @operater_kodoperatera = 'iv568zj509';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/prodaja/racun/unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'po_artiklu';
SET @podrazumijevani_tip_stampe = '58mm';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 881;
SET @naplatni_uredjaj_id = 897;
SET @firma_id = 840;

SET @operater_kodoperatera = 'la145ex649';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/prodaja/racun/unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'po_artiklu';
SET @podrazumijevani_tip_stampe = '58mm';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 585;
SET @naplatni_uredjaj_id = 590;
SET @firma_id = 543;

SET @operater_kodoperatera = 'oq678si895';
SET @operater_ime = 'OLIVERA TODOROVIC';
SET @operater_korisnicko_ime = 'olivera';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/prodaja/racun/unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = 1;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 681;
SET @naplatni_uredjaj_id = 690;
SET @firma_id = 639;

SET @operater_kodoperatera = 'yr114hy007';
SET @operater_ime = 'OLIVERA TODOROVIC';
SET @operater_korisnicko_ime = 'olivera';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = 1;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1236;
SET @naplatni_uredjaj_id = 1258;
SET @firma_id = 1193;

SET @operater_kodoperatera = 'rk015gy377';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 416;
SET @naplatni_uredjaj_id = 421;
SET @firma_id = 401;

SET @operater_kodoperatera = 've376sl005';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/prodaja/racun/unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'po_artiklu';
SET @podrazumijevani_tip_stampe = '58mm';
SET @vidi_dospjele_fakture = 1;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 614;
SET @naplatni_uredjaj_id = 621;
SET @firma_id = 572;

SET @operater_kodoperatera = 'rf011eb247';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = 1;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1235;
SET @naplatni_uredjaj_id = 1257;
SET @firma_id = 1192;

SET @operater_kodoperatera = 'xc886ti434';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 626;
SET @naplatni_uredjaj_id = 633;
SET @firma_id = 584;

SET @operater_kodoperatera = 'aa592qk946';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = 1;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 1326;
SET @naplatni_uredjaj_id = 1350;
SET @firma_id = 1281;

SET @operater_kodoperatera = 'vp191cm378';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 288;
SET @naplatni_uredjaj_id = 288;
SET @firma_id = 275;

SET @operater_kodoperatera = 'fx005ml711';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/prodaja/racun/unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'po_artiklu';
SET @podrazumijevani_tip_stampe = '58mm';
SET @vidi_dospjele_fakture = 1;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 274;
SET @naplatni_uredjaj_id = 274;
SET @firma_id = 261;

SET @operater_kodoperatera = 'pj797mq693';
SET @operater_ime = 'OLIVERA TODOROVIC';
SET @operater_korisnicko_ime = 'olivera';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/prodaja/racun/unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'po_artiklu';
SET @podrazumijevani_tip_stampe = '58mm';
SET @vidi_dospjele_fakture = 1;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 872;
SET @naplatni_uredjaj_id = 887;
SET @firma_id = 831;

SET @operater_kodoperatera = 'zb539ba322';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/racun/opsti_unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'slobodan_unos';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = NULL;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


SET @magacin_id = 114;
SET @naplatni_uredjaj_id = 114;
SET @firma_id = 114;

SET @operater_kodoperatera = 'ga549dh593';
SET @operater_ime = 'BILJANA COLIC';
SET @operater_korisnicko_ime = 'biljana';
SET @operater_lozinka = '$pbkdf2-sha256$29000$tFbKmbPW2nsv5dw7Z0xJKQ$6Tgl.eSm68OoZERmasX2im7aelnn3uo.s3HcJs0c9l4';
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

SET @podesavanje_pocetna_stranica = '/prodaja/racun/unos';
SET @podesavanje_podrazumijevani_tip_unosa_stavke_fakture = 'po_artiklu';
SET @podrazumijevani_tip_stampe = 'A4';
SET @vidi_dospjele_fakture = 1;

INSERT INTO `podesavanja_aplikacije` (
    pocetna_stranica, 
    podrazumijevani_tip_unosa_stavke_fakture, 
    podrazumijevani_tip_stampe, 
    operater_id,
    vidi_dospjele_fakture
) VALUES (
    @podesavanje_pocetna_stranica, 
    @podesavanje_podrazumijevani_tip_unosa_stavke_fakture, 
    @podrazumijevani_tip_stampe, 
    @operater_id,
    @vidi_dospjele_fakture
);

SELECT
    @firma_id,
    @firma_naziv,
    @operater_id,
    @operater_korisnicko_ime,
    '',
    @naplatni_uredjaj_id;