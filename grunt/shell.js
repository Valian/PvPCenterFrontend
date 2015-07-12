module.exports = function(grunt) {
    grunt.option('lang_dir', 'flask_frontend/translations');
    grunt.option('lang_config_path', 'flask_frontend/config/babel.cfg');
    grunt.task.registerTask('init_lang', 'Initialize new language', function(lang) {
       grunt.task.run('shell:init_lang:' + lang);
    });
    return {
        compile_lang: {
            command: 'pybabel compile -d ' + grunt.option('lang_dir')
        },
        extract_lang: {
            command: function() {
                grunt.file.mkdir(grunt.option('lang_dir'));
                return 'pybabel extract -F ' + grunt.option('lang_config_path') + ' -o ' + grunt.option('lang_dir') + '/messages.pot' + ' flask_frontend'
            }
        },
        update_lang: {
            command: 'pybabel update -i ' + grunt.option('lang_dir') + '/messages.pot' + ' -d ' + grunt.option('lang_dir')
        },
        init_lang: {
            command: function (lang) {
                if(!lang || lang == 'undefined') {
                    grunt.fail.warn('Specify language, eg. shell:init_lang:pl')
                }
                if(grunt.file.exists(grunt.option('lang_dir') + '/' + lang)) {
                    grunt.fail.warn('Translation already exists!');
                }

                return 'pybabel init -i ' + grunt.option('lang_dir') + '/messages.pot' + ' -d ' + grunt.option('lang_dir') + ' -l ' + lang;
            }
        }
    }
};