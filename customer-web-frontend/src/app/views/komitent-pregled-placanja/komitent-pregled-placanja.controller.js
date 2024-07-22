angular
    .module('app')
    .controller('KomitentPregledPlacanjaController', KomitentPregledPlacanjaController);

KomitentPregledPlacanjaController.$inject = ['$rootScope', '$state', 'api', 'komitent'];

function KomitentPregledPlacanjaController($rootScope, $state, api, komitent) {
    const ctrl = this;

    ctrl.komitent = komitent;

    ctrl.obrisi = obrisi;


    function obrisi(index) {
        $rootScope.showLoader = true;

        let id = ctrl.komitent.placanja[index].id;

        api.komitent.placanje.poId.obrisi(id).then(function() {
            $state.reload();
        });
    }
}