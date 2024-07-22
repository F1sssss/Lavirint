angular
    .module('app')
    .controller('KomitentPregledListaController', KomitentPregledListaController);

KomitentPregledListaController.$inject = ['$state', '$stateParams', 'strana', 'stampac'];

function KomitentPregledListaController($state, $stateParams, strana, stampac) {
    const ctrl = this;

    ctrl.upit_za_pretragu = $stateParams.upit_za_pretragu;
    ctrl.strana = strana;
    ctrl.broj_stranice = strana.broj_stranice;

    ctrl.naPromjenuStranice = naPromjenuStranice;
    ctrl.stampajKarticuKupca = stampajKarticuKupca;

    function naPromjenuStranice() {
        $state.go('komitent-pregled-lista', {
            broj_stavki_po_stranici: $stateParams.broj_stavki_po_stranici,
            broj_stranice: ctrl.broj_stranice,
            upit_za_pretragu: ctrl.upit_za_pretragu
        });
    }

    function stampajKarticuKupca(komitentId) {
        stampac.stampajKarticuKupca(komitentId)
    }
}