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

// ----------------------------------------------------------------------------
// EventLib
// ----------------------------------------------------------------------------
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

// ----------------------------------------------------------------------------
// Form
// ----------------------------------------------------------------------------

// \name Form
// \description new form object; takes an object with named arguments
//
// \param[args.id]      id to reference form element
// \param[args.action]  action for form upon submission
// \param[args.method]  method (e.g. "post")
// \param[args.csrf]    csrf token from Django (optional)
// \param[args.body]    url to api for retrieving form body (optional)
function Form(args)
{
  // create form element, but don't add to document yet
  this.node = document.createElement("form");

  if (typeof args !== "undefined" && "id" in args)
  {
    this.node.id = args.id;
  }

  if (typeof args !== "undefined" && "action" in args)
  {
    this.node.action = args.action;
  }

  if (typeof args !== "undefined" && "method" in args)
  {
    this.node.method = args.method;
  }

  // add csrf token input value
  if (typeof args !== "undefined" && "csrf" in args)
  {
    // create a temporary div container to convert csrf string to DOM element
    var csrf_container = document.createElement("div");
    csrf_container.innerHTML = args.csrf;

    this.node.appendChild(csrf_container.firstChild);
    this.node_csrf = csrf_container.firstChild;
  }

  // create table to organize form elements
  this.node_tbody = document.createElement("tbody");

  var form_table = document.createElement("table");
  form_table.appendChild(this.node_tbody);
  this.node.appendChild(form_table);

  // populate form table with form body if provided
  if (typeof args !== "undefined" && "body" in args)
  {
    this.getBody(args.body);
  }
}

Form.prototype = {
  constructor: Form,

  node: null, // reference to form element
  node_submit: null, // reference to submit element
  node_tbody: null, // reference to table inside form
  node_csrf: null, // reference to csrf token element

  submit_button: null, // reference to submit button element

  // \name Form.getBody
  // \description populate the form body with data from url
  //
  // \param[url]  url to get form body JSON
  // \param[row]  row to insert into table (defaults to append)
  getBody: function (url, row)
  {
    var obj = this; // used in formBodyToElement

    var formBodyToElement = function(data)
    {
      obj.node_tbody.innerHTML = data.form;
    };
    ajax({ url: url,
           method: "get",
           callback: formBodyToElement,
           asynch: false});
  },

  // \name Form.addSubmitButton
  // \description add a submit button
  //
  // \param["id"]     (optional) id on submit button, defaults to "submit"
  // \param["value"]  text to display on button, defaults to "Submit"
  // \param["row"]    (optional) row to insert, defaults to append
  addSubmitButton: function (args)
  {
    this.submit_button = document.createElement("button");

    this.submit_button.id = (typeof args !== "undefined" && "id" in args) ? args.id : "submit";
    this.submit_button.innerText = (typeof args !== "undefined" && "value" in args) ? args.value : "Submit";

    var last_row = this.node_tbody.insertRow(-1);
    last_row.insertCell(0);

    last_row.cells[0].appendChild(this.submit_button);
  },

  // \name Form.addElement
  // \description add an element to the form at a specified row/column
  //
  // \param[element]  (DOM) element to add to form
  // \param[row]      row of table to insert (defaults to append)
  // \param[col]      column of table to insert (defaults to 0)
  addElement: function (args)
  {
    var row = -1;
    if ("row" in args && args.row >= 0 && args.row < this.node_tbody.rows.length)
    {
      row = args.row;
    }

    var col = 0;
    if ("col" in args && args.col > 0)
    {
      col = args.col;
    }

    var last_row = this.node_tbody.insertRow(row);
    last_row.insertCell(col);
    last_row.cells[col].appendChild(args.element);
  },

  // \name Form.getValues
  // \description take all values of input elements on the form and place
  // them into a single object. The keys of the object are the input names
  // and the values of the object are the input values.
  getValues: function ()
  {
    var values = {};

    for (var i = 0; i < this.node.elements.length; i++)
    {
      if (this.node.elements[i].tagName.toLowerCase() != "input" &&
          this.node.elements[i].tagName.toLowerCase() != "select" &&
          this.node.elements[i].tagName.toLowerCase() != "textarea")
      {
        continue;
      }

      values[this.node.elements[i].name] = this.node.elements[i].value;
    }

    return values;
  },
}