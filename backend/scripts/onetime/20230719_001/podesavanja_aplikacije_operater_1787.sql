SET @operater_id = 1787;

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
