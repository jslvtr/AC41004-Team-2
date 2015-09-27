function populate_colleges()
{
    uni = $("#university").val();
    $("#college").empty();
    $("#course").empty();
    $.ajax({
        type: "GET",
            url: "/populate-colleges/" + uni,
            datatype: 'json',
            success: function(colleges)
            {
                $.each(colleges.colleges, function(key, value){
                $("#college").append('<option value="' + value + '">' + value + '</option>');
                });
                 populate_courses($("#college").val());
            }
    });
}

function populate_courses()
{
    uni = $("#university").val();
    college = $("#college").val();
    $.ajax({
        type: "GET",
            url: "/populate-courses/" + uni + "/" + college,
            datatype: 'json',
            success: function(courses)
            {
                $.each(courses.courses, function(key, value){
                $("#course").append('<option value="' + value + '">' + value + '</option>');
                });
            }
    });
}

function add_university()
{
    uni = $("#unitoadd").val();
    data = {uni: uni};
    $.ajax({
        type: "POST",
            url: "/add-uni",
            data: JSON.stringify(data),
            processData: false,
            contentType: "application/json",
            success: function(ss)
            {
                $("#university").append('<option value="' + uni + '">' + uni + '</option>');
            }
        });
}

function delete_university()
{

    confirm = window.confirm("Are you sure you wish to delete this university? All departments and courses will also be deleted.");

    if (confirm == true)
    {
    uni = $("#university").val();
    $.ajax({
            type: "DELETE",
            url: "/remove-uni/" + uni,
            success: function(ss){
                                       $("#university").find('option[value=\'' + uni + '\']').remove()
                                 }
        });
    }

}

function add_college()
{
    uni = $("#university").val();
    college = $("#collegetoadd").val();
    data = {uni: uni, college: college};
    $.ajax({
        type: "POST",
            url: "/add-college",
            data: JSON.stringify(data),
            processData: false,
            contentType: "application/json",
            success: function(ss)
            {
                $("#college").append('<option value="' + college + '">' + college + '</option>');
            }
        });
}

function delete_college()
{
    uni = $("#university").val();
    college = $("#college").val();
    $.ajax({
            type: "DELETE",
            url: "/remove-college/" + uni + "/" + college,
            success: function(ss){
                                       $("#college").find('option[value=\'' + college + '\']').remove()
                                 }
        });
}

function add_course()
{
    uni = $("#university").val();
    college = $("#college").val();
    course = $('#coursetoadd').val();
    data = {uni: uni, college: college, course: course};
    $.ajax({
        type: "POST",
            url: "/add-course",
            data: JSON.stringify(data),
            processData: false,
            contentType: "application/json",
            success: function(ss)
            {
                $("#course").append('<option value="' + course + '">' + course + '</option>');
            }
        });
}

function delete_course()
{
    uni = $("#university").val();
    college = $("#college").val();
    course = $("#course").val();
    $.ajax({
            type: "DELETE",
            url: "/remove-course/" + uni + "/" + college + "/" + course,
            success: function(ss){
                                       $("#course").find('option[value=\'' + course + '\']').remove()
                                 }
        });
}

$( document ).ready(function() {
    populate_colleges($("#university").val());
});
