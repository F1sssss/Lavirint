INSERT INTO
    `ordinal_number_counter_type` (`id`, `description`)
VALUES
    (1, 'Redni broj fakture u okviru naplatnog uređaja'),
    (2, 'Redni broj redovnih faktura i njihovih korekcija u okviru naplatnog uređaja'),
    (3, 'Redni broj avansnih faktura i njihovih korekcija u okviru naplatnog uređaja'),
    (4, 'Redni broj knjižnih odobrenja i njihovih korekcija u okviru naplatnog uređaja'),
    (5, 'Redni broj predračuna redovnih faktura u okviru naplatnog uređaja'),
    (6, 'Redni broj kalkulacija u okviru naplatnog uređaja');

INSERT INTO `ordinal_number_counter` (`payment_device_id`, `year`, `last_value`, `type_id`)
SELECT `payment_device_id`, `year`, `value`, 4 FROM `invoice_counter` WHERE `invoice_type_id`=6;

INSERT INTO `ordinal_number_counter` (`payment_device_id`, `year`, `last_value`, `type_id`)
SELECT `payment_device_id`, `year`, `value`, 2 FROM `invoice_counter` WHERE `invoice_type_id`=1;

INSERT INTO `ordinal_number_counter` (`payment_device_id`, `year`, `last_value`, `type_id`)
SELECT `payment_device_id`, `year`, `value`, 3 FROM `invoice_counter` WHERE `invoice_type_id`=5;