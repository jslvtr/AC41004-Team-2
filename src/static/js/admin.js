
    function delete_event(id)
    {
        $.ajax({
          type: "DELETE",
          url: "/event/"+id,
          success: function(ss){location.reload();},
        });
    }

    function update_event(id)
    {
        var formData = $("#event_edit_form"+id);
        var sdf = formData.find('#description'+id);
        var xx = sdf.val(tinyMCE.get('description'+id).getContent());
        $.ajax({
            type: "PUT",
            url: "/event",
            data: $("#event_edit_form"+id).serialize(),
            processData: false,
            contentType: "application/x-www-form-urlencoded",
            success: function(ss){location.reload();},
        });
    }

    function add_event()
    {
        var formData = $("#event_edit_form_new");
        var sdf = formData.find('#description_new');
        var xx = sdf.val(tinyMCE.get('description_new').getContent());
        $.ajax({
            type: "POST",
            url: "/event",
            data: $("#event_edit_form_new").serialize(),
            processData: false,
            contentType: "application/x-www-form-urlencoded",
            success: function(ss){
                                       location.reload();
                                 },
        });
    }


