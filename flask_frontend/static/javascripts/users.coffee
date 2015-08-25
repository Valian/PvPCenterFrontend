loadMenu = (url) ->
  if url == '#'
    return
  $.get url, (data) ->
    $('#profile_content').html(data)
