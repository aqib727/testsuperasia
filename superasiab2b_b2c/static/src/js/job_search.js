$(document).ready(function () {


    $('.oe_website_bids .a-submit, #comment .a-submit').off('click').on('click', function () {
        var my_form = $(this).closest('form');
        if (my_form.serialize() != "search=" )
	        my_form.submit();
    });

    function insertParam(key, value)
	{
	    key = encodeURI(key); value = encodeURI(value);

	    var kvp = document.location.search.substr(1).split('&');

	    var i=kvp.length; var x; while(i--) 
	    {
	        x = kvp[i].split('=');

	        if (x[0]==key)
	        {
	            x[1] = value;
	            kvp[i] = x.join('=');
	            break;
	        }
	    }

	    if(i<0) {kvp[kvp.length] = [key,value].join('=');}

	    // return kvp.join('&');
	    //this will reload the page, it's likely better to store this until finished
	    document.location.search = kvp.join('&'); 
	};

    $('#bids_grid_left').each(function () {
	    var bids_grid_left = this;

	     $(bids_grid_left).on("click", 'a[id="ct"]', function (event) {
	     		insertParam('category',$(event.target).closest('a')[0].dataset.id);
		    });
	 });

/*	window.addEventListener("scroll", affixFx);
	function affixFx(){	
		// debugger;
		if ($('#bids_grid_left').height() > $('#bids_grid').height()){
			// do nothing
			return 1;
		};

		if (document.documentElement.scrollTop > 280){
			$('#bids_grid_left').addClass('affix');
			$('#bids_nav_empty').css('display','inline');
		}
		else
		{
			$('#bids_grid_left').removeClass('affix');
			$('#bids_nav_empty').css('display','initial');
		};
	}; */
    
//    $('#example').DataTable( {
//        "lengthMenu": [[1, 25, 50, -1], [1, 25, 50, "All"]]
//     } );


});
