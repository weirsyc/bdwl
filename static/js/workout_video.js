var comm = new Icecomm('C17ZYAPgzmzVAa2l3dLDe6VMjsm/QHu7Z9DF0qmJEHboXPDy');
//TODO: room name

$(function(){
    $('#chatWindowWrapper').hide();
    $('#localWrapper').hide();
    $('#remoteWrapper').hide();
    $('#messageBox').hide();
    $('#disableCamera').hide();
    $('label').tooltip({placement : 'top'});

    $('#messageForm').submit(function(event) {
        var message = ": " + $('#message').val();
        console.log(message);
        comm.send("<p id=\"chatElement\">" + message + "</p>");
        $("<p id=\"chatElement\">" + message + "</p>").hide().appendTo('#chatWindow').fadeIn(1000);
        event.preventDefault();
        return false;
    });
});

comm.on('local', function(options) {
    console.log(options);
    localVideo.src = options.stream;
    $('#localWrapper').slideDown("slow");
    $('#disableCamera').show();
    $('#connect').hide();
});

comm.on('connected', function(options) {
    remoteVideo.src = options.stream;
    $('#chatWindowWrapper').slideDown("slow");
    $('#messageBox').slideDown("slow");
    $('#remoteWrapper').slideDown("slow");
    comm.send("<p id=\"chatElement\">Another user has joined the call.</p>");
});

comm.on('disconnect', function(options) {
    $('#chatWindow').append("<p id=\"chatElement\">User has disconnected</p>");
    $('#remoteWrapper').hide();
    $('#messageBox').hide();
});

function closeVideo() {
    if (comm.getLocalID()){
        comm.send("<p id=\"chatElement\">User has turned off their camera.</p>");
        comm.send("Hide Remote");
        comm.close();
        $("#localWrapper").slideUp("slow");
        $('#disableCamera').hide();
        $('#connect').text("Enable Camera");
        $('#connect').show();
    }
}
function openVideo() {
    if ($("#localVideo").is(":visible")){
        console.log("Session already exists");
    }
    else {
        //TODO change name here too
        comm.connect('custom room name');
        //console.log(comm.getLocalID());
    }
}
function smallVideo(videoSource) {
    $('#' + videoSource).animate({width: "315px", height: "237px"}, 500);
}
function mediumVideo(videoSource) {
    $('#' + videoSource).animate({width: "550", height: "413px"}, 500);
}
function largeVideo(videoSource) {
    $('#' + videoSource).animate({width: "931px", height: "700px"}, 500);
}

comm.on('data', function(options) {
    if (options.data === "Hide Remote"){
        $('#remoteWrapper').hide();
    }
    console.log(options.data);
    $(options.data).hide().appendTo('#chatWindow').fadeIn(1000);
});
