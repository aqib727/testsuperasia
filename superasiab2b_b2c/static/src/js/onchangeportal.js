odoo.define('superasiab2b_b2c.portal', function (require) {
'use strict';

    require('web.dom_ready');



   if ($('.opportunitylinadd_details').length) {
        var state_options = $("select[name='state_id']:enabled option:not(:first)");
        console.log(state_options);
        $('.opportunitylinadd_details').on('change', "select[name='country_id']", function () {
            var select = $("select[name='state_id']");
            console.log(select);
            state_options.detach();
            var displayed_state = state_options.filter("[data-country_id="+($(this).val() || 0)+"]");
            console.log(displayed_state);
            var nb = displayed_state.appendTo(select).show().length;
            select.parent().toggle(nb>=1);
        });
        $('.opportunitylinadd_details').find("select[name='country_id']").change();
    }


    
    

});