// GULPFILE
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// Ova datoteka sadrži sve komande potrebne za procesuiranje resursa za
// frontend

// 1. BIBLIOTEKE
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
const { src, dest, series, parallel, watch } = require("gulp");
const sass = require("sass");
const fs = require("fs");
const path = require("path");

// Define the required plugins
const plugins = {
  sass: require("gulp-sass")(sass),
  cleanCSS: require("gulp-clean-css"),
  autoprefixer: require("gulp-autoprefixer"),
  template: require("gulp-template"),
  templatecache: require("gulp-angular-templatecache"),
  clean: require("gulp-clean"),
  useref: require("gulp-useref"),
  replace: require("gulp-replace"),
  if: require("gulp-if"),
  uglify: require("gulp-uglify"),
  ngAnnotate: require("gulp-ng-annotate"),
};

// Define the tasks
const sass_task = () => {
  return src(["src/sass/style.scss", "src/sass/login.scss"])
    .pipe(plugins.sass().on("error", plugins.sass.logError))
    .pipe(plugins.cleanCSS({ compatibility: "*" }))
    .pipe(plugins.autoprefixer({ cascade: false }))
    .pipe(dest("dist"));
};

const templates = () => {
  return src("src/**/*template.html")
    .pipe(
      plugins.templatecache("app.templates.js", {
        module: "app",
        transformUrl: function (url) {
          return url.replace(/^\\/, "").replace(/^\//, "");
        },
      })
    )
    .pipe(dest("src/app"));
};

const delete_templates = () => {
  return src("src/app/app.templates.js", { allowEmpty: true }).pipe(
    plugins.clean()
  );
};

const fontawesomeSrc = () => {
  return src(
    [
      "node_modules/font-awesome/fonts/**",
      "node_modules/font-awesome/css/font-awesome.min.css",
    ],
    { base: "node_modules" }
  ).pipe(dest("src/vendor"));
};

const fontawesomeDist = () => {
  return src("node_modules/font-awesome/fonts/**").pipe(dest("dist/fonts"));
};

const vendor = () => {
  return src(
    [
      "node_modules/bootstrap/dist/**",
      "node_modules/angular-messages/angular-messages.min.js",
      "node_modules/angular-cookies/angular-cookies.min.js",
      "node_modules/angular/angular.min.js",
      "node_modules/angular/angular-csp.css",
      "node_modules/angular-sanitize/angular-sanitize.min.js",
      "node_modules/angular-ui-bootstrap/dist/ui-bootstrap.js",
      "node_modules/angular-ui-bootstrap/dist/ui-bootstrap-csp.css",
      "node_modules/ui-select/dist/select.css",
      "node_modules/ui-select/dist/select.js",
      "node_modules/select2/select2.js",
      "node_modules/select2/select2-bootstrap.css",
      "node_modules/select2/select2.css",
      "node_modules/select2/select2.png",
      "node_modules/select2/select2x2.png",
      "node_modules/select2/select2-spinner.gif",
      "node_modules/@ttskch/select2-bootstrap4-theme/dist/**",
      "node_modules/@uirouter/angularjs/release/angular-ui-router.min.js",
      "node_modules/jquery/dist/jquery.min.js",
      "node_modules/smoothscroll-polyfill/dist/smoothscroll.min.js",
      "node_modules/angular-animate/angular-animate.min.js",
      "node_modules/angular-touch/angular-touch.min.js",
      "node_modules/angular-i18n/angular-locale_sr-latn-me.js",
      "node_modules/animate.css/animate.min.css",
      "node_modules/simple-keyboard/build/index.js",
      "node_modules/simple-keyboard/build/css/index.css",
      "node_modules/big.js/big.js",
    ],
    { base: "node_modules" }
  ).pipe(dest("src/vendor/"));
};

const clean = () => {
  return src("dist", { read: false, allowEmpty: true }).pipe(plugins.clean());
};

const img = () => {
  return src("src/img/**").pipe(dest("dist/img"));
};

const manifest = () => {
  return src("src/manifest.json").pipe(dest("dist"));
};

const serviceWorker = () => {
  return src("src/service-worker.js").pipe(dest("dist"));
};

const useref = () => {
  let resourceVersion = 330;

  return src(["src/index.html", "src/login.html", "src/forbidden.html"])
    .pipe(plugins.template({ resourceVersion: resourceVersion }))
    .pipe(plugins.useref())
    .pipe(plugins.replace("select2.png", "img/select2.png"))
    .pipe(plugins.replace("select2x2.png", "img/select2x2.png"))
    .pipe(plugins.replace("select2-spinner.gif", "img/select2-spinner.gif"))
    .pipe(
      plugins.replace(
        "bundle.vendor.css",
        "bundle.vendor.css?v=" + resourceVersion
      )
    )
    .pipe(
      plugins.replace("manifest.json", "manifest.json?v=" + resourceVersion)
    )
    .pipe(
      plugins.replace(
        "bundle.vendor.js",
        "bundle.vendor.js?v=" + resourceVersion
      )
    )
    .pipe(plugins.replace("../fonts/fontawesome", "fonts/fontawesome"))
    .pipe(plugins.if("*.css", plugins.cleanCSS()))
    .pipe(plugins.if("bundle.ng.js", plugins.ngAnnotate({ add: true })))
    .pipe(plugins.replace("bundle.ng.js", "bundle.ng.js?v=" + resourceVersion))
    .pipe(dest("dist"));
};

// Custom function to copy directory recursively
const copyDirectory = (source, target) => {
  if (!fs.existsSync(target)) {
    fs.mkdirSync(target, { recursive: true });
  }

  const items = fs.readdirSync(source);

  for (const item of items) {
    const sourcePath = path.join(source, item);
    const targetPath = path.join(target, item);

    if (fs.statSync(sourcePath).isDirectory()) {
      copyDirectory(sourcePath, targetPath); // Recursively copy directories
    } else {
      fs.copyFileSync(sourcePath, targetPath); // Copy files
    }
  }
};

const copy_and_rename = (cb) => {
  const sourcePath = path.join(__dirname, "dist");
  const targetPath = path.join(__dirname, "../backend/nginx/frontend");

  try {
    copyDirectory(sourcePath, targetPath);
    cb();
  } catch (err) {
    console.error("Error copying directory:", err);
    cb(err); // Pass error to Gulp
  }
};

const watch_files = () => {
  watch(
    ["src/sass/**/*", "src/**/*.css"],
    series(sass_task, useref, copy_and_rename)
  );
  watch(
    ["src/**/*.js", "src/**/*.html", "!src/app/app.templates.js"],
    series(delete_templates, templates, useref, copy_and_rename)
  );
};

const build = series(
  clean,
  parallel(manifest, serviceWorker, templates, fontawesomeDist, sass_task),
  parallel(img, useref),
  delete_templates,
  copy_and_rename
);

// Glavna komanda, formiranje finalnih resursa
exports.default = build;
exports.clean = clean;
exports.build = build;

// Komanda za razvoj, formiranje resursa u relanom vremenu
// na osnovu promjena u datotekama
exports.posmatraj = watch_files;
exports["build:vendor"] = parallel(vendor, fontawesomeSrc);
