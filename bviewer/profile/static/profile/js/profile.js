function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var LocationHash = function () {
    var self = this;
    self.hash = '#!';
    self.map = {};

    self.set = function (key, val) {
        self.map[key] = val;
        self.hash = '#!';
        for (var key in self.map) {
            self.hash += key + '=' + self.map[key] + '&';
        }
        window.location.hash = self.hash.slice(0, -1);
    };

    self.get = function (key, def) {
        if (key in self.map) {
            return self.map[key];
        }
        return def;
    };

    self.init = function () {
        var kwargs = window.location.hash.slice(2).split('&');
        for (var i = 0; i < kwargs.length; i++) {
            var items = kwargs[i].split('=');
            var key = items[0], val = items[1];
            if (key != '')
                self.map[key] = val;
        }
    };
    self.init();
};

var locationHash = new LocationHash();

var Gallery = function (id, name) {
    var self = this;
    self.id = id;
    self.name = name;
};

var File = function (name, path, checked) {
    var self = this;
    self.name = name;
    self.path = path;
    self.checked = ko.observable(checked);
    self.url = "/profile/download/?p=" + path;

    self.underFocus = ko.observable(false);
    self.focusIn = function () {
        self.underFocus(true);
    };
    self.focusOut = function () {
        self.underFocus(false);
    };
};

var ImageModel = function () {
    var self = this;
    self.messages = ko.observableArray([]);
    self.galleries = ko.observableArray([]);

    self.chosenGallery = ko.observable();
    self.chosenGalleryId = ko.computed(function () {
        return self.chosenGallery() ? self.chosenGallery().id : '';
    });

    self.back = ko.observable('');
    self.path = ko.observable(null);

    self.splitPath = ko.observableArray();
    self.dirs = ko.observableArray();
    self.files = ko.observableArray();

    self.selectedImages = ko.computed(function () {
        return ko.utils.arrayFilter(self.files(),function (file) {
            return file.checked();
        }).length;
    });

    self.checkExistsFiles = function () {
        if (self.path() != null && self.chosenGallery() != null) {
            jQuery.each(self.files(), function (fid, fvalue) {
                fvalue.checked(false);
            });
            jQuery.getJSON('/api/v1/image/?gallery=' + self.chosenGalleryId(), function (data) {
                jQuery.each(data.objects, function (iid, item) {
                    jQuery.each(self.files(), function (fid, fvalue) {
                        if (fvalue.path == item.path) {
                            fvalue.checked(true);
                        }
                    });
                });
            });
        }
    };

    self.chosenGallery.subscribe(function (value) {
        locationHash.set('g', value.id);
        self.checkExistsFiles();
    });

    self.path.subscribe(function (value) {
        if (value != null)
            locationHash.set('p', value);
    });

    self.select = function (item) {
        self.loadFolder(item.path)
    };
    self.selectHome = function () {
        self.loadFolder('');
    };
    self.selectBack = function () {
        self.loadFolder(self.back());
    };

    self.loadGalleries = function () {
        jQuery.ajax({
            url: '/api/v1/gallery/?user=self',
            dataType: "json",
            success: function (data) {
                var galleries = jQuery.map(data.objects, function (item) {
                    return new Gallery(item.id, item.title);
                });
                self.galleries(galleries);
            },
            async: false
        });
    };

    self.loadFolder = function (path) {
        jQuery.ajax({
            url: '/profile/storage/?p=' + path,
            dataType: "json",
            success: function (data) {
                self.path(data.path);
                self.back(data.back);

                var splitPath = jQuery.map(data.split_path, function (item) {
                    return { 'name': item.name, 'path': item.path };
                });
                self.splitPath(splitPath);

                var dirs = jQuery.map(data.dirs, function (item) {
                    return new File(item.name, item.path);
                });
                self.dirs(dirs);
                var files = jQuery.map(data.files, function (item) {
                    return new File(item.name, item.path, item.checked);
                });
                self.files(files);
            },
            complete: function () {
                self.checkExistsFiles();
            },
            async: true
        });
    };

    self.save = function () {
        if (self.chosenGallery() == null) {
            self.messages.push({message: 'Select gallery', tags: 'warn'});
            return;
        }
        jQuery.ajax({
            type: 'POST',
            dataType: "json",
            url: '/profile/images/update/',
            beforeSend: function (xhr, settings) {
                var csrftoken = getCookie('csrftoken');
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            data: {
                'path': self.path(),
                'gallery': self.chosenGalleryId(),
                'images[]': jQuery.map(self.files(), function (item) {
                    if (item.checked())
                        return item.path;
                    return null;
                })
            },
            success: function (data) {
                self.messages.push({message: 'Done', tags: 'info'});
            },
            error: function (data) {
                self.messages.push({message: 'Error on saving', tags: 'error'});
                console.log(data);
            },
            async: false
        });
    };

    self.init = function () {
        self.loadGalleries();
        var gallery_id = locationHash.get('g', null);
        jQuery.each(self.galleries(), function (key, value) {
            if (value.id == gallery_id)
                self.chosenGallery(value);
        });
        var path = locationHash.get('p', '');
        self.loadFolder(path);
    };
    self.init();

};