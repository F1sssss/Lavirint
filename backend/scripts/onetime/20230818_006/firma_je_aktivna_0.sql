SELECT id, je_aktivna, naziv FROM firma WHERE id IN (765, 453, 458, 168);
UPDATE firma SET je_aktivna=0 WHERE id IN (765, 453, 458, 168);