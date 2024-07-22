angular
    .module('app')
    .controller('KomitentUnosModalController', KomitentUnosModalController);

KomitentUnosModalController.$inject = ['$uibModalInstance', 'api', 'fisConfig'];

function KomitentUnosModalController($uibModalInstance, api, fisConfig) {
    const ctrl = this;

    ctrl.buyer = {};
    ctrl.buyer.drzava = 39;

    ctrl.drzave = angular.copy(fisConfig.countries);
    ctrl.tipoviIdentifikacioneOznake = angular.copy(fisConfig.identification_types);

    ctrl.sacuvaj = sacuvaj;

    function sacuvaj() {
        ctrl.forma.$setSubmitted();
        if (ctrl.forma.$invalid) {
            return;
        }

        api.komitent.dodaj(ctrl.buyer).then(function(data) {
            $uibModalInstance.close({
                isConfirmed: true,
                komitent: data,
                komitent_id: data.id  // TODO: Should be removed
            });
        });
    }
}