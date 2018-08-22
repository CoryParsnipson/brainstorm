// common javascript functionality
// Cory Parsnipson, 2015

// ----------------------------------------------------------------------------
// init function
// ----------------------------------------------------------------------------
$(function () {
  init_flash_messages();
  init_editable();
});

// ----------------------------------------------------------------------------
// general lib functions
// ----------------------------------------------------------------------------
function get_absolute_url(relative_path) {
  if (relative_path.slice(0, 4) == 'http') {
    // if relative path is actually an absolute url, don't do anything
    return relative_path;
  }

  var url = window.location.protocol + "//";
  url += window.location.hostname;

  // account for slashes
  relative_path = relative_path.replace('\\', '/');

  if (relative_path.indexOf('/') != 0) {
    url += "/";
  }

  url += relative_path;
  return url;
}

// ----------------------------------------------------------------------------
// flash message functions
// ----------------------------------------------------------------------------

// fade out messages one by one after a certain amount of time
function fade_flash_messages() {
  var messages = $('ul.messages li');
  $(messages[0])
    .delay(2000)
    .fadeTo(1000, 0)
    .slideUp(400)
    .queue(function () { $(this).remove(); fade_flash_messages(); });
}

// setup mouseover pause on flash messages
function pause_flash_message_fade() {
  $('ul.messages').hover(
    function () {
      var first_li = $(this).children('li')[0];

      if ($(first_li).css('opacity', 0)) {
        $(first_li).stop(true, false).slideDown(400);
      }

      if (!$(first_li).css('opacity', 1)) {
        $(first_li).fadeTo(400, 1);
      }
    },
    fade_flash_messages
  );
}

function init_flash_messages() {
  pause_flash_message_fade();
  fade_flash_messages();
}

// add a flash message to the flash message area
// msg - contents of message
// msg_type - can be either "success", "error", or "warning"
function add_flash_message(msg, msg_type, enable_fade) {
  enable_fade = typeof enable_fade !== 'undefined' ? enable_fade : false;

  if (msg_type != "success" && msg_type != "error" && msg_type != "warning") {
    msg_type = "warning";
  }

  $('ul.messages').append('<li class="' + msg_type + '">' + msg + '</li>');

  if (enable_fade) {
    init_flash_messages();
  }
}

// modify String prototype with sprintf like equivelant
// (stackoverflow.com/questions/610406/javascript-equivalent-to-printf-string-format)
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
// dashboard editable list / editable control functions
// ----------------------------------------------------------------------------
function init_editable() {
  editable_delete_confirmation();
  editable_check_all('check-all');

  // get all checkboxes inside .editable-list with name="id"
  $('.editable-list :input[type="checkbox"][name="id"]').each(editable_check_id);
}

function editable_delete_confirmation() {
  // add confirm on delete for delete button
  $('.editable-control').delegate('button[value$="delete"]', 'click', function () {
    var msg = 'Really delete?';
    var result = confirm(msg);

    if (!result) {
      return false;
    }
  });
}

// when the value of the check-all checkbox (at top editable control div) changes
// value, make all the id checkboxes change too. Make container div clickable for
// more area as well
function editable_check_all(id_check_all) {
  var check_all_func = function () {
    var checkbox_all = $('#' + id_check_all);
    var check_all_value = checkbox_all.prop('checked');

    checkbox_all.prop('checked', !check_all_value);
    $('.editable-list input[type="checkbox"][name="id"]').each(function () {
      $(this).prop('checked', check_all_value);
    });
  };

  var check_all_container_func = function () {
    var checkbox_all = $('#' + id_check_all);
    var check_all_value = !checkbox_all.prop('checked');

    checkbox_all.prop('checked', check_all_value);
    $('.editable-list input[type="checkbox"][name="id"]').each(function () {
      $(this).prop('checked', check_all_value);
    });
  };

  $('#' + id_check_all).click(check_all_func);
  $('#' + id_check_all).parent().click(check_all_container_func);
}

// make the checkbox area around the id checkboxes in the editable list table area
// clickable for easier usage. NOTE: id_checkbox is jquery element, NOT string
function editable_check_id() {
  var checkbox_id = $(this);
  var check_id_func = function () {
    var check_id_value = checkbox_id.prop('checked');
    checkbox_id.prop('checked', !check_id_value);
  };

  $(this).click(function () {
    var checked_val = $(this).prop('checked');
    $(this).prop('checked', !checked_val);
  });
  $(this).parent().click(check_id_func);
}

// ----------------------------------------------------------------------------
// reading list book search prefill
// ----------------------------------------------------------------------------

function book_search_enter_triggered(event) {
  if (event.which == 13)
    book_search(event);
}

// run an ajax call to the amazon product api through slackerparadise RPC
function book_search(event) {
  // show ajax loader
  $('#book-results .loader').css({ 'display': 'block' });

  $.ajax({
    url: $('#book-search-url').val() + $('#book-search-bar').val() + '?n=3',
    method: "get",
    dataType: 'json',
    success: fillout_book_data,
    error: function () {
      add_flash_message('Book Search API Error', 'error', true);

      // re-hide loading gif
      $('#book-results .loader').css({ 'display': 'none' });
    },
  });
}

// ajax success callback that takes the Amazon product JSON data and populates
// a target div with the formatted output
function fillout_book_data(data) {
  results_html = "";

  book_preview_html = "<div class='book-book-result book-book-result-hover group'>";
  book_preview_html += "<a id='{0}' class='overlay' href='#'></a>";
  book_preview_html += "<img src='{1}' class='left'>";
  book_preview_html += "<p class='title'>{2}</p>";
  book_preview_html += "<p class='author'>{3}</p>";
  book_preview_html += "<a class='link' href='{4}' target='_blank' title='Open External Link'></a>";
  book_preview_html += "</div>";

  if (data.length == 0) {
    results_html = "<div class='book-book-result'>";
    results_html += "<p class='empty center-align'>No results found.</p>";
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

  document.getElementById('book-results').innerHTML = results_html;

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

// given a tinymce editor instance, get the contents of the editor
// window
function tinymce_snapshot(editor) {
  editor.on('loadContent', function () {
    // save snapshot on load for "revert changes" button
    original_state = editor.getContent();
  });
}

// closure containing function handler for file upload management
tinymceFileBrowser = function (upload_url, filename_url) {
  return function (field_name, url, type, win) {
    // remember tinymce elements to place url into
    var lfieldname = field_name;
    var lwin = win;

    // create OS file browser
    var file_upload = document.createElement("input");
    file_upload.type = "file";
    file_upload.name = "file_upload";
    file_upload.style.display = "none";
    file_upload.click();  // open os dialog window

    // add event listener to "ok" button on file browser window to do actual upload
    $('button:contains("Ok")').click({ file_upload: file_upload }, function (event) {
      var formData = new FormData();
      formData.append('file_upload', event.data.file_upload.files[0]);
      formData.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());

      $.ajax({
        url: upload_url,
        async: false,
        method: "post",
        data: formData,
        contentType: false,
        processData: false,
        success: function (data) {
        },
        error: function (data) {
          add_flash_message(JSON.stringify(data), 'error', false);
        },
      });
    });

    // fill out url
    $(file_upload).change({ file_upload: file_upload }, function () {
      $.ajax({
        url: filename_url + encodeURIComponent(file_upload.value),
        method: "get",
        success: function (filename) {
          lwin.document.getElementById(lfieldname).value = get_absolute_url(filename);
        },
        error: function () {
          add_flash_message('Invalid image filename...', 'error', true);
        },
      });
    });
  };
}

// function to summon a tinymce editor window on the page
// you need to specify the target DOM element to place the window along
// with some key parameters. The function body contains more tinymce
// specific parameters
function initialize_tinymce(params) {
  var default_params = {
    clear_button_id: params.clear_button_id || 'button-clear',
    revert_button_id: params.revert_button_id || 'button-revert',
    upload_url: $('#id_upload_url').val() || '/api/upload/',
    filename_url: $('#id_filename_url').val() || '/api/generate_upload_filename/full/',
  }

  var default_mce_params = {
    auto_focus: params.auto_focus || '',
    selector: params.selector || 'textarea.editor',
    plugins: params.plugins || 'advlist anchor autoresize autosave charmap code contextmenu emoticons hr image link ' +
                               'media paste preview save searchreplace tabfocus table textcolor visualblocks wordcount ',
    plugin_preview_width: params.plugin_preview_width || 620,
    plugin_preview_height: params.plugin_preview_height || 400,
    autoresize_min_height: params.autoresize_min_height || 300,
    autoresize_max_height: params.autoresize_max_height || 600,
    content_css: params.content_css || '',
    resize: params.resize || false,
    menubar: params.menubar || false,
    skin: params.skin || 'light',
    relative_urls: params.relative_urls || false,
    font_formats: params.font_formats || "Roboto=Roboto;Arial=arial,'Helvetica Neue',sans-serif;" +
                                         "Courier New=courier new,courier;Comic Sans MS=comic sans ms,sans-serif;" +
                                         "Helvetica=helvetica;Times New Roman=times new roman,times;",
    toolbar: params.toolbar || ['undo redo forecolor backcolor outdent indent bullist numlist ' +
                                'link image media emoticons charmap visualblocks',
                                'removeformat styleselect formatselect fontselect fontsizeselect preview code'],
    setup: params.setup || tinymce_snapshot,
    file_browser_callback: params.file_browser_callback ||
      tinymceFileBrowser(default_params.upload_url, default_params.filename_url),
  };

  // initialize editor window
  tinymce.init(default_mce_params);

  // clear editor window function
  if (default_params.clear_button_id) {
    tinymce_clear = function () {
      tinyMCE.get(default_mce_params.auto_focus).setContent('');
    };
    $('#' + default_params.clear_button_id).click(tinymce_clear);
  }

  // revert editor window function
  if (default_params.revert_button_id) {
    tinymce_revert = function () {
      tinyMCE.get(default_mce_params.auto_focus).setContent(original_state);
    };
    $('#' + default_params.revert_button_id).click(tinymce_revert);
  }
}
