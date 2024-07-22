angular
    .module('app')
    .controller('DospjelaFakturaPregledController', DospjelaFakturaPregledController);

DospjelaFakturaPregledController.$inject = ['dospjele_fakture'];

function DospjelaFakturaPregledController(dospjele_fakture) {
    const ctrl = this;

    ctrl.dospjele_fakture = dospjele_fakture;
}