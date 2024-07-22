angular
    .module('app')
    .directive('blurOnEnter', blurOnEnter);

blurOnEnter.$inject = [];

function blurOnEnter() {
    return {
        restirct: 'A',
        link: function (scope, element, attr) {
            element[0].addEventListener('keyup', function (event) {
                if (event.keyCode === 13) {
                    this.blur();
                }
            });
        }
    }
}