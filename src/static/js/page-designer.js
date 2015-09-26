function PageDesigner(){
    var sidebar;
    var panel;

    this.init = function(obj){
        sidebar = obj.sidebar;
        panel = obj.panel;
        toolbar = obj.toolbar;
    }

    this.add_page = function(title){
        $.ajax({
            type: "POST",
            url: "/admin/page/add/"+title,
            success: function(){
                var haha = sidebar.find("#sidebar_page_list");
                sidebar.find("#sidebar_page_list").append("<li><a>"+title+"</a></li>");
            },
        });
    }

    this.delete_page = function(title){

    }

    this.edit_page = function(){
        $.ajax({
            type: "PUT",
            url: "/admin/page/edit/",
            data: $("#edit-page-form").serialize(),
            processData: false,
            contentType: "application/x-www-form-urlencoded",
            success: function(){location.reload();},
        });
    }

}

var pageDesigner = new PageDesigner();
