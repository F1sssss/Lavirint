angular
    .module('app')
    .directive('orderGroupPicker', orderGroupPicker);

orderGroupPicker.$inject = ['fisModal', 'invoiceFactory', 'api'];

function orderGroupPicker(fisModal, invoiceFactory, api) {
    return {
        require: 'ngModel',
        restrict: 'E',
        templateUrl: 'app/directives/order-group-picker/order-group-picker.template.html',
        transclude: true,
        link: link,
        scope: {
            invoice: '=',
            fisDisabled: '&',
            fisChange: '&'
        }
    }

    function link(scope, element, attrs, ngModel) {
        element.addClass('order-group-picker');

        scope.disabled = scope.fisDisabled();

        if (attrs.buttonResponsiveClasses) {
            scope.buttonResponsiveClasses = attrs.buttonResponsiveClasses;
        } else {
            scope.buttonResponsiveClasses = 'col-6 col-lg-3 col-xxl-2';
        }

        scope.searchBuyers = function(query) {
            return api.order.listaj(query).then(function(data) {
                return data;
            });
        }

        scope.onSelect = function($item, $model, $label) {
            invoiceFactory.setOrderGroup(scope.invoice, $item);
            ngModel.$setViewValue(scope.invoice.order_group_id);
        }

        scope.showBuyerUpdateModal = function () {
            fisModal.buyerUpdateModal(scope.invoice.komitent_id).then(function(result) {
                if (result.isConfirmed) {
                    invoiceFactory.setBuyer(scope.invoice, result.komitent);
                    ngModel.$setViewValue(scope.invoice.komitent_id);
                }
            });
        }

        scope.showCreateBuyerModal = function () {
            let modalInstance = fisModal.buyerCreateModal();

            modalInstance.result.then(function(result) {
                if (result.isConfirmed) {
                    api.komitent.listaj().then(function(data) {
                        invoiceFactory.setBuyer(scope.invoice, result.komitent);
                        ngModel.$setViewValue(scope.invoice.komitent_id);
                    });
                }
            });
        }

        scope.removeBuyer = function () {
            invoiceFactory.setBuyer(scope.invoice, null);
        }
    }
}