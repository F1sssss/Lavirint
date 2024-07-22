angular.module('app').config(['uibDatepickerPopupConfig', function (uibDatepickerPopupConfig) {
    uibDatepickerPopupConfig.showWeeks = false;
    uibDatepickerPopupConfig.clearText = 'Poništi';
    uibDatepickerPopupConfig.closeText = 'Zatvori';
    uibDatepickerPopupConfig.currentText = 'Danas';
}]);