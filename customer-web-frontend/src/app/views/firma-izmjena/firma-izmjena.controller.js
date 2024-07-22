angular
    .module('app')
    .controller('FirmaIzmjenaController', FirmaIzmjenaController);

FirmaIzmjenaController.$inject = [
    '$state', '$scope', 'api', 'fisGui', 'fisModal', 'fisConfig'
];

function FirmaIzmjenaController(
    $state, $scope, api, fisGui, fisModal, fisConfig
) {
    const ctrl = this;

    ctrl.firma = angular.copy(fisConfig.user.firma);
    ctrl.drzave = angular.copy(fisConfig.countries);
    ctrl.organizacionaJedinica = angular.copy(fisConfig.user.naplatni_uredjaj.organizaciona_jedinica);
    ctrl.logoFile = null;
    ctrl.logoUrl = null;
    ctrl.cachedMailSettings = undefined;
    ctrl.mailSettings = undefined;
    ctrl.user = angular.copy(fisConfig.user);

    ctrl.upisOrganizacioneJedinice = upisOrganizacioneJedinice;
    ctrl.setMailSettings = setMailSettings;
    ctrl.updateCompanyData = updateCompanyData;
    ctrl.deleteLogo = deleteLogo;
    ctrl.uploadLogo = uploadLogo;
    ctrl.updateLogo = updateLogo;
    ctrl.updateUser = updateUser;
    ctrl.saveMailSettings = saveMailSettings;

    setMailSettings();



    if (ctrl.firma.logo_url === undefined || ctrl.firma.logo_url === null) {
        ctrl.logoUrl = null;
    } else {
        ctrl.logoUrl = ctrl.firma.logo_url;
    }

    $scope.$watch('ctrl.mailSettings.smtp_active', function (newVal) {
        if (newVal === false) {
            ctrl.mailSettings = {
                smtp_active: false,
                smtp_host: undefined,
                smtp_port: undefined,
                smtp_mail: undefined,
                smtp_username: undefined,
                smtp_password: undefined
            }
        }
    });

    function setMailSettings() {
        ctrl.cachedMailSettings = {
            smtp_active: fisConfig.user.firma.settings.smtp_active,
            smtp_host: fisConfig.user.firma.settings.smtp_host,
            smtp_port: fisConfig.user.firma.settings.smtp_port,
            smtp_mail: fisConfig.user.firma.settings.smtp_mail,
            smtp_username: fisConfig.user.firma.settings.smtp_username,
            smtp_password: undefined
        }

        ctrl.mailSettings = angular.copy(ctrl.cachedMailSettings);
    }

    function deleteLogo() {
        ctrl.logoFile = null;
        ctrl.logoUrl = null;
    }

    function uploadLogo(file) {
        ctrl.logoFile = file;
        ctrl.logoUrl = URL.createObjectURL(file);
    }

    function updateLogo() {
        let formData = new FormData();

        if (ctrl.logoUrl !== null) {
            formData.append('logo_url', ctrl.logoUrl);
        }

        if (ctrl.logoFile !== null) {
            formData.append("logo", ctrl.logoFile);
        }

        fisGui.wrapInLoader(function() {
            return api.firma.logo.izmijeni(formData);
        }).then(function() {
            return fisModal.confirm({
                headerIcon: 'fa fa-check-circle text-success',
                headerText: 'Uspjeh',
                bodyText: 'Logo je ažuriran.'
            });
        });
    }

    function updateUser() {
        ctrl.userForm.$setSubmitted();
        if (ctrl.userForm.$invalid) {
            fisModal.confirm({
                headerText: 'Greška',
                headerIcon: 'fa fa-exclamation-triangle text-danger',
                bodyText: 'Ispravite greške pa pokušajte ponovo'
            });
            return
        }

        fisGui.wrapInLoader(function() {
            let data = {};
            data.lozinka = ctrl.user.lozinka;

            return api.korisnik.poId.izmijeni(data).then(function(data) {
                return data;
            });
        }).then(function(data) {
            return fisModal.confirm({
                headerIcon: 'fa fa-check-circle text-success',
                headerText: 'Uspjeh',
                bodyText: 'Podaci su ažurirani.'
            });
        });
    }

    function updateCompanyData() {
        fisGui.wrapInLoader(function() {
            return api.firma.izmijeni(ctrl.firma).then(function() {
                return fisConfig.reload();
            });
        }).then(function() {
            return fisModal.confirm({
                headerIcon: 'fa fa-check-circle text-success',
                headerText: 'Uspjeh',
                bodyText: 'Podaci su ažurirani.'
            });
        });
    }

    function upisOrganizacioneJedinice() {
        ctrl.organisationalUnitForm.$setSubmitted();
        if (ctrl.organisationalUnitForm.$invalid) {
            return fisModal.invalidForm();
        }

        fisGui.wrapInLoader(function() {
            return api.organizacionaJedinica.poId.izmijeni(ctrl.organizacionaJedinica.id, ctrl.organizacionaJedinica).then(function(data) {
                if (data.is_success) {
                    return fisConfig.reload().then(function() {
                        return data;
                    });
                } else {
                    return data;
                }
            });
        }).then(function(data) {
            ctrl.organisationalUnitForm.$setPristine();

            if (data.is_success) {
                return fisModal.confirm({
                    headerIcon: 'fa fa-check-circle text-success',
                    headerText: 'Uspjeh',
                    bodyText: data.message
                });
            } else {
                return fisModal.confirm({
                    headerIcon: 'fa fa-exclamation-triangle text-danger',
                    headerText: 'Greška',
                    bodyText: data.message
                });
            }
        });
    }

    function saveMailSettings() {
        ctrl.mailSettingsForm.$setSubmitted();
        if (ctrl.mailSettingsForm.$invalid) {
            return fisModal.invalidForm();
        }

        fisGui.wrapInLoader(function() {
            return api.firma.podesavanja.smtp.izmijeni(ctrl.mailSettings).then(function(data) {
                return data;
            });
        }).then(function(data) {
            ctrl.mailSettingsForm.$setPristine();

            if (data.is_success) {
                ctrl.cachedMailSettings = angular.copy(ctrl.mailSettings);

                return fisModal.confirm({
                    headerText: 'Uspjeh',
                    headerIcon: 'fa fa-check-circle text-success',
                    bodyText: data.message
                }).then(function() {
                    return api.korisnik.listaj().then(function (data) {
                        fisConfig.user = data;
                        ctrl.setMailSettings();
                    });
                });
            } else {
                return fisModal.confirm({
                    headerText: 'Greška',
                    headerIcon: 'fa fa-exclamation-triangle text-danger',
                    bodyText: data.message
                });
            }
        });;
    }
}