angular
    .module('app')
    .controller('ArtikalPregledListalController', ArtikalPregledListalController);

ArtikalPregledListalController.$inject = ['$state', '$stateParams', 'strana', 'fisGui', 'fisModal', 'api']

function ArtikalPregledListalController($state, $stateParams, strana, fisGui, fisModal, api) {
    const ctrl = this;

    ctrl.pojam_za_pretragu = $stateParams.pojam_za_pretragu;
    ctrl.strana = strana;
    ctrl.broj_stranice = strana.broj_stranice;
    ctrl.pretrazi = pretrazi;
    ctrl.promijeniStranicu = promijeniStranicu;
    ctrl.deleteInvoiceItemTemplate = deleteInvoiceItemTemplate;

    function pretrazi() {
        $state.go('artikal-pregled-lista', {
            pojam_za_pretragu: ctrl.pojam_za_pretragu,
            broj_stavki_po_stranici: $stateParams.broj_stavki_po_stranici,
            broj_stranice: 1
        });
    }

    function promijeniStranicu() {
        return $state.go('artikal-pregled-lista', {
            pojam_za_pretragu: $stateParams.pojam_za_pretragu,
            broj_stavki_po_stranici: $stateParams.broj_stavki_po_stranici,
            broj_stranice: ctrl.broj_stranice
        });
    }

    function deleteInvoiceItemTemplate(invoiceItemTemplateId) {
        fisGui.wrapInLoader(function() {
            return api.artikal__poId__obrisi(invoiceItemTemplateId).then(function(data) {
                return data;
            });
        }).then(function(data) {
            if (data.is_success) {
                return fisModal.confirm({
                    headerText: 'Uspjeh',
                    bodyText: 'Artikal je obrisan.'
                }).then(function() {
                    return $state.reload();
                });
            } else {
                return fisModal.confirm({
                    headerText: 'Greška',
                    headerIcon: 'fa fa-exclamation-triangle text-danger',
                    bodyText: 'Artikal nije obrisan.'
                }).then(function() {
                    return ctrl.promijeniStranicu();
                });
            }
        });
    }
}