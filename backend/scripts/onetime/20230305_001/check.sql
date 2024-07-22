UPDATE faktura SET tax_exemption_amount=0 WHERE tax_exemption_amount IS NULL;
UPDATE faktura SET corrected_tax_exemption_amount=0 WHERE corrected_tax_exemption_amount IS NULL;
UPDATE faktura_stavka SET tax_exemption_amount=0 WHERE tax_exemption_amount IS NULL;
UPDATE faktura_stavka SET corrected_tax_exemption_amount=0 WHERE corrected_tax_exemption_amount IS NULL;
UPDATE faktura_grupa_poreza SET tax_exemption_amount=0 WHERE tax_exemption_amount IS NULL;

SELECT COUNT(id) FROM faktura WHERE tax_exemption_amount IS NULL;
SELECT COUNT(id) FROM faktura WHERE corrected_tax_exemption_amount IS NULL;
SELECT COUNT(id) FROM faktura_stavka WHERE tax_exemption_amount IS NULL;
SELECT COUNT(id) FROM faktura_stavka WHERE corrected_tax_exemption_amount IS NULL;
SELECT COUNT(id) FROM faktura_grupa_poreza WHERE tax_exemption_amount IS NULL;