// # Creates fields to be displayed in a new window on Fusion 360 based on
// # parameter list in input YAML to solicit parameter values from a user
// def createFields(inputs):
//     # Create a global list called plist to keep track of created fields
//     globals()['plist'] = []
//     # For each parameter {dictionary} in design param list
//     for param in data:
//         # Save the key of the first element as pName
//         pName = list(param.keys())[0]
//         # Get the value [attributes of field] of the key from the dictionary
//         pAttr = param[pName]
//         # Append the created global field to the plist (parameter list)
//         plist.append(pName)
//         # For fields specified by attr type: "string"
//         if pAttr["type"] == "string":
//             # param_format(id, name, default)
//             globals()[pName] = inputs.addStringValueInput(str(pName), pAttr["name"], str(pAttr["default"]))
//         # For fields specified by attr type: "dropdown"
//         elif pAttr["type"] == "dropdown":
//             # param_format(id, name, Dropdown)
//             globals()[pName] = inputs.addDropDownCommandInput(str(pName), pAttr["name"], adsk.core.DropDownStyles.TextListDropDownStyle)
//             # For each element in the list of options
//             for option in pAttr["options"]:
//                 # Append the dropdown option values from input YAML
//                 globals()[pName].listItems.add(str(option), True)
//         # For fields specified by attr type: "spinnerInt"
//         elif pAttr["type"] == "spinnerInt":
//             # param _format(id, Name, min, max, step, default)
//             globals()[pName] = inputs.addIntegerSpinnerCommandInput(str(pName), pAttr["name"], pAttr["options"][0], pAttr["options"][2], pAttr["options"][1], pAttr["options"][0])
//         # For fields specified by attr type: "spinnerFloat"
//         elif pAttr["type"] == "spinnerFloat":
//             # param _format(id, Name, min, max, step, default)
//             globals()[pName] = inputs.addFloatSpinnerCommandInput(str(pName), pAttr["name"], '', pAttr["options"][0], pAttr["options"][2], pAttr["options"][1], pAttr["options"][0])



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
  document.getElementById('p1').innerHTML = data;
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
  console.log(json);
};
