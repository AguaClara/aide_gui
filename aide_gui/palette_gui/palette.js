function sendInfoToFusion(){
    var args = {
        arg1 : "Sample argument 1",
        arg2 : "Sample argument 2"
    };
    adsk.fusionSendData('send', JSON.stringify(args));
}

window.fusionJavaScriptHandler = {handle: function(action, data){
    try {
        if (action == 'send') {
  // Update a paragraph with the data passed in.
  // document.getElementById('p1').innerHTML = data;
  // this is how were able to retrieve fusion data
  createFields(data);
}
else if (action == 'debugger') {
            debugger;
}
else {
  return 'Unexpected command type: ' + action;
        }
    } catch (e) {
        console.log(e);
        console.log('exception caught with command: ' + action + ', data: ' + data);
    }
    return 'OK';
}};


function createFields(json){
  // console.log(json);
  var list=JSON.parse(json);
  console.log(list);

  // Container <div> where dynamic content will be placed
  var container = document.getElementById("container");
  // Clear previous contents of the container
  while (container.hasChildNodes()) {
      container.removeChild(container.lastChild);
  }
  for (i=0;i<number;i++){
      // Append a node with a random text
      container.appendChild(document.createTextNode("Member " + (i+1)));
      // Create an <input> element, set its type and name attributes
      var input = document.createElement("input");
      input.type = "text";
      input.name = "member" + i;
      container.appendChild(input);
      // Append a line break
      container.appendChild(document.createElement("br"));
  }

};
