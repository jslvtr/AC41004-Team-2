function QuizJs(){

    this.init = function (init_obj){
        if (init_obj.edit)
            this.init_edit(init_obj)
        else
            this.init_normal(init_obj)
    }

    this.init_edit = function (init_obj){
        var quiz_list = init_obj.obj.find("ul#quiz-question-list");

        for (var i = 0; i < quiz_list.length;i++)
            pagination.append("<li><a onclick='quizJs.selectQuestion(this)'>"+(i+1)+"</a></li>");
    }

    this.init_normal = function (init_obj){
        init_obj.obj.find('.only-quiz-edit-mode').remove();
        var quiz_list = init_obj.obj.find("ul#quiz-question-list").children();
        var pagination = $(init_obj.obj.find("ul.pagination"));

        for (var i = 0; i < quiz_list.length;i++)
            pagination.append("<li><a onclick='quizJs.selectQuestion(this)'>"+(i+1)+"</a></li>");

        var select = $(pagination.children()[0]).children()[0]

        this.selectQuestion(select)
    }

    this.selectQuestion = function(that){
        var pagination = $(that).parent().parent().parent().find("ul.pagination");
        var questions = $(that).parent().parent().parent().find("ul#quiz-question-list").children();
        var me = $(that).parent();
        var i = 0;
        var selected = 0;
        $(pagination).children("li").each(function(){
            i++;
            var sfdf = $(this)
            if($(this)[0] == me[0]    )
                selected=i;
        })
        for (var j = 0; j < questions.length ;j++)
            $(questions[j]).hide();
        $(questions[selected-1]).show();

    }

    this.add_question = function(that){
        var pparent = $(that).parent().parent().parent().find("ul#quiz-question-list");
        var pagination = $(that).parent().parent().parent().find("ul.pagination");
        pagination.append("<li><a onclick='quizJs.selectQuestion(this)'>"+pagination[0].childElementCount+"</a></li>");
        $(pparent).children("li").each(function(){
            $(this).hide();
        })

        $(pparent).append('<li><div id="quiz-question-container">'+
                            ' <a onclick="quizJs.remove_question(this)">delete</a>'+
                            '<div class="only-quiz-edit-mode">'+
                                '<input type="text" name="question_text" >'+
                            '</div>'+
                            '<ul></ul>'+
                            '<div class="only-quiz-edit-mode">'+
                                '<input type="text" id="disabled-text-add-answer" value="Add new answer" onclick="quizJs.add_answer(this)">'+
                            '</div>'+
                         '</div></li>')
        $(parent).find("#disabled-text-add-answer")
    }

    this.add_answer = function(that){
        var ansul = $(that).parent().parent().find("ul")
        ansul.append('<li>'+
                        '<input type="checkbox" name="answer_correct">'+
                        '<input type="text" name="answer_text">'+
                        '<a onclick="quizJs.remove_answer(this)">delete</a>'+
                     '</li>')

    }

    this.remove_answer = function(that){
        $(that).parent().remove();
    }
    this.remove_question = function(that){
        var pagination = $(that).closest("#quiz-container").find("ul.pagination").children();
        $(pagination[pagination.length-1]).remove();
        $(that).parent().parent().remove();
        var bazdmeg = $($(pagination[pagination.length-1]).find("a"));
        this.selectQuestion(bazdmeg[0]);


    }


    this.generate_obj_from_form = function()
    {
            var input_array = $("#edit-quiz-form").serializeArray();
        var new_quiz = new Object();
        new_quiz.questions = [];
        var hello = 1;
        var question_counter = -1;
        var answer_counter = -1;
        var trueholder = false;
        for (var i = 0; i < input_array.length; i++)
        {
            if(input_array[i].name == "id")
                new_quiz._id = input_array[i].value;
            if(input_array[i].name == "quiz_title")
                new_quiz.title = input_array[i].value;
            if(input_array[i].name == "quiz_points")
                new_quiz.points = input_array[i].value;
            if(input_array[i].name == "question_text"){
                question_counter++;
                answer_counter = -1;
                new_quiz.questions[question_counter] = new Object();
                new_quiz.questions[question_counter].question = input_array[i].value;
                new_quiz.questions[question_counter].answers = [];
            }
            if(input_array[i].name == "answer_text"){
                answer_counter++;
                new_quiz.questions[question_counter].answers[answer_counter] = new Object();
                new_quiz.questions[question_counter].answers[answer_counter].answer_text = input_array[i].value;
                new_quiz.questions[question_counter].answers[answer_counter].correct = trueholder;
                trueholder = false;
            }
            if(input_array[i].name == "answer_correct"){
                trueholder = true;
            }
        }
        return new_quiz;
    }

    this.add_quiz = function(){
        var mydata = this.generate_obj_from_form();

        $.ajax({
            type: "POST",
            url: "/admin/quiz",
            data: JSON.stringify(mydata),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function(obj){
                if (obj.result != "ok")
                    $("#"+obj.field+"-error-message").html(obj.message)
                else
                    location.reload();
            },
        });
    }

    this.send_compelted_quiz = function(){
        var mydata = this.generate_obj_from_form();

        $.ajax({
            type: "POST",
            url: "/admin/quiz",
            data: JSON.stringify(mydata),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function(obj){
                if (obj.result != "ok")
                    $("#"+obj.field+"-error-message").html(obj.message)
                else
                    location.reload();
            },
        });
    }

    this.delete_quiz = function(id){
        $.ajax({
          type: "DELETE",
          url: "/admin/quiz/"+id,
          success: function(ss){location.reload();},
        });
    }

    this.edit_quiz = function(){
        $.ajax({
            type: "PUT",
            url: "/admin/quiz",
            data: $("#edit-quiz-form").serialize(),
            success: function(obj){
                if (obj.result != "ok")
                    $("#"+obj.field+"-error-message").html(obj.message)
                else
                    location.reload();
            },
        });
    }



}

var quizJs = new QuizJs();
