angular.module('app').config(['uibTimepickerConfig', function (uibTimepickerConfig) {
    uibTimepickerConfig.showMeridian = false;
    uibTimepickerConfig.mousewheel = false;
    uibTimepickerConfig.showSpinners = false;
    uibTimepickerConfig.showSeconds = true;
}]);