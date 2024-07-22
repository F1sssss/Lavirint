angular
    .module('app')
    .directive('fisOnOverflow', fisOnOverflow);

fisOnOverflow.$inject = [];

function fisOnOverflow() {
    return {
        restrict: 'A',
        link: link,
        scope: {
            fisOnOverflow: '&'
        }
    };

    function link(scope, element) {
        scope.$watch(function() {
            return element[0].scrollHeight
        }, function() {
            if (element[0].clientHeight < element[0].scrollHeight) {
                scope.fisOnOverflow({ hasOverflow: true });
            } else {
                scope.fisOnOverflow({ hasOverflow: false });
            }
        }, true);
    }
}