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

// \name createFormContainer
// \description create a form html element with the supplied id,
// action, and method attributes. One may also supply a csrf token for
// django csrf token middleware.
//
// \param[id]          id of the form element
// \param[action]      url to open upon form submission
// \param[method]      usually "post"
// \param[csrf_token]  string value of csrf token (usually from django backend)
// \param[submit]      value for submit button
//
// \returns form element
function createFormContainer(id, action, method, csrf_token, submit)
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

  if (typeof csrf_token !== 'undefined')
  {
    var csrf_field = document.createElement("input");
    csrf_field.hidden = true;
    csrf_field.name = "csrfmiddlewaretoken";
    csrf_field.value = csrf_token;

    form.appendChild(csrf_field);
  }

  var submit_field = document.createElement("input");
  submit_field.type = "submit";
  submit_field.value = (typeof submit !== 'undefined') ? submit : "Submit";
  form.appendChild(submit_field);

  return form;
}