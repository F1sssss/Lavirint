angular
    .module('app')
    .service('fisCustomerApi', fisCustomerApi);

fisCustomerApi.$inject = ['$q', '$http'];

function fisCustomerApi($q, $http) {
    const service = {};
    service.on_transition_finish_check_due_payments__get_notifications = on_transition_finish_check_due_payments__get_notifications;
    service.on_transition_finish_check_due_payments__turn_off_notifications = on_transition_finish_check_due_payments__turn_off_notifications;
    service.directives__credit_note_typeahead__on_typeahead_input_change = directives__credit_note_typeahead__on_typeahead_input_change;
    service.views__faktura_slobodan_unos_korekcije__fiskalizuj = views__faktura_slobodan_unos_korekcije__fiskalizuj;
    service.views__credit_note_view__on_load = views__credit_note_view__on_load;
    service.views__credit_note_create__on_buyer_typeahead_select = views__credit_note_create__on_buyer_typeahead_select;
    service.views__credit_note_create__on_fiscalize = views__credit_note_create__on_fiscalize;
    service.views__credit_note_create__on_invoice_page_change = views__credit_note_create__on_invoice_page_change;
    service.views__credit_note_create__on_load = views__credit_note_create__on_load;
    service.views__izvjestaj_po_artiklima_forma__on_submit = views__izvjestaj_po_artiklima_forma__on_submit;
    service.views__komitent_pregled_lista__on_load = views__komitent_pregled_lista__on_load;
    service.certificateUploadModalSubmit = certificateUploadModalSubmit;
    service.certificatesListViewLoad = certificatesListViewLoad;
    service.certificatesListViewDeleteCertificate = certificatesListViewDeleteCertificate;
    return service;

    function _createRequest(requestObject) {
        let canceler = $q.defer();
        requestObject.timeout = canceler.promise;

        let httpPromise = $http(requestObject).then(function(response) {
            return response.data;
        });

        httpPromise.cancel = function() {
            canceler.resolve();
        }

        return httpPromise;
    }

    function on_transition_finish_check_due_payments__get_notifications() {
        let url = new URL('/api/customer/on_transition_finish_check_due_payments/get_notifications', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: data
        });
    }

    function on_transition_finish_check_due_payments__turn_off_notifications(data) {
        let url = new URL('/api/customer/on_transition_finish_check_due_payments/turn_off_notifications', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: data
        });
    }

    function directives__credit_note_typeahead__on_typeahead_input_change(data) {
        let url = new URL('/api/customer/directives/credit_note_typeahead/on_typeahead_input_change', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: data
        });
    }

    function views__faktura_slobodan_unos_korekcije__fiskalizuj(data) {
        let url = new URL('/api/customer/views/faktura_slobodan_unos_korekcije/fiskalizuj', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: data
        });
    }

    function views__credit_note_view__on_load(data) {
        let url = new URL('/api/customer/views/credit_note_view/on_load', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: data
        });
    }

    function views__credit_note_create__on_buyer_typeahead_select(data) {
        let url = new URL('/api/customer/views/credit_note_create/on_buyer_typeahead_select', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: data
        });
    }

    function views__credit_note_create__on_fiscalize(data) {
        let url = new URL('/api/customer/views/credit_note_create/on_fiscalize', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: data
        });
    }

    function views__credit_note_create__on_invoice_page_change(data) {
        let url = new URL('/api/customer/views/credit_note_create/on_invoice_page_change', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: data
        });
    }

    function views__credit_note_create__on_load() {
        let url = new URL('/api/customer/views/credit_note_create/on_load', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString()
        });
    }

    function views__izvjestaj_po_artiklima_forma__on_submit(data) {
        let url = new URL('/api/customer/views/izvjestaj_po_artiklima_forma/on_submit', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: data
        });
    }

    function views__komitent_pregled_lista__on_load(data) {
        let url = new URL('/api/customer/views/komitent_pregled_lista/on_load', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: data
        });
    }

    function certificateUploadModalSubmit(certFile, password) {
        let url = new URL('/api/customer/certificate-upload-modal/submit', document.location.origin);

        const formData = new FormData();
        formData.append('certificate', certFile);
        formData.append('password', password);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: formData,
            headers: {
                'Content-Type': undefined
            },
            transformRequest: angular.identity
        });
    }

    function certificatesListViewLoad() {
        let url = new URL('/api/customer/certificates-list-view/load', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString()
        });
    }

    function certificatesListViewDeleteCertificate(certificateId) {
        let url = new URL('/api/customer/certificates-list-view/delete', document.location.origin);

        return _createRequest({
            method: 'POST',
            url: url.toString(),
            data: {
                certificate_id: certificateId
            }
        });
    }
}