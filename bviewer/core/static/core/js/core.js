var core = {
    shadowbox: function () {
        var isMobile = window.matchMedia("only screen and (max-width: 480px)").matches;
        if (isMobile) {
            jQuery('.shadowbox').bind('click', function (e) {
                e.preventDefault();
            });
        } else {
            Shadowbox.init({
                "overlayOpacity": 0.95,
                "slideshowDelay": 3,
                "viewportPadding": 12,
                onOpen: function (currentImage) {
                    Shadowbox.play();
                    Shadowbox.pause();
                }
            });
        }

        jQuery('#sb-body').live('click', function (e) {
            var width = jQuery(this).width() / 3;
            var x = e.pageX - jQuery(this).offset().left;
            if (x < width) {
                Shadowbox.previous()
            } else {
                Shadowbox.next();
            }
        });
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
