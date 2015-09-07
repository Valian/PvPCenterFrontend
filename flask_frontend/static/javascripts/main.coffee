ready = ->
  # Disable blank link action
  $('a[href="#"]').on 'click', (event) ->
    event.preventDefault()
  # Modal vertical center
  $('#myModal').on 'shown.bs.modal', (e) ->
    dialog = $(this).find('.modal-dialog')
    dialogHeight = dialog.height()
    dialogMarginTop = (dialog.outerHeight(true) - dialogHeight) / 2
    dialogTranslate = ($(window).height() - dialogHeight) / 2 - dialogMarginTop
    if dialogTranslate > 0
      dialog.css
        'transform': 'translateY(' + dialogTranslate + 'px)'
        '-ms-transform': 'translateY(' + dialogTranslate + 'px)'
        '-webkit-transform': 'translateY(' + dialogTranslate + 'px)'
  # Events list tab
  $('.events-list .events-menu a').on 'click', (event) ->
    event.preventDefault()
    node = $(this)
    # Check if mobile version
    mobile = $('.events-list .controller').is(':visible')
    # Mobile click only on controller icon
    if mobile and $(this).hasClass('controller')
      controlers = $('.events-list .events-menu a').not('.controller')
      controlers.not('.active').addClass('active').siblings().removeClass 'active'
      $(this).toggleClass 'fa-flip-horizontal'
    else if !$(this).hasClass('active')
      $(this).siblings().not('.controller').removeClass 'active'
      $(this).addClass 'active'
      $('.events-list .controller').toggleClass 'fa-flip-horizontal'
    $('.tab').fadeOut 'fast', ->
      $(node.attr('data-for')).fadeIn 'fast'
  # Filter toggle
  $('.filter-toggle').on 'click', ->
    $(this).toggleClass 'open'
    filterHeight = $(this).next('.filter').children('form').height() + 10
    if $(this).hasClass('open')
      $(this).next('.filter').css 'height', filterHeight + 'px'
    else
      $(this).next('.filter').css 'height', '0px'
  # Search input
  $('.search-toggle a').on 'click', ->
    $(this).children('i').toggleClass 'fa-search'
    $(this).children('i').toggleClass 'fa-times'
    $('.search-input').toggleClass 'open'
  #Rotator
  $('#rotator.work').owlCarousel
    navigation: true
    navigationText: [
      '<span class=\'glyphicon glyphicon-chevron-left icon-white\'></span>'
      '<span class=\'glyphicon glyphicon-chevron-right icon-white\'></span>'
    ]
    slideSpeed: 300
    paginationSpeed: 400
    singleItem: true
  # StickyNav onReady
  stickyNav()
  # Tooltip
  #$('.tooltip-btn').tooltip
  #  placement: 'bottom'
  #  container: 'body'

  # Profile edit new icon
  $('.icons .new').each ->
    lh = $(this).width()
    $(this).find('i').css 'line-height': lh + 'px'

searchWidth = ->
  $('#main-menu .nav').width() - $('.search-toggle').width() - 5 - ($('.search-input input').outerWidth(true) - $('.search-input input').width())


stickyNav = ->
  if window.pageYOffset >= 80
    $('#site-header').addClass 'sticky'
  else
    $('#site-header').removeClass 'sticky'

$(document).ready ready
$(document).on 'page:load', ready

$(window).scroll ->
  stickyNav()

$(document).on 'click', '.search-toggle a', ->
  $('.search-input input').width searchWidth()

$(document).pjax 'a[data-pjax]'

$(document).on 'submit', 'form[data-pjax]', (event) ->
  $.pjax.submit(event, $(this).attr('data-pjax'))
