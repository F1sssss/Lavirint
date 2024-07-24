angular
    .module('app')
    .controller('FakturaSlobodanUnosRedovnihController', FakturaSlobodanUnosRedovnihController);

FakturaSlobodanUnosRedovnihController.$inject = [
    '$rootScope', '$scope', '$timeout', '$state', 'api', 'invoiceFactory', 'stampac', 'fisConfig', 'fisModal', 'fisGui',
    'initialData'
];

function FakturaSlobodanUnosRedovnihController(
    $rootScope, $scope, $timeout, $state, api, invoiceFactory, stampac, fisConfig, fisModal, fisGui,
    initialData
) {

    const ctrl = this;

    ctrl.tax_exemption_reasons = angular.copy(fisConfig.tax_exemption_reasons);
    ctrl.jediniceMjere = angular.copy(fisConfig.units);
    ctrl.poreskeStope = angular.copy(fisConfig.poreske_stope);
    ctrl.valute = angular.copy(fisConfig.valute);
    ctrl.invoiceFactory = invoiceFactory;

    ctrl.payment_method_types = angular.copy(fisConfig.payment_method_types.filter((x) => x.id !== PAYMENT_METHOD_TYPE_ADVANCE ));
    ctrl.primary_payment_method = undefined;

    ctrl.setPaymentMethod = setPaymentMethod;
    ctrl.onCurrencyChange = onCurrencyChange;
    ctrl.addInvoiceItem = addInvoiceItem;
    ctrl.deleteInvoiceItem = deleteInvoiceItem;
    ctrl.onInvoiceItemQuantityChange = onInvoiceItemQuantityChange;

    ctrl.createInvoice = createInvoice;
    ctrl.createInvoiceTemplate = createInvoiceTemplate;
    ctrl.createOrder = createOrder;
    ctrl.onInvoiceItemTemplateSelect = onInvoiceItemTemplateSelect;
    ctrl.getStavkeLagera = getStavkeLagera;
    ctrl.naPromjenuTipaUnosa = naPromjenuTipaUnosa;
    ctrl.onFocusItemTemplateSearch = onFocusItemTemplateSearch;
    ctrl.onBlurItemTemplateSearch = onBlurItemTemplateSearch;

    ctrl.onItemUpdate = onItemUpdate;

    init();

    //------------------------------------------------------------------------------------------------------------------

    function init() {
        if (initialData.invoice_template === null || initialData.invoice_template === undefined) {
            ctrl.racun = invoiceFactory.create();

            ctrl.primary_payment_method = invoiceFactory.createPaymentMethod(8);
            ctrl.racun.is_cash = ctrl.primary_payment_method.payment_method_type.is_cash;
            ctrl.racun.payment_methods.push(ctrl.primary_payment_method);

            let item = invoiceFactory.addBlankItem(ctrl.racun);
            item.tipUnosa = fisConfig.user.podesavanja_aplikacije.podrazumijevani_tip_unosa_stavke_fakture;
        } else {
            ctrl.racun = invoiceFactory.createFromTemplate(initialData.invoice_template);
            ctrl.primary_payment_method = ctrl.racun.payment_methods[0];
            ctrl.racun.is_cash = ctrl.primary_payment_method.payment_method_type.is_cash;
            updateInvoiceInputTypes();
        }
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
        if (ctrl.racun.stavke[index].magacin_zaliha === undefined || ctrl.racun.stavke[index].magacin_zaliha === null) {
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

    function onInvoiceItemQuantityChange(index) {
        let invoiceItem = ctrl.racun.stavke[index];
        ctrl.invoiceFactory.recalculateItem(ctrl.racun, invoiceItem);
    }

    function _validateBuyer() {
        if (ctrl.racun.komitent === null || ctrl.racun.komitent === undefined) {
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
            let podaci = getData();

            if ((new Big(podaci.payment_methods[0].amount)).eq(0)) {
                podaci.payment_methods.splice(0, 1);
            }

            fisGui.wrapInLoader(function() {
                return api.api__faktura__dodaj(podaci).then(function (data) {
                    return data;
                });
            }).then(function(data) {
                if (data.result.is_success) {
                    return stampac.stampajFakturu(
                        data.invoice.id,
                        fisConfig.user.podesavanja_aplikacije.podrazumijevani_tip_stampe
                    ).then(function() {
                        let params = {};

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

    function createInvoiceTemplate() {
        _validateBuyer();
        ctrl.form.$setSubmitted();
        if (ctrl.form.$invalid) {
            fisModal.invalidForm().finally(function() {
                fisGui.scrollToNgInvalid(-56 - 20, 260);
            });
            return;
        }

        let podaci = getData();
        api.profaktura.dodaj(podaci).then(function(data) {
            if (data.is_success) {
                return stampac.stampajFakturu(data.invoice.id, 'a4').then(function() {
                    let params = {};

                    return $state.transitionTo($state.current, params, {
                        reload: true, inherit: false
                    });
                });
            } else {
                return fisModal.confirm({
                    headerIcon: 'fa fa-exclamation-circle text-danger',
                    headerText: 'Grеška',
                    bodyText: data.message
                });
            }
        });
    }

    function createOrder() {
        // TODO: ADD LOGIC FOR ORDER
        alert("Order made");
    }

    function getData() {
        let data = {};
        data.is_cash = ctrl.racun.is_cash;
        data.datumvalute = moment(ctrl.racun.datumvalute).format();
        data.poreski_period = moment(ctrl.racun.poreski_period).format();
        data.datum_prometa = moment(ctrl.racun.datum_prometa).format();
        data.napomena = ctrl.racun.napomena;
        data.valuta_id = ctrl.racun.valuta_id;
        data.komitent_id = ctrl.racun.komitent_id;
        data.kurs_razmjene = ctrl.racun.kurs_razmjene;
        data.ukupna_cijena_osnovna = ctrl.racun.ukupna_cijena_osnovna;
        data.ukupna_cijena_rabatisana = ctrl.racun.ukupna_cijena_rabatisana;
        data.ukupna_cijena_puna = ctrl.racun.ukupna_cijena_puna;
        data.ukupna_cijena_prodajna = ctrl.racun.ukupna_cijena_prodajna;
        data.porez_iznos = ctrl.racun.porez_iznos;
        data.rabat_iznos_osnovni = ctrl.racun.rabat_iznos_osnovni;
        data.rabat_iznos_prodajni = ctrl.racun.rabat_iznos_prodajni;
        data.tax_exemption_amount = ctrl.racun.tax_exemption_amount;

        data.stavke = [];
        for (let ii = 0; ii < ctrl.racun.stavke.length; ii++) {
            let oldItem = ctrl.racun.stavke[ii];
            let newItem = {};
            newItem.sifra = oldItem.sifra;
            newItem.naziv = oldItem.naziv;
            newItem.izvor_kalkulacije = oldItem.izvor_kalkulacije;

            newItem.jedinicna_cijena_osnovna = oldItem.jedinicna_cijena_osnovna;
            newItem.jedinicna_cijena_rabatisana = oldItem.jedinicna_cijena_rabatisana;
            newItem.jedinicna_cijena_puna = oldItem.jedinicna_cijena_puna;
            newItem.jedinicna_cijena_prodajna = oldItem.jedinicna_cijena_prodajna;

            newItem.porez_procenat = oldItem.porez_procenat;
            newItem.rabat_procenat = oldItem.rabat_procenat;

            newItem.kolicina = oldItem.kolicina;

            newItem.ukupna_cijena_osnovna = oldItem.ukupna_cijena_osnovna;
            newItem.ukupna_cijena_rabatisana = oldItem.ukupna_cijena_rabatisana;
            newItem.ukupna_cijena_puna = oldItem.ukupna_cijena_puna;
            newItem.ukupna_cijena_prodajna = oldItem.ukupna_cijena_prodajna;
            newItem.porez_iznos = oldItem.porez_iznos;
            newItem.rabat_iznos_osnovni = oldItem.rabat_iznos_osnovni;
            newItem.rabat_iznos_prodajni = oldItem.rabat_iznos_prodajni;
            newItem.tax_exemption_amount = oldItem.tax_exemption_amount;

            newItem.jedinica_mjere_id = oldItem.jedinica_mjere_id;
            newItem.tax_exemption_reason_id = oldItem.tax_exemption_reason_id;
            newItem.magacin_zaliha_id = oldItem.magacin_zaliha_id;
            data.stavke.push(newItem);
        }

        data.grupe_poreza = [];
        for (let ii = 0; ii < ctrl.racun.grupe_poreza.length; ii++) {
            let oldTaxGroup = ctrl.racun.grupe_poreza[ii];
            if (oldTaxGroup.broj_stavki === 0 || oldTaxGroup.ukupna_cijena_prodajna === 0) {
                continue;
            }

            let newTaxGroup = {};
            newTaxGroup.broj_stavki = oldTaxGroup.broj_stavki;
            newTaxGroup.ukupna_cijena_osnovna = oldTaxGroup.ukupna_cijena_osnovna;
            newTaxGroup.ukupna_cijena_rabatisana = oldTaxGroup.ukupna_cijena_rabatisana;
            newTaxGroup.ukupna_cijena_puna = oldTaxGroup.ukupna_cijena_puna;
            newTaxGroup.ukupna_cijena_prodajna = oldTaxGroup.ukupna_cijena_prodajna;
            newTaxGroup.porez_procenat = oldTaxGroup.porez_procenat;
            newTaxGroup.porez_iznos = oldTaxGroup.porez_iznos;
            newTaxGroup.rabat_iznos_osnovni = oldTaxGroup.rabat_iznos_osnovni;
            newTaxGroup.rabat_iznos_prodajni = oldTaxGroup.rabat_iznos_prodajni;
            newTaxGroup.tax_exemption_reason_id = oldTaxGroup.tax_exemption_reason_id;
            newTaxGroup.tax_exemption_amount = oldTaxGroup.tax_exemption_amount;
            data.grupe_poreza.push(newTaxGroup);
        }

        data.payment_methods = [];
        for (let ii = 0; ii < ctrl.racun.payment_methods.length; ii++) {
            let oldPaymentMethod = ctrl.racun.payment_methods[ii];
            let newPaymentMethod = {};
            newPaymentMethod.payment_method_type_id = oldPaymentMethod.payment_method_type_id;
            newPaymentMethod.amount = oldPaymentMethod.amount;
            data.payment_methods.push(newPaymentMethod);
        }

        return data;
    }

    function onItemUpdate() {
        invoiceFactory.recalculatePaymentMethodTotals(ctrl.racun);
    }
}