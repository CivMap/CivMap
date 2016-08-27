var gulp = require('gulp');
var browserify = require('gulp-browserify');
var rename = require('gulp-rename');

gulp.task('browserify', function() {
  return gulp.src('src/app.jsx', {read: false})
    .pipe(browserify({
      transform : 'reactify',
      extensions: ['.jsx']
    }))
    .pipe(rename('bundle.js'))
    .pipe(gulp.dest('./static/'))
});

gulp.task('watch', function() {
  var jsFiles = [
    'src/**/*.js',
    'src/**/*.jsx',
  ];
  return gulp.watch(jsFiles, ['browserify']);
});
