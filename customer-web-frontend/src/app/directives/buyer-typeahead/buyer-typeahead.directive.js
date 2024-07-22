angular
    .module('app')
    .directive('buyerTypeahead', buyerTypeahead);

buyerTypeahead.$inject = ['$parse', '$timeout', 'api', 'fisModal'];

function buyerTypeahead($parse, $timeout, api, fisModal) {
    return {
        restrict: 'E',
        replace: true,
        templateUrl: 'app/directives/buyer-typeahead/buyer-typeahead.template.html',
        link: link,
        scope: true
    }

    function link($scope, $element, $attrs) {
        $scope.ctrl = {};
        $scope.ctrl.query = '';
        $scope.ctrl.onTypeaheadSearch = onTypeaheadSearch;
        $scope.ctrl.onTypeaheadSelect = onTypeaheadSelect;
        $scope.ctrl.onAddButtonClick = onAddButtonClick;
        $scope.ctrl.onSelectCallback = $parse($attrs.onSelect);
        $scope.ctrl.keepOnBlur = 'keepOnBlur' in $attrs;

        $scope.ctrl.canAdd = 'canAdd' in $attrs;

        function onTypeaheadSearch(query) {
            return api.komitent.listaj(query, 1, 10).then(function (data) {
                return data.stavke;
            });
        }

        function onTypeaheadSelect($item, $model, $label) {
            if (!$scope.ctrl.keepOnBlur) {
                $scope.ctrl.query = '';
            }

            $scope.ctrl.onSelectCallback($scope.$parent, {
                '$model': $model
            });
        }

        $scope.ctrl.onTypeaheadFocus = function() {
            let typeaheadNgModelController = $element.find('input').controller('ngModel');
            typeaheadNgModelController.$setViewValue('');
            typeaheadNgModelController.$$setModelValue(null);
            typeaheadNgModelController.$render();

            $scope.ctrl.onSelectCallback($scope.$parent, {
                '$model': null
            });
        }

        function onAddButtonClick() {
            let modalInstance = fisModal.buyerCreateModal();

            modalInstance.result.then(function (result) {
                if (result.isConfirmed) {
                    $scope.ctrl.onSelectCallback($scope.$parent, {
                        '$model': result.model
                    });
                }
            });
        }
    }
}