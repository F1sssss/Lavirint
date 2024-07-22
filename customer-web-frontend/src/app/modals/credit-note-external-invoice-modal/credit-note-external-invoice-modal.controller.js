angular
    .module('app')
    .controller('CreditNoteExternalInvoiceModalController', CreditNoteExternalInvoiceModalController)

CreditNoteExternalInvoiceModalController.$inject = ['$uibModalInstance', 'fisModal'];

function CreditNoteExternalInvoiceModalController($uibModalInstance, fisModal) {
    let ctrl = this;

    ctrl.data = {
        iic: '',
        issue_datetime: '',
        verification_url: '',
        amount_21: 0,
        amount_7: 0,
        amount_0: 0,
        amount_exempt: 0,
        total_21: 0,
        total_7: 0,
        total_0: 0,
        total_exempt: 0
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
            action: 'confirmed',
            data: ctrl.data
        });
    }
}