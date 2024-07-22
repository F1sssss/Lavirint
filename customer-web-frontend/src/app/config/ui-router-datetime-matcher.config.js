angular
    .module('app')
    .config(uiRouterDatetimeMatcher);

uiRouterDatetimeMatcher.$inject = ['$urlMatcherFactoryProvider'];

function uiRouterDatetimeMatcher($urlMatcherFactoryProvider) {
    $urlMatcherFactoryProvider.type('datetime', {
        name: 'datetime',
        encode: function (value) {
            if (angular.isDefined(value)) {
                return moment(value).format();
            }
        },
        decode: function (value) {
            var timestamp;

            if (angular.isDate(value)) {
                return value;
            }

            if (angular.isString(value)) {
                return moment(value).toDate();
            }

            timestamp = Date.parse(value);

            if (!isNaN(timestamp)) {
                return new Date(timestamp);
            }
        },

        /**
         * @description
         * Detects whether a value is of a particular type. Accepts a native (decoded) value and determines whether
         * it matches the current Type object.
         */
        is: function (value) {
            return angular.isDefined(value) && this.decode(value) === value;
        }
    })
}