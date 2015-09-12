loadAsync = (url, target) ->
  if url == '#'
    return
  $.get url, (data) ->
    $(target).html(data)

