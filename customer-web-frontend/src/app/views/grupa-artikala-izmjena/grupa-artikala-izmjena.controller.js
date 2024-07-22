angular
    .module('app')
    .controller('GrupaArtikalaIzmjenaController', GrupaArtikalaIzmjenaController);

GrupaArtikalaIzmjenaController.$inject = [
    '$rootScope', '$stateParams', '$state', 'grupaArtikala', 'fisModal', 'fisGui', 'api'
];

function GrupaArtikalaIzmjenaController(
    $rootScope, $stateParams, $state, grupaArtikala, fisModal, fisGui, api
) {
    const ctrl = this;

    ctrl.grupaArtikala = grupaArtikala;

    ctrl.upis = upis;

    function upis() {
        fisGui.wrapInLoader(function() {
            return api.grupaArtikala.poId.izmijeni($stateParams.id, ctrl.grupaArtikala);
        }).then(function() {
            $state.go('grupa-artikala-pregled-lista');
        });
    }
}