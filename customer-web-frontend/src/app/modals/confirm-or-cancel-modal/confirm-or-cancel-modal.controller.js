angular
    .module('app')
    .controller('ConfirmOrCancelModalController', ConfirmOrCancelModalController);

ConfirmOrCancelModalController.$inject = ['$uibModalInstance', 'data'];

function ConfirmOrCancelModalController($uibModalInstance, data) {
    let ctrl = this;

    ctrl.headerText = data.headerText;
    ctrl.headerIcon = data.headerIcon ? data.headerIcon : null;
    ctrl.bodyText = data.bodyText;
    ctrl.confirmButtonText = data.confirmButtonText ? data.confirmButtonText : 'Potvrdi';
    ctrl.cancelButtonText = data.cancelButtonText ? data.cancelButtonText : 'Odustani';
}