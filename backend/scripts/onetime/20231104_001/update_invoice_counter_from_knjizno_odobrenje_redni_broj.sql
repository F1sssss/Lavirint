INSERT INTO invoice_counter (year, value, payment_device_id, invoice_type_id)
SELECT godina, vrijednost, naplatni_uredjaj_id, 6
FROM knjizno_odobrenje_redni_broj;