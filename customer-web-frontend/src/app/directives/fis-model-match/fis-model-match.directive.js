angular
    .module('app')
    .directive('fisModelMatch', fisModelMatch);

fisModelMatch.$inject = [];

function fisModelMatch() {
    return {
        require: 'ngModel',
        restrict: 'A',
        link: link
    }

    function link(scope, element, attrs, ngModel) {
        // ngModel.$validators.fisModelMatch = function(modelValue) {
        //     if (ngModel.$validators.required && ngModel.$isEmpty(modelValue)) {
        //         ngModel.$setValidity('confirm', true);
        //         return true;
        //     }
        //
        //     ngModel.$setValidity('confirm', modelValue === scope.$eval(attrs.fisModelMatch));
        //     return true;
        // }

        ngModel.$parsers.push(function(viewValue) {
            ngModel.$setValidity('confirm', viewValue === scope.$eval(attrs.fisModelMatch));
            return viewValue;
        });

        ngModel.$formatters.push(function(modelValue) {
            ngModel.$setValidity('confirm', modelValue === scope.$eval(attrs.fisModelMatch));
            return modelValue;
        });

        // scope.$watch(attrs.fisModelMatch, function() {
        //     ngModel.$render();
        // });
    }
}