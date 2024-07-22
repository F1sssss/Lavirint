import backend.serializers.schema_definitions as definitions
from backend.serializers.paginated_definitions import InvoiceSearchResultSchema
from backend.serializers.schema_definitions import DepozitSchema

komitent_schema = definitions.KomitentSchema()

faktura_schema = definitions.FakturaSchema()
invoice_view_schema = definitions.FakturaSchema(only=(
    'active_invoice_schedule',
    'advance_invoice_id',
    'credit_note_turnover_remaining',
    'datumfakture',
    'efi_broj_fakture',
    'efi_broj_fakture',
    'efi_verify_url',
    'grupe_poreza.porez_iznos',
    'grupe_poreza.porez_procenat',
    'grupe_poreza.ukupna_cijena_rabatisana',
    'id',
    'ikof',
    'ima_dokument',
    'je_korigovana',
    'korektivne_fakture',
    'korektivne_fakture.id',
    'korektivne_fakture.status',
    'korektivne_fakture.ukupna_cijena_prodajna',
    'korektivne_fakture.efi_ordinal_number',
    'korektivne_fakture.datumfakture',
    'jikr',
    'komitent.tip_identifikacione_oznake',
    'komitent.email',
    'komitent.id',
    'komitent.naziv',
    'komitent_id',
    'korigovana_ukupna_cijena_prodajna',
    'korigovana_ukupna_cijena_prodajna_valuta',
    'korigovana_ukupna_cijena_rabatisana',
    'korigovani_porez_iznos',
    'operater.ime',
    'operater.kodoperatera',
    'payment_methods',
    'payment_methods.amount',
    'payment_methods.payment_method_type.description',
    'porez_iznos',
    'efi_ordinal_number',
    'internal_ordinal_number',
    'status',
    'stavke.jedinicna_cijena_prodajna',
    'stavke.kolicina',
    'stavke.naziv',
    'stavke.porez_procenat',
    'stavke.ukupna_cijena_prodajna',
    'tip_fakture_id',
    'ukupna_cijena_prodajna',
    'ukupna_cijena_puna',
    'ukupna_cijena_prodajna_valuta',
    'ukupna_cijena_rabatisana',
    'rabat_iznos_prodajni',
    'valuta',
    'is_advance_invoice',
    'poreski_period'
))


grupa_artikala_schema = definitions.GrupaArtikalaSchema()
artikal_schema = definitions.ArtikalSchema()
jedinica_mjere_schema = definitions.JedinicaMjereSchema()
operater_schema = definitions.OperaterSchema()
magacin_schema = definitions.MagacinSchema()
kalkulacija_schema = definitions.KalkulacijaSchema()
magacin_zaliha_schema = definitions.MagacinZalihaSchema()
smjena_schema = definitions.SmjenaSchema()
tax_exemption_reason_schema = definitions.TaxExemptionReasonSchema()
poreska_stopa_schema = definitions.PoreskaStopaSchema()
vrsta_placanja_schema = definitions.VrstaPlacanjaSchema()
depozit_schema: DepozitSchema = definitions.DepozitSchema()
stanje_odgovor_schema = definitions.StanjeOdgovorSchema()
tip_identifikacione_oznake_schema = definitions.TipIdentifikacioneOznakeSchema()
administrator_schema = definitions.AdministratorSchema()
valuta_schema = definitions.ValutaSchema()
firma_schema = definitions.FirmaSchema()
izvjestaj_po_artiklima_schema = definitions.IzvjestajPoArtiklimaSchema()
izvjestaj_po_grupama_artikala_schema = definitions.IzvjestajPoGrupamaArtikalaSchema()
dospjela_faktura_schema = definitions.DospjelaFaktura()
dospjela_faktura_notifikacija_schema = definitions.DospjelaFakturaNotifikacija()
invoice_processing_schema = definitions.InvoiceProcessingSchema()
payment_method_schema = definitions.PaymentMethodSchema()
payment_method_type_schema = definitions.PaymentMethodTypeSchema()
invoice_schedule_schema = definitions.InvoiceScheduleSchema()
knjizno_odobrenje__processing_schema = definitions.KnjiznoOdobrenjeProcessingSchema()

invoice_search_result_schema = InvoiceSearchResultSchema()
