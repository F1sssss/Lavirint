angular
    .module('app')
    .controller('GrupaArtikalaPregledListaController', GrupaArtikalaPregledListaController);

GrupaArtikalaPregledListaController.$inject = ['grupeArtikala'];

function GrupaArtikalaPregledListaController(grupeArtikala) {
    const ctrl = this;

    ctrl.grupeArtikala = grupeArtikala;
}