angular
    .module('app')
    .service('fisGui', fisGui);

fisGui.$inject = ['$rootScope', '$q', '$timeout'];

function fisGui($rootScope, $q, $timeout) {
    let service = {};
    // service.isLoaderVisible = false;
    service.loaderAnimationTime = 0;

    // service.isSidebarVisible = false;
    service.siderbarAnimationTime = 0;

    service.showLoader = showLoader;
    service.hideLoader = hideLoader;
    service.wrapInLoader = wrapInLoader;
    service.showSidebar = showSidebar;
    service.hideSidebar = hideSidebar;
    service.scrollToSelector = scrollToSelector;
    service.scrollToNgInvalid = scrollToNgInvalid;
    service.scrollToInvalidFeedback = scrollToInvalidFeedback;

    return service;

    // -----------------------------------------------------------------------------------------------------------------

    function showLoader() {
        let deffered = $q.defer();

        $rootScope.showLoader = true;  // TODO Replace with service variable

        $timeout(function() {
            deffered.resolve();
        }, service.loaderAnimationTime);

        return deffered.promise;
    }

    function hideLoader() {
        let deffered = $q.defer();

        $rootScope.showLoader = false;  // TODO Replace with service variable

        $timeout(function() {
            deffered.resolve();
        }, service.loaderAnimationTime);

        return deffered.promise;
    }

    function wrapInLoader(fn) {
        return service.showLoader().then(fn).finally(function() {
            return service.hideLoader();
        });
    }

    function showSidebar() {
        let deffered = $q.defer();

        $rootScope.showSidebar = true;  // TODO Replace with service variable

        $timeout(function() {
            deffered.resolve();
        }, service.loaderAnimationTime);

        return deffered.promise;
    }

    function hideSidebar() {
        let deffered = $q.defer();

        $rootScope.showSidebar = false;  // TODO Replace with service variable

        $timeout(function() {
            deffered.resolve();
        }, service.loaderAnimationTime);

        return deffered.promise;
    }

    function scrollToSelector(selector, yOffset, timeout) {
        if (timeout === undefined) {
            timeout = 0;
        }

        return $timeout(function () {
            document.activeElement.blur();
            const el = document.querySelector(selector);
            const y = el.getBoundingClientRect().top + window.scrollY + yOffset;
            window.scrollTo({top: y, behavior: 'smooth'});
        }, timeout);
    }

    function scrollToNgInvalid(yOffset, timeout) {
        scrollToSelector('.ng-invalid:not(form):not([type=hidden])', yOffset, timeout);
    }

    function scrollToInvalidFeedback(yOffset, timeout) {
        scrollToSelector('.invalid-feedback.ng-active', yOffset, timeout);
    }
}