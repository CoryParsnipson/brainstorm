// javascript code for django blog app
// Cory Parsnipson, 2014

// \name getBeParams
// \description the backend will pass parameters through hidden fields when
// necessary. Use this to find all be parameters and gather them into an
// associative array.
//
// \returns associative array of all passed back end parameters
function getBeParams()
{
  var i = 0;
  var inputs = document.getElementsByTagName("input");
  var be_vars = {};

  for (i = 0; i < inputs.length; i++)
  {
    if (inputs[i].type != "hidden" || inputs[i].name.substring(0, 3) != "be_")
    {
      continue;
    }

    be_vars[inputs[i].name] = inputs[i].value;
  }

  return be_vars;
}

var EventLib = {
  // \name addEvent
  // \description cross browser function for adding event listeners to
  // DOM elements
  //
  // \param[target]      DOM element to add to
  // \param[event_name]  name of event to add ("click", "load", etc)
  // \param[handler]     reference to function to execute
  addEvent: function (target, event_name, handler)
  {
    if (target.addEventListener)
    {
      target.addEventListener(event_name, handler, false);
    }
    else if (target.attachEvent)
    {
      // IE <9 support
      target.attachEvent("on" + type, handler);
    }
    else
    {
      target["on" + type] = handler;
    }
  },

  // \name removeEvent
  // \description cross browser for removing event listeners
  //
  // \param[target]      DOM element to remove from
  // \param[event_name]  name of event to remove ("click", "load", etc)
  // \param[handler]     reference to function (must be same reference added)
  removeEvent: function (target, event_name, handler)
  {
    if (target.addEventListener)
    {
      target.removeEventListener(event_name, handler, false);
    }
    else if (target.detachEvent)
    {
      // IE <9 support
      target.detachEvent("on" + type, handler);
    }
    else
    {
      target["on" + type] = null;
    }
  }
}

// \name createForm
// \description create a form html element with the supplied id,
// action, and method attributes. One may also supply a csrf token for
// django csrf token middleware. Takes an object with the below fields:
//
// \param[id]          id of the form element
// \param[action]      url to open upon form submission
// \param[method]      usually "post"
// \param[csrf_token]  string value of csrf token (usually from django backend)
// \param[form_body]   string containing html of form contents
// \param[submit]      value for submit button
//
// \returns form element
function createForm(args)
{
  var id = args.id;
  var action = args.action;
  var method = args.method;
  var csrf_token = args.csrf_token;
  var form_body = args.form_body;
  var submit = args.submit;

  var form = document.createElement("form");

  if (typeof id !== 'undefined')
  {
    form.id = id;
  }

  if (typeof action !== 'undefined')
  {
    form.action = action;
  }
  else
  {
    form.action = "";
  }

  if (typeof method !== 'undefined')
  {
    form.method = method;
  }
  else
  {
    form.method = "post";
  }

  // add csrf token
  if (typeof csrf_token !== 'undefined')
  {
    form.innerHTML = csrf_token;
  }

  // a form will be organized by table always
  var form_table = document.createElement("table");
  var form_tbody = document.createElement("tbody");
  form_table.appendChild(form_tbody);
  form.appendChild(form_table);

  // populate form content body
  form_tbody.innerHTML = form_body;

  // add submit button
  var submit_field = document.createElement("button");
  submit_field.id = "id_submit";
  submit_field.type = "submit";
  submit_field.innerText = (typeof submit !== 'undefined') ? submit : "Submit";

  var last_row = form_tbody.insertRow(-1); // -1 to append row to end of tbody
  last_row.insertCell(0);
  last_row.cells[0].appendChild(submit_field);

  return form;
}