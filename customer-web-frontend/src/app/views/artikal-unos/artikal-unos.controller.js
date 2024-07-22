angular
    .module('app')
    .controller('ArtikalUnosController', ArtikalUnosController);

ArtikalUnosController.$inject = ['$state', 'api', 'fisConfig', 'initialData', 'invoiceFactory', 'fisModal'];

function ArtikalUnosController($state, api, fisConfig, initialData, invoiceFactory, fisModal) {
    const ctrl = this;

    ctrl.invoiceFactory = invoiceFactory;
    ctrl.grupeArtikala = initialData.grupe_artikala;
    ctrl.jediniceMjere = angular.copy(fisConfig.units);
    ctrl.poreskeStope = angular.copy(fisConfig.poreske_stope);
    ctrl.defaultJedinicaMjere = angular.copy(fisConfig.defaultUnit);
    ctrl.tax_exemption_reasons = angular.copy(fisConfig.tax_exemption_reasons);

    if (ctrl.grupeArtikala.length > 0) {
        ctrl.defaultGrupaArtikala = ctrl.grupeArtikala.find((x) => { return x.ui_default; });
    }

    ctrl.data = {};

    ctrl.data.magacin_zaliha = {
        izvor_kalkulacije: IZVOR_KALKULACIJE_UPB,
        jedinicna_cijena_osnovna: 0,
        jedinicna_cijena_puna: 0,
        raspoloziva_kolicina: 0,
        porez_procenat: 21
    }

    ctrl.data.artikal = {
        sifra: undefined,
        barkod: undefined,
        naziv: undefined,
        opis: undefined,
        jedinica_mjere_id: ctrl.defaultJedinicaMjere ? ctrl.defaultJedinicaMjere.id : undefined,
        jedinicna_mjere: ctrl.defaultJedinicaMjere,
        grupa_artikala_id: ctrl.defaultGrupaArtikala ? ctrl.defaultGrupaArtikala.id : undefined
    }

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

        fisModal.confirmOrCancel({
            headerText: 'Upis podataka',
            bodyText: 'Da li ste sigurni da želite da dodate artikal?',
            confirmButtonText: 'Da, dodaj',
            cancelButtonText: 'Odustani'
        }).then(function (result) {
            if (result.isConfirmed) {
                api.artikal.dodaj(ctrl.data).then(function () {
                    fisModal.confirm({
                        headerText: 'Upis podataka',
                        bodyText: 'Novi artikal je upisan.'
                    }).then(function () {
                        $state.go('artikal-pregled-lista', {
                            broj_stavki_po_stranici: 10,
                            broj_stranice: 1
                        });
                    });
                });
            }
        });
    }
}