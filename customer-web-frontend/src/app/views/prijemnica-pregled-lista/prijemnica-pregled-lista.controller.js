angular
    .module('app')
    .controller('PrijemnicaPregledListaController', PrijemnicaPregledListaController);

PrijemnicaPregledListaController.$inject = ['$state', 'stranica'];

function PrijemnicaPregledListaController($state, stranica) {
    const ctrl = this;


    ctrl.broj_stranice = stranica.broj_stranice;
    ctrl.stranica = stranica;

    ctrl.promijeniStranicu = promijeniStranicu;

    function promijeniStranicu() {
        let params = {};
        params.broj_stranice = ctrl.broj_stranice;
        params.broj_stavki_po_stranici = ctrl.stranica.broj_stavki_po_stranici;

        return $state.transitionTo($state.current, params, { inherit: false, reload: true });
    }
}