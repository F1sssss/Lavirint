angular
    .module('app')
    .controller('KomitentIzmjenaController', KomitentIzmjenaController);

KomitentIzmjenaController.$inject = [
    '$scope', '$state', '$stateParams', 'api', 'fisModal', 'fisConfig', 'komitent'
];

function KomitentIzmjenaController(
    $scope, $state, $stateParams, api, fisModal, fisConfig, komitent
) {
    const ctrl = this;

    ctrl.drzave = angular.copy(fisConfig.countries);
    ctrl.komitent = komitent;
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
            return;
        }

        fisModal.confirmOrCancel({
            headerText: 'Upis podataka',
            bodyText: "Da li ste sigurni da želite da izmijenite podatke partnera?",
            confirmButtonText: 'Da, izmijeni',
            cancelButtonText: 'Odustani',
        }).then((result) => {
            if (result.isConfirmed) {
                api.komitent.poId.izmijeni($stateParams.id, ctrl.komitent).then(function (data) {
                    if (data.greska === 1) {
                        fisModal.confirm({
                            headerText: "Greška",
                            bodyText: "Podaci nijesu upisani."
                        });
                    } else {
                        fisModal.confirm({
                            headerText: "Izmjena partnera",
                            bodyText: "Podaci partnera su izmijenjeni."
                        });
                    }

                    $state.go('komitent-pregled-lista', {
                        broj_stavki_po_stranici: 10,
                        broj_stranice: 1
                    });
                });
            }
        });
    }
}