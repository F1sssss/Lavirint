angular
    .module('app')
    .filter('fisFormatDatetime', fisFormatDatetime);

fisFormatDatetime.$inject = [];

function fisFormatDatetime() {
    return function(x, type) {
        if (!angular.isString(x)) {
            return '---';
        }

        if (type === undefined) {
            return x.slice(0, 10) + ' ' + x.slice(11, 19);
        } else if (type === 'date') {
            return x.slice(0, 10);
        } else if (type === 'date2') {
            return x.slice(8, 10) + '.' + x.slice(5, 7) + '.' + x.slice(0, 4);
        } else if (type === 'time') {
            return x.slice(11, 19)
        } else if (type === 'taxPeriod') {
            return x.slice(5, 7) + '/' + x.slice(0, 4)
        } else {
            throw Error('Invlid type: ' + type);
        }
    }
}