function populate_colleges(university)
{
    $.ajax({
        type: "GET",
            url: "/populate-colleges/" + university,
            data: university,
            success: function(colleges)
            {
                $("#college").empty();
                $.each(colleges, function(key, value){
                $("#college").append('<option value="' + value + '">' + value + '</option>');
                });
            }
    });
}
