// common javascript functionality
// Cory Parsnipson, 2015

// ----------------------------------------------------------------------------
// init function
// ----------------------------------------------------------------------------
$(function () {
  //$('#id_url').change(fillout_link_preview);
});

// ----------------------------------------------------------------------------
// general lib functions
// ----------------------------------------------------------------------------
function get_absolute_url(relative_path) {
  var url = window.location.protocol + "//";
  url += window.location.hostname;

  if (relative_path.indexOf('/') != 0)
    url += "/";
  url += relative_path;
  return url;
}

// ----------------------------------------------------------------------------
// modify String prototype with sprintf like equivelant
// (stackoverflow.com/questions/610406/javascript-equivalent-to-printf-string-format)
// ----------------------------------------------------------------------------
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

// ----------------------------------------------------------------------------
// link auto fillout functions
// ----------------------------------------------------------------------------
function fillout_link_preview(event) {
  // TODO: finish this function; running into cross origin policy errors
  var link_url = $('#id_url').val();

  fillout_link_field = function (data) {
    alert('hnnng');
  };

  retrieve_error = function (data) {
    // do nothing on error...
  };

  $.ajax({
    url: link_url,
    method: "get",
    dataType: 'jsonp',
    beforeSend: function(xhr) { xhr.setRequestHeader('Access-Control-Allow-Origin', '*'); },
    success: fillout_link_field,
    error: retrieve_error,
  });
}

// ----------------------------------------------------------------------------
// reading list amazon aws prefill
// ----------------------------------------------------------------------------
function aws_search_enter_triggered(event) {
  if (event.which == 13)
    aws_search(event);
}

// run an ajax call to the amazon product api through slackerparadise RPC
function aws_search(event) {
  // show ajax loader
  $('#aws-results .loader').css({ 'display': 'block' });

  $.ajax({
    url: $('#aws-search-url').val() + $('#aws-search-bar').val() + '?n=3',
    method: "get",
    dataType: 'json',
    success: fillout_book_data,
    error: function(data) { alert('boohoo!'); },
  });
}

// ajax success callback that takes the Amazon product JSON data and populates
// a target div with the formatted output
function fillout_book_data(data) {
  results_html = "";

  book_preview_html = "<div class='aws-book-result group'>";
  book_preview_html += "<a id='{0}' class='overlay' href='#'></a>";
  book_preview_html += "<img src='{1}' class='left'>";
  book_preview_html += "<p class='title'>{2}</p>";
  book_preview_html += "<p class='author'>{3}</p>";
  book_preview_html += "<a class='link' href='{4}' target='_blank' title='Open External Link'></a>";
  book_preview_html += "</div>";

  if (data.length == 0) {
    results_html = "<div class='aws-book-result'>";
    results_html += "<p class='author center-align'>No results found.</p>";
    results_html += "</div>";
  }

  values = []
  for (var i = 0; i < data.length; i++) {
    // prepare form values
    values[i] = {
      'id_title': decodeURIComponent(data[i].title).replace(/\+/g, ' '),
      'id_author': decodeURIComponent(data[i].author).replace(/\+/g, ' '),
      'id_link': decodeURIComponent(data[i].url).replace(/\+/g, ' '),
      'id_cover': decodeURIComponent(data[i].cover).replace(/\+/g, ' '),
    };

    results_html += book_preview_html.format(
      'id_prefill_' + i,
      values[i]['id_cover'],
      values[i]['id_title'],
      values[i]['id_author'],
      values[i]['id_link']
    );
  }

  document.getElementById('aws-results').innerHTML = results_html;

  // bind fill form action to overlay links
  for (var i = 0; i < data.length; i++) {
    $('#id_prefill_' + i).click(
      function (idx) {
        return function () { prefill_form('reading-list-form', values[idx]); }
      }(i)
    );
  }
}

// ----------------------------------------------------------------------------
// form functions
// ----------------------------------------------------------------------------

// given a form id, get all the form inputs and populate them with the values
// specified by the values parameter. The values parameter should be an Object
// where the keys are the id attributes of the input elements.
function prefill_form(form_id, values) {
  var inputs = $('#' + form_id + ' :input, textarea');
  inputs.each(function () {
    if ($(this).attr('type') == "hidden") { return; }

    if ($(this).attr('type') == "text" ||
        $(this).attr('type') == "url" ||
        $(this).attr('type') == "password" ||
        this.nodeName.toLowerCase() == "textarea") {
      $(this).val(values[$(this).attr('id')]);
    }

    if ($(this).attr('type') == "checkbox") {
      $(this).prop('checked', values[$(this).attr('id')]);
    }
  });
}

// ----------------------------------------------------------------------------
// tinyMCE functions
// ----------------------------------------------------------------------------
function tinymce_snapshot(editor) {
  editor.on('loadContent', function () {
    // save snapshot on load for "revert changes" button
    original_state = editor.getContent();
  });
}

tinymceFileBrowser = function (field_name, url, type, win) {
  var lfieldname = field_name;
  var lwin = win;

  var file_upload = document.createElement("input");
  file_upload.type = "file";
  file_upload.name = "file_upload";
  file_upload.style.display = "none";

  /* open os dialog window */
  file_upload.click();

  var test = function (data) {
    for (filename in data) {
      lwin.document.getElementById(lfieldname).value = get_absolute_url(data[filename]);
    }
  }

  var post_select = function(event) {
    //mystr = $(file_upload).val();

    var form_action = "{% url 'upload' %}";

    var formData = new FormData();
    formData.append('file_upload', event.data.file_upload[0].files[0]);
    formData.append('csrfmiddlewaretoken', "{{ csrf_token }}");

    $.ajax({
      url: form_action,
      method: "post",
      data: formData,
      contentType: false,
      processData: false,
      success: test,
    });
  }

  $(file_upload).change({file_upload: $(file_upload)}, post_select);
};

function initialize_tinymce(
  editor_id,
  selector,
  clear_button_id,
  revert_button_id,
  css_sheets
)
{
  var params = {
    auto_focus: editor_id,
    selector: selector,
    plugins: 'advlist anchor autoresize autosave charmap code contextmenu emoticons hr image link media paste preview save searchreplace tabfocus table textcolor visualblocks wordcount',
    autoresize_min_height: 300,
    autoresize_max_height: 600,
    content_css: css_sheets,
    resize: false,
    menubar: false,
    skin: "light",
    relative_urls: false,
    font_formats: "Roboto=Roboto;"+
                  "Arial=arial,helvetica,sans-serif;"+
                  "Courier New=courier new,courier;"+
                  "Comic Sans MS=comic sans ms,sans-serif;"+
                  "Helvetica=helvetica;"+
                  "Times New Roman=times new roman,times;",
    toolbar: [
      'undo redo | forecolor backcolor | alignleft aligncenter alignright | superscript subscript | removeformat | outdent indent | blockquote | bullist numlist | table | visualblocks preview code',
      'styleselect formatselect fontselect fontsizeselect | link image media emoticons charmap'
    ],
    setup: tinymce_snapshot,
    file_browser_callback: tinymceFileBrowser,
  };

  // initialize editor window
  tinymce.init(params);

  // clear editor window function
  if (clear_button_id) {
    tinymce_clear = function () {
      tinyMCE.get(editor_id).setContent('');
    };
    $('#' + clear_button_id).click(tinymce_clear);
  }

  // revert editor window function
  if (revert_button_id) {
    tinymce_revert = function () {
      tinyMCE.get(editor_id).setContent(original_state);
    };
    $('#' + revert_button_id).click(tinymce_revert);
  }
}