var gulp = require('gulp');
var babel = require('gulp-babel');
var browserify = require('gulp-browserify');
var rename = require('gulp-rename');

gulp.task('browserify', function() {
  return gulp.src('js/app.jsx', {read: false})
    .pipe(babel({
      presets: ['es2015']
    }))
    .pipe(browserify({
      transform : 'reactify',
      extensions: ['.jsx']
    }))
    .pipe(rename('bundle.js'))
    .pipe(gulp.dest('./static/'))
});

gulp.task('watch', function() {
  var jsFiles = [
    'js/**/*.js',
    'js/**/*.jsx',
  ];
  return gulp.watch(jsFiles, ['browserify']);
});
