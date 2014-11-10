// Javascript code for django blog app
// Cory Parsnipson, 2014

// \name ajax
// \description send an ajax request using javascript
//
// \param[url]       url of ajax request
// \param[method]    "GET" or "POST", etc
// \param[callback]  function to execute upon receiving data
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