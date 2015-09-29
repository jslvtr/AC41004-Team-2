function check_password(callback)
{
    var password = $("#password").val();
    var data = {password: password};
    $.ajax({
        type: "POST",
        url: "/check-password",
        data: JSON.stringify(data),
        processData: false,
        contentType: "application/json",
        success: function(obj)
        {
            if (obj.error)
                {
                    alert(obj.error)
                } else {
                    callback();
                }
        }
        });
}

function populate_colleges()
{
    var uni = $("#university").val();
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

    var uni = $("#university").val();
    var college = $("#college").val();
    $("#course").empty();
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
check_password(function() {
    var uni = $("#unitoadd").val();
    var data = {uni: uni};
    $.ajax({
        type: "POST",
            url: "/add-uni",
            data: JSON.stringify(data),
            processData: false,
            contentType: "application/json",
            success: function(obj)
            {
            if (obj.error)
                alert(obj.error)
            else
                $("#university").append('<option value="' + uni + '">' + uni + '</option>');
            }
        });
    });
}

function delete_university()
{
check_password(function(){

    var confirm = window.confirm("Are you sure you wish to delete this university? All departments and courses will also be deleted.");

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
});
}

function add_college()
{
check_password(function(){

    var uni = $("#university").val();
    var college = $("#collegetoadd").val();
    var data = {uni: uni, college: college};
    $.ajax({
        type: "POST",
            url: "/add-college",
            data: JSON.stringify(data),
            processData: false,
            contentType: "application/json",
            success: function(obj)
            {
                if (obj.error)
                    alert(obj.error)
                else
                    $("#college").append('<option value="' + college + '">' + college + '</option>');
            }
        });

        });
}

function delete_college()
{
check_password(function(){

    var confirm = window.confirm("Are you sure you wish to delete this department? All courses will also be deleted.");

    if(confirm == true)
    {
    var uni = $("#university").val();
    var college = $("#college").val();
    $.ajax({
            type: "DELETE",
            url: "/remove-college/" + uni + "/" + college,
            success: function(ss){
                                       $("#college").find('option[value=\'' + college + '\']').remove()
                                 }
        });
    }

    });
}

function add_course()
{

check_password(function() {

    var uni = $("#university").val();
    var college = $("#college").val();
    var course = $('#coursetoadd').val();
    var data = {uni: uni, college: college, course: course};
    $.ajax({
        type: "POST",
            url: "/add-course",
            data: JSON.stringify(data),
            processData: false,
            contentType: "application/json",
            success: function(obj)
            {
                if (obj.error)
                    alert(obj.error)
                else
                    $("#course").append('<option value="' + course + '">' + course + '</option>');
            }
        });

});
}

function delete_course()
{
check_password(function() {

    var confirm = window.confirm("Are you sure you wish to delete this course?");

    if(confirm == true)
    {
    var uni = $("#university").val();
    var college = $("#college").val();
    var course = $("#course").val();
    $.ajax({
            type: "DELETE",
            url: "/remove-course/" + uni + "/" + college + "/" + course,
            success: function(ss){
                                       $("#course").find('option[value=\'' + course + '\']').remove()
                                 }
        });
    }

    });
}



$( document ).ready(function() {
    populate_colleges($("#university").val());
});
