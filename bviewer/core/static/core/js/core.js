var core = {
    shadowbox: function () {
        var isMobile = window.matchMedia('only screen and (max-width: 480px)').matches;

        link2id = function (item) {
            return jQuery(item).parent().parent().attr('id')
        }

        if (isMobile) {
            jQuery('.shadowbox').bind('click', function (e) {
                e.preventDefault();
            });
            if (window.location.hash != '') {
                var id = window.location.hash.substr(2);
                jQuery('html, body').animate({ scrollTop: jQuery('#' + id).offset().top - 32 }, 500);
            }
        } else {
            var settings = {
                overlayOpacity: 0.95,
                slideshowDelay: 3,
                viewportPadding: 12,
                onOpen: function (item) {
                    window.location.hash = '#!' + link2id(item.link);
                    Shadowbox.play();
                    Shadowbox.pause();
                },
                onChange: function (item) {
                    window.location.hash = '#!' + link2id(item.link);
                },
                onClose: function (item) {
                    window.location.hash = '#!';
                }
            }
            Shadowbox.init(settings);

            var show_image = function () {
                if (window.location.hash != '') {
                    var id = window.location.hash.substr(2);
                    var a = jQuery('#' + id).find('a.shadowbox')[0];
                    if (typeof(a) != "undefined") {
                        Shadowbox.open(Shadowbox.cache[1]);
                    }
                }
            }
            // Fucking Shadowbox.init callback doesn't work
            setTimeout(show_image, 1000);

            jQuery('body').delegate('#sb-body', 'click', function (e) {
                console.log(e);
                var width = jQuery(this).width() / 3;
                var x = e.pageX - jQuery(this).offset().left;
                if (x < width) {
                    Shadowbox.previous()
                } else {
                    Shadowbox.next();
                }
            });
        }
    },

    imageLoading: function () {
        function load() {
            var height = jQuery(window).scrollTop() + jQuery(window).height();
            jQuery('.album img[data-src]').each(function (i, img) {
                var image = jQuery(img);
                if (image.offset().top < height) {
                    image.attr('src', image.attr('data-src'));
                    image.removeAttr('data-src');
                }
            });
        }

        load();

        jQuery(window).scroll(function () {
            load();
        });

        jQuery('.preview img').bind('load', function () {
            jQuery(this).css({opacity: 1});
        });
    }
};
