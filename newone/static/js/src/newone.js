/* Javascript for NewOneXBlock. */
var glob;
var suggest_count = 0;
var input_initial_value = '';
var suggest_selected = 0;

function NewOneXBlock(runtime, element) {

    function updateCount(result) {
        // $('.count', element).text(result.count);
        var list_concepts = eval("("+result.count+")");
        var list_descriptions = eval("("+result.desc+")");
        var list_links = eval("("+result.link+")");
        for(var i in list_concepts){
	    	$('.count').append("<span data-tooltip='"+list_descriptions[i]+"'><a href='"+list_links[i]+"'>"+list_concepts[i]+"</a> | </span>"); 
	    }
    }
    
    
    function updateSQL(result) {
        $('.count').append("<span data-tooltip='"+result.new_desc+"'><a href='"+result.new_link+"'>"+result.new_term+"</a> | </span>");
    }
    
    function glob_value(result) {
        $('.but', element).text(result.but); 
        glob=result.but;
                        var list_concepts = eval("("+glob+")");
                        var list_descriptions = eval("("+result.desc+")");
						var list_links = eval("("+result.link+")");
						
                        suggest_count = list_concepts.length;
                       
                        if(suggest_count > 0){
                            // перед показом слоя подсказки, его обнуляем
                            $("#search_advice_wrapper").html("").show();
                            for(var i in list_concepts){
                                if(list_concepts[i] != ''){
                                    // добавляем слою позиции
                                    $('#search_advice_wrapper').append('<ul id="ul-'+result.block_id+'-'+i+'"><li class="advice_variant">'+list_concepts[i]+'</li><li class="advice_description">'+list_descriptions[i]+'</li><li class="advice_link">'+list_links[i]+'</li></ul>');
                                }
                            }
                        }
                        else {
	                        $("#search_advice_wrapper").hide();
                        }
    }

    var handlerUrl = runtime.handlerUrl(element, 'increment_count');
    var handlerUrl2 = runtime.handlerUrl(element, 'live_search');
	var handlerUrl4 = runtime.handlerUrl(element, 'termsListCheck');
	
	$('.butto', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl4,
            data: JSON.stringify({"concept": document.getElementById("search_box").value, "description": document.getElementById("search_desc").value, "link": document.getElementById("search_link").value}),
            success: updateSQL
        });
    });
	
	//test field to show data from py
    /*
    $('p', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({"hello": "world"}),
            success: updateCount
        });
    });
	*/


    //Live search
    $('#search_box',element).keyup(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl2,
            data: JSON.stringify({"key": document.getElementById("search_box").value}),
            success: glob_value
        });
    });

	// делаем обработку клика по подсказке
    $('ul').live('click',function(){
        // ставим текст в input поиска
        $('#search_box').val($('#'+$(this).attr("id")+' .advice_variant').text());
        $('#search_desc').val($('#'+$(this).attr("id")+' .advice_description').text());
        $('#search_link').val($('#'+$(this).attr("id")+' .advice_link').text());
        
        // прячем слой подсказки
        $('#search_advice_wrapper').fadeOut(350).html('');
    });
 
    // если кликаем в любом месте сайта, нужно спрятать подсказку
    $('html').click(function(){
        $('#search_advice_wrapper').hide();
    });
    // если кликаем на поле input и есть пункты подсказки, то показываем скрытый слой
    $('#search_box').click(function(event){
        //alert(suggest_count);
        if(suggest_count>0)
            $('#search_advice_wrapper').show();
        event.stopPropagation();
    });

    function key_activate(n){
    $('#search_advice_wrapper div').eq(suggest_selected-1).removeClass('active');
 
    if(n == 1 && suggest_selected < suggest_count){
        suggest_selected++;
    }else if(n == -1 && suggest_selected > 0){
        suggest_selected--;
    }
 
    if( suggest_selected > 0){
        $('#search_advice_wrapper div').eq(suggest_selected-1).addClass('active');
        $("#search_box").val( $('#search_advice_wrapper div').eq(suggest_selected-1).text() );
    } else {
        $("#search_box").val( input_initial_value );
    }
    }
     

    $(function ($) {
        /* Here's where you'd do things on page load. */
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({"hello": "world"}),
            success: updateCount
        });
    });
}
