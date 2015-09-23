function Pagingsys() {
	this.init = function(obj)
	{
		var lis = obj.selector.find(".pages").children("ul").children("li");
		var ul = obj.selector.find(".pages").children("ul");
		var pagination = obj.selector.find(".pagination");
		var inner_html = "";

		ul.empty();

		var test = lis.size()/obj.max_on_one_page;
		for (var i = 0; i<lis.size()/obj.max_on_one_page;i++){
			if (i == 0)
				inner_html += "<div>"
			else
				inner_html += "<div style='display:none'>"

			for (var j = 0; j<obj.max_on_one_page && (i*obj.max_on_one_page)+j < lis.size();j++){
				inner_html +=lis[(i*obj.max_on_one_page)+j].outerHTML;
			}
			inner_html += "</div>"
		}
		ul.html(inner_html);
		obj.selector.__proto__.show_page = this.show_page;
		pagination.append("<ul class='pagination'></ul>");
		pagination = $(pagination.find("ul"));

		for (var i = 0; i < lis.size()/obj.max_on_one_page; i++) {
		    if(i == 0) {
			    pagination.append('<li class="active"><a onclick="$(\''+obj.selector.selector+'\').show_page('+i+', this)" >'+(i+1)+'</li>');
			} else {
			    pagination.append('<li><a onclick="$(\''+obj.selector.selector+'\').show_page('+i+', this)" >'+(i+1)+'</li>');
			}
		}
	}

	this.show_page= function(page, object)
	{
		var lis = this.find(".pages ul").children("div");
		for (var i = 0; i < lis.size(); i++)
			if (lis[i].style["display"] != "none")
				$(lis[i]).hide("fast");
				$(object).parents('ul').children(".active").removeClass("active");
		$(object).parent().addClass("active");
		$(lis[page]).show('slide', {direction: 'right'}, 400);
	}
}

pagingsys = new Pagingsys();