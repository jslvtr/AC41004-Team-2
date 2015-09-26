function populate_colleges()
{
    $uni = $("#university").val();
    $.ajax({

        type: "GET",
            url: "/populate-colleges/" + $uni,
            data: $uni,
            success: function(colleges)
            {

                $("#college").empty();
                $.each(colleges, function(key, value){
                $("#college").append('<option value="' + value + '">' + value + '</option>');
                });
                 populate_courses($("#college").val());
            }
    });
}

function populate_courses()
{
    $uni = $("#university").val();
    $college = $("#college").val();
    $.ajax({
        type: "GET",
            url: "/populate-courses/" + $uni + "/" + $college,
            data: $uni,
            success: function(courses)
            {
                $("#course").empty();
                $.each(courses, function(key, value){
                $("#course").append('<option value="' + value + '">' + value + '</option>');
                });
            }
    });
}



$( document ).ready(function() {
    populate_colleges($("#university").val());
});
