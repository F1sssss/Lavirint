angular
    .module('app')
    .controller('DepozitController', depozitController);

depozitController.$inject = ['$stateParams', '$timeout', 'fisGui', 'fisModal', 'api', 'initialData'];

function depozitController($stateParams, $timeout, fisGui, fisModal, api, initialData) {
    let ctrl = this;

    if ($stateParams['#']) {
        $timeout(function () {
            $('#' + $stateParams['#']).focus();
        });
    }

    ctrl.stanje = initialData.stanje;

    if (ctrl.stanje.danasnji_depozit !== undefined && ctrl.stanje.danasnji_depozit !== null) {
        ctrl.depositInitialAmount = ctrl.stanje.danasnji_depozit.iznos;
    } else {
        ctrl.depositInitialAmount = 0;
    }
    ctrl.depositWithdrawalAmount = 0;
    ctrl.deposits = initialData.deposits;

    ctrl.postaviDepozit = postaviDepozit;
    ctrl.podigniDepozit = podigniDepozit;

    function postaviDepozit() {
        ctrl.formaPolog.$setSubmitted();
        if (ctrl.formaPolog.$invalid) {
            fisModal.confirm({
                headerText: 'Greška',
                bodyText: 'Ispravite greške pa pokušajte ponovo'
            });
            return
        }

        fisGui.wrapInLoader(function() {
            return api.depozit.polozi({ iznos: ctrl.depositInitialAmount }).then(function (data) {
                return data;
            }).then(function(data) {
                ctrl.deposits = data.deposits;

                if ('greska' in data) {
                    return fisModal.confirm({
                        headerText: 'Greška',
                        headerIcon: 'fa fa-exclamation-triangle text-danger',
                        bodyText: data.greska
                    });
                }

                if (data.deposit.fiskalizacioni_kod === undefined || data.deposit.fiskalizacioni_kod === null) {
                    return fisModal.confirm({
                        headerText: 'Greška',
                        headerIcon: 'fa fa-exclamation-triangle text-danger',
                        bodyText: 'Depozit nije definisan.'
                    });
                }

                return api.stanje.listaj().then(function(dataStanje) {
                    ctrl.stanje = dataStanje;
                    ctrl.depositInitialAmount = data.deposit.iznos;
                    return fisModal.confirm({
                        headerText: 'Prijava depozita',
                        bodyText: 'Polaganje novca je fiskalizovano.'
                    });
                });
            });
        });
    }

    function podigniDepozit() {
        ctrl.formaPodizanje.$setSubmitted();
        if (ctrl.formaPodizanje.$invalid) {
            fisModal.confirm({
                headerText: 'Greška',
                headerIcon: 'fa fa-exclamation-triangle text-danger',
                bodyText: 'Ispravite greške pa pokušajte ponovo'
            });
            return
        }

        fisModal.confirmOrCancel({
            headerText: 'Podizanje novca',
            bodyText: 'Da li ste sigurni da želite da podignete novac?',
            confirmButtonText: 'Da, podigni',
            cancelButtonText: 'Odustani'
        }).then(function (result) {
            fisGui.wrapInLoader(function() {
                if (result.isConfirmed) {
                    return api.depozit.podigni({ iznos: ctrl.depositWithdrawalAmount }).then(function (data) {
                        return {
                            isConfirmed: true,
                            data: data
                        };
                    });
                } else {
                    return {
                        isConfirmed: false
                    }
                }
            }).then(function(result) {
                if (!result.isConfirmed) {
                    return;
                }

                ctrl.depositWithdrawalAmount = 0;
                ctrl.deposits = result.data.deposits;

                if (result.data.deposit.fiskalizacioni_kod === undefined || result.data.deposit.fiskalizacioni_kod === null) {
                    return fisModal.confirm({
                        headerText: 'Greška',
                        headerIcon: 'fa fa-exclamation-triangle text-danger',
                        bodyText: 'Depozit nije definisan.'
                    });
                }

                return fisModal.confirm({
                    headerText: 'Prijava depozita',
                    bodyText: 'Podizanje novca je fiskalizovano.'
                });
            });
        });
    }
}