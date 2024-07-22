angular
    .module('app')
    .controller('KomitentIzmjenaModalController', KomitentIzmjenaModalController);

KomitentIzmjenaModalController.$inject = ['$uibModalInstance', 'api', 'fisConfig', 'komitent'];

function KomitentIzmjenaModalController($uibModalInstance, api, fisConfig, komitent) {
    const ctrl = this;

    ctrl.buyer = komitent;
    ctrl.drzave = angular.copy(fisConfig.countries);
    ctrl.tipoviIdentifikacioneOznake = angular.copy(fisConfig.identification_types);

    ctrl.sacuvaj = sacuvaj;

    function sacuvaj() {
        ctrl.forma.$setSubmitted();
        if (ctrl.forma.$invalid) {
            return;
        }

        api.komitent.poId.izmijeni(ctrl.buyer.id, ctrl.buyer).then(function(data) {
            $uibModalInstance.close({
                isConfirmed: true,
                komitent: data.podaci,
                komitent_id: ctrl.buyer.id  // TODO: Should be removed
            });
        });
    }
}