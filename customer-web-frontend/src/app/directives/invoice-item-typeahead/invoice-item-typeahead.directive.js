angular
    .module('app')
    .directive('invoiceItemTypeahead', invoiceItemTypeahead);

invoiceItemTypeahead.$inject = ['$rootScope', '$timeout', 'api', 'fisConfig'];

function invoiceItemTypeahead($rootScope, $timeout, api, fisConfig) {
    return {
        restrict: 'E',
        replace: true,
        templateUrl: 'app/directives/invoice-item-typeahead/invoice-item-typeahead.template.html',
        link: link,
        scope: {
            size: '@size',  // sm, lg
            isRounded: '=',
            typeaheadPopupClasses: '=',
            typeaheadAppendTo: '=',
            typeaheadOnFocusChange: '&',
            typeaheadOnLoadingChange: '&',
            typeaheadOnOpenChange: '&',
            onAdd: '&'
        }
    }

    function link(scope, element, attrs) {
        scope.podaci = {};
        scope.podaci.kolicina = 1;
        scope.podaci.magacin_zaliha = null;
        scope.query = '';

        scope.isEditingQuantity = false;
        scope.typeaheadIsLoading = false;
        scope.typeaheadIsOpen = false;
        scope.typeaheadHasFocus = false;

        let quantityInput = angular.element(element.find('input')[0]);
        let typeaheadInput = angular.element(element.find('input')[1]);

        scope.$watch('typeaheadHasFocus', function(newValue) {
            $timeout(function() {
                scope.typeaheadOnFocusChange({
                    isFocused: newValue
                });
            }, 300);
        });

        scope.$watch('typeaheadIsLoading', function(newValue) {
            $timeout(function() {
                scope.typeaheadOnLoadingChange({
                    isLoading: newValue
                });
            }, 300);
        });

        scope.$watch('typeaheadIsOpen', function(newValue) {
            $timeout(function() {
                scope.typeaheadOnOpenChange({
                    isOpen: newValue
                });
            }, 300);
        });

        if (scope.size === 'lg' || scope.size === 'sm') {
            scope.inputGroupClasses = 'input-group-' + scope.size;
        }

        scope.debouncePromise = null;
        scope.request = null;

        scope.onSelect = onSelect;
        scope.getZalihe = getZalihe;
        scope.clearAmount = clearAmount;
        scope.onResetButtonClick = onResetButtonClick;
        scope.onInputKeydown = onInputKeydown;
        scope.focusTypeahead = focusTypeahead;

        function reset() {
            scope.podaci.kolicina = 1;
            scope.query = '';
        }

        function onSelect($item, $model, $label, $eventType) {
            if (scope.podaci.kolicina === null) {
                scope.podaci.kolicina = 1;
            }

            scope.podaci.magacin_zaliha = angular.copy($item);
            scope.onAdd({ $data: angular.copy(scope.podaci), $eventType: $eventType });

            reset();
        }

        function getZalihe(pojam_za_pretragu) {
            $timeout.cancel(scope.debouncePromise);

            scope.debouncePromise = $timeout(function() {
                return api.magacin.poId.zalihe
                    .listaj(
                        fisConfig.user.magacin_id,
                        {pojam_za_pretragu: pojam_za_pretragu, broj_stranice: 1, broj_stavki_po_stranici: 50})
                    .then(function (data) {
                        return data.stavke;
                    });
            }, 300);

            return scope.debouncePromise;
        }

        function clearAmount() {
            scope.query = '';
            scope.podaci.magacin_zaliha = null;
            scope.podaci.kolicina = null;

            $timeout(function () {
                quantityInput.focus();
            });
        }

        function onResetButtonClick() {
            reset();
        }

        let emptyCount = 1;

        function onInputKeydown(event) {
            $timeout(function() {
                if (scope.query === '' && (event.key === '' || event.key === 'Backspace' || event.keyCode === 8 || event.charCode === 8)) {
                    emptyCount += 1;
                } else {
                    emptyCount = 1;
                }

                if (emptyCount > 1) {
                    emptyCount = 1;
                    scope.podaci.kolicina = null;
                    scope.isEditingQuantity = true;
                    quantityInput.focus();
                }
            });

        }

        scope.onQuantityBlur = function($event) {
            scope.isEditingQuantity = false;
            if (
                scope.podaci.kolicina === undefined
                || scope.podaci.kolicina === null
                || scope.podaci.kolicina === ''
            ) {
                scope.podaci.kolicina = 1;
            }

            focusTypeahead();
        }

        scope.onQuantityChange = function() {
            if (
                scope.podaci.kolicina === undefined
                || scope.podaci.kolicina === null
                || scope.podaci.kolicina === ''
            ) {
                return;
            }

            const newValue = scope.podaci.kolicina.replace(/,/g, '.');

            let shouldBlur = newValue.endsWith('*') || newValue.endsWith('x') || newValue.endsWith('X');

            // Remove all non-numeric and non-decimal point characters
            let filteredValue = newValue.replace(/[^\d.]/g, '');

            if (filteredValue === "") {
                scope.podaci.kolicina = 1;
                focusTypeahead();
                return;
            }

            // Ensure that only the first decimal point remains
            const decimalIndex = filteredValue.indexOf('.');
            if (decimalIndex !== -1) {
                const integerPart = filteredValue.slice(0, decimalIndex);
                const decimalPart = filteredValue.slice(decimalIndex + 1).replace(/\./g, '');
                scope.podaci.kolicina = integerPart + '.' + decimalPart;
            } else {
                scope.podaci.kolicina = filteredValue;
            }

            if (shouldBlur) {
                scope.podaci.kolicina = parseFloat(scope.podaci.kolicina);
                focusTypeahead();
            }
        }

        function onQueryChange() {
            if (
                scope.query === undefined
                || scope.query === null
            ) {
                quantityInput.focus();
            }
        }

        function focusTypeahead() {
            typeaheadInput.attr('inputmode', 'none');
            typeaheadInput.focus();
        }
    }
}