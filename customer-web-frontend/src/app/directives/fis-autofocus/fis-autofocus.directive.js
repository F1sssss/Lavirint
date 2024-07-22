angular
    .module('app')
    .directive('fisAutofocus', fisAutofocus);

fisAutofocus.$inject = ['$timeout'];

function fisAutofocus($timeout) {
    return {
        restrict: 'A',
        link: link,
        scope: {
            fisAutofocus: '&'
        }
    }

    function link(scope, element) {
        let autofocus = scope.fisAutofocus();

        if (autofocus) {
            $timeout(function () {
                element.focus();
            });
        } else {
            $timeout(function () {
                element.blur();
            });
        }
    }
}