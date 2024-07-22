angular
    .module('app')
    .controller('CreditNoteTurnoverUsedModalController', CreditNoteTurnoverUsedModalController)

CreditNoteTurnoverUsedModalController.$inject = ['$uibModalInstance', 'modalData', 'fisModal'];

function CreditNoteTurnoverUsedModalController($uibModalInstance, modalData, fisModal) {
    let ctrl = this;

    ctrl.cachedItem = angular.copy(modalData.invoice);
    ctrl.data = {
        amount_21: 0,
        amount_7: 0,
        amount_0: 0,
        amount_exempt: 0,
        total_21: 0,
        total_7: 0,
        total_0: 0,
        total_exempt: 0
    }

    if (ctrl.cachedItem) {
        ctrl.invoice = angular.copy(ctrl.cachedItem);
    } else {
        ctrl.invoice = {
            description: undefined,
            taxRate: undefined,
            amount: 0
        }
    }

    let tax21 = ctrl.invoice.grupe_poreza.find(function(x) {return x.porez_procenat === 21; })
    ctrl.data.total_21 = tax21 ? tax21.credit_note_turnover_remaining : 0;

    let tax7 = ctrl.invoice.grupe_poreza.find(function(x) {return x.porez_procenat === 7; })
    ctrl.data.total_7 = tax7 ? tax7.credit_note_turnover_remaining : 0;

    let tax0 = ctrl.invoice.grupe_poreza.find(function(x) {return x.porez_procenat === 0; })
    ctrl.data.total_0 = tax0 ? tax0.credit_note_turnover_remaining : 0;

    let taxExempt = ctrl.invoice.grupe_poreza.find(function(x) {return x.porez_procenat === null; })
    ctrl.data.total_exempt = taxExempt ? taxExempt.credit_note_turnover_remaining : 0;

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
            action: 'confirmed',
            data: ctrl.data
        });
    }
}