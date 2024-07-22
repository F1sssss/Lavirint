import base64
from decimal import Decimal
from io import BytesIO

import pdfkit
import qrcode
from bottle import SimpleTemplate
from datauri import DataURI

from backend import calc
from backend.models import Faktura
from backend.opb import komitent_opb
from backend.opb.helpers import get_efi_verify_url
from backend.podesavanja import podesavanja

with open(podesavanja.PRINT_FONT_FILEPATH_REGULAR, 'rb') as font_file:
    content = font_file.read()
    FONT_REGULAR_URL = 'data:font/truetype;charset=utf-8;base64,%s' % base64.b64encode(content).decode()

with open(podesavanja.PRINT_FONT_FILEPATH_LIGHT, 'rb') as font_file:
    content = font_file.read()
    FONT_LIGHT_URL = 'data:font/truetype;charset=utf-8;base64,%s' % base64.b64encode(content).decode()


def get_invoice_qr_code_as_bytesio(link):
    qr_code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=0,
    )
    qr_code.add_data(link)
    qr_code.make()
    image = qr_code.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def get_invoice_qr_code_as_bytes(link):
    return get_invoice_qr_code_as_bytesio(link).read()


def get_invoice_qr_code_as_datauri(link):

    invoice_qr_code_bytes = get_invoice_qr_code_as_bytes(link)
    return DataURI.make('image/png', charset='utf-8', base64=True, data=invoice_qr_code_bytes)


def save_to_file(faktura, filepath, tip_stampe='a4'):
    page, wkhtmltopdf_options = get_invoice_template_for_pdfkit(faktura, tip_stampe)
    pdfkit.from_string(page, filepath, options=wkhtmltopdf_options)


def get_invoice_template_pdf_as_bytes(faktura, tip_stampe='a4'):
    page, wkhtmltopdf_options = get_invoice_template_for_pdfkit(faktura, tip_stampe)
    return pdfkit.PDFKit(page, "string", options=wkhtmltopdf_options).to_pdf()


def get_invoice_print_kwargs(invoice: Faktura, a4_margin):
    kwargs = {}
    kwargs['faktura'] = invoice
    kwargs['format_number'] = calc.format_decimal
    kwargs['font_regular_url'] = FONT_REGULAR_URL
    kwargs['font_light_url'] = FONT_LIGHT_URL
    kwargs['qr_code'] = get_invoice_qr_code_as_datauri(invoice.efi_verify_url)

    if invoice.komitent_id is not None:
        kwargs['buyer_fiscalized_debt'] = komitent_opb.get_fiscalized_debt_by_id(invoice.komitent_id)
        kwargs['buyer_total_payments'] = komitent_opb.get_total_payments_by_id(invoice.komitent_id)
        kwargs['buyer_previous_debt'] = Decimal(0) if invoice.komitent.previous_debt is None else invoice.komitent.previous_debt

    kwargs['company_logo_datauri'] = None
    if invoice.firma.logo_filepath is not None:
        kwargs['company_logo_datauri'] = DataURI.from_file(invoice.firma.logo_filepath)

    kwargs['a4_margin_top'] = a4_margin
    kwargs['a4_margin_bottom'] = a4_margin
    kwargs['a4_margin_left'] = a4_margin
    kwargs['a4_margin_right'] = a4_margin

    return kwargs


def get_invoice_template(invoice, page_size):
    page_size = page_size.lower()

    if invoice.tip_fakture_id == Faktura.TYPE_INVOICE_TEMPLATE:
        if page_size == 'a4':
            template_path = 'backend/templates/print/invoice_template_a4.html'
        else:
            raise Exception('Invalid template page_size: %s' % page_size)
    else:
        if page_size == 'a4':
            template_path = 'backend/templates/print/invoice_a4.html'
        elif page_size == '58mm':
            if invoice.naplatni_uredjaj.tip_naplatnog_uredjaja_id == 2:
                invoice.efi_verify_url_short = get_efi_verify_url(invoice, is_long=False)
                template_path = 'backend/templates/print/invoice_58mm_pipo.html'
            else:
                template_path = 'backend/templates/print/invoice_58mm.html'
        else:
            raise Exception('Invalid template page_size: %s' % page_size)

    with open(template_path, 'r') as file:
        return SimpleTemplate(file.read(), encoding='utf-8')


def get_invoice_template_for_pdfkit(invoice, page_size):
    page_size_lower = page_size.lower()
    if page_size_lower not in ['a4', '58mm']:
        raise Exception('Invalid template page_size_lower: %s' % page_size_lower)

    wkhtmltopdf_options = {}
    if page_size_lower == 'a4':
        wkhtmltopdf_options['page-size'] = 'A4'
        wkhtmltopdf_options['zoom'] = '1.275'
        wkhtmltopdf_options['margin-top'] = '8mm'
        wkhtmltopdf_options['margin-bottom'] = '8mm'
        wkhtmltopdf_options['margin-left'] = '8mm'
        wkhtmltopdf_options['margin-right'] = '8mm'
    elif page_size_lower == '58mm':
        wkhtmltopdf_options['page-width'] = '58mm'
        wkhtmltopdf_options['page-height'] = '3000mm'
        wkhtmltopdf_options['margin-top'] = '4mm'
        wkhtmltopdf_options['margin-bottom'] = '4mm'
        wkhtmltopdf_options['margin-left'] = '4mm'
        wkhtmltopdf_options['margin-right'] = '4mm'

    print_kwargs = get_invoice_print_kwargs(invoice, a4_margin='0mm')

    return get_invoice_template(invoice, page_size).render(**print_kwargs), wkhtmltopdf_options


def get_invoice_template_for_browser(invoice: Faktura, page_size: str):
    page_size_lower = page_size.lower()
    if page_size_lower not in ['a4', '58mm']:
        raise Exception('Invalid template page_size_lower: %s' % page_size_lower)

    print_kwargs = get_invoice_print_kwargs(invoice, a4_margin='8mm')

    return get_invoice_template(invoice, page_size).render(**print_kwargs)


def get_credit_note_template(credit_note):
    credit_note.qr_kod = get_invoice_qr_code_as_datauri(credit_note.efi_verify_url)

    credit_note.firma_logo_datauri = None
    if credit_note.firma.logo_filepath is not None:
        credit_note.firma_logo_datauri = DataURI.from_file(credit_note.firma.logo_filepath)

    with open('backend/templates/print/credit_note_a4.html', 'r') as file:
        return SimpleTemplate(file.read(), encoding='utf-8')


def get_credit_note_template_for_browser(credit_note):
    template = get_credit_note_template(credit_note)

    print_kwargs = get_credit_note_print_kwargs(credit_note, a4_margin='8mm')

    return template.render(**print_kwargs)


def get_credit_note_print_kwargs(credit_note, a4_margin):
    kwargs = {}
    kwargs['knjizno_odobrenje'] = credit_note
    kwargs['format_number'] = calc.format_decimal
    kwargs['qr_code'] = get_invoice_qr_code_as_datauri(credit_note.efi_verify_url)

    kwargs['company_logo_datauri'] = None
    if credit_note.firma.logo_filepath is not None:
        kwargs['company_logo_datauri'] = DataURI.from_file(credit_note.firma.logo_filepath)

    kwargs['a4_margin'] = a4_margin

    return kwargs


def get_credit_note_template_for_pdfkit(credit_note):
    wkhtmltopdf_options = {}
    wkhtmltopdf_options['page-size'] = 'A4'
    wkhtmltopdf_options['zoom'] = '1.275'
    wkhtmltopdf_options['margin-top'] = '8mm'
    wkhtmltopdf_options['margin-bottom'] = '8mm'
    wkhtmltopdf_options['margin-left'] = '8mm'
    wkhtmltopdf_options['margin-right'] = '8mm'

    template = get_credit_note_template(credit_note)

    print_kwargs = get_credit_note_print_kwargs(credit_note, a4_margin='0mm')

    return template.render(**print_kwargs), wkhtmltopdf_options


def save_credit_note_to_file(credit_note, filepath):
    page, wkhtmltopdf_options = get_credit_note_template_for_pdfkit(credit_note)
    pdfkit.from_string(page, filepath, options=wkhtmltopdf_options)


def append_to_pdf(pdf_bytes, company, invoice):
    # TODO Why import inside function
    import io

    from PyPDF2 import PdfFileReader
    from PyPDF2 import PdfFileWriter
    from reportlab.lib import units
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    invoice_qr_code_bytesio = get_invoice_qr_code_as_bytesio(invoice.efi_verify_url)

    existing_pdf = PdfFileReader(io.BytesIO(pdf_bytes))

    packet = io.BytesIO()
    canvas_instance = canvas.Canvas(packet, bottomup=0)

    for _ in range(existing_pdf.numPages - 1):
        canvas_instance.showPage()

    image = ImageReader(invoice_qr_code_bytesio)
    canvas_instance.drawImage(
        image,
        x=float(company.dokument_qr_code_x) * units.mm,
        y=float(company.dokument_qr_code_y) * units.mm,
        width=float(company.dokument_qr_code_width) * units.mm,
        height=float(company.dokument_qr_code_height) * units.mm,
        preserveAspectRatio=True,
        mask='auto'
    )

    canvas_instance.setFontSize(8)

    canvas_instance.drawString(
        x=float(company.dokument_ikof_x) * units.mm,
        y=(float(company.dokument_ikof_y) + 2) * units.mm,
        text='IIC: %s' % invoice.ikof
    )

    canvas_instance.drawString(
        x=float(company.dokument_jikr_x) * units.mm,
        y=(float(company.dokument_jikr_y) + 2) * units.mm,
        text='FIC: %s' % invoice.jikr
    )

    canvas_instance.drawString(
        x=float(company.dokument_kod_operatera_x) * units.mm,
        y=(float(company.dokument_kod_operatera_y) + 2) * units.mm,
        text='Operator Code: %s' % invoice.operater.kodoperatera
    )

    canvas_instance.drawString(
        x=float(company.dokument_efi_verify_url_x) * units.mm,
        y=(float(company.dokument_efi_verify_url_y) + 2) * units.mm,
        text='Invoice Id: %s' % invoice.efi_broj_fakture
    )

    canvas_instance.save()
    packet.seek(0)

    new_pdf = PdfFileReader(packet)

    output = PdfFileWriter()

    for i in range(len(existing_pdf.pages)):
        page = existing_pdf.getPage(i)
        page.mergePage(new_pdf.getPage(i))
        output.addPage(page)

    outputStream = io.BytesIO()
    output.write(outputStream)
    outputStream.seek(0)

    return outputStream
    # return DataURI.make('application/pdf', charset='utf-8', base64=True, data=outputStream.read())
