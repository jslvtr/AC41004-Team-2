
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





    function delete_article(id)
    {
        $.ajax({
          type: "DELETE",
          url: "/article/"+id,
          success: function(ss){location.reload();},
        });
    }

    function update_article(id)
    {
        var formData = $("#article_edit_form"+id);
        var sdf = formData.find('#summary'+id);
        var xx = sdf.val(tinyMCE.get('summary'+id).getContent());
        $.ajax({
            type: "PUT",
            url: "/article",
            data: $("#article_edit_form"+id).serialize(),
            processData: false,
            contentType: "application/x-www-form-urlencoded",
            success: function(ss){location.reload();},
        });
    }

    function add_article()
    {
        var formData = $("#article_edit_form_new");
        var sdf = formData.find('#summary_new');
        var xx = sdf.val(tinyMCE.get('summary_new').getContent());
        $.ajax({
            type: "POST",
            url: "/article",
            data: $("#article_edit_form_new").serialize(),
            processData: false,
            contentType: "application/x-www-form-urlencoded",
            success: function(ss){
                                       location.reload();
                                 },
        });
    }

    function change_permission(name, access, object) {
        $.ajax({
            type: "GET",
            url: "/admin/permissions/" + name + "/" + access,
            success: function(ss){
                                       if($(object).hasClass('glyphicon-ok')) {
                                            $(object).removeClass('glyphicon-ok');
                                            $(object).addClass('glyphicon-ban-circle');
                                       } else {
                                            $(object).removeClass('glyphicon-ban-circle');
                                            $(object).addClass('glyphicon-ok');
                                       }
                                 }
        });
    }




