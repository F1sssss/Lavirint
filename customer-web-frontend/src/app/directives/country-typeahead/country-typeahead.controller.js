angular
    .module('app')
    .controller('CountryTypeaheadController', CountryTypeaheadController);

CountryTypeaheadController.$inject = ['$scope', '$parse', '$attrs', 'fisConfig'];

function CountryTypeaheadController($scope, $parse, $attrs, fisConfig) {
    const ctrl = this;

    ctrl.query = '';
    ctrl.onTypeaheadInputChange = onTypeaheadInputChange;
    ctrl.onTypeaheadSelect = onTypeaheadSelect;
    ctrl.initialize = initialize;
    ctrl.onSelectCallback = $parse($attrs.onSelect);

    function initialize(ngModelController) {
        ctrl.ngModelController = ngModelController;
    }

    function onTypeaheadInputChange(query) {
        if (typeof query === "string" && query.length > 0) {
            let queryLowercase = query.toLowerCase();

            return angular.copy(fisConfig.countries).filter(function(country) {
                if (country.drzava.toLowerCase().indexOf(queryLowercase) >= 0) {
                    return true;
                }

                if (country.drzavaeng.toLowerCase().indexOf(queryLowercase) >= 0) {
                    return true;
                }

                if (country.drzava_skraceno_3.toLowerCase().indexOf(queryLowercase) >= 0) {
                    return true;
                }

                return false;
            });
        }

        return angular.copy(fisConfig.countries);
    }

    function onTypeaheadSelect($item, $model, $label) {
        if (ctrl.ngModelController) {
            ctrl.ngModelController.$setViewValue($item.id);
            ctrl.ngModelController.$render();
        }

        ctrl.onSelectCallback($scope.$parent, {
            '$model': $item
        });
    }
}