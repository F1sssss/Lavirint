angular
    .module('app')
    .controller('FakturaKorekcijaController', FakturaKorekcijaController);

FakturaKorekcijaController.$inject = [
    '$rootScope', '$scope', '$state', 'faktura', 'api', 'stampac', 'fisConfig', 'fisGui', 'invoiceFactory', 'fisModal'
];

function FakturaKorekcijaController(
    $rootScope, $scope, $state, faktura, api, stampac, fisConfig, fisGui, invoiceFactory, fisModal
) {
    let ctrl = this;

    ctrl.fisModal = fisModal;

    ctrl.corrective_invoice = null;

    ctrl.original_invoice = angular.copy(faktura);
    invoiceFactory.copyToCorrectedFields(ctrl.original_invoice);

    ctrl.updated_invoice = angular.copy(faktura);
    invoiceFactory.copyToCorrectedFields(ctrl.updated_invoice);

    ctrl.onInvoiceCorrection = onInvoiceCorrection;
    ctrl.onPriceDifferenceChange = onPriceDifferenceChange;
    ctrl.onPaymentMethodTypeaheadSelect = onPaymentMethodTypeaheadSelect;
    ctrl.koriguj = koriguj;

    // -----------------------------------------------------------------------------------------------------------------

    initialize();

    // -----------------------------------------------------------------------------------------------------------------
    function initialize() {
        ctrl.corrective_invoice = invoiceFactory.createCorrectiveInvoice(ctrl.original_invoice);
        invoiceFactory.getCorrectiveInvoiceFromDiff(ctrl.original_invoice, ctrl.updated_invoice, ctrl.corrective_invoice);
        ctrl.corrective_invoice.payment_methods = angular.copy(ctrl.updated_invoice.payment_methods);
        invoiceFactory.recalculatePaymentMethodTotals(ctrl.corrective_invoice);
    }

    function onInvoiceCorrection() {
        ctrl.corrective_invoice = angular.extend(
            ctrl.corrective_invoice,
            invoiceFactory.getCorrectiveInvoiceFromDiff(ctrl.original_invoice, ctrl.updated_invoice, ctrl.corrective_invoice)
        );
    }

    function onPriceDifferenceChange(index) {
        let original = ctrl.original_invoice.stavke[index];
        let updated = ctrl.updated_invoice.stavke[index];
    }

    function onPaymentMethodTypeaheadSelect($item, $model, $label) {
        ctrl.corrective_invoice.payment_methods = invoiceFactory.mergePaymentMethods(ctrl.corrective_invoice.payment_methods, [invoiceFactory.createPaymentMethod($item.id)]);
        invoiceFactory.recalculatePaymentMethodTotals(ctrl.corrective_invoice);
    }

    function koriguj() {
        let isUnchanged = true;

        for (let ii = 0; ii < ctrl.original_invoice.stavke.length; ii++) {
            let original = ctrl.original_invoice.stavke[ii];
            let updated = ctrl.updated_invoice.stavke[ii];

            if (
                !(new Big(original.kolicina)).eq(updated.kolicina)
                || !(new Big(original.jedinicna_cijena_osnovna)).eq(updated.jedinicna_cijena_osnovna)
                || !(new Big(original.jedinicna_cijena_puna)).eq(updated.jedinicna_cijena_puna)
                || !(new Big(original.tax_exemption_amount)).eq(updated.tax_exemption_amount)
            ) {
                isUnchanged = false;
                break;
            }
        }

        if (ctrl.corrective_invoice.payment_methods_total_difference !== 0) {
            fisModal.confirm({
                headerText: 'Greška',
                headerIcon: 'fa fa-exclamation-triangle text-danger',
                bodyText: 'Upisani podaci nisu ispravni. Ispravite greške pa pokušajte ponovo'
            });
            return;
        }

        if (isUnchanged) {
            fisModal.confirm({
                headerText: 'Greška',
                headerIcon: 'fa fa-exclamation-triangle text-danger',
                bodyText: 'Nije izmijenjena nijedna stavka fakture. Napravite promjenu pa pokušajte ponovo.'
            });
            return;
        }

        fisGui.wrapInLoader(function() {
            return api.api__faktura__po_id__koriguj(ctrl.original_invoice.id, ctrl.updated_invoice, ctrl.corrective_invoice).then(function(data) {
                return data;
            });
        }).then(function(data) {
            if (data.is_success) {
                return stampac.stampajFakturu(data.corrective_invoice.id, fisConfig.user.podesavanja_aplikacije.podrazumijevani_tip_stampe).then(function() {
                    return $state.go('faktura_pregled_redovnih', {
                        broj_stavki_po_stranici: 10,
                        broj_stranice: 1
                    });
                });
            } else {
                return fisModal.confirm({
                    headerText: 'Greška',
                    headerIcon: 'fa fa-exclamation-triangle text-danger',
                    bodyText: data.message
                });
            }
        });
    }
}