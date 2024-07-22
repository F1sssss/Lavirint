const addResourcesToCache = async (resources) => {
    const cache = await caches.open("1");
    await cache.addAll(resources);
};

const dbRequest = indexedDB.open('fiscalization', 1);

self.addEventListener('install', (event) => {
    event.waitUntil(
        addResourcesToCache([
            "/",
            "/fonts/FontAwesome.otf",
            "/fonts/fontawesome-webfont.eot",
            "/fonts/fontawesome-webfont.svg",
            "/fonts/fontawesome-webfont.ttf",
            "/fonts/fontawesome-webfont.woff",
            "/fonts/fontawesome-webfont.woff2",
            "/img/select2.png",
            "/img/select2-spinner.gif",
            "/img/select2x2.png",
            "/bundle.ng.js",
            "/bundle.vendor.css",
            "/bundle.vendor.js",
            "/forbidden.html",
            "/index.html",
            "/login.bundle.js",
            "/login.css",
            "/login.html",
            "/manifest.json",
            "/service-worker.js",
            "/style.css"
        ])
    )
});

self.addEventListener('sync', (event) => {
    console.log(event);
});

self.addEventListener('fetch', (event) => {
    console.log(event.request);
    // event.respondWith(
    //     caches.match(event.request).then((response) => response || fetch(event.request))
    // );

    if (navigator.onLine) {
        event.respondWith(fetch(event.request));
    } else {
        let body = {
            isSuccess: true
        };

        let response = new Response(JSON.stringify(body), {
            status: 200,
            headers: {
                "Content-Type": "application/json"
            }
        });

        event.respondWith(response);
    }
});

dbRequest.onerror = (event) => {
    // Do something with request.errorCode!po
};

dbRequest.onsuccess = (event) => {
    // Do something with request.result!
}

dbRequest.onupgradeneeded = function(event) {
    const db = event.target.result;

    if (event.oldVersion === 1) {
        db.createObjectStore('invoices', { keyPath: 'id', autoIncrement: true });
    }

    if (event.oldVersion < 2) {

    }
}