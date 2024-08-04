angular
    .module('app')
    .directive('invoiceFilterForm', invoiceFilterForm);

invoiceFilterForm.$inject = ['fisConfig', 'api'];

function invoiceFilterForm(fisConfig, api) {
    return {
        replace: true,
        link: link,
        templateUrl: 'app/directives/invoice-filter-form/invoice-filter-form.template.html',
        scope: {
            filters: '=',
            shouldHidePaymentMethod: "=",
            onConfirm: '&',
            onClose: '&',
            onBuyerSelect: '&'
        }
    }

    function link(scope, element, attrs) {        
        scope.payment_method_types = angular.copy(fisConfig.payment_method_types);

        scope.onPaymentMethodSelect = function($item, $model, $label) {
            if (scope.filters.payment_method_types.findIndex(x => x.id === $item.id) >= 0) {
                return;
            }

            scope.filters.payment_method_types.push($item);
            scope.filters.payment_type_id.push($item.id);
        }

        scope.deletePaymentMethodType = function($index) {
            scope.filters.payment_method_types.splice($index, 1);
            scope.filters.payment_type_id.splice($index, 1);
        }

        scope.searchBuyers = function(query) {
            return api.komitent.listaj(query, 1, 20).then(function(data) {
                return data.stavke;
            });
        }

        scope.onSelect = function($item, $model, $label) {
            if (scope.filters.buyers.findIndex(x => x.id === $item.id) >= 0) {
                return;
            }

            scope.filters.client_id.push($item.id);
            scope.filters.buyers.push($item);

            scope.onBuyerSelect();
        }

        scope.deleteBuyer = function($index) {
            scope.filters.client_id.splice($index, 1);
            scope.filters.buyers.splice($index, 1);
        }
    }
}