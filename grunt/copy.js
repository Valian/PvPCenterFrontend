module.exports = {
    bootstrap_font: {
        files: [{
            cwd: 'bower_components/bootstrap/dist',
            src: 'fonts/*',
            dest: 'flask_frontend/dist',
            expand: true,
            flatten: false,
            filter: 'isFile'
        }]
    },
    font_awesome: {
        files: [{
            cwd: 'bower_components/components-font-awesome',
            src: 'fonts/*',
            dest: 'flask_frontend/dist',
            expand: true,
            flatten: false,
            filter: 'isFile'
        }]
    },
    flag_icons: {
        files: [{
            cwd: 'bower_components/flag-icon-css',
            src: 'flags/**/*',
            dest: 'flask_frontend/dist',
            expand: true,
            flatten: false,
            filter: 'isFile'
        }]
    }
};