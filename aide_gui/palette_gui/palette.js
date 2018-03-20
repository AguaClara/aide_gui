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
  document.getElementById('demo').innerHTML = list[0];
  console.log(list);
};
