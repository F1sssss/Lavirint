angular
    .module('app')
    .controller('PrijemnicaStavkaModalController', PrijemnicaStavkaModalController);

PrijemnicaStavkaModalController.$inject = ['$uibModalInstance', 'item'];

function PrijemnicaStavkaModalController($uibModalInstance, item) {
    const ctrl = this;

    ctrl.item = item;

    ctrl.select = function (action, item) {
        $uibModalInstance.close({
            action: action,
            item: item
        });
    }

    ctrl.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}
