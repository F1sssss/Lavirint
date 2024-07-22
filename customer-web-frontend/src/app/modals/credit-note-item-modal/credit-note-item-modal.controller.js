angular
    .module('app')
    .controller('CreditNoteItemModal', CreditNoteItemModal)

CreditNoteItemModal.$inject = ['$uibModalInstance', 'modalData', 'fisModal'];

function CreditNoteItemModal($uibModalInstance, modalData, fisModal) {
    let ctrl = this;

    ctrl.options = modalData.options;
    ctrl.cachedItem = angular.copy(modalData.item);

    if (ctrl.cachedItem) {
        ctrl.item = angular.copy(ctrl.cachedItem);
    } else {
        ctrl.item = {
            description: undefined,
            taxRate: undefined,
            amount: 0
        }
    }

    ctrl.confirm = confirm;

    function confirm() {
        ctrl.form.$setSubmitted();
        if (ctrl.form.$invalid) {
            fisModal.confirm({
                headerIcon: 'fa fa-exclamation-triangle text-danger',
                headerText: 'Greška',
                bodyText: 'Ispravite greške pa pokušajte ponovo'
            });
            return;
        }

        $uibModalInstance.close({
            action: 'save',
            item: ctrl.item
        });
    }
}