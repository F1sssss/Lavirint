SET @obrada_id = 2;

INSERT INTO csv_obrada ( id, naziv, lokacija_ulaznih_csv_datoteka, lokacija_neuspjelih_csv_datoteka, lokacija_uspjelih_csv_datoteka, lokacija_izlaznih_csv_datoteka, lokacija_debug_datoteka) 
VALUES (@obrada_id, 'Perfekt', '/home/perfetkttim/input/', '/home/perfetkttim/fail/', '/home/perfetkttim/success/', '/home/perfetkttim/output/', '/home/perfetkttim/debug/');

SET @firma_id = 540;

INSERT INTO csv_obrada_ovlascenje (csv_obrada_id, firma_id) VALUES (@obrada_id, @firma_id);