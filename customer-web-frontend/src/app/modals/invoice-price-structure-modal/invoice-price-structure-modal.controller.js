angular
    .module('app')
    .controller('InvoicePriceStructureModalController', InvoicePriceStructureModalController);

InvoicePriceStructureModalController.$inject = ['$uibModalInstance', 'initialData'];

function InvoicePriceStructureModalController($uibModalInstance, initialData) {
    let ctrl = this;
    ctrl.invoice = initialData.invoice;
}