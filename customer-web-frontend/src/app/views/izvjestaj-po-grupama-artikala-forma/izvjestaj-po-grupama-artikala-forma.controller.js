angular
    .module('app')
    .controller('IzvjestajPoGrupamaArtikalaFormaController', IzvjestajPoGrupamaArtikalaFormaController);

IzvjestajPoGrupamaArtikalaFormaController.$inject = ['fisReportService'];

function IzvjestajPoGrupamaArtikalaFormaController(fisReportService) {
    let ctrl = this;

    ctrl.datumOd = fisReportService.getDayRelative(-2);

    let endOfDay = fisReportService.getDayRelative();
    endOfDay.setHours(23, 59, 59, 0);
    ctrl.datumDo = endOfDay;
}
