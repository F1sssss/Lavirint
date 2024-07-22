angular
    .module('app')
    .controller('ConfirmModalController', ConfirmModalController);

ConfirmModalController.$inject = ['$uibModalInstance', 'data'];

function ConfirmModalController($uibModalInstance, data) {
    let ctrl = this;

    ctrl.headerText = data.headerText;
    ctrl.headerIcon = data.headerIcon ? data.headerIcon : null;
    ctrl.bodyText = data.bodyText;
    ctrl.buttonText = data.confirmButtonText ? data.confirmButtonText : 'U redu';
}