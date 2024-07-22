angular
    .module('app')

    .directive('invoiceCard', invoiceCard);

invoiceCard.$inject = ['$state', 'api', 'stampac', 'fisModal', 'fisGui', 'fisConfig'];

function invoiceCard($state, api, stampac, fisModal, fisGui, fisConfig) {
    return {
        restrict: 'E',
        replace: true,
        link: link,
        templateUrl: 'app/directives/invoice-card/invoice-card.template.html',
        scope: {
            invoice: '=',
            mode: '=',
            onCancellation: '&'
        }
    }

    function link($scope, $element, $attrs) {
        $scope.options = {};

        $scope.stampac = stampac;

        $scope.showCijena = true;
        $scope.showPaymentMethods = true;
        $scope.showKomitent = true;
        $scope.showEmail = true;
        $scope.showPrometZaKnjizno = false;
        $scope.showUpload = $attrs.uploadEnabled === 'false';

        $scope.corrective_invoices = $scope.invoice.korektivne_fakture.filter(invoice => invoice.status === 2);

        $scope.upload = function(file) {
            let fakturaId = $scope.invoice.id;

            api.faktura.poId.dokument.upload(fakturaId, file).then(function() {
                stampac.stampajDokument(fakturaId);
                $scope.invoice.ima_dokument = true;
            });
        }

        $scope.cancel = function storniraj() {
            fisModal.confirmOrCancel({
                headerText: 'Storiranje računa',
                bodyText: 'Da li ste sigurni da želite da stornirate račun?',
                confirmButtonText: 'Da, storniraj',
                cancelButtonText: 'Odustani'
            }).then(function (result) {
                if (!result.isConfirmed) {
                    return;
                }

                fisGui.wrapInLoader(function() {
                    return api.faktura.storniraj($scope.invoice.id).then(function (data) {
                        if (data.result.is_success) {

                            return stampac.stampajFakturu(
                                data.invoice.id,
                                fisConfig.user.podesavanja_aplikacije.podrazumijevani_tip_stampe
                            ).then(function() {
                                return $state.transitionTo($state.current, { broj_stranice: 1 }, {
                                    reload: true, inherit: false
                                });
                            });
                        } else {
                            return fisModal.confirm({
                                headerText: 'Grеška',
                                bodyText: data.result.message,
                                confirmButtonText: 'U redu'
                            });
                        }
                    });
                });
            });
        }

        $scope.sendMail = function sendMail() {
            fisModal.confirmOrCancel({
                headerText: 'Slanje e-mail-a',
                bodyText:
                    'Kopija računa će biti proslijeđena na adresu <span class="fw-bold">' + $scope.invoice.komitent.email + '</span>. ' +
                    'Da li ste sigurni da želite da pošaljete kopiju?'
            }).then(function(result) {
                if (result.isConfirmed) {
                    fisGui.wrapInLoader(function() {
                        return api.faktura.poId.mail($scope.invoice.id).then(function(data) {
                            if (data.is_success) {
                                return fisModal.confirm({
                                    headerText: 'Uspjeh',
                                    bodyText: data.message
                                });
                            } else {
                                return fisModal.confirm({
                                    headerText: 'Grеška',
                                    bodyText: data.message
                                })
                            }
                        }).finally(function() {
                            $state.reload();
                        });
                    });
                }
            });
        }

        $scope.invoiceScheduleModal = function() {
            fisModal.invoiceScheduleModal($scope.invoice).then(function(result) {
                if (result.isConfirmed) {
                    if (result.invoice_schedule.is_active) {
                        $scope.invoice.active_invoice_schedule = result.invoice_schedule;
                    }
                }
            });
        }
    }
}