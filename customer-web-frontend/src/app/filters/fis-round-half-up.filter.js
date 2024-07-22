angular
    .module('app')
    .filter('fisRoundHalfUp', fisRoundHalfUp);

fisRoundHalfUp.$inject = [];

function fisRoundHalfUp() {
    return function(x, decimal_places) {
        return (new Big(x)).round(decimal_places).toNumber().toFixed(decimal_places);
    }
}