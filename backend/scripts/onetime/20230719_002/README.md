Pronađena duplikovana podešavanja korisnika

```
SELECT * FROM podesavanja_aplikacije WHERE operater_id IN (SELECT operater_id FROM podesavanja_aplikacije GROUP BY operater_id HAVING COUNT(id) > 1);
```

+------+---------------------+-------------+------------------------------------------+----------------------------+-----------------------+
| id   | pocetna_stranica    | operater_id | podrazumijevani_tip_unosa_stavke_fakture | podrazumijevani_tip_stampe | vidi_dospjele_fakture |
+------+---------------------+-------------+------------------------------------------+----------------------------+-----------------------+
|  221 | /prodaja/racun/unos |         223 | po_artiklu                               | 58mm                       |                     1 |
|  222 | /prodaja/racun/unos |         223 | po_artiklu                               | 58mm                       |                     1 |
|  234 | /prodaja/racun/unos |         236 | po_artiklu                               | 58mm                       |                     1 |
|  235 | /prodaja/racun/unos |         236 | po_artiklu                               | 58mm                       |                     1 |
|  236 | /prodaja/racun/unos |         237 | po_artiklu                               | 58mm                       |                     1 |
|  237 | /prodaja/racun/unos |         237 | po_artiklu                               | 58mm                       |                     1 |
|  323 | /prodaja/racun/unos |         323 | po_artiklu                               | 58mm                       |                     1 |
|  324 | /prodaja/racun/unos |         323 | po_artiklu                               | 58mm                       |                     1 |
|  347 | /prodaja/racun/unos |         347 | po_artiklu                               | 58mm                       |                     1 |
|  348 | /prodaja/racun/unos |         347 | po_artiklu                               | 58mm                       |                     1 |
|  356 | /prodaja/racun/unos |         355 | po_artiklu                               | 58mm                       |                     1 |
|  357 | /prodaja/racun/unos |         355 | po_artiklu                               | 58mm                       |                     1 |
|  400 | /prodaja/racun/unos |         395 | po_artiklu                               | 58mm                       |                     1 |
|  404 | /prodaja/racun/unos |         399 | po_artiklu                               | 58mm                       |                     1 |
|  405 | /prodaja/racun/unos |         399 | po_artiklu                               | 58mm                       |                     1 |
|  417 | /prodaja/racun/unos |         411 | po_artiklu                               | A4                         |                     1 |
|  418 | /prodaja/racun/unos |         411 | po_artiklu                               | A4                         |                     1 |
|  420 | /prodaja/racun/unos |         413 | po_artiklu                               | 58mm                       |                     1 |
|  421 | /prodaja/racun/unos |         413 | po_artiklu                               | 58mm                       |                     1 |
|  431 | /prodaja/racun/unos |         423 | po_artiklu                               | 58mm                       |                     1 |
|  432 | /prodaja/racun/unos |         423 | po_artiklu                               | 58mm                       |                     1 |
|  600 | /prodaja/racun/unos |         395 | slobodan_unos                            | 58mm                       |                     1 |
|  713 | /prodaja/racun/unos |         694 | po_artiklu                               | 58mm                       |                     1 |
|  894 | /prodaja/racun/unos |         875 | po_artiklu                               | 58mm                       |                     1 |
| 1057 | /racun/opsti_unos   |         694 | slobodan_unos                            | A4                         |                     1 |
| 1136 | /racun/opsti_unos   |        1116 | slobodan_unos                            | A4                         |                     1 |
| 1137 | /racun/opsti_unos   |        1117 | slobodan_unos                            | A4                         |                     1 |
| 1138 | /racun/opsti_unos   |        1118 | slobodan_unos                            | A4                         |                     1 |
| 1143 | /prodaja/racun/unos |        1123 | po_artiklu                               | 58mm                       |                     1 |
| 1289 | /prodaja/racun/unos |         875 | po_artiklu                               | 58mm                       |                  NULL |
| 1577 | /racun/opsti_unos   |        1116 | slobodan_unos                            | A4                         |                  NULL |
| 1578 | /racun/opsti_unos   |        1117 | slobodan_unos                            | A4                         |                  NULL |
| 1580 | /prodaja/racun/unos |        1118 | po_artiklu                               | 58mm                       |                  NULL |
| 1588 | /racun/opsti_unos   |        1123 | slobodan_unos                            | A4                         |                  NULL |
+------+---------------------+-------------+------------------------------------------+----------------------------+-----------------------+

Kroz Python skriptu provjereno je koje se od duplikovanih podešavanja selektuju za određenog operatera:

```
>>> db.session.query(models.Operater).get(223).podesavanja_aplikacije.id
221
>>> db.session.query(models.Operater).get(236).podesavanja_aplikacije.id
234
>>> db.session.query(models.Operater).get(237).podesavanja_aplikacije.id
236
>>> db.session.query(models.Operater).get(323).podesavanja_aplikacije.id
323
>>> db.session.query(models.Operater).get(347).podesavanja_aplikacije.id
347
>>> db.session.query(models.Operater).get(355).podesavanja_aplikacije.id
356
>>> db.session.query(models.Operater).get(395).podesavanja_aplikacije.id
400
>>> db.session.query(models.Operater).get(399).podesavanja_aplikacije.id
404
>>> db.session.query(models.Operater).get(411).podesavanja_aplikacije.id
417
>>> db.session.query(models.Operater).get(413).podesavanja_aplikacije.id
420
>>> db.session.query(models.Operater).get(423).podesavanja_aplikacije.id
431
>>> db.session.query(models.Operater).get(694).podesavanja_aplikacije.id
713
>>> db.session.query(models.Operater).get(875).podesavanja_aplikacije.id
894
>>> db.session.query(models.Operater).get(1116).podesavanja_aplikacije.id
1136
>>> db.session.query(models.Operater).get(1117).podesavanja_aplikacije.id
1137
>>> db.session.query(models.Operater).get(1118).podesavanja_aplikacije.id
1138
>>> db.session.query(models.Operater).get(1123).podesavanja_aplikacije.id
1143
```