// GULPFILE
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// Ova datoteka sadrži sve komande potrebne za procesuiranje resursa za
// frontend

// 1. BIBLIOTEKE
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
const { src, dest, series, parallel, watch } = require('gulp');
const sass = require('sass'); // Updated import for sass

const plugins = {
  sass: require('gulp-sass')(sass), // Use sass instead of node-sass
  cleanCSS: require('gulp-clean-css'),
  autoprefixer: require('gulp-autoprefixer'),
  template: require('gulp-template'),
  templatecache: require('gulp-angular-templatecache'),
  clean: require('gulp-clean'),
  useref: require('gulp-useref'),
  replace: require('gulp-replace'),
  if: require('gulp-if'),
  uglify: require('gulp-uglify'),
  ngAnnotate: require('gulp-ng-annotate')
};

// Updated sass_task function
const sass_task = () => {
  return src([
    'src/sass/style.scss',
    'src/sass/login.scss'
  ])
    .pipe(plugins.sass().on('error', plugins.sass.logError)) // Log errors with gulp-sass
    .pipe(plugins.cleanCSS({compatibility: '*'}))
    .pipe(plugins.autoprefixer({cascade: false}))
    .pipe(dest('dist'))
};

const templates = () => {
    return src('src/**/*template.html')
        .pipe(plugins.templatecache('app.templates.js', {
            module: 'app',
            transformUrl: function(url) {
                return url
                    .replace(/^\\/, '')  // Changes '\' to '/'
                    .replace(/^\//, '');  // Removes '/' at the begining of URL
            }
        }))
        .pipe(dest('src/app'))
}

const delete_templates = () => {
    return src('src/app/app.templates.js')
        .pipe(plugins.clean());
}

const fontawesomeSrc = () => {
    return src([
        'node_modules/font-awesome/fonts/**',
        'node_modules/font-awesome/css/font-awesome.min.css'
    ], {base: 'node_modules'}).pipe(dest('src/vendor'))
}

const fontawesomeDist = () => {
    return src([ 'node_modules/font-awesome/fonts/**' ])
        .pipe(dest('dist/fonts'))
}

const vendor = () => {
    return src([
        'node_modules/bootstrap/dist/**',
        'node_modules/angular-messages/angular-messages.min.js',
        'node_modules/angular-cookies/angular-cookies.min.js',
        'node_modules/angular/angular.min.js',
        'node_modules/angular/angular-csp.css',
        'node_modules/angular-sanitize/angular-sanitize.min.js',
        'node_modules/angular-ui-bootstrap/dist/ui-bootstrap.js',
        'node_modules/angular-ui-bootstrap/dist/ui-bootstrap-csp.css',
        'node_modules/ui-select/dist/select.css',
        'node_modules/ui-select/dist/select.js',
        'node_modules/select2/select2.js',
        'node_modules/select2/select2-bootstrap.css',
        'node_modules/select2/select2.css',
        'node_modules/select2/select2.png',
        'node_modules/select2/select2x2.png',
        'node_modules/select2/select2-spinner.gif',
        'node_modules/@ttskch/select2-bootstrap4-theme/dist/**',
        'node_modules/@uirouter/angularjs/release/angular-ui-router.min.js',
        'node_modules/jquery/dist/jquery.min.js',
        'node_modules/smoothscroll-polyfill/dist/smoothscroll.min.js',
        'node_modules/angular-animate/angular-animate.min.js',
        'node_modules/angular-touch/angular-touch.min.js',
        'node_modules/angular-i18n/angular-locale_sr-latn-me.js',
        'node_modules/animate.css/animate.min.css',
        'node_modules/simple-keyboard/build/index.js',
        'node_modules/simple-keyboard/build/css/index.css',
        'node_modules/big.js/big.js'
    ], {base: 'node_modules'}).pipe(dest('src/vendor/'));
}

const clean = () => {
    return src('dist', { read: false, allowEmpty: true })
        .pipe(plugins.clean());
}

const img = () => {
    return src('src/img/**').pipe(dest('dist/img'));
}

const manifest = () => {
    return src('src/manifest.json')
        .pipe(dest('dist'));
}

const serviceWorker = () => {
    return src('src/service-worker.js')
        .pipe(dest('dist'));
}

const useref = () => {
    let resourceVersion = 330;

    return src(['src/index.html', 'src/login.html', 'src/forbidden.html'])
        .pipe(plugins.template({ resourceVersion: resourceVersion }))
        .pipe(plugins.useref())
        .pipe(plugins.replace('select2.png', 'img/select2.png'))
        .pipe(plugins.replace('select2x2.png', 'img/select2x2.png'))
        .pipe(plugins.replace('select2-spinner.gif', 'img/select2-spinner.gif'))
        .pipe(plugins.replace('bundle.vendor.css', 'bundle.vendor.css?v=' + resourceVersion))
        .pipe(plugins.replace('manifest.json', 'manifest.json?v=' + resourceVersion))
        .pipe(plugins.replace('bundle.vendor.js', 'bundle.vendor.js?v=' + resourceVersion))
        .pipe(plugins.replace('../fonts/fontawesome', 'fonts/fontawesome'))
        .pipe(plugins.if('*.css', plugins.cleanCSS()))
        // .pipe(plugins.if('*.js', plugins.uglify()))
        .pipe(plugins.if('bundle.ng.js', plugins.ngAnnotate({ add: true })))
        .pipe(plugins.replace('bundle.ng.js', 'bundle.ng.js?v=' + resourceVersion))
        .pipe(dest('dist'))
}

const posmatraj = {
    sass: (cb) => {
        watch(['src/sass/*/'], sass_task);
        cb();
    }
}

const build = series(
    parallel(
        manifest,
        serviceWorker,
        templates,
        fontawesomeDist,
        sass_task
    ),
    parallel(
        img,
        useref
    ),
    parallel(
        delete_templates
    )
)

// Glavna komanda, formiranje finalnih resursa
exports.default = series(
    clean,
    build
)

exports.clean = clean;

exports.build = build;

// Komanda za razvoj, formiranje resursa u relanom vremenu
// na osnovu promjena u datotekama
exports.posmatraj = parallel(
    sass_task,
    posmatraj.sass
)

exports['build:vendor'] = parallel(
    vendor,
    fontawesomeSrc
);