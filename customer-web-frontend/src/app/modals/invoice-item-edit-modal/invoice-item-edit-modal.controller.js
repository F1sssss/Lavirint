angular
    .module('app')
    .controller('InvoiceItemEditModalController', InvoiceItemEditModalController);

InvoiceItemEditModalController.$inject = ['$uibModalInstance', 'initialData', 'invoiceFactory'];

function InvoiceItemEditModalController($uibModalInstance, initialData, invoiceFactory) {
    const ctrl = this;

    ctrl.invoice = angular.copy(initialData.invoice);
    ctrl.item = ctrl.invoice.stavke[initialData.itemIndex];
    ctrl.invoiceFactory = invoiceFactory;

    ctrl.confirm = confirm;
    ctrl.deleteItem = deleteItem;

    function deleteItem() {
        initialData.invoice.stavke.splice(initialData.itemIndex, 1);
        invoiceFactory.recalculateTotals(initialData.invoice);
        invoiceFactory.recalculateTaxGroups(initialData.invoice);

        $uibModalInstance.close({
            isConfirmed: true,
            action: 'delete'
        });
    }

    function confirm() {
        ctrl.forma.$setSubmitted();
        if (ctrl.forma.$invalid) {
            return;
        }

        initialData.invoice.stavke[initialData.itemIndex] = ctrl.item;
        invoiceFactory.recalculateItem(initialData.invoice, initialData.invoice.stavke[initialData.itemIndex]);

        $uibModalInstance.close({
            isConfirmed: true,
            action: 'save',
            item: initialData.invoice.stavke[initialData.itemIndex]
        });
    }
}