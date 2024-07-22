angular
    .module('app')
    .controller('InvoiceBuyerSelectModal', InvoiceBuyerSelectModal);

InvoiceBuyerSelectModal.$inject = [
    '$timeout', '$uibModalInstance', 'api', 'initialData', 'invoiceFactory', 'fisModal'
];

function InvoiceBuyerSelectModal(
    $timeout, $uibModalInstance, api, initialData, invoiceFactory, fisModal
) {
    let ctrl = this;

    ctrl.query = '';
    ctrl.invoice = angular.copy(initialData.invoice);

    ctrl.typeaheadState = {};
    ctrl.typeaheadState.isOpen = false;

    ctrl.confirm = confirm;
    ctrl.onTypeaheadSearch = onTypeaheadSearch;
    ctrl.setTypeaheadFocused = setTypeaheadFocused;
    ctrl.onSelect = onSelect;
    ctrl.showBuyerUpdateModal = showBuyerUpdateModal;
    ctrl.showCreateBuyerModal = showCreateBuyerModal;
    ctrl.removeBuyer = removeBuyer;

    function confirm() {
        initialData.invoice.komitent = ctrl.invoice.komitent;
        initialData.invoice.komitent_id = ctrl.invoice.komitent_id;
        $uibModalInstance.close({
            isConfirmed: true
        });
    }

    function onTypeaheadSearch(query) {
        return api.komitent.listaj(query).then(function(data) {
            return data;
        });
    }

    function setTypeaheadFocused(isFocused, delay) {
        $timeout(function() {
            ctrl.typeaheadState.isFocused = isFocused;
        }, delay)
    }

    function onSelect($item, $model, $label) {
        invoiceFactory.setBuyer(ctrl.invoice, $item);
        ctrl.query = '';
    }

    function showBuyerUpdateModal() {
        fisModal.buyerUpdateModal(ctrl.invoice.komitent_id).then(function(result) {
            if (result.isConfirmed) {
                invoiceFactory.setBuyer(ctrl.invoice, result.komitent);
                ngModel.$setViewValue(ctrl.invoice.komitent_id);
            }
        });
    }

    function showCreateBuyerModal() {
        let modalInstance = fisModal.buyerCreateModal();

        modalInstance.result.then(function(result) {
            if (result.isConfirmed) {
                api.komitent.listaj().then(function(data) {
                    invoiceFactory.setBuyer(ctrl.invoice, result.komitent);
                    ngModel.$setViewValue(ctrl.invoice.komitent_id);
                });
            }
        });
    }

    function removeBuyer() {
        invoiceFactory.setBuyer(ctrl.invoice, null);
    }
}