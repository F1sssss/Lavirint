angular
    .module('app')
    .directive('fisMinDate', fisMinDate);

fisMinDate.$inject = [];

function fisMinDate() {
    return {
        restrict: 'A',
        require: 'ngModel',
        priority: 200,
        link: link
    }

    function link(scope, element, attrs, ngModel) {
        ngModel.$validators.mindate = function(modelValue, viewValue) {
            let minDate = attrs.fisMinDate ? scope.$eval(attrs.fisMinDate) : new Date();
            ngModel.$setValidity('minDate', modelValue > minDate);
            return modelValue > minDate;
        }
    }
}