angular
    .module('app')
    .directive('fisPagination', fisPagination);

fisPagination.$inject = ['$timeout'];

function fisPagination($timeout) {
    return {
        restrict: 'E',
        replace: true,
        templateUrl: 'app/directives/fis-pagination/fis-pagination.template.html',
        link: link,
        scope: {
            currentPage: '=',
            pageData: '=',
            onPageChange: '&'
        }
    }

    function link($scope, $element, $attrs) {
        if ('class' in $attrs) {
            $element.children().addClass($attrs.class);
        }

        $scope.onPageChangeWrapper = function() {
            $timeout(function() {
                $scope.onPageChange();
            });
        }
    }
}