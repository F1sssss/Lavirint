angular
    .module('app')
    .controller('IzvjestajDnevniFormaController', IzvjestajDnevniFormaController);

IzvjestajDnevniFormaController.$inject = ['fisReportService'];

function IzvjestajDnevniFormaController(fisReportService) {
    let ctrl = this;

    ctrl.datum = fisReportService.getDayRelative(-1);
}
