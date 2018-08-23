$(document).ready(function() {

  // Markdown Editor
  let element = document.getElementById('field-notes')
  if (element) {
    let editor = new SimpleMDE({element: element})
    document.querySelector('span.editor-info-block').style.display = 'none'
  }

  // Related stories
  $('#field-related-stories').select2({
    placeholder: 'Click to get a drop-down list or start typing a story title'
  })

  // Groups
  $('#field-groups').select2({
    placeholder: 'Click to get a drop-down list or start typing a group title'
  })

})
