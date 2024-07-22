angular
    .module('app')
    .controller('CertificateUploadModalController', CertificateUploadModalController);

CertificateUploadModalController.$inject = ['$rootScope', '$uibModalInstance', 'fisCustomerApi'];

function CertificateUploadModalController($rootScope, $uibModalInstance, fisCustomerApi) {
    const ctrl = this;

    ctrl.confirm = confirm;
    ctrl.handleFileUpload = handleFileUpload;

    ctrl.file = null;
    ctrl.password = '';
    ctrl.error = null;

    function confirm() {
        ctrl.form.$setSubmitted();
        if (ctrl.form.$invalid) {
            return;
        }

        fisCustomerApi.certificateUploadModalSubmit(ctrl.file, ctrl.password).then(function(response) {
            if (response.error) {
                ctrl.error = response.error;
            } else {
                $rootScope.setCertificateExpirationDate(response.certificate_expiration_date);

                $uibModalInstance.close({
                    isConfirmed: true
                });
            }
        });
    }

    function handleFileUpload(file) {
        ctrl.file = file;
        ctrl.filename = ctrl.file.name;
    }
}