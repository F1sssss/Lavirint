## 1.0.2 - December 13, 2022

### Functional changes
* Fixed not being able to make corrective invoice when changing price difference
* Added credit note create, view and print
* Changed certificate password storage method, moved from files to database

### Database changes

Table `faktura`
  * Added column `credit_note_turnover_remaining` 
  * Added column `credit_note_turnover_used`

Table `faktura_stavka`
  * Added column `credit_note_turnover_remaining` 
  * Added column `credit_note_turnover_used`

Table `faktura_grupa_poreza`
  * Added column `credit_note_turnover_remaining` 
  * Added column `credit_note_turnover_used`

Table `firma`
  * Added column `certificate_password`

Table `credit_note_processing_lock`
  * Dropped and recreated
  * Added column `id` as primary key and foreign key to `naplatni_uredjaj.id` 

Table `knjizno_odobrenje`
  * Altered column `redni_broj`, set as `nullable=True`
  * Altered column `datum_fiskalizacije`, set as `nullable=True`

Table `knjizno_odobrenje`
  * Added column `tax_amount` 
  * Added column `return_amount` 
  * Added column `return_amount_with_tax` 
  * Added column `discount_amount` 
  * Added column `discount_amount_with_tax` 
  * Added column `return_and_discount_amount` 
  * Added column `return_and_discount_amount_with_tax`
  * Dropped column `porez_iznos` 
  * Dropped column `ukupna_cijena_osnovna` 
  * Dropped column `rabat_iznos_prodajni` 
  * Dropped column `ukupna_cijena_prodajna` 
  * Dropped column `ukupna_cijena_puna` 
  * Dropped column `ukupna_cijena_rabatisana` 
  * Dropped column `rabat_iznos_osnovni` 
  * Dropped column `ukupna_cijena_osnovna` 

Table `knjizno_odobrenje_grupa_poreza`
  * Added columns `tax_rate` 
  * Added column `tax_amount` 
  * Added column `return_amount` 
  * Added column `return_amount_with_tax` 
  * Added column `discount_amount` 
  * Added column `discount_amount_with_tax` 
  * Added column `return_and_discount_amount` 
  * Added column `return_and_discount_amount_with_tax`
  * Dropped column `porez_iznos` 
  * Dropped column `porez_procenat` 
  * Dropped column `rabat_iznos_prodajni` 
  * Dropped column `ukupna_cijena_prodajna` 
  * Dropped column `ukupna_cijena_puna` 
  * Dropped column `ukupna_cijena_rabatisana` 
  * Dropped column `rabat_iznos_osnovni` 
  * Dropped column `ukupna_cijena_osnovna` 

Table `knjizno_odobrenje_stavka`
  * Added columns`description` 
  * Added column `tax_rate` 
  * Added column `tax_amount` 
  * Added column `return_amount` 
  * Added column `return_amount_with_tax` 
  * Added column `discount_amount` 
  * Added column `discount_amount_with_tax` 
  * Added column `type`
  * Dropped column `porez_iznos` 
  * Dropped column `oslobodjen_od_poreza_iznos` 
  * Dropped column `rabat_procenat` 
  * Dropped column `porez_procenat` 
  * Dropped column `rabat_iznos_prodajni` 
  * Dropped column `ukupna_cijena_prodajna` 
  * Dropped column `ukupna_cijena_puna` 
  * Dropped column `ukupna_cijena_rabatisana` 
  * Dropped column `rabat_iznos_osnovni` 
  * Dropped column `povrat_iznos` 


## 1.0.1 - Jul 15, 2022

### Functional changes:
* Added multiple payment methods to invoice
* Removed cummulative invoice fiscalisation on correction

### Database changes:

Table `payment_method_type` 
  * New table, contains payment method types.

Table `payment_method`
  * New table, contains concrete invoice payment methods 

Table `vrsta_placanja` 
  * Dropped table, it is replaced by `payment_method_type`

Table `faktura` 
  * Added column `is_cash`

Table `payment_device_lock`
  * Renamed to `invoice_processing_lock`

Table `credit_note_processing_lock`
  * New table


## 1.0.0 - Jul 15, 2022

Initial version

