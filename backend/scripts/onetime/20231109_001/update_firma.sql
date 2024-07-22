UPDATE 
    podesavanja_aplikacije 
SET 
    podrazumijevani_tip_unosa_stavke_fakture='slobodan_unos',
    podrazumijevani_tip_stampe='A4', 
    pocetna_stranica='/racun/opsti_unos' 
WHERE 
    operater_id=687;

UPDATE 
    organizaciona_jedinica 
SET 
    adresa='MAINSKI PUT 56', 
    grad='BUDVA' 
WHERE 
    firma_id=455;

UPDATE 
    naplatni_uredjaj 
SET 
    efi_kod='ob811mk551' 
WHERE 
    id=474;