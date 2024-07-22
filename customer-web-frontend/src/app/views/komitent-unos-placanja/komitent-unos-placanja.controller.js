angular
    .module('app')
    .controller('KomitentUnosPlacanjaController', KomitentUnosPlacanjaController);

KomitentUnosPlacanjaController.$inject = ['$rootScope', '$state', 'fisModal', 'api', 'komitenti'];

function KomitentUnosPlacanjaController($rootScope, $state, fisModal, api, komitenti) {
    const ctrl = this;

    ctrl.komitenti = komitenti;

    ctrl.dodaj = dodaj;
    ctrl.upis = upis;
    ctrl.obrisi = obrisi;


    ctrl.placanje = {
        komitent_id: undefined,
        datum_placanja: new Date(),
        iznos: undefined
    }

    ctrl.placanja = [];

    function dodaj() {
        ctrl.forma.$setSubmitted();
        if (ctrl.forma.$invalid) {
            fisModal.confirm({
                headerText: 'Greška',
                bodyText: 'Ispravite greške pa pokušajte ponovo'
            });
            return;
        }


        let novoPlacanje = angular.copy(ctrl.placanje);
        novoPlacanje.komitent_id = novoPlacanje.komitent.id;

        ctrl.placanja.push(novoPlacanje);

        ctrl.placanje.iznos = undefined;

        ctrl.forma.$setPristine();
    }

    function upis() {
        $rootScope.showLoader = true;

        let data = angular.copy(ctrl.placanja);

        for (let ii = 0; ii < data.length; ii++) {
            data[ii].komitent_id = data[ii].komitent.id;
            delete data[ii].komitent;
        }

        api.komitent.placanje.dodaj_bulk(data).then(function() {
            $state.go('komitent-pregled-lista', {
                broj_stavki_po_stranici: 10,
                broj_stranice: 1,
                upit_za_pretragu: ''
            });
        });
    }

    function obrisi(index) {
        ctrl.placanja.splice(index, 1);
    }
}