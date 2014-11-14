// common javascript functionality
// Cory Parsnipson, 2014

// \name ajax
// \description send an ajax request using javascript. Supply an object
// with the following fields:
//
// \param[url]        url of ajax request
// \param[method]     "GET" or "POST", etc
// \param[callback]   function to execute upon receiving data (will receive 1 argument, JSON data)
// \param[data]       send post data (an object)
//
// \returns the XMLHttpRequest object
function ajax(args)
{
  var request = new XMLHttpRequest();

  request.onreadystatechange = function()
  {
    if (request.readyState == 4 && request.status == 200)
    {
      args.callback(JSON.parse(request.responseText));
    }
  }

  request.open(args.method, args.url, true);
  if (args.method.toLowerCase() == "post")
  {
    request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    // generate parameter string and send parameters
    var params = "";
    for (var param in args.data)
    {
      // TODO: urlencode this and sanitize
      params += param + "=" + args.data[param] + "&";
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
