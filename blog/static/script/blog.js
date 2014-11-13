// Javascript code for django blog app
// Cory Parsnipson, 2014

// \name ajax
// \description send an ajax request using javascript
//
// \param[url]       url of ajax request
// \param[method]    "GET" or "POST", etc
// \param[callback]  function to execute upon receiving data (will receive 1 argument, JSON data)
//
// \returns reference to javascript XMLHttpRequest object
function ajax(url, method, callback)
{
  var data = null;
  var ajaxRequest = new XMLHttpRequest();

  ajaxRequest.onreadystatechange = function()
  {
    if (ajaxRequest.readyState == 4 && ajaxRequest.status == 200)
    {
      callback(JSON.parse(ajaxRequest.responseText));
    }
  }
  ajaxRequest.open(method, url, true);
  ajaxRequest.send();

  return ajaxRequest;
}

// \name removeElement
// \description given a node, remove it from the DOM tree
function removeElement(node)
{
  if (typeof node === "undefined" || node == null)
  {
    return;
  }
  node.parentNode.removeChild(node);
}

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

// \name getUrlParams
// \description obtain all GET variables passed in for this url
//
// \returns object with key value pairs
function getUrlParams()
{
  // regex for replacing plus with space
  var plus = /\+/g;

  var search = /([^&=]+)=?([^&]*)/g;
  var decode = function(s) { return decodeURIComponent(s.replace(plus, " ")); };

  // "window.location.search" is the query string
  var query = window.location.search.substring(1)

  var urlParams = {};
  while (match = search.exec(query))
  {
    urlParams[decode(match[1])] = decode(match[2]);
  }

  return urlParams;
}

// \name createForm
// \description create a form html element with the supplied id,
// action, and method attributes. One may also supply a csrf token for
// django csrf token middleware.
//
// \param[id]          id of the form element
// \param[action]      url to open upon form submission
// \param[method]      usually "post"
// \param[csrf_token]  string value of csrf token (usually from django backend)
// \param[form_body]   string containing html of form contents
// \param[submit]      value for submit button
//
// \returns form element
function createForm(id, action, method, csrf_token, form_body, submit)
{
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
  var submit_field = document.createElement("input");
  submit_field.type = "submit";
  submit_field.value = (typeof submit !== 'undefined') ? submit : "Submit";

  var last_row = form_tbody.insertRow(-1); // -1 to append row to end of tbody
  last_row.insertCell(0);
  last_row.cells[0].appendChild(submit_field);

  return form;
}