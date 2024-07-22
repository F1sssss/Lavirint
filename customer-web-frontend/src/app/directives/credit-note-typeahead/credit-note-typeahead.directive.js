angular
    .module('app')
    .directive('creditNoteTypeahead', creditNoteTypeahead);

creditNoteTypeahead.$inject = ['$parse', 'fisCustomerApi'];

function creditNoteTypeahead($parse, fisCustomerApi) {
    return {
        require: '?ngModel',
        restrict: 'E',
        replace: true,
        templateUrl: 'app/directives/credit-note-typeahead/credit-note-typeahead.template.html',
        link: link,
        scope: true
    }

    function link(scope, element, attrs, ngModelController) {
        let ctrl = {};
        scope.ctrl = ctrl;

        ctrl.query = '';

        ctrl.onTypeaheadInputChange = onTypeaheadInputChange;
        ctrl.onTypeaheadSelect = onTypeaheadSelect;
        ctrl.onSelectCallback = $parse(attrs.onSelect);

        function onTypeaheadInputChange(query) {
            return fisCustomerApi.directives__credit_note_typeahead__on_typeahead_input_change({
                query: query
            }).then(function(data) {
                return data.creditNotes;
            });
        }

        function onTypeaheadSelect($item, $model, $label) {
            ctrl.query = '';

            if (ngModelController) {
                ngModelController.$setViewValue($item.id);
            }

            ctrl.onSelectCallback(scope.$parent, {
                '$model': $item
            });
        }
    }
}