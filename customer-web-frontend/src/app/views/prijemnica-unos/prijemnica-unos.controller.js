angular
    .module('app')
    .controller('PrijemnicaUnosController', PrijemnicaUnosController);

PrijemnicaUnosController.$inject = [
    '$scope', '$rootScope', '$timeout', '$state', '$uibModal', 'api', 'fisModal', 'magacini', 'fisConfig',
    'komitenti', 'artikli'
];

function PrijemnicaUnosController(
    $scope, $rootScope, $timeout, $state, $uibModal, api, fisModal, magacini, fisConfig,
    komitenti, artikli
) {
    const ctrl = this;

    ctrl.prijemnica = {
        magacin_id: fisConfig.user.magacin_id,
        stavke: []
    }

    ctrl.magacini = magacini;
    ctrl.komitenti = komitenti;
    ctrl.artikli = artikli;

    ctrl.dodajStavku = dodajStavku;
    ctrl.obrisiStavku = obrisiStavku;
    ctrl.upis = upis;

    function dodajStavku() {
        if (ctrl.formaStavka.$invalid) {
            ctrl.formaStavka.$setSubmitted();
            fisModal.confirm({
                headerText: 'Greška',
                bodyText: 'Ispravite greške pa pokušajte ponovo'
            });
            return;
        }

        for (let ii = 0; ii < ctrl.prijemnica.stavke.length; ii++) {
            if (ctrl.prijemnica.stavke[ii].artikal_id === ctrl.stavka.artikal.id) {
                fisModal.confirmOrCancel({
                    title: 'Stavka već postoji',
                    text: 'Da li želite da dodate na postojeću količinu?',
                    confirmButtonText: 'Da, saberi količine',
                    cancelButtonText: 'Odustani'
                }).then(function (result) {
                    if (result.isConfirmed) {
                        ctrl.prijemnica.stavke[ii].kolicina += ctrl.stavka.kolicina;
                        ctrl.stavka = {
                            kolicina: 1,
                            artikal: undefined
                        };
                        ctrl.formaStavka.$setPristine();
                        $scope.$apply();
                    }
                });

                return;
            }
        }

        ctrl.prijemnica.stavke.push({
            artikal: ctrl.stavka.artikal,
            artikal_id: ctrl.stavka.artikal.id,
            kolicina: ctrl.stavka.kolicina
        });

        ctrl.stavka = {
            kolicina: 1,
            artikal: undefined
        };

        $timeout(function() {
            ctrl.formaStavka.$setPristine();
        });
    }

    function obrisiStavku(index) {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/prijemnica-stavka-modal/prijemnica-stavka-modal.template.html',
            controller: 'PrijemnicaStavkaModalController',
            controllerAs: 'ctrl',
            size: 'large',
            backdrop: 'static',
            resolve: {
                item: function () {
                    return angular.copy(ctrl.prijemnica.stavke[index]);
                }
            }
        });

        modalInstance.result.then(function (result) {
            if (result.action === 'delete') {
                ctrl.prijemnica.stavke.splice(index, 1);
                return;
            }

            if (result.action === 'save') {
                ctrl.prijemnica.stavke[index] = result.item;
            }
        });
    }

    function upis() {
        if (ctrl.prijemnica.stavke.length === 0) {
            fisModal.confirm({
                headerText: 'Prijemnica je prazna',
                bodyText: 'Unesite stavke prijemnice pa pokušajte ponovo.'
            });
            return;
        }

        ctrl.forma.$setSubmitted();
        if (ctrl.forma.$invalid) {
            fisModal.invalidForm();
            return;
        }

        let requestData = angular.copy(ctrl.prijemnica);
        requestData.datum_ulazne_fakture = moment(requestData.datum_ulazne_fakture).format();

        api.kalkulacija.dodaj(requestData).then(function (data) {
            fisModal.confirm({
                headerText: 'Podaci upisani',
                bodyText: 'Nova prijemnica je sačuvana.'
            }).then(function () {
                $state.go('prijemnica-pregled-lista');
            });
        });
    }
}