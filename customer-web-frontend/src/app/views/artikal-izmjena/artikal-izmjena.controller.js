angular
    .module('app')
    .controller('ArtikalIzmjenaController', ArtikalIzmjenaController);

ArtikalIzmjenaController.$inject = [
    '$state', '$stateParams', 'api', 'fisModal', 'fisGui', 'fisConfig', 'initialData', 'invoiceFactory'];

function ArtikalIzmjenaController(
    $state, $stateParams, api, fisModal, fisGui, fisConfig, initialData, invoiceFactory
) {
    const ctrl = this;

    ctrl.invoiceFactory = invoiceFactory;

    ctrl.grupeArtikala = initialData.grupe_artikala;
    ctrl.jediniceMjere = angular.copy(fisConfig.units);
    ctrl.poreskeStope = angular.copy(fisConfig.poreske_stope);
    ctrl.tax_exemption_reasons = angular.copy(fisConfig.tax_exemption_reasons);

    ctrl.data = {};
    ctrl.data.artikal = initialData.artikal;
    ctrl.data.magacin_zaliha = initialData.magacin_zaliha;

    ctrl.upis = upis;

    function upis() {
        ctrl.forma.$setSubmitted();

        if (ctrl.forma.$invalid) {
            fisModal.confirm({
                headerText: 'Greška',
                bodyText: 'Ispravite greške pa pokušajte ponovo'
            });
            return;
        }

        fisGui.wrapInLoader(function() {
            return api.artikal.izmijeni($stateParams.id, ctrl.data).then(function(data) {
                return data;
            });
        }).then(function() {
            return fisModal.confirm({
                headerText: 'Upis podataka',
                bodyText: 'Artikal je sačuvan'
            }).then(function() {
                return $state.go('artikal-pregled-lista', {
                    broj_stavki_po_stranici: 10,
                    broj_stranice: 1
                });
            });
        });
    }
}