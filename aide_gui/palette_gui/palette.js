function sendInfoToFusion(action, src){
    var command = {
        type: action,
        link: src
    };
    adsk.fusionSendData('send', JSON.stringify(command));
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

// activate the datatable when ready
$(document).ready( function () {
    $('#myTable').DataTable();
} );
