angular
    .module('app', ['ngMessages'])
    .controller('LoginController', LoginController);

LoginController.$inject = ['$http'];

function LoginController($http) {
    const ctrl = this;

    ctrl.podaci = {
        pib: '',
        email: '',
        lozinka: ''
    }

    ctrl.prijava = function () {
        ctrl.form.$setSubmitted();
        if (ctrl.form.$invalid) {
            return
        }

        $http({
            url: '/api/customer/login',
            method: 'POST',
            data: ctrl.podaci
        }).then(function (odgovor) {
            if (odgovor.data.imaGresku) {
                ctrl.errorMessage = odgovor.data.opisGreske;
                return;
            }

            window.location.href = "./"
        });
    }
}