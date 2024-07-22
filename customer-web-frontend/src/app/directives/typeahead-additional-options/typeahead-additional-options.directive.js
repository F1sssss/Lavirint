angular
    .module('app')
    .directive('typeaheadAdditionalOptions', typeaheadAdditionalOptions);

typeaheadAdditionalOptions.$inject = [];

function typeaheadAdditionalOptions() {
    return {
        require: 'ngModel',
        scope: {
            options: '=typeaheadAdditionalOptions'
        },
        link: function ($scope, element, attrs, ngModel) {
            element.bind('focus', function () {
                if ($scope.options.clearOnFocus) {
                    ngModel.$setViewValue("")
                    ngModel.$render();
                }

                if ($scope.options.openOnFocus) {
                    $(element).trigger('input');
                    $(element).trigger('change');
                }
            });
        }
    };
}