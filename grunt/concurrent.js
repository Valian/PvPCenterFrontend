module.exports = {

    // Task options
    options: {
        limit: 3
    },

    // Dev tasks
    devFirst: [
        'clean'
    ],

    // Production tasks
    prodFirst: [
        'clean'
    ],

    // Image tasks
    imgFirst: [
        'imagemin'
    ]
};