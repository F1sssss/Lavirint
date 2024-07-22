angular
    .module('breakpoints', [])
    .service('breakpointsService', breakpointsService);

breakpointsService.$inject = ['$rootScope', '$window'];

function breakpointsService($rootScope, $window) {
    let service = {
        keys: {
            xs: 'xs',
            sm: 'sm',
            md: 'md',
            lg: 'lg',
            xl: 'xl',
            xxl: 'xxl'
        },
        breakpoints: {
            xs: 0,
            sm: 576,
            md: 768,
            lg: 992,
            xl: 1200,
            xxl: 1400,
        }
    };

    service.current = getCurrent();

    $window.addEventListener('resize', function() {
        service.current = getCurrent();
        $rootScope.$apply();
    });
    service.gte = gte;
    service.ls = ls;

    function gte(key) {
        if (key in service.breakpoints) {
            return $window.innerWidth >= service.breakpoints[key];
        } else {
            throw Error('Invalid breakpoint "' + key + '"');
        }
    }

    function ls(key) {
        if (key in service.breakpoints) {
            return $window.innerWidth < service.breakpoints[key];
        } else {
            throw Error('Invalid breakpoint "' + key + '"');
        }
    }

    function getCurrent() {
        let keys = Object.keys(service.breakpoints);

        for (let ii = keys.length; ii >= 0; ii--) {
            if ($window.innerWidth >= service.breakpoints[keys[ii]]) {
                return keys[ii];
            }
        }
    }

    return service;
}