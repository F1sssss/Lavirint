SELECT * FROM (
    SELECT 
        storno_faktura_id as korigovana_faktura_id, 
        id as korektivna_faktura_id, 
        datumfakture as datumfakture,
        1 as is_cancellation
    FROM 
        faktura 
    WHERE 
        storno_faktura_id IS NOT NULL 
        AND tip_fakture_id=2

    UNION
    
    SELECT
        veza.korigovana_faktura_id as korigovana_faktura_id,
        corrective.id as korektivna_faktura_id,
        corrective.datumfakture as datumfakture,
        NULL as is_cancellation
    FROM veza_korektivna_faktura veza
        LEFT JOIN faktura corrective ON veza.korektivna_faktura_id=corrective.id

) as t1
WHERE korektivna_faktura_id NOT IN (SELECT korektivna_faktura_id FROM veza_korektivna_faktura)
ORDER BY datumfakture;


UPDATE faktura corrective
    LEFT JOIN faktura corrected ON corrected.storno_faktura_id=corrective.id
SET 
    corrective.storno_faktura_id=corrected.id,
    corrected.storno_faktura_id=NULL
 WHERE
    corrected.storno_faktura_id IS NOT NULL AND corrected.tip_fakture_id=1;