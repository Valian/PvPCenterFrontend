module.exports = {
    all: {
        files: [{
            expand: true,
            cwd: 'flask_frontend/static/',
            src: ['images/*.{png,jpg,gif}', 'favicon.ico'],
            dest: 'flask_frontend/dist/'
        }]
    }
};