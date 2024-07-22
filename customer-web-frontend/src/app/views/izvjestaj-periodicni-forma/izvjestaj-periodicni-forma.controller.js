angular
    .module('app')
    .controller('IzvjestajPeriodicniFormaController', IzvjestajPeriodicniFormaController);

IzvjestajPeriodicniFormaController.$inject = ['fisReportService'];

function IzvjestajPeriodicniFormaController(fisReportService) {
    let ctrl = this;

    ctrl.datumOd = fisReportService.getDayRelative(-2);


    let endOfDay = fisReportService.getDayRelative();
    endOfDay.setHours(23, 59, 59, 0);
    ctrl.datumDo = endOfDay;
}
