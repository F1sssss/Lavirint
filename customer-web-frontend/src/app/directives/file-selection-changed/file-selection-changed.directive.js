angular
    .module('app')
    .directive('fileSelectionChanged', fileSelectionChanged);

fileSelectionChanged.$inject = ['$window'];

function fileSelectionChanged($window) {
    return {
        link: link,
        scope: {
            fileSelectionChanged: '&'
        }
    }

    function link(scope, element) {
        let isMulti = false;

        scope.fileInputElement = document.createElement('input');
        scope.fileInputElement.type = 'file';
        scope.fileInputElement.className = 'd-none';

        let container = document.createElement('div');
        $window.document.body.append(container);
        scope.$on('$destroy', function() {
            $window.document.body.removeChild(container);
        });

        if (isMulti) {
            scope.fileInputElement.multiple = true;
        }

        angular.element(scope.fileInputElement).bind('change', function(event) {
            scope.fileSelectionChanged({ files: event.target.files });
            scope.$apply();
        });

        element.on('click', function() {
            scope.fileInputElement.click();
        });
    }
}