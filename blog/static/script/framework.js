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

  url += "/" + relative_path;
  return url;
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
// form functions
// ----------------------------------------------------------------------------
function prefill_form(values) {
  alert(Object.keys($(':input')));

  $(':input').each(function () {


    alert('INPUT: ' + $(this).attr('type'));
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

function initialize_tinymce(editor_id, selector, clear_button_id, revert_button_id, css_sheets) {
  var params = {
    auto_focus: editor_id,
    selector: selector,
    plugins: 'advlist anchor autoresize autosave charmap code contextmenu emoticons hr image link media paste preview save searchreplace tabfocus table textcolor visualblocks wordcount',
    autoresize_min_height: 300,
    autoresize_max_height: 600,
    width: "100%",
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
  tinymce_clear = function () {
    tinyMCE.get(editor_id).setContent('');
  };
  $('#' + clear_button_id).click(tinymce_clear);

  // revert editor window function
  tinymce_revert = function () {
    tinyMCE.get(editor_id).setContent(original_state);
  };
  $('#' + revert_button_id).click(tinymce_revert);
}