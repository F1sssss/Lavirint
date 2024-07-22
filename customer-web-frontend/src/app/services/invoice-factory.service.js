let IZVOR_KALKULACIJE_UPB = 1;  // Osnovica
let IZVOR_KALKULACIJE_UPA = 2;  // Puna cijena

let PAYMENT_METHOD_TYPE_BANKNOTE = 1;
let PAYMENT_METHOD_TYPE_CARD = 2;
let PAYMENT_METHOD_TYPE_CHECK = 3;
let PAYMENT_METHOD_TYPE_SVOUCHER = 4;
let PAYMENT_METHOD_TYPE_COMPANY = 5;
let PAYMENT_METHOD_TYPE_ORDER = 6;
let PAYMENT_METHOD_TYPE_ADVANCE = 7;
let PAYMENT_METHOD_TYPE_ACCOUNT = 8;
let PAYMENT_METHOD_TYPE_FACTORING = 9;
let PAYMENT_METHOD_TYPE_COMPENSATION = 10;
let PAYMENT_METHOD_TYPE_TRANSFER = 11;
let PAYMENT_METHOD_TYPE_WAIVER = 12;
let PAYMENT_METHOD_TYPE_KIND = 13;
let PAYMENT_METHOD_TYPE_OTHER = 14;
let PAYMENT_METHOD_TYPE_BUSINESSCARD = 15;
let PAYMENT_METHOD_TYPE_OTHER_CASH = 16;

let CORRECTION_TYPE_QUANTITY = 1;
let CORRECTION_TYPE_UPB = 2;
let CORRECTION_TYPE_UPA = 3;
let CORRECTION_TYPE_TAX_FREE_AMOUNT = 4;

angular
    .module('app')
    .service('invoiceFactory', invoiceFactory);

invoiceFactory.$inject = ['fisConfig'];

function invoiceFactory(fisConfig) {
    let PRECISION = 4;

    let service = {};
    service.setBuyer = setBuyer;
    //
    service.copyToCorrectedFields = copyToCorrectedFields;
    service.copyItemsFromAdvanceInvoice = copyItemsFromAdvanceInvoice;
    //
    service.create = create;
    service.createFromTemplate = createFromTemplate;
    //
    service.createPaymentMethod = createPaymentMethod;
    service.splitAmount = splitAmount;
    service.distributeEvenlyToPaymentMethods = distributeEvenlyToPaymentMethods;
    service.isCash = isCash;
    service.addBlankItem = addBlankItem;
    service.addPaymentMethodByTypeId = addPaymentMethodByTypeId;
    service.sortPaymentMethodTypes = sortPaymentMethodTypes;
    service.sortPaymentMethods = sortPaymentMethods;
    service.mergePaymentMethods = mergePaymentMethods;
    service.addItemFromItemTemplate = addItemFromItemTemplate;
    service.updateItemFromItemTemplate = updateItemFromItemTemplate;
    service.recalculateTotals = recalculateTotals;
    service.recalculatePaymentMethodTotals = recalculatePaymentMethodTotals;
    service.recalculateTaxGroups = recalculateTaxGroups;
    service.recalculateItem = recalculateItem;
    service.recalculateItemBasedOnUPB = recalculateItemBasedOnUPB;
    service.recalculateItemBasedOnUPA = recalculateItemBasedOnUPA;
    service.recalculateItemBasedOnExemption = recalculateItemBasedOnExemption;
    service.getInvoiceItem = getInvoiceItem;
    service.createCorrectiveInvoice = createCorrectiveInvoice;
    service.getCorrectiveInvoiceFromDiff = getCorrectiveInvoiceFromDiff;
    service.updateCorrectiveInvoiceItemsFromDiff = updateCorrectiveInvoiceItemsFromDiff;
    //
    service.recalculateInvoiceItemTemplate = recalculateInvoiceItemTemplate;
    service.recalculateInvoiceItemTemplateFromUPB = recalculateInvoiceItemTemplateFromUPB;
    service.recalculateInvoiceItemTemplateFromUPA = recalculateInvoiceItemTemplateFromUPA;
    //
    service.setCorrectedInvoiceReference = setCorrectedInvoiceReference;
    service.setCorrectedCreditNoteReference = setCorrectedCreditNoteReference;
    //
    service.getPaymentMethod = getPaymentMethod;
    //
    return service;

    // -----------------------------------------------------------------------------------------------------------------

    function _getItemRebateMultiplier(rebatePercentage) {
        return (new Big(100)).minus(rebatePercentage).div(100).toNumber();
    }

    function _getItemTaxMultiplier(taxRatePercentage) {
        return (new Big(taxRatePercentage)).div(100).plus(1).toNumber();
    }


    /**
     * Formiranje cijene na osnovu UPB
     * @param invoice
     * @param item
     * @private
     */
    function recalculateItemBasedOnUPB(invoice, item) {
        let rebatePercentage = item.rabat_procenat === undefined || item.rabat_procenat === null ? 0 : item.rabat_procenat;
        let quantity = item.kolicina === undefined || item.kolicina === null ? 0 : item.kolicina;
        let jedinicna_cijena_osnovna = item.jedinicna_cijena_osnovna === undefined || item.jedinicna_cijena_osnovna === null ? 0 : item.jedinicna_cijena_osnovna;

        let rebate_multiplier = _getItemRebateMultiplier(rebatePercentage);
        let tax_multiplier = _getItemTaxMultiplier(item.porez_procenat);

        item.izvor_kalkulacije = IZVOR_KALKULACIJE_UPB;

        item.jedinicna_cijena_rabatisana = (new Big(jedinicna_cijena_osnovna)).times(rebate_multiplier).round(PRECISION).toNumber();
        item.jedinicna_cijena_puna = (new Big(jedinicna_cijena_osnovna)).times(tax_multiplier).round(PRECISION).toNumber();
        item.jedinicna_cijena_prodajna = (new Big(item.jedinicna_cijena_rabatisana)).times(tax_multiplier).round(PRECISION).toNumber();

        item.ukupna_cijena_rabatisana = (new Big(jedinicna_cijena_osnovna)).times(rebate_multiplier).times(quantity).round(PRECISION).toNumber();
        item.porez_iznos = (new Big(item.ukupna_cijena_rabatisana)).times(item.porez_procenat).div(100).round(PRECISION).toNumber();
        item.ukupna_cijena_prodajna = (new Big(item.ukupna_cijena_rabatisana)).plus(item.porez_iznos).round(PRECISION).toNumber();

        item.ukupna_cijena_puna = (new Big(item.ukupna_cijena_prodajna)).div(rebate_multiplier).round(PRECISION).toNumber();
        item.rabat_iznos_prodajni = (new Big(item.ukupna_cijena_puna)).minus(item.ukupna_cijena_prodajna).round(PRECISION).toNumber();

        item.ukupna_cijena_osnovna = (new Big(jedinicna_cijena_osnovna)).times(quantity).round(PRECISION).toNumber();
        item.rabat_iznos_osnovni = (new Big(item.ukupna_cijena_osnovna)).minus(item.ukupna_cijena_rabatisana).round(PRECISION).toNumber();

        item.tax_exemption_amount = 0;

        item.credit_note_turnover_used = 0;
        item.credit_note_turnover_remaining = item.ukupna_cijena_prodajna;

        service.recalculateTotals(invoice);
        service.recalculateTaxGroups(invoice);
        service.recalculatePaymentMethodTotals(invoice);
    }

    /**
     * Formiranje cijene na osnovu UPA
     * @param invoice
     * @param item
     * @private
     */
    function recalculateItemBasedOnUPA(invoice, item) {
        let rebatePercentage = item.rabat_procenat === undefined || item.rabat_procenat === null ? 0 : item.rabat_procenat;
        let quantity = item.kolicina === undefined || item.kolicina === null ? 0 : item.kolicina;
        let jedinicna_cijena_puna = item.jedinicna_cijena_puna === undefined || item.jedinicna_cijena_puna === null ? 0 : item.jedinicna_cijena_puna;

        let rebate_multiplier = _getItemRebateMultiplier(rebatePercentage);
        let tax_multiplier = _getItemTaxMultiplier(item.porez_procenat);

        item.izvor_kalkulacije = IZVOR_KALKULACIJE_UPA;

        item.jedinicna_cijena_prodajna = (new Big(jedinicna_cijena_puna)).times(rebate_multiplier).round(PRECISION).toNumber();
        item.jedinicna_cijena_rabatisana = (new Big(item.jedinicna_cijena_prodajna)).div(tax_multiplier).round(PRECISION).toNumber();
        item.jedinicna_cijena_osnovna = (new Big(item.jedinicna_cijena_rabatisana)).div(rebate_multiplier).round(PRECISION).toNumber();

        item.ukupna_cijena_prodajna = (new Big(item.jedinicna_cijena_prodajna)).times(quantity).round(PRECISION).toNumber();
        item.ukupna_cijena_rabatisana = (new Big(item.ukupna_cijena_prodajna)).div(tax_multiplier).round(PRECISION).toNumber();
        item.porez_iznos = (new Big(item.ukupna_cijena_prodajna)).minus(item.ukupna_cijena_rabatisana).round(PRECISION).toNumber();

        item.ukupna_cijena_puna = (new Big(jedinicna_cijena_puna)).times(quantity).round(PRECISION).toNumber();
        item.rabat_iznos_prodajni = (new Big(item.ukupna_cijena_puna)).minus(item.ukupna_cijena_prodajna).round(PRECISION).toNumber();

        item.ukupna_cijena_osnovna = (new Big(item.ukupna_cijena_rabatisana)).div(rebate_multiplier).round(PRECISION).toNumber();
        item.rabat_iznos_osnovni = (new Big(item.ukupna_cijena_osnovna)).minus(item.ukupna_cijena_rabatisana).round(PRECISION).toNumber();

        item.tax_exemption_amount = 0;

        item.credit_note_turnover_used = 0;
        item.credit_note_turnover_remaining = item.ukupna_cijena_prodajna;

        service.recalculateTotals(invoice);
        service.recalculateTaxGroups(invoice);
        service.recalculatePaymentMethodTotals(invoice);
    }

    function recalculateItemBasedOnExemption(invoice, item) {
        let rebatePercentage = item.rabat_procenat === undefined || item.rabat_procenat === null ? 0 : item.rabat_procenat;
        let quantity = item.kolicina === undefined || item.kolicina === null ? 0 : item.kolicina;

        let rebate_multiplier = _getItemRebateMultiplier(rebatePercentage);

        item.izvor_kalkulacije = IZVOR_KALKULACIJE_UPB;

        item.jedinicna_cijena_osnovna = (new Big(item.tax_exemption_amount)).round(PRECISION).toNumber();
        item.jedinicna_cijena_rabatisana = (new Big(item.jedinicna_cijena_osnovna)).times(rebate_multiplier).round(PRECISION).toNumber();
        item.jedinicna_cijena_puna = item.jedinicna_cijena_osnovna;
        item.jedinicna_cijena_prodajna = item.jedinicna_cijena_rabatisana;

        item.ukupna_cijena_rabatisana = (new Big(item.jedinicna_cijena_osnovna)).times(rebate_multiplier).times(quantity).round(PRECISION).toNumber();
        item.porez_iznos = 0;
        item.ukupna_cijena_prodajna = item.ukupna_cijena_rabatisana;

        item.ukupna_cijena_puna = (new Big(item.ukupna_cijena_prodajna)).div(rebate_multiplier).round(PRECISION).toNumber();
        item.rabat_iznos_prodajni = (new Big(item.ukupna_cijena_puna)).minus(item.ukupna_cijena_prodajna).round(PRECISION).toNumber();

        item.ukupna_cijena_osnovna = (new Big(item.jedinicna_cijena_osnovna)).times(quantity).round(PRECISION).toNumber();
        item.rabat_iznos_osnovni = (new Big(item.ukupna_cijena_osnovna)).minus(item.ukupna_cijena_rabatisana).round(PRECISION).toNumber();

        item.credit_note_turnover_used = 0;
        item.credit_note_turnover_remaining = item.tax_exemption_amount;

        service.recalculateTotals(invoice);
        service.recalculateTaxGroups(invoice);
        service.recalculatePaymentMethodTotals(invoice);
    }

    function recalculateItem(invoice, item) {
        if (item.porez_procenat === null) {
            service.recalculateItemBasedOnExemption(invoice, item);
            return;
        }

        if (item.izvor_kalkulacije === IZVOR_KALKULACIJE_UPB) {
            service.recalculateItemBasedOnUPB(invoice, item);
            return;
        }

        if (item.izvor_kalkulacije === IZVOR_KALKULACIJE_UPA) {
            service.recalculateItemBasedOnUPA(invoice, item);
            return;
        }

        throw Error('Neispravno polje za tip kalkulacije iznosa stavke.');
    }

    // -----------------------------------------------------------------------------------------------------------------

    function _setInvoiceDateFields(invoice) {
        let currentTime = new Date();

        let taxPeriod = angular.copy(currentTime);
        taxPeriod.setDate(1);
        taxPeriod.setHours(0, 0, 0, 0);

        invoice.datumvalute = angular.copy(currentTime);
        invoice.datum_prometa = angular.copy(currentTime);
        invoice.poreski_period = taxPeriod;
    }

    function setBuyer(invoice, buyer) {
        if (buyer === undefined || buyer === null) {
            invoice.komitent = null;
            invoice.komitent_id = null;
        } else {
            invoice.komitent = angular.copy(buyer);
            invoice.komitent_id = buyer.id;
        }
    }

    function copyToCorrectedFields(invoice) {
        invoice.ukupna_cijena_osnovna = invoice.korigovana_ukupna_cijena_osnovna;
        invoice.ukupna_cijena_prodajna = invoice.korigovana_ukupna_cijena_prodajna;
        invoice.ukupna_cijena_rabatisana = invoice.korigovana_ukupna_cijena_rabatisana;
        invoice.ukupna_cijena_puna = invoice.korigovana_ukupna_cijena_puna;
        invoice.porez_iznos = invoice.korigovani_porez_iznos;
        invoice.rabat_iznos_osnovni = invoice.korigovani_rabat_iznos_osnovni;
        invoice.rabat_iznos_prodajni = invoice.korigovani_rabat_iznos_prodajni;

        for (let ii = 0; ii < invoice.stavke.length; ii++) {
            let invoice_item = invoice.stavke[ii];
            invoice_item.jedinicna_cijena_osnovna = invoice_item.korigovana_jedinicna_cijena_osnovna;
            invoice_item.jedinicna_cijena_rabatisana = invoice_item.korigovana_jedinicna_cijena_rabatisana;
            invoice_item.jedinicna_cijena_puna = invoice_item.korigovana_jedinicna_cijena_puna;
            invoice_item.jedinicna_cijena_prodajna = invoice_item.korigovana_jedinicna_cijena_prodajna;

            invoice_item.ukupna_cijena_osnovna = invoice_item.korigovana_ukupna_cijena_osnovna;
            invoice_item.ukupna_cijena_prodajna = invoice_item.korigovana_ukupna_cijena_prodajna;
            invoice_item.ukupna_cijena_rabatisana = invoice_item.korigovana_ukupna_cijena_rabatisana;
            invoice_item.ukupna_cijena_puna = invoice_item.korigovana_ukupna_cijena_puna;
            invoice_item.porez_iznos = invoice_item.korigovani_porez_iznos;
            invoice_item.rabat_iznos_osnovni = invoice_item.korigovani_rabat_iznos_osnovni;
            invoice_item.rabat_iznos_prodajni = invoice_item.korigovani_rabat_iznos_prodajni;
            invoice_item.tax_exemption_amount = invoice_item.corrected_tax_exemption_amount;
            invoice_item.kolicina = invoice_item.korigovana_kolicina;
        }
    }

    function copyItemsFromAdvanceInvoice(advance_invoice, dest_invoice) {
        for (let ii = 0; ii < advance_invoice.stavke.length; ii++) {
            let newInvoiceItem = angular.copy(advance_invoice.stavke[ii]);
            newInvoiceItem.kolicina = 0;
            newInvoiceItem.advance_invoice_item_index = ii;
            dest_invoice.stavke.push(newInvoiceItem);
            service.recalculateItem(dest_invoice, newInvoiceItem);
        }

        service.recalculateTotals(dest_invoice);
        service.recalculateTaxGroups(dest_invoice);
    }

    function create(paymentMethodTypeId) {
        // frontend only fields: payment_methods_total_amount

        let invoice = {}
        invoice.komitent_id = null;
        invoice.komitent = null;
        invoice.is_cash = null;
        invoice.valuta_id = 50;
        invoice.valuta = fisConfig.valute.find((x) => { return x.id === invoice.valuta_id });
        invoice.kurs_razmjene = 1;

        invoice.payment_methods = [];
        if (paymentMethodTypeId) {
            invoice.payment_methods.push(service.createPaymentMethod(paymentMethodTypeId));
            invoice.is_cash = invoice.payment_methods[0].payment_method_type.is_cash;
        }

        invoice.ukupna_cijena_osnovna = 0;
        invoice.ukupna_cijena_rabatisana = 0;
        invoice.ukupna_cijena_prodajna = 0;
        invoice.ukupna_cijena_puna = 0;
        invoice.porez_iznos = 0;
        invoice.rabat_iznos_osnovni = 0;
        invoice.rabat_iznos_prodajni = 0;
        invoice.tax_exemption_amount = 0;

        invoice.payment_methods_total_amount = 0;
        invoice.payment_methods_total_difference = 0;

        invoice.napomena = fisConfig.user.naplatni_uredjaj.organizaciona_jedinica.settings.default_invoice_note;

        invoice.stavke = [];
        invoice.grupe_poreza = _getTaxGroups();

        _setInvoiceDateFields(invoice);

        return invoice;
    }

    function getInvoiceItem() {
        let item = {};
        item.sifra = 1;
        item.naziv = '';
        item.jedinica_mjere_id = fisConfig.defaultUnit.id;
        item.jedinica_mjere = angular.copy(fisConfig.defaultUnit);
        item.izvor_kalkulacije = IZVOR_KALKULACIJE_UPB;

        item.jedinicna_cijena_osnovna = 0;
        item.jedinicna_cijena_puna = 0;
        item.jedinicna_cijena_rabatisana = 0;
        item.jedinicna_cijena_prodajna = 0;

        item.kolicina = 1;
        item.ukupna_cijena_osnovna = 0;
        item.ukupna_cijena_rabatisana = 0;
        item.ukupna_cijena_prodajna = 0;
        item.ukupna_cijena_puna = 0;

        item.poreska_stopa = angular.copy(fisConfig.defaultTaxRate);
        item.porez_procenat = fisConfig.defaultTaxRate.procenat;
        item.porez_iznos = 0;

        item.rabat_procenat = 0;
        item.rabat_iznos_prodajni = 0;
        item.rabat_iznos_osnovni = 0;

        item.credit_note_turnover_remaining = 0;
        item.credit_note_turnover_used = 0;

        item.tax_exemption_reason_id = null;
        item.tax_exemption_amount = 0;

        item.magacin_zaliha = null;
        item.magacin_zaliha_id = null;

        return item;
    }

    function addBlankItem(invoice) {
        let item = getInvoiceItem();

        invoice.stavke.push(item);
        service.recalculateTaxGroups(invoice);
        service.recalculateTotals(invoice);

        return item;
    }

    function addItemFromItemTemplate(invoice, itemTemplate) {
        let newItem = getInvoiceItem();
        service.updateItemFromItemTemplate(invoice, newItem, itemTemplate);
        invoice.stavke.push(newItem);
        return newItem;
    }

    function updateItemFromItemTemplate(invoice, item, itemTemplate) {
        item.naziv = itemTemplate.artikal.naziv;
        item.jedinica_mjere_id = itemTemplate.artikal.jedinica_mjere_id;
        item.jedinica_mjere = fisConfig.units.find(function(x) { return x.id === itemTemplate.artikal.jedinica_mjere_id; })
        item.jedinicna_cijena_osnovna = itemTemplate.jedinicna_cijena_osnovna;
        item.jedinicna_cijena_puna = itemTemplate.jedinicna_cijena_puna;
        item.porez_procenat = itemTemplate.porez_procenat;
        item.magacin_zaliha_id = itemTemplate.id;
        item.magacin_zaliha = angular.copy(itemTemplate);
        item.izvor_kalkulacije = itemTemplate.izvor_kalkulacije;
        service.recalculateItem(invoice, item);
    }

    function createFromTemplate(invoiceTemplate) {
        let invoice = invoiceTemplate;
        _setInvoiceDateFields(invoiceTemplate);
        return invoice;
    }

    function addPaymentMethodByTypeId(invoice, paymentMethodTypeId) {
        let paymentMethod = service.createPaymentMethod(paymentMethodTypeId);
        invoice.payment_methods.push(paymentMethod);
    }

    function sortPaymentMethodTypes(payment_method_types) {
        payment_method_types.sort(function(a, b) {
            return a.sort_weight - b.sort_weight;
        });
    }

    function sortPaymentMethods(payment_methods) {
        payment_methods.sort(function(a, b) {
            return a.payment_method_type.sort_weight - b.payment_method_type.sort_weight;
        });
    }

    function mergePaymentMethods(a, b) {
        let merged = angular.copy(a);
        for (let ii = 0; ii < b.length; ii++) {
            let c = merged.find(function(x) { return x.payment_method_type_id === b[ii].payment_method_type_id  });
            if (c === undefined) {
                merged.push(b[ii]);
            } else {
                merged[ii].amount += b[ii].amount;
            }
        }

        return merged;
    }

    function createPaymentMethod(paymentMethodTypeId) {
        return {
            payment_method_type: fisConfig.getPaymentMethodById(paymentMethodTypeId),
            payment_method_type_id: paymentMethodTypeId,
            amount: 0,
            advance_invoice: undefined
        }
    }

    function splitAmount(amount, numberOfParts) {
        let equalPart = new Big(amount)
            .div(numberOfParts)
            .round(2)
            .toNumber();

        let parts = [];
        for (let ii = 0; ii < numberOfParts - 1; ii++) {
            parts.push(equalPart);
            amount = new Big(amount).minus(equalPart).toNumber();
        }
        parts.push(amount);

        return parts;
    }

    function distributeEvenlyToPaymentMethods(invoice, payment_methods, distribute_amount) {
        let parts = service.splitAmount(distribute_amount, payment_methods.length);

        for (let ii = 0; ii < payment_methods.length; ii++) {
            payment_methods[ii].amount += parts[ii];
        }

        service.recalculateTotals(invoice);
    }

    function isCash(paymentMethodTypeId) {
        return fisConfig.getPaymentMethodById(paymentMethodTypeId).is_cash;
    }

    function recalculateTotals(invoice) {
        let ukupna_cijena_osnovna = (new Big(0));
        let ukupna_cijena_rabatisana = (new Big(0));
        let ukupna_cijena_prodajna = (new Big(0));
        let ukupna_cijena_puna = (new Big(0));
        let rabat_iznos_prodajni = (new Big(0));
        let rabat_iznos_osnovni = (new Big(0));
        let porez_iznos = (new Big(0));
        let tax_exemption_amount = (new Big(0));

        for (let ii = 0; ii < invoice.stavke.length; ii++) {
            ukupna_cijena_osnovna = ukupna_cijena_osnovna.plus(invoice.stavke[ii].ukupna_cijena_osnovna);
            ukupna_cijena_rabatisana = ukupna_cijena_rabatisana.plus(invoice.stavke[ii].ukupna_cijena_rabatisana);
            ukupna_cijena_prodajna = ukupna_cijena_prodajna.plus(invoice.stavke[ii].ukupna_cijena_prodajna);
            ukupna_cijena_puna = ukupna_cijena_puna.plus(invoice.stavke[ii].ukupna_cijena_puna);
            rabat_iznos_prodajni = rabat_iznos_prodajni.plus(invoice.stavke[ii].rabat_iznos_prodajni);
            rabat_iznos_osnovni = rabat_iznos_osnovni.plus(invoice.stavke[ii].rabat_iznos_osnovni);
            porez_iznos = porez_iznos.plus(invoice.stavke[ii].porez_iznos);
            tax_exemption_amount = tax_exemption_amount.plus(invoice.stavke[ii].tax_exemption_amount);
        }

        invoice.ukupna_cijena_osnovna = ukupna_cijena_osnovna.toNumber();
        invoice.ukupna_cijena_rabatisana = ukupna_cijena_rabatisana.toNumber();
        invoice.ukupna_cijena_prodajna = ukupna_cijena_prodajna.toNumber();
        invoice.ukupna_cijena_puna = ukupna_cijena_puna.toNumber();
        invoice.rabat_iznos_prodajni = rabat_iznos_prodajni.toNumber();
        invoice.rabat_iznos_osnovni = rabat_iznos_osnovni.toNumber();
        invoice.porez_iznos = porez_iznos.toNumber();
        invoice.tax_exemption_amount = tax_exemption_amount.toNumber();
    }

    function recalculatePaymentMethodTotals(invoice, autodistribute) {
        let ukupna_cijena_prodajna = new Big(invoice.ukupna_cijena_prodajna);

        if (angular.isUndefined(autodistribute)) {
            autodistribute = true;
        }

        if (autodistribute
            && invoice.payment_methods.length === 1
            && invoice.payment_methods[0].payment_method_type_id !== PAYMENT_METHOD_TYPE_ADVANCE) {
            invoice.payment_methods[0].amount = ukupna_cijena_prodajna.toNumber();
            invoice.payment_methods_total_difference = 0;
            invoice.payment_method_total_amount = ukupna_cijena_prodajna.toNumber();
            return;
        }

        let payment_methods_total_amount = new Big(0);
        for (let ii = 0; ii < invoice.payment_methods.length; ii++) {
            payment_methods_total_amount = payment_methods_total_amount
                .plus(invoice.payment_methods[ii].amount || 0);
        }

        invoice.payment_methods_total_difference = (new Big(ukupna_cijena_prodajna))
            .minus(payment_methods_total_amount)
            .toNumber();
        invoice.payment_methods_total_amount = payment_methods_total_amount
            .toNumber();
    }

    function _getTaxGroups() {
        let taxGroups = [21, 7, 0].map(function (taxRate) {
            return {
                broj_stavki: 0,
                ukupna_cijena_osnovna: 0,
                ukupna_cijena_rabatisana: 0,
                ukupna_cijena_puna: 0,
                ukupna_cijena_prodajna: 0,
                porez_procenat: taxRate,
                porez_iznos: 0,
                rabat_iznos_osnovni: 0,
                rabat_iznos_prodajni: 0,
                credit_note_turnover_remaining: 0,
                credit_note_turnover_used: 0,
                tax_exemption_reason_id: 0,
                tax_exemption_amount: 0
            };
        });

        let exemptionGroups = fisConfig.tax_exemption_reasons.map(function(exemptionReason) {
            return {
                broj_stavki: 0,
                ukupna_cijena_osnovna: 0,
                ukupna_cijena_rabatisana: 0,
                ukupna_cijena_puna: 0,
                ukupna_cijena_prodajna: 0,
                porez_procenat: null,
                porez_iznos: 0,
                rabat_iznos_osnovni: 0,
                rabat_iznos_prodajni: 0,
                credit_note_turnover_remaining: 0,
                credit_note_turnover_used: 0,
                tax_exemption_reason_id: exemptionReason.id,
                tax_exemption_reason: exemptionReason,
                tax_exemption_amount: 0
            }
        });

        return taxGroups.concat(exemptionGroups);
    }

    function recalculateTaxGroups(invoice) {
        for (let ii = 0; ii < invoice.grupe_poreza.length; ii++) {
            let taxGroup = invoice.grupe_poreza[ii];
            taxGroup.broj_stavki = 0;
            taxGroup.ukupna_cijena_osnovna = new Big(0);
            taxGroup.ukupna_cijena_rabatisana = new Big(0);
            taxGroup.ukupna_cijena_puna = new Big(0);
            taxGroup.ukupna_cijena_prodajna = new Big(0);
            taxGroup.porez_iznos = new Big(0);
            taxGroup.rabat_iznos_osnovni = new Big(0);
            taxGroup.rabat_iznos_prodajni = new Big(0);
            taxGroup.credit_note_turnover_remaining = new Big(0);
            taxGroup.credit_note_turnover_used = new Big(0);
            taxGroup.tax_exemption_amount = new Big(0);
        }

        invoice.stavke.forEach(function (stavka) {
            let taxGroup = invoice.grupe_poreza.find(function (x) {
                if (x.porez_procenat === null) {
                    return x.porez_procenat === stavka.porez_procenat
                        && x.tax_exemption_reason_id === stavka.tax_exemption_reason_id;
                } else {
                    return x.porez_procenat === stavka.porez_procenat;
                }
            });

            if (stavka.porez_procenat === null && (taxGroup === undefined || taxGroup === null)) {
                return;
            }

            taxGroup.broj_stavki += 1;
            taxGroup.ukupna_cijena_osnovna = taxGroup.ukupna_cijena_osnovna.plus(stavka.ukupna_cijena_osnovna);
            taxGroup.ukupna_cijena_rabatisana = taxGroup.ukupna_cijena_rabatisana.plus(stavka.ukupna_cijena_rabatisana);
            taxGroup.ukupna_cijena_puna = taxGroup.ukupna_cijena_puna.plus(stavka.ukupna_cijena_puna);
            taxGroup.ukupna_cijena_prodajna = taxGroup.ukupna_cijena_prodajna.plus(stavka.ukupna_cijena_prodajna);
            taxGroup.porez_iznos = taxGroup.porez_iznos.plus(stavka.porez_iznos);
            taxGroup.rabat_iznos_osnovni = taxGroup.rabat_iznos_osnovni.plus(stavka.rabat_iznos_osnovni);
            taxGroup.rabat_iznos_prodajni = taxGroup.rabat_iznos_prodajni.plus(stavka.rabat_iznos_prodajni);
            taxGroup.credit_note_turnover_remaining = taxGroup.credit_note_turnover_remaining.plus(stavka.credit_note_turnover_remaining);
            taxGroup.credit_note_turnover_used = taxGroup.credit_note_turnover_used.plus(stavka.credit_note_turnover_used);
            taxGroup.tax_exemption_amount = taxGroup.tax_exemption_amount.plus(stavka.tax_exemption_amount);
        });

        for (let ii = 0; ii < invoice.grupe_poreza.length; ii++) {
            let taxGroup = invoice.grupe_poreza[ii];
            taxGroup.ukupna_cijena_osnovna = taxGroup.ukupna_cijena_osnovna.round(PRECISION).toNumber();
            taxGroup.ukupna_cijena_rabatisana = taxGroup.ukupna_cijena_rabatisana.round(PRECISION).toNumber();
            taxGroup.ukupna_cijena_puna = taxGroup.ukupna_cijena_puna.round(PRECISION).toNumber();
            taxGroup.ukupna_cijena_prodajna = taxGroup.ukupna_cijena_prodajna.round(PRECISION).toNumber();
            taxGroup.porez_iznos = taxGroup.porez_iznos.round(PRECISION).toNumber();
            taxGroup.rabat_iznos_osnovni = taxGroup.rabat_iznos_osnovni.round(PRECISION).toNumber();
            taxGroup.rabat_iznos_prodajni = taxGroup.rabat_iznos_prodajni.round(PRECISION).toNumber();
            taxGroup.credit_note_turnover_remaining = taxGroup.credit_note_turnover_remaining.round(PRECISION).toNumber();
            taxGroup.credit_note_turnover_used = taxGroup.credit_note_turnover_used.round(PRECISION).toNumber();
            taxGroup.tax_exemption_amount = taxGroup.tax_exemption_amount.round(PRECISION).toNumber();
        }
    }

    function createCorrectiveInvoice(original_invoice) {
        let corrective_invoice = {};
        corrective_invoice.stavke = {};
        corrective_invoice.payment_methods = angular.copy(original_invoice.payment_methods);
        corrective_invoice.grupe_poreza = _getTaxGroups();
        return corrective_invoice;
    }

    function getCorrectiveInvoiceFromDiff(original_invoice, updated_invoice, corrective_invoice) {
        corrective_invoice.stavke = [];

        for (let ii = 0; ii < original_invoice.stavke.length; ii++) {
            service.updateCorrectiveInvoiceItemsFromDiff(original_invoice, updated_invoice, corrective_invoice, ii);
        }

        service.recalculateTotals(corrective_invoice);
        service.recalculatePaymentMethodTotals(corrective_invoice);
        service.recalculateTaxGroups(corrective_invoice);

        return corrective_invoice;
    }


    function updateCorrectiveInvoiceItemsFromDiff(original_invoice, updated_invoice, corrective_invoice, index) {
        let original = original_invoice.stavke[index];
        let updated = updated_invoice.stavke[index];

        service.recalculateItem(updated_invoice, updated);

        if (updated.kolicina !== original.kolicina) {
            let c1 = {};
            c1.izvor_kalkulacije = original.izvor_kalkulacije;
            c1.kolicina = updated.kolicina - original.kolicina;
            c1.jedinicna_cijena_osnovna = original.jedinicna_cijena_osnovna;
            c1.jedinicna_cijena_puna = original.jedinicna_cijena_puna;
            c1.tax_exemption_amount = original.tax_exemption_amount;
            c1.porez_procenat = original.porez_procenat;
            c1.rabat_procenat = original.rabat_procenat;
            c1.tax_exemption_reason_id = original.tax_exemption_reason_id;
            c1.corrected_invoice_item_id = original.id;
            c1.correction_type_id = CORRECTION_TYPE_QUANTITY;
            c1.magacin_zaliha = original.magacin_zaliha;
            c1.magacin_zaliha_id = original.magacin_zaliha_id;
            c1.naziv = original.naziv + ' - korekcija količine';
            c1.sifra = original.sifra;
            c1.jedinica_mjere = original.jedinica_mjere;
            c1.jedinica_mjere_id = original.jedinica_mjere_id;
            corrective_invoice.stavke.push(c1);
            service.recalculateItem(corrective_invoice, c1);
        }

        let correction_type_id = undefined;
        if (updated.porez_procenat === undefined || updated.porez_procenat === null) {
            if (updated.tax_exemption_amount !== original.tax_exemption_amount) {
                correction_type_id = CORRECTION_TYPE_TAX_FREE_AMOUNT;
            }
        } else {
            if (updated.izvor_kalkulacije === IZVOR_KALKULACIJE_UPA) {
                if (updated.jedinicna_cijena_puna !== original.jedinicna_cijena_puna) {
                    correction_type_id = CORRECTION_TYPE_UPA;
                }
            } else if (updated.izvor_kalkulacije === IZVOR_KALKULACIJE_UPB) {
                if (updated.jedinicna_cijena_osnovna !== original.jedinicna_cijena_osnovna) {
                    correction_type_id = CORRECTION_TYPE_UPB;
                }
            } else {
                throw Error('Invalid invoice item price calculation type');
            }
        }

        if (correction_type_id !== undefined) {
            let c2 = {};
            c2.izvor_kalkulacije = original.izvor_kalkulacije;
            c2.corrected_invoice_item_id = original.id;
            c2.porez_procenat = original.porez_procenat;
            c2.rabat_procenat = original.rabat_procenat;
            c2.tax_exemption_reason_id = original.tax_exemption_reason_id;
            c2.magacin_zaliha = original.magacin_zaliha;
            c2.magacin_zaliha_id = original.magacin_zaliha_id;
            c2.naziv = original.naziv + " - korekcija cijene";
            c2.jedinica_mjere = original.jedinica_mjere;
            c2.jedinica_mjere_id = original.jedinica_mjere_id;
            c2.sifra = original.sifra;

            if (correction_type_id === CORRECTION_TYPE_TAX_FREE_AMOUNT) {
                let tax_exemption_amount = (new Big(updated.tax_exemption_amount))
                    .minus(original.tax_exemption_amount)
                    .toNumber();
                c2.kolicina = (new Big(updated.kolicina))
                    .times(tax_exemption_amount < 0 ? -1 : 1)
                    .toNumber();
                c2.tax_exemption_amount = Math.abs(tax_exemption_amount);
                c2.correction_type_id = CORRECTION_TYPE_TAX_FREE_AMOUNT;
            } else if (correction_type_id === CORRECTION_TYPE_UPA) {
                let new_upa = (new Big(updated.jedinicna_cijena_puna))
                    .minus(original.jedinicna_cijena_puna)
                    .toNumber();
                c2.kolicina = (new Big(updated.kolicina))
                    .times(new_upa < 0 ? -1 : 1)
                    .toNumber();
                c2.jedinicna_cijena_puna = Math.abs(new_upa);
                c2.correction_type_id = CORRECTION_TYPE_UPA;
            } else if (correction_type_id === CORRECTION_TYPE_UPB) {
                let new_upb = (new Big(updated.jedinicna_cijena_osnovna))
                    .minus(original.jedinicna_cijena_osnovna)
                    .toNumber();
                c2.kolicina = (new Big(updated.kolicina))
                    .times(new_upb < 0 ? -1 : 1)
                    .toNumber();
                c2.jedinicna_cijena_osnovna = Math.abs(new_upb);
                c2.correction_type_id = CORRECTION_TYPE_UPB;
            }

            corrective_invoice.stavke.push(c2);
            service.recalculateItem(corrective_invoice, c2);
        }
    }

    function recalculateInvoiceItemTemplate(invoiceTemplate) {
        if (invoiceTemplate.izvor_kalkulacije === IZVOR_KALKULACIJE_UPB) {
            recalculateInvoiceItemTemplateFromUPB(invoiceTemplate);
            return;
        }

        if (invoiceTemplate.izvor_kalkulacije === IZVOR_KALKULACIJE_UPA) {
            recalculateInvoiceItemTemplateFromUPA(invoiceTemplate);
            return;
        }

        throw Error('Neispravno polje za tip kalkulacije iznosa stavke.');
    }

    function recalculateInvoiceItemTemplateFromUPB(invoiceTemplate) {
        invoiceTemplate.izvor_kalkulacije = IZVOR_KALKULACIJE_UPB;
        let tax_multiplier = _getItemTaxMultiplier(invoiceTemplate.porez_procenat ? invoiceTemplate.porez_procenat : 0);
        invoiceTemplate.jedinicna_cijena_puna = (new Big(invoiceTemplate.jedinicna_cijena_osnovna)).times(tax_multiplier).round(PRECISION).toNumber();
    }

    function recalculateInvoiceItemTemplateFromUPA(invoiceTemplate) {
        invoiceTemplate.izvor_kalkulacije = IZVOR_KALKULACIJE_UPA;
        let tax_multiplier = _getItemTaxMultiplier(invoiceTemplate.porez_procenat ? invoiceTemplate.porez_procenat : 0);
        invoiceTemplate.jedinicna_cijena_osnovna = (new Big(invoiceTemplate.jedinicna_cijena_puna)).div(tax_multiplier).round(PRECISION).toNumber();
    }

    function setCorrectedInvoiceReference(invoice, $model) {
        invoice.correctedInvoiceReference = {
            type: 'invoice',
            id: $model.id,
            invoice: $model
        }
    }

    function setCorrectedCreditNoteReference(invoice, $model) {
        invoice.correctedInvoiceReference = {
            type: 'credit_note',
            creditNoteId: $model.id,
            creditNote: $model
        }

        invoice.komitent_id = $model.buyer.id;
        invoice.komitent = {};
        invoice.komitent.naziv = $model.buyer.name;
        invoice.komitent.grad = $model.buyer.city;
        invoice.komitent.adresa = $model.buyer.address;
        invoice.komitent.drzava = $model.buyer.country.id;
        invoice.komitent.identifikaciona_oznaka = $model.buyer.identificationNumber;
        invoice.komitent.tip_identifikacione_oznake = {};
        invoice.komitent.tip_identifikacione_oznake_id = $model.buyer.identificationType.id;
        invoice.komitent.tip_identifikacione_oznake.id = $model.buyer.identificationType.id;
        invoice.komitent.tip_identifikacione_oznake.naziv = $model.buyer.identificationType.description;
    }

    function getPaymentMethod(paymentMethodId) {
        return fisConfig.payment_method_types.find((x) => {
            return x.id === paymentMethodId;
        });
    }
}
