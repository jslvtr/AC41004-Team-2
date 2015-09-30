
    function delete_event(id)
    {
        $.ajax({
          type: "DELETE",
          url: "/admin/event/"+id,
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
            url: "/admin/event",
            data: $("#event_edit_form"+id).serialize(),
            processData: false,
            contentType: "application/x-www-form-urlencoded",
            success: function(ss){location.reload();},
        });
    }

    function add_event(id)
    {
        var formData = $("#event_edit_form"+id);
        var sdf = formData.find('#description'+id);
        var xx = sdf.val(tinyMCE.get('description'+id).getContent());
        $.ajax({
            type: "POST",
            url: "/admin/event",
            data: $("#event_edit_form"+id).serialize(),
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
          url: "/admin/article/"+id,
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
            url: "/admin/article/",
            data: $("#article_edit_form"+id).serialize(),
            processData: false,
            contentType: "application/x-www-form-urlencoded",
            success: function(ss){location.reload();},
        });
    }

    function add_article(id)
    {
        var formData = $("#article_edit_form"+id);
        var sdf = formData.find('#summary'+id);
        var xx = sdf.val(tinyMCE.get('summary'+id).getContent());
        $.ajax({
            type: "POST",
            url: "/admin/article/",
            data: $("#article_edit_form"+id).serialize(),
            processData: false,
            contentType: "application/x-www-form-urlencoded",
            success: function(ss){
                                       location.reload();
                                 },
        });
    }

    function change_attended(name, event, object) {
    $.ajax({
            type: "GET",
            url: "/admin/update-attended/" + name + "/" + event,
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

    function remove_permission(name, object) {
        $.ajax({
            type: "DELETE",
            url: "/admin/permissions/" + name,
            success: function(ss){
                                       $(object).parents("tr").remove()
                                 }
        });
    }

    function add_permission() {
        object = $('#add-permission');
        access = [];
        if ($("#admin-permission").is(":checked")) {
            access.push("admin");
        }
        if ($("#user-permission").is(":checked")) {
            access.push("user");
        }
        if ($("#events-permission").is(":checked")) {
            access.push("events");
        }
        if ($("#articles-permission").is(":checked")) {
            access.push("articles");
        }
        data = {name: $("#new-permission").val(),
                access: access};
        $.ajax({
            type: "POST",
            url: "/admin/permissions",
            data: JSON.stringify(data),
            processData: false,
            contentType: "application/json",
            success: function(ss){
                                       if(ss.error)
                                       {
                                            alert("Please enter a permission name");
                                       }
                                       else
                                       {
                                            location.reload();
                                       }
                                 }
        });
    }

    function remove_point_type(name, object) {
        $.ajax({
            type: "DELETE",
            url: "/admin/point_types/" + name,
            success: function(ss){
                                       $(object).parents("tr").remove()
                                 }
        });
    }

    function add_point_type() {
        object = $('#add-point-type');
        access = [];
        data = {name: $("#new-point-type").val()};
        $.ajax({
            type: "POST",
            url: "/admin/point_types",
            data: JSON.stringify(data),
            processData: false,
            contentType: "application/json",
            success: function(ss){
                                       location.reload();
                                 }
        });
    }




