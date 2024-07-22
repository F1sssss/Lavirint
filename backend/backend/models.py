from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy import and_
from sqlalchemy.orm import Mapped, declarative_base
from sqlalchemy.orm import relationship

from backend.podesavanja import podesavanja

Base = declarative_base()


# TODO: rename corrective_to_corrected
VezaKorektivnaFaktura = Table(
    'veza_korektivna_faktura',
    Base.metadata,
    Column(
        'korigovana_faktura_id',
        Integer,
        ForeignKey('faktura.id', name='fk__veza_korektivna_faktura__korigovana_faktura')
    ),
    Column(
        'korektivna_faktura_id',
        Integer,
        ForeignKey('faktura.id', name='fk__veza_korektivna_faktura__korektivna_faktura')
    ),
)

CreditNoteToCorrectiveInvoice = Table(
    'credit_note_to_corrective_invoice',
    Base.metadata,
    Column(
        'credit_note_id',
        Integer,
        ForeignKey('knjizno_odobrenje.id', name='FK_D8F870A18E90')
    ),
    Column(
        'corrective_invoice_id',
        Integer,
        ForeignKey('faktura.id', name='FK_B16CB51CBC51')
    ),
)

CorrectedToCorrective = Table(
    'corrected_to_corrective',
    Base.metadata,
    Column('corrected_invoice_id', Integer, ForeignKey('faktura.id', name='FK_C0AA1A13E759')),
    Column('corrective_invoice_id', Integer, ForeignKey('faktura.id', name='FK_E452FA82FFCA'))
)


# TODO: rename summary_to_invoice
VezaZbirnaFaktura = Table(
    'veza_zbirna_faktura',
    Base.metadata,
    Column(
        'zbirna_faktura_id',
        Integer,
        ForeignKey('faktura.id', name='fk__veza_zbirna_faktura__zbirna_faktura')
    ),
    Column(
        'clanica_faktura_id',
        Integer,
        ForeignKey('faktura.id', name='fk__veza_zbirna_faktura__clanica_faktura')
    ),
)

# TODO: rename credit_note_to_invoice
VezaKnjiznoOdobrenjeFaktura = Table(
    'veza_knjizno_odobrenje_faktura',
    Base.metadata,
    Column(
        'knjizno_odobrenje_id',
        Integer(),
        ForeignKey('knjizno_odobrenje.id', name="fk__veza_knjizno_odobrenje_faktura__knjizno_odobrenje"),
        nullable=False
    ),
    Column(
        'faktura_id',
        Integer(),
        ForeignKey('faktura.id', name="fk__veza_knjizno_odobrenje_faktura__faktura"),
        nullable=False
    ),
)

# TODO: What is this for?
FakturaVeza = Table(
    'faktura_veza',
    Base.metadata,
    Column(
        'faktura_roditelj_id',
        Integer,
        ForeignKey('faktura.id', name='fk__faktura_veza__faktura_roditelj_id')
    ),
    Column(
        'faktura_dijete_id',
        Integer,
        ForeignKey('faktura.id', name='fk__faktura_veza__faktura_dijete_id')
    ),
)


class Drzave(Base):
    __tablename__ = 'drzave'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    sifravalute: Mapped[int] = Column(Integer())
    opisvalute: Mapped[str] = Column(String(3))
    drzava_skraceno_2: Mapped[str] = Column(String(2))
    drzava_skraceno_3: Mapped[str] = Column(String(3))
    drzava: Mapped[str] = Column(String(50))
    drzavaeng: Mapped[str] = Column(String(50))
    paritet: Mapped[int] = Column(Integer())
    issepa: Mapped[int] = Column(Integer())


class Valuta(Base):
    __tablename__ = 'valuta'

    DOMESTIC_CURRENCY_ID = 50

    id: Mapped[int] = Column(Integer(), primary_key=True)
    naziv_me: Mapped[str] = Column(String(150))
    naziv_en: Mapped[str] = Column(String(150))
    iso_4217_numericki_kod: Mapped[str] = Column(String(3))  # ISO 4217 kod
    iso_4217_alfanumericki_kod: Mapped[str] = Column(String(3))  # ISO 4217 kod


class PaymentMethodType(Base):
    __tablename__ = 'payment_method_type'

    id: Mapped[int] = Column(Integer(), primary_key=True, autoincrement=False)
    efi_code: Mapped[str] = Column(String(30))
    description: Mapped[str] = Column(String(100))
    is_cash: Mapped[bool] = Column(Boolean(create_constraint=True, name='payment_method_type_chk_1'))
    sort_weight: Mapped[int] = Column(Integer())
    is_active: Mapped[bool] = Column(Boolean(create_constraint=True, name='payment_method_type_chk_2'))
    is_noncash: Mapped[bool] = Column(Boolean(create_constraint=True, name='payment_method_type_chk_3'))


class PaymentMethod(Base):
    __tablename__ = 'payment_method'

    TYPE_BANKNOTE = 1
    TYPE_CARD = 2
    TYPE_CHECK = 3
    TYPE_SVOUCHER = 4
    TYPE_COMPANY = 5
    TYPE_ORDER = 6
    TYPE_ADVANCE = 7
    TYPE_ACCOUNT = 8
    TYPE_FACTORING = 9
    TYPE_COMPENSATION = 10
    TYPE_TRANSFER = 11
    TYPE_WAIVER = 12
    TYPE_KIND = 13
    TYPE_OTHER = 14
    TYPE_BUSINESSCARD = 15
    TYPE_OTHER_CASH = 16

    TYPE_EFI_BANKNOTE = 'BANKNOTE'
    TYPE_EFI_CARD = 'CARD'
    TYPE_EFI_CHECK = 'CHECK'
    TYPE_EFI_SVOUCHER = 'SVOUCHER'
    TYPE_EFI_COMPANY = 'COMPANY'
    TYPE_EFI_ORDER = 'ORDER'
    TYPE_EFI_ADVANCE = 'ADVANCE'
    TYPE_EFI_ACCOUNT = 'ACCOUNT'
    TYPE_EFI_FACTORING = 'FACTORING'
    TYPE_EFI_COMPENSATION = 'COMPENSATION'
    TYPE_EFI_TRANSFER = 'TRANSFER'
    TYPE_EFI_WAIVER = 'WAIVER'
    TYPE_EFI_KIND = 'KIND'
    TYPE_EFI_OTHER = 'OTHER'
    TYPE_EFI_BUSINESSCARD = 'BUSINESSCARD'
    TYPE_EFI_OTHER_CASH = 'OTHER-CASH'

    SUBTYPE_EFI_CASH = 'CASH'
    SUBTYPE_EFI_NONCASH = 'NONCASH'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    invoice_id: Mapped[int] = Column(Integer(), ForeignKey('faktura.id', name='fk__payment_method__faktura'))
    payment_method_type_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('payment_method_type.id', name='fk__payment_method_type__payment_method'))
    amount: Mapped[Decimal] = Column(Numeric(15, 6))
    advance_invoice_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('faktura.id', name='fk__payment_method__advance_faktura'))

    payment_method_type: Mapped[PaymentMethodType] = relationship(
        'PaymentMethodType',
        foreign_keys=payment_method_type_id
    )
    advance_invoice: Mapped[Faktura] = relationship('Faktura', foreign_keys=advance_invoice_id)


class VrstaPlacanja(Base):
    __tablename__ = 'vrsta_placanja'

    TYPE_BANKNOTE = 1
    TYPE_CARD = 2
    TYPE_CHECK = 3
    TYPE_SVOUCHER = 4
    TYPE_COMPANY = 5
    TYPE_ORDER = 6
    TYPE_ADVANCE = 7
    TYPE_ACCOUNT = 8
    TYPE_FACTORING = 9
    TYPE_COMPENSATION = 10
    TYPE_TRANSFER = 11
    TYPE_WAIVER = 12
    TYPE_KIND = 13
    TYPE_OTHER = 14
    TYPE_BUSINESSCARD = 15
    TYPE_OTHER_CASH = 16

    id: Mapped[int] = Column(Integer(), primary_key=True, autoincrement=False)
    kod: Mapped[str] = Column(String(30))
    naziv: Mapped[str] = Column(String(100))
    tip_naziv: Mapped[str] = Column(String(30))
    tip_kod: Mapped[str] = Column(String(30))
    je_aktivna: Mapped[bool] = Column(Boolean(create_constraint=True, name='vrsta_placanja_chk_1'), nullable=False)
    sort_value: Mapped[int] = Column(Integer(), nullable=False, default=0)


class TaxExemptionReason(Base):
    __tablename__ = 'tax_exemption_reason'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    efi_code: Mapped[str] = Column(String(50))
    description: Mapped[str] = Column(String(255))
    is_active: Mapped[bool] = Column(Boolean(create_constraint=False))


class CompanySettings(Base):
    __tablename__ = 'company_settings'

    company_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('firma.id', name='fk__company_settings__firma'),
        primary_key=True,
        nullable=False
    )
    smtp_active: Mapped[bool] = Column(Boolean(create_constraint=True, name='company_settings_chk_1'))
    smtp_host: Mapped[str] = Column(String(120), nullable=True)
    smtp_port: Mapped[int] = Column(Integer())
    smtp_mail: Mapped[str] = Column(String(255))
    smtp_username: Mapped[str] = Column(String(255))
    smtp_password: Mapped[str] = Column(String(255))

    can_schedule: Mapped[bool] = Column(Boolean(create_constraint=True, name='company_settings_chk_2'))


class Firma(Base):
    __tablename__ = 'firma'

    TIP_NAPLATNOG_UREDJAJA_SUUNMI = 1
    TIP_NAPLATNOG_UREDJAJA_PIPO = 2
    TIP_NAPLATNOG_UREDJAJA_NZ91 = 3

    id: Mapped[int] = Column(Integer(), primary_key=True)
    naziv: Mapped[str] = Column(String(250))
    pib: Mapped[str] = Column(String(15))
    pdvbroj: Mapped[str] = Column(String(15))
    ziroracun: Mapped[str] = Column(Text())
    je_poreski_obaveznik: Mapped[bool] = Column(Boolean(create_constraint=False))
    grad: Mapped[str] = Column(String(200))
    adresa: Mapped[str] = Column(Text())
    drzava: Mapped[int] = Column(Integer(), ForeignKey('drzave.id', name='firma_ibfk_1'))
    telefon: Mapped[str] = Column(Text())  # TODO: Why is this a text field?
    email: Mapped[str] = Column(Text())  # TODO: Why is this a text field?
    logo_filepath: Mapped[str] = Column(String(255))
    logo_filename: Mapped[str] = Column(String(255))
    ima_upload_dokumenta: Mapped[bool] = Column(Boolean(create_constraint=True, name='firma_chk_1'))
    dokument_qr_code_x: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_qr_code_y: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_qr_code_width: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_qr_code_height: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_ikof_x: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_ikof_y: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_ikof_font_size: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_jikr_x: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_jikr_y: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_jikr_font_size: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_efi_verify_url_x: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_efi_verify_url_y: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_efi_verify_url_font_size: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_kod_operatera_x: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_kod_operatera_y: Mapped[Decimal] = Column(Numeric(15, 6))
    dokument_kod_operatera_font_size: Mapped[Decimal] = Column(Numeric(15, 6))
    je_aktivna: Mapped[bool] = Column(Boolean(create_constraint=True, name='firma_chk_2'))
    certificate_password: Mapped[str] = Column(String(255))
    next_certificate_id: Mapped[int] = (
        Column(Integer(), ForeignKey('fiscalization_certificate.id', name='FK_A960B5AE8DCC'))
    )
    current_certificate_id: Mapped[int] = (
        Column(Integer(), ForeignKey('fiscalization_certificate.id', name='FK_B53887B9C3E1'))
    )

    drzave: Mapped[Drzave] = relationship('Drzave', lazy='joined', foreign_keys=drzava)
    settings: Mapped[CompanySettings] = relationship('CompanySettings', uselist=False)  # TODO Add foreign_keys
    next_certificate: Mapped[FiscalizationCertificate] = (
        relationship('FiscalizationCertificate', foreign_keys=next_certificate_id)
    )
    current_certificate: Mapped[FiscalizationCertificate] = (
        relationship('FiscalizationCertificate', foreign_keys=current_certificate_id)
    )
    certificates: Mapped[List[FiscalizationCertificate]] = relationship(back_populates='owner', foreign_keys='[FiscalizationCertificate.owner_id]')

    @property
    def logo_url(self):
        if self.logo_filepath is not None:
            return '/api/customer/firma/datoteka/' + self.logo_filename


class OrganizationalUnitSettings(Base):
    __tablename__ = 'organizational_unit_settings'

    organizational_unit_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('organizaciona_jedinica.id', name='FK_8CA97D54D662'),
        primary_key=True,
        autoincrement=False
    )
    default_invoice_note: Mapped[str] = Column(Text())


class OrganizacionaJedinica(Base):
    __tablename__ = 'organizaciona_jedinica'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    efi_kod: Mapped[str] = Column(String(10))
    firma_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name='organizaciona_jedinica_ibfk_1'))
    adresa: Mapped[str] = Column(Text())
    grad: Mapped[str] = Column(String(200))
    drzava_id: Mapped[int] = Column(Integer(), ForeignKey('drzave.id', name='organizaciona_jedinica_ibfk_2'))
    naziv: Mapped[str] = Column(String(255))

    firma: Mapped[Firma] = relationship('Firma', foreign_keys=firma_id)
    drzava: Mapped[Drzave] = relationship('Drzave', lazy='joined', foreign_keys=drzava_id)

    # TODO Add foreign_keys
    settings: Mapped[OrganizationalUnitSettings] = relationship('OrganizationalUnitSettings', uselist=False)

    @property
    def puna_adresa(self) -> str:
        s = []

        if self.adresa:
            s.append(self.adresa)

        if self.grad:
            s.append(self.grad)

        if self.drzava_id:
            s.append(self.drzava.drzava)

        return ", ".join(s)


class NaplatniUredjaj(Base):
    __tablename__ = 'naplatni_uredjaj'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    efi_kod: Mapped[str] = Column(String(10))
    organizaciona_jedinica_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('organizaciona_jedinica.id', name='naplatni_uredjaj_ibfk_1')
    )
    tip_naplatnog_uredjaja_id: Mapped[int] = Column(Integer(), nullable=False)
    podrazumijevani_iznos_depozita: Mapped[Decimal] = Column(Numeric(15, 6))

    organizaciona_jedinica: Mapped[OrganizacionaJedinica] = relationship('OrganizacionaJedinica')

    # a4_first_page_margin_top: Mapped[int] = Column(Integer())


class MagacinZaliha(Base):
    __tablename__ = 'magacin_zaliha'

    IZVOR_KALKULACIJE_UPB = 1  # jedinicna_cijena_osnovna
    IZVOR_KALKULACIJE_UPA = 2  # jedinicna_cijena_puna

    id: Mapped[int] = Column(Integer(), primary_key=True)
    magacin_id: Mapped[int] = Column(Integer(), ForeignKey('magacin.id', name='magacin_zaliha_ibfk_1'))
    artikal_id: Mapped[int] = Column(Integer(), ForeignKey('artikal.id', name='magacin_zaliha_ibfk_2'))
    jedinicna_cijena_osnovna: Mapped[Decimal] = Column(Numeric(15, 6))
    jedinicna_cijena_puna: Mapped[Decimal] = Column(Numeric(15, 6))
    raspoloziva_kolicina: Mapped[Decimal] = Column(Numeric(15, 6))
    izvor_kalkulacije: Mapped[int] = Column(Integer())
    porez_procenat: Mapped[Decimal] = Column(Numeric(15, 6))
    tax_exemption_reason_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('tax_exemption_reason.id', name='FK_AF58CDCBEE5B'),
        nullable=True)

    magacin: Mapped[Magacin] = relationship('Magacin', foreign_keys=magacin_id)
    artikal: Mapped[Artikal] = relationship('Artikal', foreign_keys=artikal_id)


class Magacin(Base):
    __tablename__ = 'magacin'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    naziv: Mapped[str] = Column(String(255))
    firma_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name='magacin_ibfk_2'))

    firma: Mapped[Firma] = relationship('Firma', foreign_keys=firma_id)


class PodesavanjaAplikacije(Base):
    __tablename__ = 'podesavanja_aplikacije'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    pocetna_stranica: Mapped[str] = Column(String(100))
    operater_id: Mapped[int] = Column(Integer(), ForeignKey('operater.id', name='podesavanja_aplikacije_ibfk_1'))
    podrazumijevani_tip_unosa_stavke_fakture: Mapped[str] = Column(String(20))  # 1 - Slobodan unos, 2 - Po artiklu
    podrazumijevani_tip_stampe: Mapped[str] = Column(String(10))  # 1 - A4, 2 - 58mm
    vidi_dospjele_fakture: Mapped[bool] = Column(Boolean(create_constraint=True, name='podesavanja_aplikacije_chk_1'))


class Operater(Base):
    __tablename__ = 'operater'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    ime: Mapped[str] = Column(String(100))
    lozinka: Mapped[str] = Column(String(200))
    email: Mapped[str] = Column(String(200))
    kodoperatera: Mapped[str] = Column(String(10))
    admin: Mapped[int] = Column(Integer())
    aktivan: Mapped[int] = Column(Integer())
    firma_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name='operater_ibfk_1'))
    magacin_id: Mapped[int] = Column(Integer(), ForeignKey('magacin.id', name='operater_ibfk_2'))
    naplatni_uredjaj_id: Mapped[int] = Column(Integer(), ForeignKey('naplatni_uredjaj.id', name='operater_ibfk_3'))

    firma: Mapped[Firma] = relationship('Firma')
    magacin: Mapped[Magacin] = relationship('Magacin')
    naplatni_uredjaj: Mapped[NaplatniUredjaj] = relationship('NaplatniUredjaj')
    podesavanja_aplikacije: Mapped[PodesavanjaAplikacije] = relationship('PodesavanjaAplikacije', uselist=False)


class Administrator(Base):
    __tablename__ = 'administrator'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    korisnicko_ime: Mapped[str] = Column(String(200))
    lozinka: Mapped[str] = Column(String(200))


class DospjelaFaktura(Base):
    __tablename__ = 'dospjela_faktura'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    firma_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name='dospjela_faktura_ibfk_1'))
    period: Mapped[datetime] = Column(DateTime())
    datum_kreiranja: Mapped[datetime] = Column(DateTime(), default=datetime.now)
    lokacija_dokumenta: Mapped[str] = Column(String(255))
    opis: Mapped[str] = Column(String(255))


class DospjelaFakturaNotifikacija(Base):
    __tablename__ = 'dospjela_faktura_notifikacija'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    dospjela_faktura_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('dospjela_faktura.id', name='fk__dospjela_faktura_notifikacija__dospjela_faktura')
    )
    operater_id: Mapped[int] = Column(Integer())
    je_vidio: Mapped[bool] = Column(Boolean(create_constraint=True, name='dospjela_faktura_notifikacija_chk_1'))

    dospjela_faktura: Mapped[DospjelaFaktura] = relationship('DospjelaFaktura')


class TipIdentifikacioneOznake(Base):
    __tablename__ = 'tip_identifikacione_oznake'

    id: Mapped[int] = Column(Integer(), primary_key=True, autoincrement=False)
    naziv: Mapped[str] = Column(String(50))
    efi_kod: Mapped[str] = Column(String(50))


class JedinicaMjere(Base):
    __tablename__ = 'jedinica_mjere'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    ui_default: Mapped[bool] = Column(Boolean(create_constraint=True, name='jedinica_mjere_chk_1'), default=0)
    naziv: Mapped[str] = Column(String(15))
    opis: Mapped[str] = Column(String(255))
    firma_id: Mapped[int] = Column(Integer, ForeignKey('firma.id', name='jedinica_mjere_ibfk_1'))

    firma: Mapped[Firma] = relationship('Firma', foreign_keys=firma_id)


class Komitent(Base):
    __tablename__ = 'komitent'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    naziv: Mapped[str] = Column(String(250))
    pib: Mapped[str] = Column(String(15))
    pdvbroj: Mapped[str] = Column(String(15))
    adresa: Mapped[str] = Column(Text())  # TODO Why is this a text field?
    telefon: Mapped[str] = Column(Text())  # TODO Why is this a text field?
    email: Mapped[str] = Column(Text())  # TODO Why is this a text field?
    ziroracun: Mapped[str] = Column(Text())  # TODO Why is this a text field?
    grad: Mapped[str] = Column(String(200))
    napomena: Mapped[str] = Column(Text())
    pibvlasnikapodatka: Mapped[str] = Column(String(15))
    je_komitent: Mapped[bool] = Column(Boolean(create_constraint=True, name='komitent_chk_1'))
    je_dobavljac: Mapped[bool] = Column(Boolean(create_constraint=True, name='komitent_chk_2'))
    drzava: Mapped[int] = Column(Integer(), ForeignKey('drzave.id', name='komitent_ibfk_1'), index=True)
    tip_identifikacione_oznake_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('tip_identifikacione_oznake.id', name='komitent_ibfk_2'))
    identifikaciona_oznaka: Mapped[str] = Column(String(100))
    show_total_debt: Mapped[bool] = Column(Boolean(create_constraint=True, name='komitent_chk_3'))
    previous_debt: Mapped[Decimal] = Column(Numeric(15, 6))

    tip_identifikacione_oznake: Mapped[TipIdentifikacioneOznake] = relationship('TipIdentifikacioneOznake')
    drzave: Mapped[Drzave] = relationship('Drzave', lazy='joined')
    placanja: Mapped[List[KomitentPlacanje]] = relationship(
        'KomitentPlacanje',
        back_populates='komitent')


class InvoiceSchedule(Base):
    __tablename__ = 'invoice_schedule'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    source_invoice_id: Mapped[int] = Column(Integer(), ForeignKey('faktura.id', name='fk__invoice_schedule__faktura'))
    frequency_interval: Mapped[int] = Column(Integer())
    frequency_type: Mapped[int] = Column(Integer())
    start_datetime: Mapped[datetime] = Column(DateTime())
    end_datetime: Mapped[datetime] = Column(DateTime())
    last_run_datetime: Mapped[datetime] = Column(DateTime())
    next_run_datetime: Mapped[datetime] = Column(DateTime())
    is_active: Mapped[bool] = Column(Boolean(create_constraint=True, name='invoice_schedule_chk_1'))
    operater_id: Mapped[int] = Column(Integer(), ForeignKey('operater.id', name='FK_8AE59688B892'))

    source_invoice: Mapped[Faktura] = relationship('Faktura', back_populates='invoice_schedules')
    operater: Mapped[Operater] = relationship('Operater')


class FakturaStavka(Base):
    __tablename__ = 'faktura_stavka'

    IZVOR_KALKULACIJE_UPA = 1
    IZVOR_KALKULACIJE_UPB = 2

    id: Mapped[int] = Column(Integer(), primary_key=True)
    faktura_id: Mapped[int] = Column(Integer, ForeignKey('faktura.id', name='faktura_stavka_ibfk_1'))
    sifra: Mapped[str] = Column(String(50))
    kolicina: Mapped[Decimal] = Column(Numeric(15, 6))
    jedinicna_cijena_osnovna: Mapped[Decimal] = Column(Numeric(15, 6))
    jedinicna_cijena_rabatisana: Mapped[Decimal] = Column(Numeric(15, 6))
    jedinicna_cijena_puna: Mapped[Decimal] = Column(Numeric(15, 6))
    jedinicna_cijena_prodajna: Mapped[Decimal] = Column(Numeric(15, 6))
    ukupna_cijena_osnovna: Mapped[Decimal] = Column(Numeric(15, 6))
    ukupna_cijena_rabatisana: Mapped[Decimal] = Column(Numeric(15, 6))
    ukupna_cijena_puna: Mapped[Decimal] = Column(Numeric(15, 6))
    ukupna_cijena_prodajna: Mapped[Decimal] = Column(Numeric(15, 6))
    # tax_rate_id: Mapped[int] = Column(Integer(), ForeignKey('poreska_stopa.id', name='FK_A09951B129F7'))
    porez_procenat: Mapped[Decimal] = Column(Numeric(15, 6))
    porez_iznos: Mapped[Decimal] = Column(Numeric(15, 6))
    rabat_procenat: Mapped[Decimal] = Column(Numeric(15, 6))
    rabat_iznos_osnovni: Mapped[Decimal] = Column(Numeric(15, 6))
    rabat_iznos_prodajni: Mapped[Decimal] = Column(Numeric(15, 6))
    naziv: Mapped[str] = Column(Text())
    jedinica_mjere_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('jedinica_mjere.id', name='faktura_stavka_ibfk_2'))
    tax_exemption_reason_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('tax_exemption_reason.id', name='FK_EDF2B661779B'),
        nullable=True)
    magacin_zaliha_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('magacin_zaliha.id', name='faktura_stavka_ibfk_4'))

    korigovana_kolicina: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovana_ukupna_cijena_osnovna: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovana_ukupna_cijena_rabatisana: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovana_ukupna_cijena_puna: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovana_ukupna_cijena_prodajna: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovani_porez_iznos: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovani_rabat_iznos_osnovni: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovani_rabat_iznos_prodajni: Mapped[Decimal] = Column(Numeric(15, 6))
    izvor_kalkulacije: Mapped[int] = Column(Integer())
    credit_note_turnover_used: Mapped[Decimal] = Column(Numeric(15, 6), nullable=False)
    credit_note_turnover_remaining: Mapped[Decimal] = Column(Numeric(15, 6), nullable=False)
    tax_exemption_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    corrected_tax_exemption_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    corrected_invoice_item_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('faktura_stavka.id', name='FK_9D49FAE3C64E'),
        nullable=True)
    correction_type_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('invoice_item_correction_type.id', name='FK_A9D722C0C26F'),
        nullable=True
    )
    korigovana_jedinicna_cijena_osnovna: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovana_jedinicna_cijena_rabatisana: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovana_jedinicna_cijena_puna: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovana_jedinicna_cijena_prodajna: Mapped[Decimal] = Column(Numeric(15, 6))

    faktura: Mapped[Faktura] = relationship("Faktura", back_populates="stavke", foreign_keys=faktura_id)
    jedinica_mjere: Mapped[JedinicaMjere] = relationship('JedinicaMjere', foreign_keys=jedinica_mjere_id)
    tax_exemption_reason: Mapped[TaxExemptionReason] = relationship(
        'TaxExemptionReason',
        foreign_keys=tax_exemption_reason_id
    )
    magacin_zaliha: Mapped[MagacinZaliha] = relationship('MagacinZaliha', foreign_keys=magacin_zaliha_id)
    corrected_invoice_item: Mapped[FakturaStavka] = relationship(
        'FakturaStavka',
        foreign_keys=corrected_invoice_item_id
    )


class InvoiceItemCorrectionType(Base):
    __tablename__ = 'invoice_item_correction_type'

    TYPE_QUANTITY = 1
    TYPE_UPB = 2
    TYPE_UPA = 3
    TYPE_TAX_FREE_AMOUNT = 4

    id: Mapped[int] = Column(Integer(), primary_key=True, autoincrement=False)
    description: Mapped[str] = Column(String(255), nullable=False)


class Faktura(Base):
    __tablename__ = 'faktura'

    TYPE_REGULAR = 1
    TYPE_CANCELLATION = 2
    TYPE_CUMMULATIVE = 3
    TYPE_PERIODIC = 4
    TYPE_ADVANCE = 5
    TYPE_CREDIT_NOTE = 6
    TYPE_CORRECTIVE = 7
    TYPE_ERROR_CORRECTIVE = 8
    TYPE_INVOICE_TEMPLATE = 9

    STATUS_STORED = 1
    STATUS_FISCALISATION_SUCCESS = 2
    STATUS_FISCALISATION_FAIL = 3
    STATUS_CANCELLED = 4
    STATUS_IN_CREDIT_NOTE = 5
    STATUS_HAS_ERROR_CORRECTIVE = 6

    id: Mapped[int] = Column(Integer(), primary_key=True)
    uuid: Mapped[str] = Column(String(100))
    redni_broj_fakture: Mapped[int] = Column(Integer())
    efi_ordinal_number: Mapped[int] = Column(Integer())
    internal_ordinal_number: Mapped[int] = Column(Integer())
    datumfakture: Mapped[datetime] = Column(DateTime())
    datumvalute: Mapped[datetime] = Column(DateTime())
    status: Mapped[int] = Column(Integer())
    napomena: Mapped[str] = Column(Text())
    vrstaplacanja_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('vrsta_placanja.id', name='faktura_ibfk_1'),
        name='vrstaplacanja')
    brojoperatera: Mapped[int] = Column(Integer(), ForeignKey('operater.id', name='faktura_ibfk_2'))
    komitent_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('komitent.id', name='faktura_ibfk_3'), index=True,
        nullable=True)
    ukupna_cijena_osnovna: Mapped[Decimal] = Column(Numeric(15, 6))
    ukupna_cijena_rabatisana: Mapped[Decimal] = Column(Numeric(15, 6))
    ukupna_cijena_puna: Mapped[Decimal] = Column(Numeric(15, 6))
    ukupna_cijena_prodajna: Mapped[Decimal] = Column(Numeric(15, 6))
    porez_iznos: Mapped[Decimal] = Column(Numeric(15, 6))
    rabat_iznos_osnovni: Mapped[Decimal] = Column(Numeric(15, 6))
    rabat_iznos_prodajni: Mapped[Decimal] = Column(Numeric(15, 6))
    firma_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name='faktura_ibfk_4'))
    efi_broj_fakture: Mapped[str] = Column(String(1000), nullable=True)
    efi_verify_url: Mapped[str] = Column(String(1000), nullable=True)
    ikof: Mapped[str] = Column(String(1000), nullable=True)  # TODO: Mapped[Duplicate] of iic
    jikr: Mapped[str] = Column(String(1000), nullable=True)
    iic: Mapped[str] = Column(String(32), nullable=True)  # TODO: Mapped[Duplicate] of ikof
    xml_request: Mapped[str] = Column(Text())
    xml_response: Mapped[str] = Column(Text())
    storno_faktura_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('faktura.id', name='fk__faktura__storno_faktura'),
        nullable=True
    )
    naplatni_uredjaj_id: Mapped[int] = Column(Integer(), ForeignKey('naplatni_uredjaj.id', name='faktura_ibfk_6'))
    valuta_id: Mapped[int] = Column(Integer(), ForeignKey('valuta.id', name='fk__faktura__valuta'))
    kurs_razmjene: Mapped[Decimal] = Column(Numeric(15, 6))
    poreski_period: Mapped[datetime] = Column(DateTime())
    tip_fakture_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('faktura_tip.id', name='fk__faktura__tip_fakture'),
        nullable=False
    )
    lokacija_dokumenta: Mapped[str] = Column(String(255))
    korigovana_ukupna_cijena_osnovna: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovana_ukupna_cijena_rabatisana: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovana_ukupna_cijena_puna: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovana_ukupna_cijena_prodajna: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovani_porez_iznos: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovani_rabat_iznos_osnovni: Mapped[Decimal] = Column(Numeric(15, 6))
    korigovani_rabat_iznos_prodajni: Mapped[Decimal] = Column(Numeric(15, 6))
    datum_prometa: Mapped[datetime] = Column(DateTime())
    is_cash: Mapped[bool] = Column(Boolean(create_constraint=True, name='faktura_chk_2'))
    source_invoice_id: Mapped[int] = Column(Integer(), ForeignKey('faktura.id', name='FK_CF286C39278F'))
    credit_note_turnover_used: Mapped[Decimal] = Column(Numeric(15, 6), nullable=False)
    credit_note_turnover_remaining: Mapped[Decimal] = Column(Numeric(15, 6), nullable=False)
    tax_exemption_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    corrected_tax_exemption_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    advance_invoice_id: Mapped[int] = Column(Integer(), ForeignKey('faktura.id', name='FK_CBDCC72AEA2D'))
    corrective_advance_invoice_id: Mapped[int] = Column(Integer(), ForeignKey('faktura.id', name='FK_660E715072A8'))
    is_advance_invoice: Mapped[bool] = Column(Boolean(create_constraint=False))
    error_corrective_invoice_id: Mapped[int] = Column(Integer(), ForeignKey('faktura.id', name='FK_D99A2890FCA6'))
    customer_invoice_view: Mapped[int] = Column(Integer())

    vrstaplacanja: Mapped[VrstaPlacanja] = relationship('VrstaPlacanja', foreign_keys=vrstaplacanja_id)
    operater: Mapped[Operater] = relationship('Operater', foreign_keys=brojoperatera)
    komitent: Mapped[Komitent] = relationship('Komitent', lazy='joined', foreign_keys=komitent_id)
    firma: Mapped[Firma] = relationship('Firma', lazy='joined', foreign_keys=firma_id)
    stavke: Mapped[List[FakturaStavka]] = relationship("FakturaStavka", back_populates="faktura")
    grupe_poreza: Mapped[List[FakturaGrupaPoreza]] = relationship(
        "FakturaGrupaPoreza",
        back_populates="faktura"
    )
    storno_faktura: Mapped[Faktura] = relationship(
        'Faktura',
        foreign_keys=storno_faktura_id,
        uselist=False
    )
    naplatni_uredjaj: Mapped[NaplatniUredjaj] = relationship(
        'NaplatniUredjaj',
        foreign_keys=naplatni_uredjaj_id
    )
    valuta: Mapped[Valuta] = relationship(
        'Valuta',
        foreign_keys=valuta_id
    )
    tip_fakture: Mapped[FakturaTip] = relationship(
        'FakturaTip',
        foreign_keys=tip_fakture_id
    )
    payment_methods: Mapped[List[PaymentMethod]] = relationship(
        'PaymentMethod',
        primaryjoin=PaymentMethod.invoice_id == id)
    korigovana_faktura: Mapped[Faktura] = relationship(
        'Faktura',
        secondary=CorrectedToCorrective,
        primaryjoin=CorrectedToCorrective.c.corrective_invoice_id == id,
        secondaryjoin=CorrectedToCorrective.c.corrected_invoice_id == id,
        uselist=False,
        back_populates='korektivne_fakture'
    )
    korektivne_fakture: Mapped[List[Faktura]] = relationship(
        'Faktura',
        secondary=CorrectedToCorrective,
        primaryjoin=CorrectedToCorrective.c.corrected_invoice_id == id,
        secondaryjoin=CorrectedToCorrective.c.corrective_invoice_id == id,
        back_populates='korigovana_faktura'
    )
    clanice_zbirne_fakture: Mapped[List[Faktura]] = relationship(
        'Faktura',
        secondary=VezaZbirnaFaktura,
        primaryjoin=VezaZbirnaFaktura.c.zbirna_faktura_id == id,
        secondaryjoin=VezaZbirnaFaktura.c.clanica_faktura_id == id
    )
    fakture_djeca: Mapped[List[Faktura]] = relationship(
        'Faktura',
        secondary=FakturaVeza,
        primaryjoin=FakturaVeza.c.faktura_roditelj_id == id,
        secondaryjoin=FakturaVeza.c.faktura_dijete_id == id,
        back_populates='fakture_roditelji'
    )
    fakture_roditelji: Mapped[List[Faktura]] = relationship(
        'Faktura',
        secondary=FakturaVeza,
        primaryjoin=FakturaVeza.c.faktura_dijete_id == id,
        secondaryjoin=FakturaVeza.c.faktura_roditelj_id == id,
        back_populates='fakture_djeca'
    )
    invoice_schedules: Mapped[List[InvoiceSchedule]] = relationship(
        'InvoiceSchedule',
        primaryjoin=and_(id == InvoiceSchedule.source_invoice_id, InvoiceSchedule.is_active.is_(True)),
        uselist=True,
        order_by=InvoiceSchedule.id.desc(),
        back_populates='source_invoice')
    error_corrective_invoice: Mapped[Faktura] = relationship(
        'Faktura',
        foreign_keys=error_corrective_invoice_id,
        remote_side=id
    )
    corrected_credit_note: Mapped[KnjiznoOdobrenje] = relationship(
        'KnjiznoOdobrenje',
        secondary=CreditNoteToCorrectiveInvoice,
        uselist=False,
        back_populates='korektivne_fakture'
    )

    @property
    def tax_exemption_base(self):
        value = Decimal(0)
        for grupa_poreza in self.grupe_poreza:
            if grupa_poreza.tax_exemption_reason_id is None:
                continue
            value += grupa_poreza.ukupna_cijena_rabatisana
        return value

    @property
    def tax_exemption_discount(self):
        value = Decimal(0)
        for grupa_poreza in self.grupe_poreza:
            if grupa_poreza.tax_exemption_reason_id is None:
                continue
            value += grupa_poreza.rabat_iznos_osnovni
        return value

    @property
    def ukupna_cijena_prodajna_valuta(self):
        return self.ukupna_cijena_prodajna * 1 / self.kurs_razmjene

    @property
    def korigovana_ukupna_cijena_prodajna_valuta(self):
        if self.tip_fakture_id == Faktura.TYPE_REGULAR:
            return Decimal(self.korigovana_ukupna_cijena_prodajna * 1 / self.kurs_razmjene)
        else:
            return Decimal(0)


class Artikal(Base):
    __tablename__ = 'artikal'

    IZVOR_KALKULACIJE_UPB = 1  # jedinicna_cijena_osnovna
    IZVOR_KALKULACIJE_UPA = 2  # jedinicna_cijena_puna

    id: Mapped[int] = Column(Integer(), primary_key=True)
    sifra: Mapped[str] = Column(String(50), nullable=True)
    barkod: Mapped[str] = Column(String(50), nullable=True)
    naziv: Mapped[str] = Column(Text())
    opis: Mapped[str] = Column(Text())

    grupa_artikala_id: Mapped[int] = Column(Integer, ForeignKey('grupa_artikala.id', name='artikal_ibfk_1'))
    jedinica_mjere_id: Mapped[int] = Column(Integer, ForeignKey('jedinica_mjere.id', name='artikal_ibfk_2'))

    slika_filepath: Mapped[str] = Column(String(255))
    slika_filename: Mapped[str] = Column(String(255))

    is_deleted: Mapped[bool] = Column(Boolean(create_constraint=False))

    grupa_artikala: Mapped[GrupaArtikala] = relationship('GrupaArtikala')
    jedinica_mjere: Mapped[JedinicaMjere] = relationship('JedinicaMjere')


class GrupaArtikala(Base):
    __tablename__ = 'grupa_artikala'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    naziv: Mapped[str] = Column(String(255))
    ui_default: Mapped[bool] = Column(Boolean(create_constraint=True, name='grupa_artikala_chk_1'))
    firma_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name='grupa_artikala_ibfk_1'))
    boja: Mapped[str] = Column(String(20))

    firma: Mapped[Firma] = relationship('Firma')


class Kalkulacija(Base):
    __tablename__ = 'kalkulacija'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    broj_ulazne_fakture: Mapped[str] = Column(String(50), nullable=True)
    redni_broj_kalkulacije: Mapped[int] = Column(Integer())
    datum_kalkulacije: Mapped[datetime] = Column(DateTime())
    datum_ulazne_fakture: Mapped[datetime] = Column(DateTime(), nullable=True)
    firma_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name='kalkulacija_ibfk_1'))
    dobavljac_id: Mapped[int] = Column(Integer(), ForeignKey('komitent.id', name='kalkulacija_ibfk_2'), nullable=True)
    operater_id: Mapped[int] = Column(Integer(), ForeignKey('operater.id', name='kalkulacija_ibfk_3'))
    magacin_id: Mapped[int] = Column(Integer(), ForeignKey('magacin.id', name='kalkulacija_ibfk_4'))

    dobavljac: Mapped[Komitent] = relationship('Komitent')
    firma: Mapped[Firma] = relationship('Firma')
    operater: Mapped[Operater] = relationship('Operater', lazy='joined')
    magacin: Mapped[Magacin] = relationship('Magacin', foreign_keys=magacin_id)
    stavke: Mapped[List[KalkulacijaStavka]] = relationship('KalkulacijaStavka', back_populates='kalkulacija')


class MagacinRedniBrojKalkulacije(Base):
    __tablename__ = 'magacin_redni_broj_kalkulacije'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    magacin_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('magacin.id', name='magacin_redni_broj_kalkulacije_ibfk_1'),
        nullable=False)
    godina: Mapped[int] = Column(Integer(), nullable=False)
    redni_broj: Mapped[int] = Column(Integer(), nullable=False)

    magacin: Mapped[Magacin] = relationship('Magacin')


class KalkulacijaStavka(Base):
    __tablename__ = 'kalkulacija_stavka'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    kalkulacija_id: Mapped[int] = Column(Integer(), ForeignKey('kalkulacija.id', name='kalkulacija_stavka_ibfk_1'))
    artikal_id: Mapped[int] = Column(Integer(), ForeignKey('artikal.id', name='kalkulacija_stavka_ibfk_2'))
    kolicina: Mapped[Decimal] = Column(Numeric(15, 6))

    kalkulacija: Mapped[Kalkulacija] = relationship('Kalkulacija', back_populates='stavke')
    artikal: Mapped[Artikal] = relationship('Artikal')


class Depozit(Base):
    __tablename__ = 'depozit'

    STATUS_STORED = 1
    STATUS_FISCALISE_SUCCESS = 2
    STATUS_FISCALIZE_FAILED = 3

    TIP_DEPOZITA_INITIAL = 1
    TIP_DEPOZITA_WITHDRAW = 2

    id: Mapped[int] = Column(Integer(), primary_key=True)
    datum_slanja: Mapped[datetime] = Column(DateTime())
    iznos: Mapped[Decimal] = Column(Numeric(15, 6))
    firma_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name="depozit_ibfk_1"))
    operater_id: Mapped[int] = Column(Integer(), ForeignKey('operater.id', name='depozit_ibfk_2'))
    smjena_id: Mapped[int] = Column(Integer(), ForeignKey('smjena.id', name='depozit_ibfk_3'), nullable=True)
    je_pocetak_dana: Mapped[bool] = Column(Boolean(create_constraint=True, name='depozit_chk_1'))
    tip_depozita: Mapped[int] = Column(Integer())
    fiskalizacioni_kod: Mapped[str] = Column(String(255), nullable=True)
    status: Mapped[int] = Column(Integer())
    datum_kreiranja: Mapped[datetime] = Column(DateTime(), default=datetime.now)
    naplatni_uredjaj_id: Mapped[int] = Column(Integer(), ForeignKey('naplatni_uredjaj.id', name='depozit_ibfk_4'))

    firma: Mapped[Firma] = relationship('Firma')
    operater: Mapped[Operater] = relationship('Operater', foreign_keys=[operater_id])
    smjena: Mapped[Smjena] = relationship('Smjena')
    naplatni_uredjaj: Mapped[NaplatniUredjaj] = relationship('NaplatniUredjaj')


class Smjena(Base):
    __tablename__ = 'smjena'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    datum_pocetka: Mapped[datetime] = Column(DateTime())
    datum_zavrsetka: Mapped[datetime] = Column(DateTime(), nullable=True)
    operater_id: Mapped[int] = Column(Integer(), ForeignKey('operater.id', name='smjena_ibfk_1'))
    firma_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name='smjena_ibfk_2'))

    operater: Mapped[Operater] = relationship('Operater', foreign_keys=[operater_id])
    firma: Mapped[Firma] = relationship('Firma', foreign_keys=[firma_id])


class OrdinalNumberCounter(Base):
    __tablename__ = 'ordinal_number_counter'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    year: Mapped[int] = Column(Integer())
    last_value: Mapped[int] = Column(Integer())
    payment_device_id: Mapped[int] = Column(Integer(), ForeignKey('naplatni_uredjaj.id', name='FK_085E34139A95'))
    type_id: Mapped[int] = Column(Integer(), ForeignKey('ordinal_number_counter_type.id', name='FK_EE03E095368A'))


class OrdinalNumberCounterType(Base):
    __tablename__ = 'ordinal_number_counter_type'

    id: Mapped[int] = Column(Integer(), primary_key=True, autoincrement=False)
    description: Mapped[str] = Column(String(255))


class InvoiceCounter(Base):
    # TODO Remove
    __tablename__ = 'invoice_counter'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    year: Mapped[int] = Column(Integer())
    value: Mapped[int] = Column(Integer())
    payment_device_id: Mapped[int] = Column(Integer(), ForeignKey('naplatni_uredjaj.id', name='FK_EC290607829E'))
    invoice_type_id: Mapped[int] = Column(Integer(), ForeignKey('faktura_tip.id', name='FK_52EFAE01A4AB'))


class PoreskaStopa(Base):
    __tablename__ = 'poreska_stopa'

    TAX_RATE_21 = 1
    TAX_RATE_7 = 2
    TAX_RATE_0 = 3
    TAX_RATE_EXEMPTION = 4

    id: Mapped[int] = Column(Integer(), primary_key=True, autoincrement=False)
    procenat: Mapped[Decimal] = Column(Numeric(15, 6))
    label: Mapped[str] = Column(String(255))


class RegisterInvoiceRequest(Base):
    __tablename__ = 'register_invoice_request'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    uuid: Mapped[str] = Column(String(255), nullable=True)
    xml: Mapped[str] = Column(Text(), nullable=True)
    faktura_id: Mapped[int] = Column(Integer(), ForeignKey('faktura.id', name='register_invoice_request_ibfk_1'))
    register_invoice_response_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('register_invoice_response.id', name='register_invoice_request_ibfk_2'),
        nullable=True)

    faktura: Mapped[Faktura] = relationship('Faktura')
    register_invoice_response: Mapped[RegisterInvoiceRequest] = relationship(
        'RegisterInvoiceResponse',
        foreign_keys=[register_invoice_response_id])


class RegisterInvoiceResponse(Base):
    __tablename__ = 'register_invoice_response'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    uuid: Mapped[str] = Column(String(255), nullable=True)
    xml: Mapped[str] = Column(Text(), nullable=True)
    faktura_id: Mapped[int] = Column(Integer(), ForeignKey('faktura.id', name='register_invoice_response_ibfk_1'))
    faultcode: Mapped[str] = Column(String(255))
    faultstring: Mapped[str] = Column(Text())

    faktura: Mapped[Faktura] = relationship('Faktura', foreign_keys=[faktura_id])


class RegisterDepositRequest(Base):
    __tablename__ = 'register_deposit_request'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    uuid: Mapped[str] = Column(String(50), nullable=True)
    xml: Mapped[str] = Column(Text(), nullable=True)
    depozit_id: Mapped[int] = Column(Integer(), ForeignKey('depozit.id', name='register_deposit_request_ibfk_1'))
    register_deposit_response_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('register_deposit_response.id', name='register_deposit_request_ibfk_2'),
        nullable=True)

    depozit: Mapped[Depozit] = relationship('Depozit')
    register_deposit_response: Mapped[RegisterDepositResponse] = relationship(
        'RegisterDepositResponse',
        foreign_keys=[register_deposit_response_id])


class RegisterDepositResponse(Base):
    __tablename__ = 'register_deposit_response'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    uuid: Mapped[str] = Column(String(50), nullable=True)
    xml: Mapped[str] = Column(Text(), nullable=True)
    depozit_id: Mapped[int] = Column(Integer(), ForeignKey('depozit.id', name='register_deposit_response_ibfk_1'))
    faultcode: Mapped[str] = Column(String(255), nullable=True)
    faultstring: Mapped[str] = Column(Text(), nullable=True)

    depozit: Mapped[Depozit] = relationship('Depozit')


class CsvObrada(Base):
    __tablename__ = 'csv_obrada'

    FORMAT_PERFEKT = 'perfekt'
    FORMAT_ELAVIRINT = 'elavirint'

    id: Mapped[int] = Column(Integer(), primary_key=True, autoincrement=False)
    naziv: Mapped[str] = Column(String(255), nullable=False)
    lokacija_ulaznih_csv_datoteka: Mapped[str] = Column(String(255), nullable=False)
    lokacija_neuspjelih_csv_datoteka: Mapped[str] = Column(String(255), nullable=False)
    lokacija_uspjelih_csv_datoteka: Mapped[str] = Column(String(255), nullable=False)
    lokacija_izlaznih_csv_datoteka: Mapped[str] = Column(String(255), nullable=False)
    lokacija_debug_datoteka: Mapped[str] = Column(String(255), nullable=False)
    format_datoteke: Mapped[str] = Column(String(255), nullable=False)  # perfekt, elavirint


class CsvObradaOvlascenje(Base):
    __tablename__ = 'csv_obrada_ovlascenje'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    csv_obrada_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('csv_obrada.id', name='fk__csv_obrada_ovlascenje__csv_obrada')
    )
    firma_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('firma.id', name='fk__csv_obrada_ovlascenje__firma'),
        nullable=False
    )
    datum_kreiranja: Mapped[datetime] = Column(DateTime(), default=datetime.now)

    csv_obrada: Mapped[CsvObrada] = relationship('CsvObrada')
    firma: Mapped[Firma] = relationship('Firma')


class CsvDatoteka(Base):
    __tablename__ = 'csv_datoteka'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    putanja: Mapped[str] = Column(String(255), nullable=False)
    naziv: Mapped[str] = Column(String(255), nullable=False)
    status: Mapped[int] = Column(Integer(), nullable=False)
    datum_kreiranja: Mapped[datetime] = Column(DateTime(), default=datetime.now)

    csv_upload_ovlascenje_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('csv_obrada_ovlascenje.id', name='fk__cv_datoteka__csv_obrada_ovlascenje'))


class CsvObradaLog(Base):
    __tablename__ = 'csv_obrada_log'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    opis: Mapped[str] = Column(Text(), nullable=False)
    datum_kreiranja: Mapped[datetime] = Column(DateTime(), default=datetime.now)
    csv_datoteka_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('csv_datoteka.id', name='fk__csv_obrada_log__csv_datoteka'),
        nullable=False)
    faktura_id: Mapped[int] = Column(Integer(), ForeignKey('faktura.id', name='fk__csv_obrada_log__faktura'))

    csv_datoteka: Mapped[CsvDatoteka] = relationship('CsvDatoteka')
    faktura: Mapped[Faktura] = relationship('Faktura')


class FakturaGrupaPoreza(Base):
    __tablename__ = 'faktura_grupa_poreza'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    broj_stavki: Mapped[int] = Column(Integer())

    ukupna_cijena_osnovna: Mapped[Decimal] = Column(Numeric(15, 6))
    ukupna_cijena_rabatisana: Mapped[Decimal] = Column(Numeric(15, 6))
    ukupna_cijena_puna: Mapped[Decimal] = Column(Numeric(15, 6))
    ukupna_cijena_prodajna: Mapped[Decimal] = Column(Numeric(15, 6))

    # tax_rate_id: Mapped[int] = Column(Integer(), ForeignKey('poreska_stopa.id', name='FK_402A70FA1A08'))
    porez_procenat: Mapped[Decimal] = Column(Numeric(15, 6))
    porez_iznos: Mapped[Decimal] = Column(Numeric(15, 6))

    rabat_iznos_osnovni: Mapped[Decimal] = Column(Numeric(15, 6))
    rabat_iznos_prodajni: Mapped[Decimal] = Column(Numeric(15, 6))
    faktura_id: Mapped[int] = Column(Integer(), ForeignKey('faktura.id', name='fk__faktura_grupa_poreza__faktura'))
    credit_note_turnover_used: Mapped[Decimal] = Column(Numeric(15, 6), nullable=False)
    credit_note_turnover_remaining: Mapped[Decimal] = Column(Numeric(15, 6), nullable=False)
    tax_exemption_reason_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('tax_exemption_reason.id', name='FK_8BAFBAF29EDA'))
    tax_exemption_amount: Mapped[Decimal] = Column(Numeric(15, 6))

    faktura: Mapped[Faktura] = relationship(
        'Faktura',
        back_populates='grupe_poreza',
        foreign_keys=faktura_id
    )
    tax_exemption_reason: Mapped[TaxExemptionReason] = relationship(
        'TaxExemptionReason',
        foreign_keys=tax_exemption_reason_id
    )


class FakturaTip(Base):
    __tablename__ = 'faktura_tip'

    id: Mapped[int] = Column(Integer(), primary_key=True, autoincrement=False)
    naziv: Mapped[str] = Column(String(255), nullable=False)
    efi_kod: Mapped[str] = Column(String(50))
    je_aktivno: Mapped[bool] = Column(Boolean(create_constraint=True, name='faktura_tip_chk_1'), nullable=False)


class SoapUser(Base):
    __tablename__ = 'soap_user'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    username: Mapped[str] = Column(String(255))
    password: Mapped[str] = Column(String(255))
    is_active: Mapped[bool] = Column(Boolean(create_constraint=True, name='soap_user_chk_1'))


class SoapPermission(Base):
    __tablename__ = 'soap_permission'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    company_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name='fk__soap_permission__firma'))
    soap_user_id: Mapped[int] = Column(Integer(), ForeignKey('soap_user.id', name='fk__soap_permission__soap_user'))

    company: Mapped[Firma] = relationship('Firma')
    soap_user: Mapped[SoapUser] = relationship('SoapUser')


class KomitentPlacanje(Base):
    __tablename__ = 'komitent_placanje'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    firma_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name='fk__komitent_placanje__firma'))
    komitent_id: Mapped[int] = Column(Integer(), ForeignKey('komitent.id', name='fk__komitent_placanje__komitent'))
    iznos: Mapped[Decimal] = Column(Numeric(15, 6))
    datum_placanja: Mapped[datetime] = Column(DateTime(), nullable=False)
    datum_kreiranja: Mapped[datetime] = Column(DateTime(), default=datetime.now)

    firma: Mapped[Firma] = relationship('Firma')
    komitent: Mapped[Komitent] = relationship('Komitent', back_populates='placanja')


class FakturaMailKampanja(Base):
    __tablename__ = 'faktura_mail_kampanja'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    naziv: Mapped[str] = Column(String(255))
    firma_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('firma.id', name='fk__faktura_mail_kampanja__firma'),
        nullable=False)
    datum_pocetka: Mapped[datetime] = Column(DateTime(), nullable=False)
    datum_zavrsetka: Mapped[datetime] = Column(DateTime(), nullable=False)
    datum_kreiranja: Mapped[datetime] = Column(DateTime(), default=datetime.now, nullable=False)


class FakturaMailKampanjaStavka(Base):
    __tablename__ = 'faktura_mail_kampanja_stavka'

    STATUS_PENDING = 1
    STATUS_SUCCESS = 2
    STATUS_FAIL = 3
    STATUS_FAIL_ON_CREATE = 4

    id: Mapped[int] = Column(Integer(), primary_key=True)
    faktura_mail_kampanja_id = Column(
        Integer(),
        ForeignKey('faktura_mail_kampanja.id', name='fk__faktura_mail_kampanja_stavka__faktura_mail_kampanja'),
        nullable=True)
    komitent_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('komitent.id', name='fk__faktura_mail_kampanja_stavka__komitent'),
        nullable=False)
    faktura_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('faktura.id', name='fk__faktura_mail_kampanja_stavka__faktura'),
        nullable=False)
    status: Mapped[int] = Column(Integer(), nullable=False)
    mail_from: Mapped[str] = Column(String(255), nullable=False)
    mail_to: Mapped[str] = Column(String(255), nullable=False)
    opis_greske: Mapped[str] = Column(String(500))
    datum_slanja: Mapped[datetime] = Column(DateTime())
    datum_kreiranja: Mapped[datetime] = Column(DateTime(), default=datetime.now, nullable=False)

    faktura_mail_kampanja: Mapped[FakturaMailKampanja] = relationship('FakturaMailKampanja')
    faktura: Mapped[Faktura] = relationship('Faktura')


class OrderGrupa(Base):
    __tablename__ = 'order_grupa'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    naziv: Mapped[str] = Column(String(200), nullable=False)
    naplatni_uredjaj_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('naplatni_uredjaj.id', name='fk__order_grupa__naplatni_uredjaj'),
        nullable=False)
    komitent_id: Mapped[int] = Column(Integer(), ForeignKey('komitent.id', name='fk__order_grupa__komitent'))

    stavke: Mapped[List[OrderGrupaStavka]] = relationship('OrderGrupaStavka', back_populates="order_grupa")


class OrderGrupaStavka(Base):
    __tablename__ = 'order_grupa_stavka'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    order_grupa_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('order_grupa.id', name='fk__order_grupa_stavka__order_grupa'),
        nullable=False)
    faktura_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('faktura.id', name='fk__order_grupa_stavka__faktura'),
        nullable=False)

    order_grupa: Mapped[OrderGrupa] = relationship('OrderGrupa', back_populates="stavke")
    faktura: Mapped[Faktura] = relationship('Faktura')


class KnjiznoOdobrenje(Base):
    __tablename__ = 'knjizno_odobrenje'

    STATUS_UPISANO = 1
    STATUS_FISKALIZOVANO = 2
    STATUS_NEUSPJELA_FISKALIZACIJA = 3

    id: Mapped[int] = Column(Integer(), primary_key=True)
    status: Mapped[int] = Column(Integer())
    redni_broj: Mapped[int] = Column(Integer())
    efi_ordinal_number: Mapped[int] = Column(Integer())
    internal_ordinal_number: Mapped[int] = Column(Integer())
    datum_fiskalizacije: Mapped[datetime] = Column(DateTime())
    datum_valute: Mapped[datetime] = Column(DateTime(), nullable=False)
    datum_prometa: Mapped[datetime] = Column(DateTime(), nullable=False)
    uuid: Mapped[str] = Column(String(100))
    vrsta_placanja_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('vrsta_placanja.id', name="fk__knjizno_odobrenje__vrsta_placanja"))
    firma_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('firma.id', name="fk__knjizno_odobrenje__firma"),
        nullable=False)
    komitent_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('komitent.id', name="fk__knjizno_odobrenje__komitent"),
        nullable=False)
    datum_kreiranja: Mapped[datetime] = Column(DateTime(), default=datetime.now)
    operater_id = Column(
        Integer(),
        ForeignKey('operater.id', name="fk__knjizno_odobrenje__operater"))
    naplatni_uredjaj_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('naplatni_uredjaj.id', name="fk__knjizno_odobrenje__naplatni_uredjaj"))

    efi_broj_fakture: Mapped[str] = Column(String(1000), nullable=True)
    efi_verify_url: Mapped[str] = Column(String(1000), nullable=True)
    ikof: Mapped[str] = Column(String(1000), nullable=True)
    jikr: Mapped[str] = Column(String(1000), nullable=True)
    iic: Mapped[str] = Column(String(32), nullable=True)
    poreski_period: Mapped[datetime] = Column(DateTime())
    valuta_id: Mapped[int] = Column(Integer(), ForeignKey('valuta.id', name='fk__knjizno_odobrenje__valuta'))
    kurs_razmjene: Mapped[Decimal] = Column(Numeric(15, 6))
    xml_request: Mapped[str] = Column(Text())
    xml_response: Mapped[str] = Column(Text())
    napomena: Mapped[str] = Column(Text())
    tax_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    return_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    return_amount_with_tax: Mapped[Decimal] = Column(Numeric(15, 6))
    discount_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    discount_amount_with_tax: Mapped[Decimal] = Column(Numeric(15, 6))
    return_and_discount_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    return_and_discount_amount_with_tax: Mapped[Decimal] = Column(Numeric(15, 6))

    vrsta_placanja: Mapped[VrstaPlacanja] = relationship('VrstaPlacanja')
    firma: Mapped[Firma] = relationship('Firma')
    komitent: Mapped[Komitent] = relationship('Komitent')
    stavke: Mapped[List[KnjiznoOdobrenjeStavka]] = relationship('KnjiznoOdobrenjeStavka')
    operater: Mapped[Operater] = relationship('Operater')
    naplatni_uredjaj: Mapped[NaplatniUredjaj] = relationship('NaplatniUredjaj')
    fakture: Mapped[List[Faktura]] = relationship(
        'Faktura',
        secondary=VezaKnjiznoOdobrenjeFaktura,
        primaryjoin=VezaKnjiznoOdobrenjeFaktura.c.knjizno_odobrenje_id == id,
        # secondaryjoin=VezaKnjiznoOdobrenjeFaktura.c.faktura_id == Faktura.id
    )
    valuta: Mapped[Valuta] = relationship('Valuta')
    grupe_poreza: Mapped[List[FakturaGrupaPoreza]] = relationship(
        "KnjiznoOdobrenjeGrupaPoreza",
        back_populates="knjizno_odobrenje"
    )
    korektivne_fakture: Mapped[List[Faktura]] = relationship(
        'Faktura',
        secondary=CreditNoteToCorrectiveInvoice,
        back_populates='corrected_credit_note'
    )
    iic_refs: Mapped[List[CreditNoteIICRef]] = relationship(
        'CreditNoteIICRef',
        back_populates='credit_note'
    )


class KnjiznoOdobrenjeGrupaPoreza(Base):
    __tablename__ = 'knjizno_odobrenje_grupa_poreza'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    broj_stavki: Mapped[int] = Column(Integer())
    knjizno_odobrenje_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('knjizno_odobrenje.id', name='fk__knjizno_odobrenje_grupa_poreza__knjizno_odobrenje'))
    tax_rate: Mapped[Decimal] = Column(Numeric(15, 6))
    tax_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    return_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    return_amount_with_tax: Mapped[Decimal] = Column(Numeric(15, 6))
    discount_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    discount_amount_with_tax: Mapped[Decimal] = Column(Numeric(15, 6))
    return_and_discount_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    return_and_discount_amount_with_tax: Mapped[Decimal] = Column(Numeric(15, 6))

    knjizno_odobrenje: Mapped[KnjiznoOdobrenje] = relationship(
        "KnjiznoOdobrenje",
        back_populates="grupe_poreza"
    )


class KnjiznoOdobrenjeStavka(Base):
    __tablename__ = 'knjizno_odobrenje_stavka'

    ITEM_TYPE_RETURN = 1
    ITEM_TYPE_DISCOUNT = 2

    id: Mapped[int] = Column(Integer(), primary_key=True)
    knjizno_odobrenje_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('knjizno_odobrenje.id', name="fk__knjizno_odobrenje_stavka__knjizno_odobrenje"),
        nullable=False)

    fakture_ukupna_cijena_osnovna: Mapped[Decimal] = Column(Numeric(15, 6))
    fakture_ukupna_cijena_rabatisana: Mapped[Decimal] = Column(Numeric(15, 6))
    fakture_ukupna_cijena_prodajna: Mapped[Decimal] = Column(Numeric(15, 6))
    fakture_ukupna_cijena_puna: Mapped[Decimal] = Column(Numeric(15, 6))
    fakture_porez_iznos: Mapped[Decimal] = Column(Numeric(15, 6))
    fakture_rabat_iznos_osnovni: Mapped[Decimal] = Column(Numeric(15, 6))
    fakture_rabat_iznos_prodajni: Mapped[Decimal] = Column(Numeric(15, 6))

    description: Mapped[str] = Column(String(255))
    tax_rate: Mapped[Decimal] = Column(Numeric(15, 6))
    tax_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    return_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    return_amount_with_tax: Mapped[Decimal] = Column(Numeric(15, 6))
    discount_amount: Mapped[Decimal] = Column(Numeric(15, 6))
    discount_amount_with_tax: Mapped[Decimal] = Column(Numeric(15, 6))
    type: Mapped[int] = Column(Integer())


class CreditNoteRequest(Base):
    __tablename__ = 'credit_note_request'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    uuid: Mapped[str] = Column(String(255), nullable=True)
    xml: Mapped[str] = Column(Text(), nullable=True)
    knjizno_odobrenje_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('knjizno_odobrenje.id', name="fk__credit_note_request__knjizno_odobrenje"))
    credit_note_response_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('credit_note_response.id', name="fk__credit_note_request__credit_note_response"),
        nullable=True)

    knjizno_odobrenje: Mapped[KnjiznoOdobrenje] = relationship('KnjiznoOdobrenje')
    credit_note_response: Mapped[CreditNoteResponse] = relationship('CreditNoteResponse')


class CreditNoteResponse(Base):
    __tablename__ = 'credit_note_response'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    uuid: Mapped[str] = Column(String(255), nullable=True)
    xml: Mapped[str] = Column(Text(), nullable=True)
    knjizno_odobrenje_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('knjizno_odobrenje.id', name="fk__credit_note_response__knjizno_odobrenje"))
    faultcode: Mapped[str] = Column(String(255))
    faultstring: Mapped[str] = Column(Text())

    knjizno_odobrenje: Mapped[KnjiznoOdobrenje] = relationship('KnjiznoOdobrenje')


class InvoiceProcessingLock(Base):
    __tablename__ = 'invoice_processing_lock'

    id: Mapped[int] = Column(
        Integer(),
        ForeignKey('naplatni_uredjaj.id', name="fk__payment_device_lock__naplatni_uredjaj"),
        primary_key=True)


class CreditNoteProcessingLock(Base):
    __tablename__ = 'credit_note_processing_lock'

    id: Mapped[int] = Column(
        Integer(),
        ForeignKey('naplatni_uredjaj.id', name='credit_note_processing_lock_ibfk_1'),
        primary_key=True)


class AgentUser(Base):
    __tablename__ = 'agent_user'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    name: Mapped[str] = Column(String(255))
    username: Mapped[str] = Column(String(255))
    password: Mapped[str] = Column(String(255))
    is_active: Mapped[bool] = Column(Boolean(create_constraint=False))


class PaymentDeviceLock(Base):
    __tablename__ = 'payment_device_lock'

    id: Mapped[int] = Column(ForeignKey('naplatni_uredjaj.id', name="FK_E8A750A4AC78"), primary_key=True)


class CreditNoteIICRef(Base):
    __tablename__ = 'credit_note_iic_ref'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    credit_note_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('knjizno_odobrenje.id', name="FK_BF33DA39337D"),
        nullable=False)
    invoice_id: Mapped[int] = Column(
        Integer(),
        ForeignKey('faktura.id', name="FK_D27719BCDDF8"),
        nullable=True)
    iic: Mapped[str] = Column('iic', String(32), nullable=False)
    verification_url: Mapped[str] = Column(String(1000), nullable=False)
    issue_datetime: Mapped[datetime] = Column(DateTime(), nullable=False)

    total_21: Mapped[int] = Column(Numeric(15, 6), nullable=False)
    total_7: Mapped[int] = Column(Numeric(15, 6), nullable=False)
    total_0: Mapped[int] = Column(Numeric(15, 6), nullable=False)
    total_exempt: Mapped[int] = Column(Numeric(15, 6), nullable=False)

    amount_21: Mapped[int] = Column(Numeric(15, 6), nullable=False)
    amount_7: Mapped[int] = Column(Numeric(15, 6), nullable=False)
    amount_0: Mapped[int] = Column(Numeric(15, 6), nullable=False)
    amount_exempt: Mapped[int] = Column(Numeric(15, 6), nullable=False)

    credit_note: Mapped[KnjiznoOdobrenje] = relationship(
        'KnjiznoOdobrenje',
        back_populates='iic_refs')
    invoice: Mapped[Faktura] = relationship(
        'Faktura',
        foreign_keys=invoice_id
    )


class FiscalizationCertificate(Base):
    __tablename__ = 'fiscalization_certificate'

    id: Mapped[int] = Column(Integer(), primary_key=True)
    fingerprint: Mapped[bytes] = Column(String(64))
    not_valid_before: Mapped[datetime] = Column(DateTime(), nullable=False)
    not_valid_after: Mapped[datetime] = Column(DateTime(), nullable=False)
    password: Mapped[str] = Column(String(255), nullable=False)
    owner_id: Mapped[int] = Column(Integer(), ForeignKey('firma.id', name="FK_C46E0DE61C29"), nullable=False)

    owner: Mapped[Firma] = relationship(foreign_keys=owner_id, back_populates='certificates')


# Search indexes
Index('IX_6D851962D0F8', Faktura.firma_id, Faktura.iic)
Index('IX_DDEF1ED69C9E', Faktura.iic)
Index('IX_AB073009DB3F', Faktura.customer_invoice_view)
Index('IX_D5DC1D3EFF98', Faktura.naplatni_uredjaj_id, Faktura.customer_invoice_view)

Index('grupa_artikala_id', Artikal.grupa_artikala_id)
Index('jedinica_mjere_id', Artikal.jedinica_mjere_id)

Index('firma_id', Depozit.firma_id)
Index('operater_id', Depozit.operater_id)
Index('smjena_id', Depozit.smjena_id)
Index('naplatni_uredjaj_id', Depozit.naplatni_uredjaj_id)

Index('firma_id', Depozit.firma_id)

Index('vrstaplacanja', Faktura.vrstaplacanja_id)
Index('brojoperatera', Faktura.brojoperatera)
Index('firma_id', Faktura.firma_id)
Index('ix_faktura_komitent_id', Faktura.komitent_id)
Index('naplatni_uredjaj_id', Faktura.naplatni_uredjaj_id)
Index('storno_faktura_id', Faktura.storno_faktura_id)

Index('drzava', Firma.drzava)

Index('firma_id', DospjelaFaktura.firma_id)

Index('firma_id', GrupaArtikala.firma_id)

Index('firma_id', JedinicaMjere.firma_id)

Index('firma_id', Kalkulacija.firma_id)
Index('dobavljac_id', Kalkulacija.dobavljac_id)
Index('operater_id', Kalkulacija.operater_id)
Index('magacin_id', Kalkulacija.magacin_id)

Index('kalkulacija_id', KalkulacijaStavka.kalkulacija_id)
Index('artikal_id', KalkulacijaStavka.artikal_id)

Index('tip_identifikacione_oznake_id', Komitent.tip_identifikacione_oznake_id)

Index('firma_id', Magacin.firma_id)

Index('magacin_id', MagacinRedniBrojKalkulacije.magacin_id)

Index('magacin_id', MagacinZaliha.magacin_id)
Index('artikal_id', MagacinZaliha.artikal_id)

Index('firma_id', Operater.firma_id)
Index('magacin_id', Operater.magacin_id)
Index('naplatni_uredjaj_id', Operater.naplatni_uredjaj_id)

Index('organizaciona_jedinica_id', NaplatniUredjaj.organizaciona_jedinica_id)

Index('firma_id', OrganizacionaJedinica.firma_id)
Index('drzava_id', OrganizacionaJedinica.drzava_id)

Index('operater_id', PodesavanjaAplikacije.operater_id)

Index('depozit_id', RegisterDepositRequest.depozit_id)
Index('register_deposit_response_id', RegisterDepositRequest.register_deposit_response_id)

Index('depozit_id', RegisterDepositResponse.depozit_id)


Index('faktura_id', RegisterInvoiceRequest.faktura_id)
Index('register_invoice_response_id', RegisterInvoiceRequest.register_invoice_response_id)

Index('faktura_id', RegisterInvoiceResponse.faktura_id)

Index('operater_id', Smjena.operater_id)
Index('firma_id', Smjena.firma_id)

Index('faktura_id', FakturaStavka.faktura_id)
Index('jedinica_mjere_id', FakturaStavka.jedinica_mjere_id)
Index('magacin_zaliha_id', FakturaStavka.magacin_zaliha_id)

Index('IX_FCDFDCCC7ABA', FiscalizationCertificate.owner_id)
