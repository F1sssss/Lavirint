angular
    .module('app')
    .controller('GrupaArtikalaUnosController', ArtikalaUnosController);

ArtikalaUnosController.$inject = ['$state', 'fisModal', 'fisGui', 'api'];

function ArtikalaUnosController($state, fisModal, fisGui, api) {
    const ctrl = this;

    ctrl.grupaArtikala = {}

    ctrl.upis = upis;

    function upis() {
        ctrl.forma.$setSubmitted();
        if (ctrl.forma.$invalid) {
            fisModal.confirm({
                headerText: 'Greška',
                bodyText: 'Ispravite greške pa pokušajte ponovo',
                headerIcon: 'fa fa-exclamation-triangle text-danger'
            });
            return;
        }

        fisGui.wrapInLoader(function() {
            return api.grupaArtikala.dodaj(ctrl.grupaArtikala);
        }).then(function() {
            return fisModal.confirm({
                headerText: 'Upis podataka',
                bodyText: 'Grupa artikala je sačuvana'
            });
        }).then(function() {
            $state.go('grupa-artikala-pregled-lista');
        });
    }
}