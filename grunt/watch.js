module.exports = {

    options: {
        spawn: false,
        livereload: true
    },

    static: {
        options: { livereload: true },
        files: [
            'flask_frontend/**/templates/*',
            'flask_frontend/static/javascripts/*.coffee',
            'flask_frontend/static/stylesheets/**/*'
        ]
    },

    translations: {
        options: { livereload: true },
        files: ['flask_frontend/translations/**/*'],
        tasks: ['shell:compile_lang']
    },

    configFiles: {
        files: [ 'Gruntfile.js', 'grunt/*.js' ],
        options: {
          reload: true
        }
      }
};