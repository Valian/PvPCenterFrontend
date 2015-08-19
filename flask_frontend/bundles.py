# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)

from flask_assets import Environment, Bundle

static = '../static/'
bower = '../../bower_components/'

bundles = {
    'main_js': Bundle(
        static + 'javascripts/*.coffee',
        '../blueprints/**/javascripts/*.coffee',
        filters=['coffeescript', 'rjsmin'], output='js/main.min.js'),
    'libs_js': Bundle(
        bower + 'jquery/dist/jquery.min.js',
        bower + '*/dist/**/*.min.js',
        bower + 'owlcar/owl-carousel/*.min.js',
        output='js/libs.min.js'),
    'css': Bundle(
        static + 'stylesheets/*.less',
        filters=['less'], output='stylesheets/styles.css'),
    'libs_css': Bundle(
        bower + 'bootstrap/dist/css/bootstrap.css',
        bower + 'bootstrap/dist/css/bootstrap-theme.css',
        bower + 'components-font-awesome/css/font-awesome.css',
        bower + 'flag-icon-css/css/flag-icon.css',
        bower + 'owlcar/owl-carousel/*.min.css',
        output='stylesheets/lib_styles.css')
}


def create_bundles(app):
    assets = Environment(app)
    for name, bundle in bundles.items():
        assets.register(name, bundle)