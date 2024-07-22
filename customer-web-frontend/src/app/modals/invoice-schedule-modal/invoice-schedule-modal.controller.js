angular
    .module('app')
    .controller('InvoiceScheduleModalController', InvoiceScheduleModalController);

InvoiceScheduleModalController.$inject = ['$uibModalInstance', 'initialData', 'api'];

function InvoiceScheduleModalController($uibModalInstance, initialData, api) {
    let ctrl = this;

    if (initialData.invoiceSchedule === undefined || initialData.invoiceSchedule === null) {
        let currentTime = new Date();

        let startDate = angular.copy(currentTime);
        startDate.setDate(startDate.getDate() + 1);
        startDate.setHours(startDate.getHours(), 0, 0, 0);

        let endDate = angular.copy(startDate);
        endDate.setMonth(endDate.getMonth() + 1)

        ctrl.end_datetime = endDate;
        ctrl.endDatetimeMode = 1;

        ctrl.invoice_schedule = {
            start_datetime: startDate,
            frequency_interval: 1
        }
    } else {
        ctrl.invoice_schedule = angular.copy(initialData.invoiceSchedule);
        ctrl.invoice_schedule.start_datetime = moment(ctrl.invoice_schedule.start_datetime).toDate()

        if (ctrl.invoice_schedule.end_datetime === undefined || ctrl.invoice_schedule.end_datetime === null) {
            ctrl.endDatetimeMode = 1;
        } else {
            ctrl.end_datetime = moment(ctrl.invoice_schedule.end_datetime).toDate();
            ctrl.invoice_schedule.end_datetime = moment(ctrl.invoice_schedule.end_datetime).toDate();
            ctrl.endDatetimeMode = 2;
        }
    }

    ctrl.cancel = cancel;
    ctrl.setEndDatetimeMode= setEndDatetimeMode;
    ctrl.confirm = confirm;

    function cancel() {
        $uibModalInstance.dismiss('cancel');
    }

    function setEndDatetimeMode(value) {
        if (ctrl.endDatetimeMode === value) {
            return;
        }

        ctrl.endDatetimeMode = value;
        if (ctrl.endDatetimeMode === 1) {
            ctrl.invoice_schedule.end_datetime = undefined;
        } else if (ctrl.endDatetimeMode === 2) {
            ctrl.invoice_schedule.end_datetime = undefined;
        } else {
            throw Error('Invalid end datetime mode');
        }
    }

    function confirm() {
        ctrl.form.$setSubmitted();
        if (ctrl.form.$invalid) {
            return;
        }

        let data = angular.copy(ctrl.invoice_schedule);

        data.start_datetime = moment(data.start_datetime).format();
        if (data.end_datetime !== undefined && data.end_datetime !== null) {
            data.end_datetime = moment(data.end_datetime).format();
        }

        ctrl.isLoading = true;
        api.faktura.poId.invoice_schedule.add(ctrl.invoice_schedule.source_invoice_id, data).then(function(data) {
            $uibModalInstance.close({
                isConfirmed: true,
                invoice_schedule: data
            });
        }).finally(function() {
            ctrl.isLoading = false;
        });
    }
}