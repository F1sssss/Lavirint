angular
    .module('app')
    .controller('IzvjestajZurnalFormaController', IzvjestajZurnalFormaController);

IzvjestajZurnalFormaController.$inject = ['fisReportService'];

function IzvjestajZurnalFormaController(fisReportService) {
    let ctrl = this;

    ctrl.datumOd = fisReportService.getDayRelative(-2);

    let endOfDay = fisReportService.getDayRelative();
    endOfDay.setHours(23, 59, 59, 0);
    ctrl.datumDo = endOfDay;
}
