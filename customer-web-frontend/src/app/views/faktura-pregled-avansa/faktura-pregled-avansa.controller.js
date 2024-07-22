angular
    .module('app')
    .controller('FakturaPregledAvansaController', FakturaPregledAvansaController);

FakturaPregledAvansaController.$inject = [
    '$rootScope', '$stateParams', '$state', '$cookies', '$uibModal', 'api', 'fisGui', 'fisModal', 'fisConfig',
    'stampac', 'initialData']

function FakturaPregledAvansaController(
    $rootScope, $stateParams, $state, $cookies, $uibModal, api, fisGui, fisModal, fisConfig,
    stampac, initialData) {
    const ctrl = this;

    ctrl.tab = 'regular';
    ctrl.areFiltersVisible = false;

    ctrl.viewType = $cookies.get('invoiceOverview.viewType');
    if (ctrl.viewType === undefined) {
        ctrl.viewType = 'grid';
        $cookies.put('invoiceOverview.viewType', 'grid')
    }

    ctrl.fakturaModal = {
        jeVidljiv: false,
        src: undefined
    }

    ctrl.komitenti = initialData.komitenti;
    ctrl.areFiltersCollapsed = true;
    ctrl.stranica = initialData.stranica;
    ctrl.broj_stranice = initialData.stranica.broj_stranice;

    ctrl.fiscalizationDateGteDropdownOpen = false;
    ctrl.fiscalizationDateLteDropdownOpen = false;

    ctrl.filters = {}
    ctrl.filters.ordinal_id = $stateParams.ordinal_id;
    ctrl.filters.total_price_gte = $stateParams.total_price_gte;
    ctrl.filters.total_price_lte = $stateParams.total_price_lte;
    ctrl.filters.fiscalization_date_gte = $stateParams.fiscalization_date_gte;
    ctrl.filters.fiscalization_date_lte = $stateParams.fiscalization_date_lte;
    ctrl.filters.payment_type_id = [];
    ctrl.filters.payment_method_types = [];
    ctrl.filters.client_id = [];
    ctrl.filters.buyers = [];
    if ($stateParams.payment_type_id) {
        ctrl.filters.payment_type_id = $stateParams.payment_type_id;
        ctrl.filters.payment_method_types = fisConfig.filterPaymentMethodsByIds($stateParams.payment_type_id);
    }
    if ($stateParams.client_id) {
        ctrl.filters.client_id = $stateParams.client_id;
        ctrl.filters.buyers = ctrl.komitenti.filter(function(x) {
            return $stateParams.client_id.indexOf(x.id) >= 0
        });
    }


    ctrl.stampac = stampac;
    ctrl.storniraj = storniraj;
    ctrl.promijeniStranicu = promijeniStranicu;
    ctrl.ponistiPretragu = ponistiPretragu;
    ctrl.posaljiMail = posaljiMail;
    ctrl.setViewType = setViewType;
    ctrl.applyFilters = applyFilters;

    function ponistiPretragu($event) {
        $event.preventDefault();
        $state.transitionTo($state.current, {}, {inherit: false, reload: true, notify: false});
    }

    function posaljiMail(fakturaId) {
        fisModal.confirmOrCancel({
            headerText: 'Slanje e-mail-a',
            bodyText: 'Da li ste sigurni da želite da pošaljete e-mail?'
        }).then(function(result) {
            if (result.isConfirmed) {
                fisGui.wrapInLoader(function() {
                    return api.faktura.poId.mail(fakturaId).then(function(data) {
                        if (data.is_success) {
                            return fisModal.confirm({
                                headerText: 'Uspjeh',
                                bodyText: data.message
                            });
                        } else {
                            return fisModal.confirm({
                                headerText: 'Grеška',
                                bodyText: data.message
                            });
                        }
                    }).finally(function() {
                        $state.reload();
                    });
                });
            }
        });
    }

    function promijeniStranicu() {
        let params = angular.copy(ctrl.filters);
        params.broj_stranice = ctrl.broj_stranice;

        return $state.transitionTo($state.current, params, { inherit: false, reload: true });
    }

    function storniraj($index) {
        let faktura = ctrl.stranica.stavke[$index];

        fisModal.confirmOrCancel({
            headerText: 'Storniranje računa',
            bodyText: 'Da li ste sigurni da želite da stornirate račun?',
            confirmButtonText: 'U redu',
            cancelButtonText: 'Odustani'
        }).then(function (result) {
            if (!result.isConfirmed) {
                return;
            }

            fisGui.wrapInLoader(function() {
                return api.faktura.storniraj(faktura.id).then(function (data) {
                    if (data.result.is_success) {
                        return $state.reload();
                    } else {
                        return fisModal.confirm({
                            headerText: 'Grеška prilikom fiskalizacije',
                            bodyText: data.result.message
                        });
                    }
                });
            });
        });
    }

    function setViewType(viewType) {
        ctrl.viewType = viewType;
        $cookies.put('invoiceOverview.viewType', viewType);
    }

    function applyFilters() {
        let params = ctrl.filters;
        params.broj_stranice = 1;
        return $state.transitionTo($state.current, params, { inherit: false, reload: true });
    }
}