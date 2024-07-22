angular
    .module('app')
    .controller('StanjeController', StanjeController);

StanjeController.$inject = ['$rootScope', '$stateParams', '$state', '$timeout', 'api', 'stanje', 'fisConfig'];

function StanjeController($rootScope, $stateParams, $state, $timeout, api, stanje, fisConfig) {
    const ctrl = this;

    ctrl.stanje = stanje;

    ctrl.depozit = {
        iznos: 0
    };

    if (ctrl.stanje.danasnji_depozit === null) {
        if (fisConfig.user.naplatni_uredjaj.podrazumijevani_iznos_depozita !== null) {
            ctrl.depozit.iznos = fisConfig.user.naplatni_uredjaj.podrazumijevani_iznos_depozita;
        }
    } else {
        ctrl.depozit.iznos = ctrl.stanje.danasnji_depozit.iznos;
    }

    ctrl.isplata = {
        iznos: 0
    };
}