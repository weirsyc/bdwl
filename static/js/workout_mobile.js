$(function(){
    $.mobile.loading().hide();

    var section_count = $('#section_count').attr("count");
    console.log("Section Count: " + section_count);

    var current_section = 1;
    // Bind the swipeleftHandler callback function to the swipe event on div.box
    $('#workout_section_wrapper').on("swipeleft", swipeleftHandler);
    // Callback function references the event target and adds the 'swipeleft' class to it
    function swipeleftHandler(event){
        if (current_section >= section_count){
            console.log("Next section not found on left swipe.");
            return;
        }
        current_section += 1;
        console.log("SWIPED: " + current_section);
        var toShow = '#section_' + current_section;
        var toHide = '#section_' + (current_section - 1);
        $(toHide).toggle( "slide" );
        $(toShow).toggle( "slide" );
    }
    $('#workout_section_wrapper').on("swiperight", swiperightHandler);
    // Callback function references the event target and adds the 'swiperight' class to it
    function swiperightHandler(event){
        if (current_section <= 1){
            console.log("Previous section not found on right swipe.");
            return;
        }
        current_section -= 1;
        console.log("SWIPED: " + current_section);
        var toShow = '#section_' + current_section;
        var toHide = '#section_' + (current_section + 1);
        $(toHide).toggle( "slide" );
        $(toShow).toggle( "slide" );
    }

    $("#helpInfo").hide();
});


function toggleHelp(){
    if ($("#helpInfo").is(":visible")){
        $("#helpInfo").slideUp(1000);
        $("#help").html("Help");
    }
    else {
        $("#helpInfo").slideDown(1000);
        $("#help").html("Hide");
    }
}