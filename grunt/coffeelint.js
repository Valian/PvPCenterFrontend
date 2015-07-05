module.exports = {

    options: {
        reporter: require('coffeelint-stylish')
    },

    main: [
        'flask_frontend/static/javascripts/*.coffee'
    ]
};