odoo.define('mwbecloud_sbportalmanager.Productconf', function (require) {
'use strict';
var ajax = require('web.ajax');

$(document).ready(function(){

        
        $(".add-row").click(function(){

            var name = $("#name").val();

            var email = $("#email").val();

            var markup = "<tr><td><input type='checkbox' id ='events_chc_box_rad_id' name='record'></td><td>" + name + "</td><td>" + email + "</td></tr>";

            $("table tbody").append(markup);

        });

        

        // Find and remove selected table rows

        $(".delete-row").click(function(){

            $("table tbody").find('input[name="record"]').each(function(){

                if($(this).is(":checked")){

                    $(this).parents("tr").remove();

                }

            });

        });


        $(".submit-rows").click(function(){
			console.log('printtttaaaatt');
			// document.getElementById('info').innerHTML = "";
        	var myTab = document.getElementById('empTable');			// var myTab = $('#events_chc_box_rad_id:checked').val();
			console.log(myTab);
	        var arrValues = new Array();


	        // loop through each row of the table.
	        for (var row = 1; row < myTab.rows.length - 1; row++) {
	        	// loop through each cell in a row.
				console.log('rpwsssss')

	            for (var c = 0; c < myTab.rows[row].cells.length; c++) {  
	                var element = myTab.rows.item(row).cells[c];

					console.log(element);
					console.log('ssssselement');
					arrValues.push(element.innerText)
	            }
	        }
	        
	        // The final output.
	        // document.getElementById('output').innerHTML = arrValues;
			console.log(arrValues);
			ajax.jsonRpc('/newquote', 'call', {'invoices_id': arrValues}).then(function (url) {
				myTempWindow = window.open(url);

				location.reload(true);
				window.location = window.location.href+'?eraseCache=true';
				$('html[manifest=saveappoffline.appcache]').attr('content', ''); 
			});
			});







    });    

});