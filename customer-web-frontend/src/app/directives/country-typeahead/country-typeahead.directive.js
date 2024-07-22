angular
    .module('app')
    .directive('countryTypeahead', countryTypeahead);

countryTypeahead.$inject = ['$parse', '$timeout', 'fisConfig'];

function countryTypeahead($parse, $timeout, fisConfig) {
    return {
        require: ['countryTypeahead', '?ngModel'],
        replace: true,
        restrict: 'E',
        controller: 'CountryTypeaheadController',
        controllerAs: 'ctrl',
        bindToController: true,
        templateUrl: 'app/directives/country-typeahead/country-typeahead.template.html',
        link: link,
        scope: true
    }

    function link($scope, $element, $attrs, $controllers) {
        let countryTypeaheadController = $controllers[0];
        let ngModelController = $controllers[1];
        countryTypeaheadController.initialize(ngModelController);
    }
}