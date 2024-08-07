angular
    .module('app')
    .controller('FakturaKonacniRacunController', FakturaKonacniRacunController);

FakturaKonacniRacunController.$inject = [
    '$rootScope', '$scope', '$timeout', '$state', 'api', 'invoiceFactory', 'stampac', 'fisConfig', 'fisModal', 'fisGui',
    'initialData'
];

function FakturaKonacniRacunController(
    $rootScope, $scope, $timeout, $state, api, invoiceFactory, stampac, fisConfig, fisModal, fisGui,
    initialData
) {
    const ctrl = this;

    ctrl.tax_exemption_reasons = angular.copy(fisConfig.tax_exemption_reasons);
    ctrl.jediniceMjere = angular.copy(fisConfig.units);
    ctrl.poreskeStope = angular.copy(fisConfig.poreske_stope);
    ctrl.valute = angular.copy(fisConfig.valute);
    ctrl.invoiceFactory = invoiceFactory;
    ctrl.fisModal = fisModal;

    ctrl.payment_method_types = angular.copy(fisConfig.payment_method_types
        .filter((x) => x.id !== PAYMENT_METHOD_TYPE_ADVANCE ));
    ctrl.primary_payment_method = undefined;
    ctrl.advance_payment_method = undefined;

    ctrl.setPaymentMethod = setPaymentMethod;
    ctrl.onCurrencyChange = onCurrencyChange;
    ctrl.addInvoiceItem = addInvoiceItem;
    ctrl.deleteInvoiceItem = deleteInvoiceItem;
    ctrl.resetInvoiceItem = resetInvoiceItem;
    ctrl.onInvoiceItemQuantityChange = onInvoiceItemQuantityChange;

    ctrl.onBuyerSelect = onBuyerSelect;
    ctrl.showBuyerUpdateModal = showBuyerUpdateModal;

    ctrl.createInvoice = createInvoice;
    ctrl.onInvoiceItemTemplateSelect = onInvoiceItemTemplateSelect;
    ctrl.getStavkeLagera = getStavkeLagera;
    ctrl.naPromjenuTipaUnosa = naPromjenuTipaUnosa;
    ctrl.onFocusItemTemplateSearch = onFocusItemTemplateSearch;
    ctrl.onBlurItemTemplateSearch = onBlurItemTemplateSearch;

    ctrl.onItemUpdate = onItemUpdate;
    ctrl.onAdvanceInvoiceCorrection = onAdvanceInvoiceCorrection;

    init();

    //------------------------------------------------------------------------------------------------------------------

    function init() {
        ctrl.original_advance_invoice = angular.copy(initialData.advance_invoice);
        invoiceFactory.copyToCorrectedFields(ctrl.original_advance_invoice);

        ctrl.updated_advance_invoice = initialData.advance_invoice;
        invoiceFactory.copyToCorrectedFields(ctrl.updated_advance_invoice);

        ctrl.corrective_for_advance_invoice = invoiceFactory.createCorrectiveInvoice(ctrl.original_advance_invoice);
        invoiceFactory.getCorrectiveInvoiceFromDiff(
            ctrl.original_advance_invoice,
            ctrl.updated_advance_invoice,
            ctrl.corrective_for_advance_invoice);

        ctrl.racun = invoiceFactory.create();

        ctrl.racun.is_cash = false;

        ctrl.primary_payment_method = invoiceFactory.createPaymentMethod(PAYMENT_METHOD_TYPE_ACCOUNT);
        ctrl.racun.is_cash = ctrl.primary_payment_method.payment_method_type.is_cash;
        ctrl.racun.payment_methods.push(ctrl.primary_payment_method);

        ctrl.advance_payment_method = invoiceFactory.createPaymentMethod(PAYMENT_METHOD_TYPE_ADVANCE);
        ctrl.advance_payment_method.advance_invoice = ctrl.updated_advance_invoice;
        ctrl.advance_payment_method.advance_invoice_id = ctrl.updated_advance_invoice.id;
        ctrl.racun.payment_methods.push(ctrl.advance_payment_method);

        invoiceFactory.copyItemsFromAdvanceInvoice(initialData.advance_invoice, ctrl.racun);
        for (let ii = 0; ii < ctrl.racun.stavke.length; ii++) {
            ctrl.racun.stavke[ii].isDisabled = true;
        }

        updateInvoiceInputTypes();

        ctrl.racun.komitent = ctrl.updated_advance_invoice.komitent;
        ctrl.racun.komitent_id = ctrl.updated_advance_invoice.komitent_id;
    }

    function updateInvoiceInputTypes() {
        for (let ii = 0; ii < ctrl.racun.stavke.length; ii++) {
            if (ctrl.racun.stavke[ii].magacin_zaliha_id) {
                ctrl.racun.stavke[ii].tipUnosa = 'po_artiklu';
                ctrl.racun.stavke[ii].query = ctrl.racun.stavke[ii].magacin_zaliha.artikal.naziv;
            } else {
                ctrl.racun.stavke[ii].tipUnosa = 'slobodan_unos';
            }
        }
    }

    function onInvoiceItemTemplateSelect(index, $item, $model, $label) {
        invoiceFactory.updateItemFromItemTemplate(ctrl.racun, ctrl.racun.stavke[index], $item);
        ctrl.racun.stavke[index].query = ctrl.racun.stavke[index].magacin_zaliha.artikal.naziv;
    }

    function onFocusItemTemplateSearch(index) {
        let item = invoiceFactory.getInvoiceItem();
        item.tipUnosa = ctrl.racun.stavke[index].tipUnosa;
        ctrl.racun.stavke[index] = item;
    }

    function onBlurItemTemplateSearch(index) {
        if (
            ctrl.racun.stavke[index].magacin_zaliha === undefined
            || ctrl.racun.stavke[index].magacin_zaliha === null
        ) {
            let item = invoiceFactory.getInvoiceItem();
            item.tipUnosa = ctrl.racun.stavke[index].tipUnosa;
            ctrl.racun.stavke[index].query = '';
        }
    }

    function getStavkeLagera(pojam_za_pretragu) {
        return api.magacin.poId.zalihe.listaj(fisConfig.user.magacin_id, {
            pojam_za_pretragu: pojam_za_pretragu,
            broj_stranice: 1,
            broj_stavki_po_stranici: 50
        }).then(function (data) {
            return data.stavke;
        });
    }

    function naPromjenuTipaUnosa(index) {
        let item = invoiceFactory.getInvoiceItem()
        item.tipUnosa = ctrl.racun.stavke[index].tipUnosa;

        ctrl.racun.stavke[index] = item;
        invoiceFactory.recalculateTotals(ctrl.racun);
        invoiceFactory.recalculateTaxGroups(ctrl.racun);
        invoiceFactory.recalculatePaymentMethodTotals(ctrl.racun);
    }

    function resetInvoiceItem(index) {
        ctrl.racun.stavke[index] = invoiceFactory.getInvoiceItem();
    }

    function onInvoiceItemQuantityChange(index) {
        let invoiceItem = ctrl.racun.stavke[index];
        ctrl.invoiceFactory.recalculateItem(ctrl.racun, invoiceItem);

        let advance_invoice_item_index = invoiceItem.advance_invoice_item_index;
        if (advance_invoice_item_index >= 0) {
            ctrl.updated_advance_invoice.stavke[advance_invoice_item_index].kolicina =
                (new Big(ctrl.original_advance_invoice.stavke[advance_invoice_item_index].kolicina))
                    .minus(invoiceItem.kolicina)
                    .toNumber();

            onAdvanceInvoiceCorrection(advance_invoice_item_index);
        }
    }

    function _validateBuyer() {
        if (
            ctrl.racun.komitent === null
            || ctrl.racun.komitent === undefined
        ) {
            if (ctrl.racun.is_cash) {
                ctrl.form.komitent_id.$setValidity('required', true);
                ctrl.form.komitent_id.$setUntouched();
                ctrl.form.komitent_id.$setPristine();
            } else {
                ctrl.form.komitent_id.$setValidity('required', false);
            }
        } else {
            if (!ctrl.racun.komitent.tip_identifikacione_oznake_id
                || !ctrl.racun.komitent.identifikaciona_oznaka
                || !ctrl.racun.komitent.adresa
                || !ctrl.racun.komitent.grad
                || !ctrl.racun.komitent.drzava) {
                ctrl.form.komitent_id.$setValidity('nepotpuno', false);
            } else {
                ctrl.form.komitent_id.$setValidity('required', true);
                ctrl.form.komitent_id.$setUntouched();
                ctrl.form.komitent_id.$setPristine();
            }
        }
    }

    function setPaymentMethod() {
        ctrl.primary_payment_method.payment_method_type = fisConfig.payment_method_types.find((x) => {
            return x.id === ctrl.primary_payment_method.payment_method_type_id
        });
        ctrl.racun.is_cash = ctrl.primary_payment_method.payment_method_type.is_cash;
        invoiceFactory.recalculatePaymentMethodTotals(ctrl.racun);
    }

    function onCurrencyChange() {
        ctrl.racun.valuta = ctrl.valute.find(function(x) {
            return x.id === ctrl.racun.valuta_id;
        });

        if (ctrl.racun.valuta_id === 50) {
            ctrl.racun.kurs_razmjene = 1;
        } else {
            ctrl.racun.kurs_razmjene = undefined;
        }
    }

    function addInvoiceItem() {
        let item = invoiceFactory.addBlankItem(ctrl.racun);
        item.tipUnosa = fisConfig.user.podesavanja_aplikacije.podrazumijevani_tip_unosa_stavke_fakture;

        $timeout(function () {
            fisGui.scrollToSelector('#invoice-item-' + (ctrl.racun.stavke.length - 1), -56);
        });
    }

    function deleteInvoiceItem(index) {
        fisModal.confirmOrCancel({
            headerText: 'Brisanje stavke',
            bodyText: "Da li ste sigurni da želite da obrišete stavku?",
            confirmButtonText: 'Da, obriši',
            cancelButtonText: 'Odustani'
        }).then((result) => {
            if (result.isConfirmed) {
                return $timeout(function () {
                    ctrl.racun.stavke.splice(index, 1)

                    if (ctrl.racun.stavke.length === 0) {
                        addInvoiceItem();
                    }
                });
            }
        }).finally(function() {
            fisGui.scrollToSelector('#invoice-item-' + Math.max(0, index - 1), -120);
        });
    }

    function onBuyerSelect(model) {
        ctrl.racun.komitent_id = model.id;
        ctrl.racun.komitent = model;
        _validateBuyer();
    }

    function createInvoice(invoice) {
        _validateBuyer();
        ctrl.form.$setSubmitted();
        if (ctrl.form.$invalid) {
            fisModal.invalidForm().finally(function() {
                fisGui.scrollToNgInvalid(-56 - 20, 260);
            });
            return;
        }

        fisModal.confirmOrCancel({
            headerText: 'Upis računa',
            bodyText: "Da li ste sigurni da želite da fiskalizujete račun?",
            confirmButtonText: 'Da, upiši',
            cancelButtonText: 'Odustani'
        }).then(function(result) {
            if (result.isConfirmed) {
                sendInvoiceData();
            }
        });

        function sendInvoiceData() {
            let podaci = angular.copy(ctrl.racun);
            podaci.datumvalute = moment(podaci.datumvalute).format();
            podaci.datum_prometa = moment(podaci.datum_prometa).format();
            podaci.poreski_period = moment(podaci.poreski_period).format();

            if ((new Big(podaci.payment_methods[0].amount)).eq(0)) {
                podaci.payment_methods.splice(0, 1);
            }

            fisGui.wrapInLoader(function() {
                return api.api__final_invoice__create(
                    podaci,
                    ctrl.updated_advance_invoice,
                    ctrl.corrective_for_advance_invoice
                ).then(function (data) {
                    return data;
                });
            }).then(function(data) {
                if (data.result.is_success) {
                    return stampac.stampajFakturu(
                        data.invoice.id,
                        fisConfig.user.podesavanja_aplikacije.podrazumijevani_tip_stampe
                    ).then(function() {
                        let params = {};
                        params.advance_invoice_id = ctrl.updated_advance_invoice.id;

                        return $state.transitionTo($state.current, params, {
                            reload: true, inherit: false
                        });
                    });
                } else {
                    return fisModal.confirm({
                        headerIcon: 'fa fa-exclamation-circle text-danger',
                        headerText: 'Grеška',
                        bodyText: data.result.message
                    });
                }
            });
        }
    }

    function showBuyerUpdateModal() {
        fisModal.buyerUpdateModal(ctrl.racun.komitent_id).then(function(result) {
            if (result.isConfirmed) {
                ctrl.racun.komitent = result.komitent;
                ctrl.racun.komitent_id = result.komitent.id;
            }
        });
    }

    function onItemUpdate() {
        ctrl.advance_payment_method.amount = (new Big(ctrl.corrective_for_advance_invoice.ukupna_cijena_prodajna))
            .times(-1)
            .toNumber();
        ctrl.primary_payment_method.amount = Math.max(
            0,
            (new Big(ctrl.racun.ukupna_cijena_prodajna)).minus(ctrl.advance_payment_method.amount).toNumber()
        );

        invoiceFactory.recalculatePaymentMethodTotals(ctrl.racun);
    }

    function onAdvanceInvoiceCorrection() {
        ctrl.corrective_for_advance_invoice = angular.extend(
            ctrl.corrective_for_advance_invoice,
            invoiceFactory.getCorrectiveInvoiceFromDiff(
                ctrl.original_advance_invoice,
                ctrl.updated_advance_invoice,
                ctrl.corrective_for_advance_invoice
            )
        )

        ctrl.onItemUpdate();
    }
}