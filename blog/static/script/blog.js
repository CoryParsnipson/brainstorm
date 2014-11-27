// javascript code for django blog app
// Cory Parsnipson, 2014
//
// dependencies: "framework.js"

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