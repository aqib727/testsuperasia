odoo.define('bista_superasia_theme.recent_product', function (require) {
"use strict";
var ajax = require('web.ajax');
var core = require('web.core');
var qweb = core.qweb;

ajax.loadXML('/bista_superasia_theme/static/src/xml/website_sale_recent_product_inherit.xml', qweb);
})
var a = 0;
$(window).scroll(function() {

  if($('.counter-value').length){
  var oTop = $('#counter').offset().top - window.innerHeight;
  if (a == 0 && $(window).scrollTop() > oTop) {
    $('.counter-value').each(function() {
      var $this = $(this),
        countTo = $this.attr('data-count');
      $({
        countNum: $this.text()
      }).animate({
          countNum: countTo
        },

        {

          duration: 7000,
          easing: 'swing',
          step: function() {
            $this.text(Math.floor(this.countNum));
          },
          complete: function() {
            $this.text(this.countNum);
          }

        });
    });
    a = 1;
  }
  }

});


$(document).ready(function(){

/* Mobile menu toggle click */
var nav_links = $(".navbar-links");
//var nav_items = $(".nav-item");
//var nav_items = $(".nav-menus");
var nav_items = $(".nav-menus");
$("#toggle_menu").on("click", function(){
    for(var i=0; i<nav_links.length; i++)
    nav_links[i].classList.toggle('show');
    for(var i=0; i<nav_items.length; i++)
    nav_items[i].classList.toggle('show');
})
/* Mobile menu toggle click */




/* Collapse Keep Open For Products Category And Brand  */
 var collapseStatus = JSON.parse(localStorage.getItem('collapseStatus'));
  if(collapseStatus === null) {
    collapseStatus = {};
  }

    $(".show_category").on("click", function(){
        var products_categories = $('#wsale_products_categories_collapse').attr('class');
        products_categories == "collapse" ? collapseStatus['wsale_products_categories_collapse'] = "open" : collapseStatus['wsale_products_categories_collapse'] = "closed";

        localStorage.setItem('collapseStatus', JSON.stringify(collapseStatus));
    });
    $(".show_brands").on("click", function(){
        var products_categories = $('#wsale_products_attributes_collapse').attr('class');
        products_categories == "collapse" ? collapseStatus['wsale_products_attributes_collapse'] = "open" : collapseStatus['wsale_products_attributes_collapse'] = "closed";

        localStorage.setItem('collapseStatus', JSON.stringify(collapseStatus));
    });
    var collapseKeys = Object.keys(collapseStatus);
    var collapseValues = Object.values(collapseStatus);
    for(i = 0;i<collapseKeys.length;i++) {
        if(collapseKeys[i] === "wsale_products_categories_collapse"){
            collapseValues[i] == 'open' ? $('div[id="' + collapseKeys[i] + '"]').addClass("show") : $('div[id="' + collapseKeys[i] + '"]').removeClass("show");
        }else if(collapseKeys[i] === "wsale_products_attributes_collapse"){
            collapseValues[i] == 'open' ? $('div[id="' + collapseKeys[i] + '"]').addClass("show") : $('div[id="' + collapseKeys[i] + '"]').removeClass("show");
        }

    }


/* Top HomePage Search Box */
$(".top_search").change(function(){
  if ($(this).val()){
   var redirect_link = '/shop/product/'
   redirect_link  += $(this).val()
   window.location.href = redirect_link

  }})

$(".top_search").select2({
        theme:"bootstrap",
        allowClear: true,
        formatResult: function (opt) {
        var opt_text = opt.text;
        var opt_thumb_image = $(opt.element).attr('src');
        var $res = opt_thumb_image ? $('<span><img src="' + opt_thumb_image + '" width="auto" height="50px" /><span id="p_txt"> ' + opt.text + '</span></span>') : opt_text;
        return $res;
},});
/* Top HomePage Search Box */


/* Auto Typing on Hompage Top Banner */
if ($('.typing').length){
var typed = new Typed(".typing", {
//    strings: ["Hello.!!!","Super Asia Foods."],
    strings: ["Hello.!!!","Super Asia Foods."],
    typeSpeed: 100,
    backSpeed: 60,
    loop: false,
    });
// setTimeout(function () {
//           $('.catalogue_btn').removeClass('d-none');
//          }, 10000);
}
/* Auto Typing on Hompage Top Banner */

    });

    $(document).ready(function(){
        $('[data-toggle="tooltip"]').tooltip();
        $(".hover-flag-dropdown").hover(function(){
            var dropdownMenu = $(this).children(".dropdown-menu-toggle");
            if(dropdownMenu.is(":visible")){
                dropdownMenu.parent().toggleClass("open");
            }
        });
    });



$(document).ready(function(){

  var $clientcarousel = $('#clients-list');
  var clients = $clientcarousel.children().length;
  var clientwidth = (clients * 220); // 140px width for each client item
  $clientcarousel.css('width',clientwidth);

  var rotating = true;
  var clientspeed = 0;
  var seeclients = setInterval(rotateClients, clientspeed);

  $(document).on({
    mouseenter: function(){
      rotating = false; // turn off rotation when hovering
    },
    mouseleave: function(){
      rotating = true;
    }
  }, '#clients');

  function rotateClients() {
    if(rotating != false) {
      var $first = $('#clients-list li:first');
      $first.animate({ 'margin-left': '-220px' }, 2000, "linear", function() {
        $first.remove().css({ 'margin-left': '0px' });
        $('#clients-list li:last').after($first);
      });
    }
  }


    });



    $('#recipeCarousel').carousel({
      interval :50000
    });

    $('.carousel .carousel-item').each(function(){
        var next = $(this).next();
        if (!next.length) {
        next = $(this).siblings(':first');
        }
        next.children(':first-child').clone().appendTo($(this));

        for (var i=0;i<1;i++) {
            next=next.next();
            if (!next.length) {
              next = $(this).siblings(':first');
            }

            next.children(':first-child').clone().appendTo($(this));
          }
    });
