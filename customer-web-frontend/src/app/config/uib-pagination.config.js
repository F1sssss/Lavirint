angular.module('app').config(['uibPaginationConfig', function (uibPaginationConfig) {
    uibPaginationConfig.firstText = 'Prva';
    uibPaginationConfig.previousText = 'Prethodna';
    uibPaginationConfig.nextText = 'Sledeća';
    uibPaginationConfig.lastText = 'Poslednja';
}]);