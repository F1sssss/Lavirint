angular
    .module('app')
    .controller('CreditNoteViewController', CreditNoteViewController);

CreditNoteViewController.$inject = ['$state', 'stampac', 'viewData'];

function CreditNoteViewController($state, stampac, viewData) {
    let ctrl = this;

    ctrl.stranica = viewData.stranica;
    ctrl.odabranaStranica = viewData.stranica.broj_stranice;

    ctrl.stampac = stampac;

    ctrl.onPageChange = onPageChange;

    function onPageChange() {
        $state.go('credit_note_view', {
            broj_stranice: ctrl.odabranaStranica,
            broj_stavki_po_stranici: ctrl.stranica.broj_stavki_po_stranici
        }, {inherit: false, reload: true});
    }
}