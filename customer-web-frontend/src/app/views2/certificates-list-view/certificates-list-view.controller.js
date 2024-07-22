angular
    .module('app')
    .controller('CertificatesListViewController', CertificatesListViewController);

CertificatesListViewController.$inject = ['$rootScope', '$state', 'fisModal', 'fisCustomerApi', 'viewData'];

function CertificatesListViewController($rootScope, $state, modalService, fisCustomerApi, viewData) {
    const ctrl = this;

    ctrl.certificates = viewData.certificates;
    ctrl.openCertificateUploadModal = openCertificateUploadModal;
    ctrl.openConfirmDeletionModal = openConfirmDeletionModal;

    function openCertificateUploadModal() {
        modalService.certificateUpload().then(function(result) {
            if (result.isConfirmed) {
                refresh();
            }
        });
    }

    function openConfirmDeletionModal(certificateId) {
        modalService.confirmOrCancel({
            headerText: 'Brisanje sertifikata',
            bodyText: 'Da li ste sigurni da želite da obrišete sertifikat?',
            confirmButtonText: 'Obriši',
            cancelButtonText: 'Odustani'
        }).then(function(result) {
            if (!result.isConfirmed) {
                return;
            }

            fisCustomerApi.certificatesListViewDeleteCertificate(certificateId).then(function(response) {
                if (response.error) {
                    refresh();
                } else {
                    $rootScope.setCertificateExpirationDate(response.certificate_expiration_date);
                    refresh();
                }
            });
        });
    }

    function refresh() {
        return $state.transitionTo($state.current, {}, {
            reload: true, inherit: false
        });
    }
}