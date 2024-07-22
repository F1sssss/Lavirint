angular
    .module('app')
    .directive('numericKeyboard', numericKeyboard);

numericKeyboard.$inject = [];

function numericKeyboard() {
    return {
        restrict: 'EAC',
        require: 'ngModel',
        link: link,
        scope: {
            numericKeyboard: '@numericKeyboard'
        }
    }

    function link(scope, element, attrs, ngModelCtrl) {
        let Keyboard = window.SimpleKeyboard.default;

        element.addClass(scope.numericKeyboard);

        let lalaKeyboard = new Keyboard('.' + scope.numericKeyboard, {
            onChange: input => onChange(input),
            onKeyPress: button => onKeyPress(button),
            layout: {
                default: [
                    "7 8 9",
                    "4 5 6",
                    "1 2 3",
                    "{bksp} 0 .",
                ],
                shift: ["! / #", "$ % ^", "& * (", "{shift} ) +", "{bksp}"]
            },
            inputPattern: /^([1-9][0-9]*|0)\.?([0-9]{0,3})?$/,
            display: {
                '{bksp}': 'Briši'
            },
            buttonTheme: [
                {
                    class: 'invisible',
                    buttons: '{blank}'
                },
                {
                    class: 'h4 mb-0',
                    buttons: '.'
                }
            ],
                theme: "hg-theme-default hg-layout-numeric numeric-theme bg-white p-0"
        });

        lalaKeyboard.setInput(ngModelCtrl.$viewValue);

        scope.$watch(function () {
            return ngModelCtrl.$viewValue;
        }, function(newValue) {
            lalaKeyboard.setInput(newValue);
        });

        function onChange(input) {
            ngModelCtrl.$$setModelValue(parseFloat(input));
            ngModelCtrl.$setViewValue(input);
        }

        function onKeyPress(button) {
            console.log("Button pressed", button);

            /**
             * If you want to handle the shift and caps lock buttons
             */
            if (button === "{shift}" || button === "{lock}") handleShift();
        }

        function handleShift() {
            let currentLayout = keyboard.options.layoutName;
            let shiftToggle = currentLayout === "default" ? "shift" : "default";

            lalaKeyboard.setOptions({
                layoutName: shiftToggle
            });
        }
    }
}