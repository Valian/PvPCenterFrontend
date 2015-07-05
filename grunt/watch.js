module.exports = {

    options: {
        spawn: false,
        livereload: true
    },

    static: {
        options: { livereload: true },
        files: [
            'flask_frontend/templates/*',
            'flask_frontend/static/javascripts/*.coffee',
            'flask_frontend/static/stylesheets/*'
        ]
    }
};