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
            var list=JSON.parse(data);
            console.log(list);
        }else if (action == 'debugger') {
            debugger;
        }else {
            return 'Unexpected command type: ' + action;
        }
    } catch (e) {
        console.log(e);
        console.log('exception caught with command: ' + action + ', data: ' + data);
    }
    return 'OK';
}};
