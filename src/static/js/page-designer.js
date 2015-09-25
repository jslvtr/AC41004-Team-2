function PageDesigner(){
    var sidebar;
    var panel;
    var toolbar;

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
                sidebar.find("#sidebar_page_list").append("<li>"+title+"</li>");
            },
        });
    }

    this.delete_page = function(title){

    }

    this.select_page = function(title){

    }

}

var pageDesigner = new PageDesigner();
var ifdsf = 2;
