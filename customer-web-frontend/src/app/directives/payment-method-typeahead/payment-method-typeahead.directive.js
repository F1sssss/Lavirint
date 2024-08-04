angular
    .module('app')
    .directive('paymentMethodTypeahead', paymentMethodTypeahead);

paymentMethodTypeahead.$inject = ['fisConfig'];

function paymentMethodTypeahead(fisConfig) {
    return {
        restrict: 'E',
        templateUrl: 'app/directives/payment-method-typeahead/payment-method-typeahead.template.html',
        link: link,
        scope: {
            onSelect: '&',
            isCash: '=',
            shouldHideOrderType: '='
        }
    }

    function link(scope, element, attrs) {
        scope.fisConfig = fisConfig;
        scope.query = '';
    }
}