angular
    .module('app')
    .controller('FakturaPosUnosController', FakturaPosUnosController);

FakturaPosUnosController.$inject = [
    '$rootScope', '$scope', '$state', '$timeout', '$uibModal', 'api', 'stampac', 'invoiceFactory', 'fisModal',
    'fisConfig', 'fisGui'
];

function FakturaPosUnosController(
    $rootScope, $scope, $state, $timeout, $uibModal, api, stampac, invoiceFactory, fisModal,
    fisConfig, fisGui
) {
    const ctrl = this;

    ctrl.fisModal = fisModal;

    ctrl.racun = invoiceFactory.create();

    ctrl.typeaheadDesktopState = {};
    ctrl.typeaheadMobileState = {};

    $timeout(function () {
        $('.invoice-item-input input').focus();
    });

    ctrl.updateTypeaheadMobileState = function(data) {
        ctrl.typeaheadMobileState = angular.extend(ctrl.typeaheadMobileState, data);
    }
    ctrl.updateTypeaheadDesktopState = function(data) {
        ctrl.typeaheadDesktopState = angular.extend(ctrl.typeaheadDesktopState, data);
    }
    ctrl.addInvoiceItem = addInvoiceItem;
    ctrl.editInvoiceItem = editInvoiceItem;
    ctrl.upis = upis;
    ctrl.porudzbina = porudzbina;

    function addInvoiceItem($data, $eventType) {
        let index = null;
        for (let ii = 0; ii < ctrl.racun.stavke.length; ii++) {
            if (ctrl.racun.stavke[ii].magacin_zaliha.artikal_id === $data.magacin_zaliha.artikal.id) {
                index = ii;
            }
        }

        if (index === null) {
            let item = invoiceFactory.addItemFromItemTemplate(ctrl.racun, $data.magacin_zaliha);
            item.kolicina = $data.kolicina;
            invoiceFactory.recalculateItem(ctrl.racun, item);
            invoiceFactory.recalculateTaxGroups(ctrl.racun);
            invoiceFactory.recalculateTotals(ctrl.racun);

            index = ctrl.racun.stavke.length - 1

            if ($eventType === 'doubleClick') {
                fisModal.invoiceItemEdit(ctrl.racun, index).then(function(data) {
                    if (data.action === 'delete') {
                        return;
                    }

                    highlightItem(index);
                });
            } else {
                highlightItem(index);
            }
        } else {
            fisModal.invoiceItemEdit(ctrl.racun, index).then(function(data) {
                if (data.action === 'delete') {
                    return;
                }

                highlightItem(index);
            });
        }


    }

    function highlightItem(index) {
        $timeout(function() {
            let desktopScrollContainer = angular.element('#desktop-invoice-item-scroll-container');
            let desktopItem = angular.element('#desktop-invoice-item-tbody tr:eq(' + index + ')');

            let mobileScrollContainer = angular.element('#mobile-invoice-item-scroll-container');
            let mobileItem = angular.element('#mobile-invoice-item-tbody tr:eq(' + index + ')');

            desktopScrollContainer[0].scrollTop = desktopItem[0].offsetTop;
            desktopItem.removeClass('bg-white').addClass('bg-warning-light');

            mobileScrollContainer[0].scrollTop = mobileItem[0].offsetTop;
            mobileItem.removeClass('bg-white').addClass('bg-warning-light');
        }, 0);

        $timeout(function() {
            let desktopItem = angular.element('#desktop-invoice-item-tbody tr:eq(' + index + ')');
            let mobileItem = angular.element('#mobile-invoice-item-tbody tr:eq(' + index + ')');


            desktopItem.addClass('bg-white').removeClass('bg-warning-light');
            mobileItem.addClass('bg-white').removeClass('bg-warning-light');
        }, 500);
    }

    function editInvoiceItem(index) {
        return fisModal.invoiceItemEdit(ctrl.racun, index).then(function(data) {
            if (!data.isConfirmed || data.action === 'delete') {
                return;
            }

            highlightItem(index);
        });
    }

    function upis(paymentMethodTypeId) {
        if (ctrl.racun.stavke.length === 0) {
            fisModal.confirm({
                headerText: 'Račun je prazan',
                headerIcon: 'fa fa-exclamation-triangle text-danger',
                bodyText: 'Dodajte stavke pa probajte ponovo.'
            });
            return;
        }

        if (paymentMethodTypeId === 8 && !ctrl.racun.komitent_id) {
            ctrl.fisModal.invoiceBuyerSelectModal(ctrl.racun);
            return;
        }

        let podaci = angular.copy(ctrl.racun);

        podaci.is_cash = fisConfig.getPaymentMethodById(paymentMethodTypeId).is_cash;
        podaci.payment_methods = [invoiceFactory.createPaymentMethod(paymentMethodTypeId)];

        let currentTime = new Date();

        podaci.poreski_period = angular.copy(currentTime);
        podaci.poreski_period.setDate(1);
        podaci.poreski_period.setHours(0, 0, 0, 0);
        podaci.poreski_period = moment(podaci.poreski_period).format()

        podaci.datumfakture = moment(podaci.datumfakture).format()

        podaci.datumvalute = angular.copy(currentTime);
        podaci.datumvalute = moment(podaci.datumvalute).format();

        fisGui.wrapInLoader(function() {
            return api.api__faktura__dodaj(podaci).then(function (data) {
                if (data.result.is_success) {
                    return stampac.stampajFakturu(
                        data.invoice.id,
                        fisConfig.user.podesavanja_aplikacije.podrazumijevani_tip_stampe
                    );
                } else {
                    return fisModal.confirm({
                        headerText: 'Grеška prilikom fiskalizacije',
                        headerIcon: 'fa fa-exclamation-triangle text-danger',
                        bodyText: data.result.message
                    });
                }
            }).catch(() => {
                return fisModal.confirm({
                    headerText: 'Greška',
                    headerIcon: 'fa fa-exclamation-triangle text-danger',
                    bodyText: 'Došlo je do nepredviđene greške. Kontaktirajte administratore sistema.'
                });
            });
        }).finally(function() {
            $state.reload();
        });
    }


    function porudzbina() {
        if (ctrl.racun.stavke.length === 0) {
            fisModal.confirm({
                headerText: 'Porudžbina je prazna',
                headerIcon: 'fa fa-exclamation-triangle text-danger',
                bodyText: 'Dodajte stavke pa probajte ponovo.'
            });
            return;
        }

        let podaci = angular.copy(ctrl.racun);
        
        podaci.is_cash = false;

        let currentTime = new Date();

        podaci.poreski_period = angular.copy(currentTime);
        podaci.poreski_period.setDate(1);
        podaci.poreski_period.setHours(0, 0, 0, 0);
        podaci.poreski_period = moment(podaci.poreski_period).format()

        podaci.datumfakture = moment(podaci.datumfakture).format()

        podaci.datumvalute = angular.copy(currentTime);
        podaci.datumvalute = moment(podaci.datumvalute).format();

        fisGui.wrapInLoader(function() {
            return api.api__order__create(podaci).then(function (data) {
                if (data.result.is_success) {
                    return stampac.stampajFakturu(
                        data.invoice.id,
                        fisConfig.user.podesavanja_aplikacije.podrazumijevani_tip_stampe
                    );
                } else {
                    return fisModal.confirm({
                        headerText: 'Grеška prilikom kreiranja',
                        headerIcon: 'fa fa-exclamation-triangle text-danger',
                        bodyText: data.result.message
                    });
                }
            }).catch(() => {
                return fisModal.confirm({
                    headerText: 'Greška',
                    headerIcon: 'fa fa-exclamation-triangle text-danger',
                    bodyText: 'Došlo je do nepredviđene greške. Kontaktirajte administratore sistema.'
                });
            });
        }).finally(function() {
            $state.reload();
        });
    }
}
