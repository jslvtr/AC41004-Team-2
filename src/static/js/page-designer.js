function PageDesigner(){
    var sidebar;
    var panel;

    this.init = function(obj){
        sidebar = obj.sidebar;
        panel = obj.panel;
        toolbar = obj.toolbar;
    }

    this.add_page = function(title){
        var formData = $("#edit-page-form");
        var sdf = formData.find("#page_content");
        sdf.val(tinyMCE.get('page_content').getContent());

        $.ajax({
            type: "POST",
            url: "/admin/page/add/",
            data: $("#edit-page-form").serialize(),
            success: function(obj){
                if (obj.result != "ok")
                    $("#"+obj.field+"-error-message").html(obj.message)
                else
                    location.reload();
            },
        });
    }

    this.delete_page = function(id){
        $.ajax({
          type: "DELETE",
          url: "/admin/page/"+id,
          success: function(ss){location.reload();},
        });
    }

    this.edit_page = function(){
        var formData = $("#edit-page-form");
        var sdf = formData.find("#page_content");
        sdf.val(tinyMCE.get('page_content').getContent());

        $.ajax({
            type: "PUT",
            url: "/admin/page/edit/",
            data: $("#edit-page-form").serialize(),
            processData: false,
            contentType: "application/x-www-form-urlencoded",
            success: function(obj){
               if (obj.result != "ok")
                    $("#"+obj.field+"-error-message").html(obj.message)
                else
                    location.reload();
            },
        });
    }

}

var pageDesigner = new PageDesigner();
