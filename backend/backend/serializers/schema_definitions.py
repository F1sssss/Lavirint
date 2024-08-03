from marshmallow import Schema
from marshmallow import post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import fields

from backend import models
from backend.calc import format_decimal


class BaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        load_instance = True
        include_relationships = True
        include_fk = True

    def __init__(self, load_json=False, *args, **kwargs):
        self.load_json = load_json
        super(BaseSchema, self).__init__(*args, **kwargs)

    @post_load
    def make_instance(self, data):
        """Deserialize data to an instance of the model. Update an existing row
        if specified in `self.instance` or loaded by primary key(s) in the data;
        else create a new row.
        :param data: Data to deserialize.
        """
        if self.load_json:
            return data
        return super(BaseSchema, self).make_instance(data)


class TipIdentifikacioneOznakeSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.TipIdentifikacioneOznake
        include_relationships = False

        fields = [
            'id',
            'naziv'
        ]


class JedinicaMjereSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.JedinicaMjere


class KomitentPlacanjeSchema(BaseSchema):
    # iznos = fields.Number()

    class Meta(BaseSchema.Meta):
        model = models.KomitentPlacanje


class KomitentSchema(BaseSchema):
    tip_identifikacione_oznake = fields.Nested(TipIdentifikacioneOznakeSchema)
    placanja = fields.Nested(KomitentPlacanjeSchema, many=True)

    class Meta(BaseSchema.Meta):
        model = models.Komitent
        include_relationships = False

class GrupaOrderaSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.OrderGrupa
        include_relationships = False

class VrstaPlacanjaSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.VrstaPlacanja
        include_relationships = False


class ValutaSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.Valuta


class DospjelaFaktura(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = models.DospjelaFaktura

        fields = [
            'id',
            'opis'
        ]


class DospjelaFakturaNotifikacija(BaseSchema):

    dospjela_faktura = fields.Nested(DospjelaFaktura)

    class Meta(BaseSchema.Meta):
        model = models.DospjelaFakturaNotifikacija


class MagacinSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.Magacin


class ArtikalSchema(BaseSchema):
    # jedinicna_cijena_osnovna = fields.Number()
    # jedinicna_cijena_puna = fields.Number()

    # ukupna_cijena_osnovna = fields.Number()
    # ukupna_cijena_puna = fields.Number()

    # porez_iznos = fields.Number()
    # porez_procenat = fields.Number()

    jedinica_mjere = fields.Nested(JedinicaMjereSchema)

    # kolicina = fields.Number()

    class Meta(BaseSchema.Meta):
        model = models.Artikal
        include_relationships = False


class FakturaGrupaPorezaSchema(BaseSchema):
    # broj_stavki = fields.Number()
    # ukupna_cijena_osnovna = fields.Number()
    # ukupna_cijena_rabatisana = fields.Number()
    # ukupna_cijena_puna = fields.Number()
    # ukupna_cijena_prodajna = fields.Number()
    # porez_procenat = fields.Number()
    # porez_iznos = fields.Number()
    # rabat_iznos_osnovni = fields.Number()
    # rabat_iznos_prodajni = fields.Number()
    # credit_note_turnover_remaining = fields.Number()
    # credit_note_turnover_used = fields.Number()

    class Meta(BaseSchema.Meta):
        model = models.FakturaGrupaPoreza


class MagacinZalihaSchema(BaseSchema):
    # jedinicna_cijena_osnovna = fields.Number()
    # jedinicna_cijena_puna = fields.Number()
    magacin = fields.Nested(MagacinSchema)
    artikal = fields.Nested(ArtikalSchema)
    # raspoloziva_kolicina = fields.Number()

    class Meta(BaseSchema.Meta):
        model = models.MagacinZaliha
        include_relationships = False


class FakturaStavkaSchema(BaseSchema):
    # kolicina = fields.Number()

    # jedinicna_cijena_osnovna = fields.Number()
    # jedinicna_cijena_rabatisana = fields.Number()
    # jedinicna_cijena_prodajna = fields.Number()
    # jedinicna_cijena_puna = fields.Number()

    # ukupna_cijena_osnovna = fields.Number()
    # ukupna_cijena_rabatisana = fields.Number()
    # ukupna_cijena_prodajna = fields.Number()
    # ukupna_cijena_puna = fields.Number()

    # korigovana_kolicina = fields.Number()
    # korigovana_ukupna_cijena_osnovna = fields.Number()
    # korigovana_ukupna_cijena_rabatisana = fields.Number()
    # korigovana_ukupna_cijena_puna = fields.Number()
    # korigovana_ukupna_cijena_prodajna = fields.Number()
    # korigovani_porez_iznos = fields.Number()
    # korigovani_rabat_iznos_osnovni = fields.Number()
    # korigovani_rabat_iznos_prodajni = fields.Number()

    # porez_procenat = fields.Number()
    # porez_iznos = fields.Number()
    # rabat_procenat = fields.Number()
    # rabat_iznos_osnovni = fields.Number()
    # rabat_iznos_prodajni = fields.Number()

    jedinica_mjere = fields.Nested(JedinicaMjereSchema)
    magacin_zaliha = fields.Nested(MagacinZalihaSchema)

    class Meta(BaseSchema.Meta):
        model = models.FakturaStavka


class PaymentMethodTypeSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = models.PaymentMethodType
        fields = [
            'id',
            'description',
            'is_cash',
            'sort_weight'
        ]


class PaymentMethodSchema(BaseSchema):

    # amount = fields.Number()
    payment_method_type = fields.Nested(PaymentMethodTypeSchema)

    class Meta(BaseSchema.Meta):
        model = models.PaymentMethod
        fields = [
            'amount',
            'payment_method_type_id',
            'payment_method_type'
        ]


class InvoiceScheduleSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = models.InvoiceSchedule


class FakturaSchema(BaseSchema):
    komitent = fields.Nested(KomitentSchema)
    vrstaplacanja = fields.Nested(VrstaPlacanjaSchema)
    valuta = fields.Nested(ValutaSchema)

    # ukupna_cijena_osnovna = fields.Number()
    # ukupna_cijena_rabatisana = fields.Number()
    # ukupna_cijena_prodajna = fields.Number()
    # ukupna_cijena_puna = fields.Number()
    # porez_iznos = fields.Number()
    # rabat_iznos_osnovni = fields.Number()
    # rabat_iznos_prodajni = fields.Number()
    # kurs_razmjene = fields.Number()

    # korigovana_ukupna_cijena_osnovna = fields.Number()
    # korigovana_ukupna_cijena_rabatisana = fields.Number()
    # korigovana_ukupna_cijena_prodajna = fields.Number()
    # korigovana_ukupna_cijena_puna = fields.Number()
    # korigovani_porez_iznos = fields.Number()
    # korigovani_rabat_iznos_osnovni = fields.Number()
    # korigovani_rabat_iznos_prodajni = fields.Number()

    # credit_note_turnover_remaining = fields.Number()
    # credit_note_turnover_used = fields.Number()

    korektivne_fakture = fields.Nested(lambda: FakturaSchema(), many=True)

    je_korigovana = fields.Method('get_je_korigovana')
    ima_dokument = fields.Method('get_ima_dokument')
    porez_21 = fields.Method('get_porez_21')
    porez_7 = fields.Method('get_porez_7')
    porez_0 = fields.Method('get_porez_0')
    stavke = fields.Nested(FakturaStavkaSchema, many=True)
    payment_methods = fields.Nested(PaymentMethodSchema, many=True)
    grupe_poreza = fields.Nested(FakturaGrupaPorezaSchema, many=True)

    active_invoice_schedule = fields.Method('get_active_invoice_schedule')
    ukupna_cijena_prodajna_valuta = fields.Function(
        lambda obj: format_decimal(obj.ukupna_cijena_prodajna_valuta, 2, 2))
    korigovana_ukupna_cijena_prodajna_valuta = fields.Function(
        lambda obj: format_decimal(obj.korigovana_ukupna_cijena_prodajna_valuta, 2, 2))

    def get_active_invoice_schedule(self, obj):
        if len(obj.invoice_schedules) == 0:
            return None

        if not obj.invoice_schedules[-1].is_active:
            return None

        return InvoiceScheduleSchema().dump(obj.invoice_schedules[-1])

    def get_porez_21(self, obj):
        for gp in obj.grupe_poreza:
            if gp.porez_procenat == 21:
                return FakturaSchema._tax_group_to_obj(gp)

    def get_porez_7(self, obj):
        for gp in obj.grupe_poreza:
            if gp.porez_procenat == 7:
                return FakturaSchema._tax_group_to_obj(gp)

    def get_porez_0(self, obj):
        for gp in obj.grupe_poreza:
            if gp.porez_procenat == 0:
                return FakturaSchema._tax_group_to_obj(gp)

    @staticmethod
    def _tax_group_to_obj(tax_group):
        return {
            'broj_stavki': tax_group.broj_stavki,
            'ukupna_cijena_osnovna': tax_group.ukupna_cijena_osnovna,
            'ukupna_cijena_rabatisana': tax_group.ukupna_cijena_rabatisana,
            'ukupna_cijena_puna': tax_group.ukupna_cijena_puna,
            'ukupna_cijena_prodajna': tax_group.ukupna_cijena_prodajna,
            'porez_iznos': tax_group.porez_iznos,
            'rabat_iznos_osnovni': tax_group.rabat_iznos_osnovni,
            'rabat_iznos_prodajni': tax_group.rabat_iznos_prodajni,
            'credit_note_turnover_remaining': tax_group.credit_note_turnover_remaining,
            'credit_note_turnover_used': tax_group.credit_note_turnover_used
        }

    def get_je_korigovana(self, obj):
        if obj.korektivne_fakture is None or len(obj.korektivne_fakture) == 0:
            return False

        for faktura in obj.korektivne_fakture:
            if faktura.status == 2:
                return True

        return False

    def get_ima_dokument(self, obj):
        return obj.lokacija_dokumenta is not None

    class Meta(BaseSchema.Meta):
        model = models.Faktura

        exclude = [
            'xml_request',
            'xml_response',
            'lokacija_dokumenta',
        ]


class GrupaArtikalaSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.GrupaArtikala


class DrzavaSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.Drzave


class SmjenaSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.Smjena


class PodesavanjaAplikacijeSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.PodesavanjaAplikacije
        include_relationships = False

        fields = [
            'pocetna_stranica',
            'podrazumijevani_tip_unosa_stavke_fakture',
            'podrazumijevani_tip_stampe',
            'vidi_dospjele_fakture'
        ]


class CompanySettingsSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = models.CompanySettings

        exclude = [
            'smtp_password'
        ]


class FirmaSchema(BaseSchema):

    settings = fields.Nested(CompanySettingsSchema)

    class Meta(BaseSchema.Meta):
        model = models.Firma
        include_relationships = False

        fields = [
            'pib',
            'naziv',
            'ima_upload_dokumenta',
            'adresa',
            'grad',
            'drzava',
            'pdvbroj',
            'telefon',
            'email',
            'ziroracun',
            'logo_url',
            'settings',
            'je_poreski_obaveznik'
        ]


class OrganizationalUnitSettingsSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.OrganizationalUnitSettings

        fields = [
            'default_invoice_note'
        ]


class OrganizacionaJedinicaSchema(BaseSchema):

    drzava = fields.Nested(DrzavaSchema)

    settings = fields.Nested(OrganizationalUnitSettingsSchema)

    class Meta(BaseSchema.Meta):
        model = models.OrganizacionaJedinica

        fields = [
            'id',
            'naziv',
            'adresa',
            'grad',
            'drzava_id',
            'drzava',
            'settings'
        ]


class NaplatniUredjajSchema(BaseSchema):
    # podrazumijevani_iznos_depozita = fields.Number()
    organizaciona_jedinica = fields.Nested(OrganizacionaJedinicaSchema)

    class Meta(BaseSchema.Meta):
        model = models.NaplatniUredjaj
        include_relationships = False

        fields = [
            'efi_kod',
            'podrazumijevani_iznos_depozita',
            'organizaciona_jedinica'
        ]


class OperaterSchema(BaseSchema):
    aktivna_smjena = fields.Nested(SmjenaSchema)
    podesavanja_aplikacije = fields.Nested(PodesavanjaAplikacijeSchema)
    firma = fields.Nested(FirmaSchema)
    naplatni_uredjaj = fields.Nested(NaplatniUredjajSchema)

    class Meta(BaseSchema.Meta):
        model = models.Operater

        fields = [
            'ime',
            'email',
            'magacin_id',
            'aktivna_smjena',
            'podesavanja_aplikacije',
            'firma',
            'naplatni_uredjaj'
        ]


class KalkulacijaStavkaSchema(BaseSchema):
    # kolicina = fields.Number()

    class Meta(BaseSchema.Meta):
        model = models.KalkulacijaStavka


class KalkulacijaSchema(BaseSchema):
    stavke = fields.Nested(KalkulacijaStavkaSchema, many=True)
    magacin = fields.Nested(MagacinSchema)
    dobavljac = fields.Nested(KomitentSchema)
    operater = fields.Nested(OperaterSchema)

    class Meta(BaseSchema.Meta):
        model = models.Kalkulacija
        include_relationships = False


class TaxExemptionReasonSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.TaxExemptionReason
        include_relationships = False


class PoreskaStopaSchema(BaseSchema):
    # procenat = fields.Number()

    class Meta(BaseSchema.Meta):
        model = models.PoreskaStopa
        include_relationships = False


class DepozitSchema(BaseSchema):
    datum_kreiranja = fields.DateTime()
    status = fields.Integer()

    # iznos = fields.Number()

    class Meta(BaseSchema.Meta):
        model = models.Depozit
        include_relationships = False


class StanjeOdgovorSchema(Schema):
    depozit = fields.Number()
    suma_racuna = fields.Number()
    isplate = fields.Number()
    ukupno = fields.Number()
    danasnji_depozit = fields.Nested(DepozitSchema)


class AdministratorSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.Administrator


class IzvjestajPoArtiklimaSchema(Schema):

    artikal_id = fields.Integer()
    artikal_naziv = fields.String()
    # ukupna_cijena_prodajna = fields.Number()
    # kolicina = fields.Number()


class IzvjestajPoGrupamaArtikalaSchema(Schema):
    artikal_id = fields.Integer()
    artikal_naziv = fields.String()
    # ukupna_cijena_prodajna = fields.Number()
    # kolicina = fields.Number()


class InvoiceProcessingResultSchema(Schema):

    is_success = fields.Boolean()
    message = fields.String()


class InvoiceProcessingSchema(Schema):

    result = fields.Nested(InvoiceProcessingResultSchema)
    invoice = fields.Nested(FakturaSchema, only=('id',))


class KnjiznoOdobrenjeStavkaSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = models.KnjiznoOdobrenjeStavka


class KnjiznoOdobrenjeGrupaPorezaSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = models.KnjiznoOdobrenjeGrupaPoreza


class KnjiznoOdobrenjeSchema(BaseSchema):

    stavke = fields.Nested(KnjiznoOdobrenjeStavkaSchema, many=True)
    fakture = fields.Nested(FakturaSchema, many=True)
    grupe_poreza = fields.Nested(KnjiznoOdobrenjeGrupaPorezaSchema, many=True)
    komitent = fields.Nested(KomitentSchema)

    class Meta(BaseSchema.Meta):
        model = models.KnjiznoOdobrenje


class KnjiznoOdobrenjeProcessingSchema(Schema):

    is_success = fields.Boolean()
    message = fields.Dict()
    credit_note = fields.Nested(KnjiznoOdobrenjeSchema)
