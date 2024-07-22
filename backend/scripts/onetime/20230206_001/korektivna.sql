SELECT 
    korigovana_faktura_id, 
    COUNT(korigovana_faktura_id) 
FROM 
    veza_korektivna_faktura 
WHERE 
        2=(SELECT status FROM faktura WHERE id=korigovana_faktura_id) 
    AND 2=(SELECT status FROM faktura WHERE id=korektivna_faktura_id) 
GROUP BY 
    korigovana_faktura_id 
HAVING 
    COUNT(korigovana_faktura_id) > 1;











SELECT * FROM faktura WHERE id=2281515;