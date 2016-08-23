/* Javascript for NewOneXBlock. */
var glob;
var suggest_count = 0;
var input_initial_value = '';
var suggest_selected = 0;

function NewOneXBlock(runtime, element) {

    function updateCount(result) {
        $('.count', element).text(result.count);
    }
    
    function updateSparql(result) {
        $('.sparql', element).text(result.sprql);
    }
    
    function updateSQL(result) {
        $('.sparql_search', element).text(result.new_term);
    }
    
    function glob_value(result) {
        $('.but', element).text(result.but); 
        glob=result.but;
    }

    var handlerUrl = runtime.handlerUrl(element, 'increment_count');
    var handlerUrl2 = runtime.handlerUrl(element, 'sub_but');
    var handlerUrl3 = runtime.handlerUrl(element, 'sparql_q');
	var handlerUrl4 = runtime.handlerUrl(element, 'termsListCheck');
	
	$('.butto', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl4,
            data: JSON.stringify({"key": document.getElementById("search_box").value}),
            success: updateSQL
        });
    });
	
    $('p', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({"hello": "world"}),
            success: updateCount
        });
    });
    
    $('#search_box_sp', element).blur(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl3,
            data: JSON.stringify({"key": document.getElementById("search_box_sp").value}),
            success: updateSparql
        });
    });
    
    $('#search_box',element).keyup(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl2,
            data: JSON.stringify({"key": document.getElementById("search_box").value}),
            success: glob_value
        });
        if($(this).val().length>1){
						input_initial_value = $(this).val();
                        var list = eval("("+glob+")");
                        suggest_count = list.length;
                        if(suggest_count > 0){
                            // перед показом слоя подсказки, его обнуляем
                            $("#search_advice_wrapper").html("").show();
                            for(var i in list){
                                if(list[i] != ''){
                                    // добавляем слою позиции
                                    $('#search_advice_wrapper').append('<div class="advice_variant">'+list[i]+'</div>');
                                }
                            }
                        }
                
        }
    });

	// делаем обработку клика по подсказке
    $('.advice_variant').live('click',function(){
        // ставим текст в input поиска
        $('#search_box').val($(this).text());
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
        if(suggest_count)
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
    });
}
