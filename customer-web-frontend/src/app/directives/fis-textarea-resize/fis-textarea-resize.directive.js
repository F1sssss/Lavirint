angular
    .module('app')
    .directive('fisTextareaResize', fisTextareaResize);

fisTextareaResize.$inject = ['$window'];

function fisTextareaResize($window) {
    return {
        restrict: 'A',
        link: link
    }

    function link(scope, element, attrs) {
        element[0].style.resize = 'none';

        angular.element($window).on('resize', function() {
            resizeTextarea();
        });

        scope.$watch(attrs.ngModel, function(){
            resizeTextarea();
        });

        resizeTextarea();

        function resizeTextarea(){
            let offset = element.innerHeight() - element.height();

            if (element.innerHeight() < element.get(0).scrollHeight) {
                // Grow the field if scroll height is smaller
                element.height(element.get(0).scrollHeight - offset);
            } else {
                // Shrink the field and then re-set it to the scroll height in case it needs to shrink
                element.height(1);
                element.height(element.get(0).scrollHeight - offset);
            }
        }
    }
}