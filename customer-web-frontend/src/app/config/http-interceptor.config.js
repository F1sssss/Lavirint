angular.module('app').config(['$httpProvider', function ($httpProvider) {
    $httpProvider.interceptors.push(function ($q, $window) {
        return {
            responseError: function (rejection) {
                if (rejection.status === -1) {
                    return;
                }

                if (rejection.config.url.match('^/api')) {
                    if (rejection.status === 401) {
                        $window.location.href = './login.html';
                        return;
                    }

                    if (rejection.status === 403) {
                        $window.location.href = './forbidden.html';
                        return;
                    }
                }

                $window.location.href = './login.html';
            }
        }
    });
}]);

