// common javascript functionality
// Cory Parsnipson, 2014

// \name ajax
// \description send an ajax request using javascript. Supply an object
// with the following fields:
//
// \param[url]          url of ajax request
// \param[method]       "GET" or "POST", etc
// \param[callback]     function to execute upon receiving data (will receive 1 argument, JSON data)
// \param[data]         send post data (an object)
// \param[asynch]       run ajax request in parallel? (defaults to true)
//
// \returns the XMLHttpRequest object
function ajax(args)
{
  var request = new XMLHttpRequest();

  request.onreadystatechange = function()
  {
    if (request.readyState == 4 && request.status == 200)
    {
      if (typeof args.callback !== "undefined")
      {
        args.callback(JSON.parse(request.responseText));
      }
    }
  }

  var async = true;
  if ("asynch" in args)
  {
    async = args.asynch;
  }

  request.open(args.method, args.url, async);
  if (args.method.toLowerCase() == "post")
  {
    request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    // generate parameter string and send parameters
    var params = "";
    for (var param in args.data)
    {
      // TODO: sanitize!!
      params += encodeURIComponent(param) + "=" + encodeURIComponent(args.data[param]) + "&";
    }
    params = params.substring(0, params.length - 1);

    request.send(params);
  }
  else
  {
    request.send();
  }

  return request;
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

// \name getChildren
// \description returns an array of childen of given element without any
// text nodes (same as .children, but without DOM4 support prereq)
//
// \param[element]  element to count children of
//
// \returns javascript array of child elements
function getChildren(element)
{
  var children = new Array();

  for (var i = 0; i < element.childNodes.length; i++)
  {
    if (element.childNodes[i].nodeType != 1)
    {
      continue;
    }

    children.push(element.childNodes[i]);
  }

  return children;
}