angular.module('app', [
    'breakpoints',
    'ngCookies',
    'ngSanitize',
    'ngMessages',
    'ngAnimate',
    'ngLocale',
    'ui.bootstrap',
    'ui.select',
    'ui.router',
    'ui.bootstrap',
    'fiscalisation.config'
]);

angular.module('app').constant('fisInvoiceConfig', {
    itemsPerPage: 12
    
});
