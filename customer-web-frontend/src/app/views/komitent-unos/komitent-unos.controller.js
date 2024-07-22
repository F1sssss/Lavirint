angular
    .module('app')
    .controller('KomitentUnosController', KomitentUnosController);

KomitentUnosController.$inject = ['$scope', '$state', 'api', 'fisModal', 'fisConfig'];

function KomitentUnosController($scope, $state, api, fisModal, fisConfig) {
    const ctrl = this;

    ctrl.komitent = {
        show_total_debt: false,
        previous_debt: 0,
        drzava: 39
    }
    ctrl.drzave = angular.copy(fisConfig.countries);
    ctrl.tipoviIdentifikacioneOznake = angular.copy(fisConfig.identification_types);

    ctrl.upis = upis;

    $scope.$watch('ctrl.komitent.tip_identifikacione_oznake_id', function(newVal) {
        if (newVal === undefined || newVal === null) {
            ctrl.komitent.identifikaciona_oznaka = null;
        }
    });

    function upis() {
        ctrl.forma.$setSubmitted();
        if (ctrl.forma.$invalid) {
            fisModal.confirm({
                headerText: 'Greška',
                bodyText: 'Ispravite greške pa pokušajte ponovo'
            });
            return
        }

        fisModal.confirmOrCancel({
            headerText: 'Upis podataka',
            bodyText: "Da li ste sigurni da želite da dodate novog partnera?",
            confirmButtonText: 'Da, dodaj',
            cancelButtonText: 'Odustani',
        }).then((result) => {
            if (result.isConfirmed) {
                api.komitent.dodaj(ctrl.komitent).then(function (data) {
                    if (data.greska === 1) {
                        fisModal.confirm({
                            headerText: "Greška",
                            bodyText: "Podaci nijesu upisani."
                        });
                        return;
                    }

                    fisModal.confirm({
                        headerText: "Dodavanje partnera",
                        bodyText: "Novi partner je upisan."
                    }).then(function () {
                        $state.go('komitent-pregled-lista', {
                            broj_stavki_po_stranici: 10,
                            broj_stranice: 1
                        });
                    });
                });
            }
        });
    }
}