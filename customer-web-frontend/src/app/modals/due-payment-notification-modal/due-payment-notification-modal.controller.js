angular
    .module('app')
    .controller('DuePaymentNotificationModal', DuePaymentNotificationModal);

DuePaymentNotificationModal.$inject = ['$uibModalInstance', 'initialData'];

function DuePaymentNotificationModal($uibModalInstance, initialData) {
    const ctrl = this;

    ctrl.notifications = initialData.notifications;

    ctrl.confirm = confirm;

    function confirm() {
        $uibModalInstance.close();
    }
}