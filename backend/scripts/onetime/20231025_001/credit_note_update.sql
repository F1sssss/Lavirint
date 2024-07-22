SELECT
    id,
    status,
    firma_id,
    discount_amount,
    return_amount,
    discount_amount_with_tax,
    return_amount_with_tax,
    return_and_discount_amount,
    return_and_discount_amount_with_tax
FROM
    knjizno_odobrenje;

UPDATE
    knjizno_odobrenje
SET
    discount_amount=-1*discount_amount,
    return_amount=-1*return_amount,
    discount_amount_with_tax=-1*discount_amount_with_tax,
    return_amount_with_tax=-1*return_amount_with_tax,
    return_and_discount_amount=-1*return_and_discount_amount,
    return_and_discount_amount_with_tax=-1*return_and_discount_amount_with_tax,
    tax_amount=-1*tax_amount
WHERE
    id <= 58;