angular
    .module('app')
    .controller('NumericInputModalController', NumericInputModalController);

NumericInputModalController.$inject = ['$uibModalInstance', 'initialData'];

function NumericInputModalController($uibModalInstance, initialData) {
    let ctrl = this;
    ctrl.value = initialData.value ? initialData.value : 0;

    ctrl.confirm = confirm;
    ctrl.onEnter = onEnter;

    function onEnter($event) {
        if ($event.keyCode === 13) {
            ctrl.confirm();
        }
    }

    function confirm() {
        $uibModalInstance.close({
            isConfirmed: true, value: ctrl.value
        });
    }
}