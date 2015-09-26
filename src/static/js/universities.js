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

function add_university()
{
    $uni = $("#unitoadd").val();
    data = {uni: $uni};
    $.ajax({
        type: "POST",
            url: "/add-uni",
            data: JSON.stringify(data),
            processData: false,
            contentType: "application/json",
            success: function(ss)
            {
                $("#university").append('<option value="' + $uni + '">' + $uni + '</option>');
            }
        });
}


$( document ).ready(function() {
    populate_colleges($("#university").val());
});
