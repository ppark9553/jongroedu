var gulp = require('gulp');
var sass = require('gulp-sass');
var useref = require('gulp-useref');
var uglify = require('gulp-uglify');
var cssnano = require('gulp-cssnano');
var gulpIf = require('gulp-if');
var imagemin = require('gulp-imagemin');
var cache = require('gulp-cache');

// Copy vendor libraries from /node_modules into /vendor
gulp.task('copy', function() {
    gulp.src(['node_modules/bootstrap/dist/**/*', '!**/npm.js', '!**/bootstrap-theme.*', '!**/*.map'])
        .pipe(gulp.dest('static/vendor/bootstrap'))

    gulp.src(['node_modules/jquery/dist/jquery.js', 'node_modules/jquery/dist/jquery.min.js'])
        .pipe(gulp.dest('static/vendor/jquery'))

    gulp.src([
            'node_modules/font-awesome/**',
            '!node_modules/font-awesome/**/*.map',
            '!node_modules/font-awesome/.npmignore',
            '!node_modules/font-awesome/*.txt',
            '!node_modules/font-awesome/*.md',
            '!node_modules/font-awesome/*.json'
        ])
        .pipe(gulp.dest('static/vendor/font-awesome'))
})

gulp.task('scss', function() {
	return gulp.src('static/sass/*.scss')
	.pipe(sass())
	.pipe(gulp.dest('static/css'))
});

gulp.task('sass', function() {
    return gulp.src('static/sass/*.sass')
    .pipe(sass())
    .pipe(gulp.dest('static/css'))
});

gulp.task('watch', function() {
	gulp.watch('static/sass/*.scss', ['scss']);
    gulp.watch('static/sass/*.sass', ['sass']);
});