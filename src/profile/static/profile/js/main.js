function active_tab(name) {
    var tab = $( '#tab-' + name );
    tab.addClass( 'active' );
    tab.find( 'a' ).attr( 'href', '#' );
}

function build_ul_tree(list) {
    console.log( 'build ul tree' );
    var str = "";
    for (var i in list) {
        str += build_li_tree( list[i] )
    }
    return str;
}

function build_li_tree(document) {
    var str = '<li id="gallery-' + document['id'] + '" >' +
            '<div class="btn-group pull-right">' +
            '<a href="#" class="btn btn-plus"><i class="icon-plus"></i></a>' +
            '<a href="#" class="btn btn-minus"><i class="icon-minus"></i></a>' +
            '</div>' +
            '<span>' + document['title'] + '</span>' +
            '</li>';
    if (document.hasOwnProperty( 'children' )) {
        str += '<ul>';
        var children = document['children']
        for (var i = 0; i < children.length; i++) {
            str += build_li_tree( children[i] );
        }
        str += '</ul>';
    }
    return str;
}

function load_galleries_tree(setFirst) {
    console.log( 'load galleries tree ' );
    $.ajax( {
        url:'/api/gallery/tree/main/',
        dataType:'json',
        success:function (data) {
            $( '#galleries-tree' ).html( build_ul_tree( data ) );
            if (setFirst == true) {
                var li = $( '#galleries-tree' ).children()[0];
                jQuery( li ).addClass( 'active' );
                var id = jQuery( li ).attr( 'id' ).split( '-' )[1];
                load_album( id );
            }
        }
    } );
}

function load_galleries() {
    console.log( 'load galleries ' );
    $.ajax( {
        url:'/api/gallery/all/',
        dataType:'json',
        success:function (data) {
            $( '#find-album' ).typeahead( { 'source':data } );
        }
    } );
}

function load_about() {
    console.log( 'load about ' );
    $.ajax( {
        url:'/api/users/get/',
        dataType:'json',
        success:function (data) {
            var title = data['profile']['about_title'];
            var text = data['profile']['about_text'];
            $( '#about-title' ).attr( 'value', title );
            $( '#about-description' ).val( text );
        }
    } );
}


function build_li_images(document) {
    var str = '<li id="gallery-image-' + document['id'] + '" class="gallery-thumbnails-image">' +
            '<a href="#" class="thumbnail thumbnail-admin">' +
            '<div class="controls"><i class="icon-white icon-user"></i><i class="icon-white icon-picture"></i><i class="icon-white icon-remove"></i></div>' +
            '<img src="/user/download/small/' + document['id'] + '.jpg" alt="">' +
            '<p class="caption">' + document['path'].split( '/' ).pop() + '</p>' +
            '</a>' +
            '</li>';
    return str;
}

function build_li_images2(document) {
    var str = '<li id="gallery-image-' + document + '" class="storage-thumbnails-image" >' +
            '<a href="#" class="thumbnail thumbnail-admin">' +
            '<img src="/profile/image/?p=' + document + '" alt="">' +
            '<p class="caption">' + document.split( '/' ).pop() + '</p>' +
            '</a>' +
            '</li>';
    return str;
}

function build_li_video(document) {
    var str = '<li id="gallery-video-' + document['id'] + '" >' +
            '<a href="#" class="btn btn-minus pull-right"><i class="icon-minus"></i></a>' +
            '<span>' + document['title'] + '</span>' +
            '</li>';
    return str;
}

function build_li_dir(document) {
    var str = '<li id="dir-' + document + '" class="storage-thumbnails-dir" >' +
            '<a href="#" class="thumbnail thumbnail-admin">' +
            '<img src="/static/core/img/gallery.png" alt="">' +
            '<p class="caption-abs">' + document.split( '/' ).pop() + '</p>' +
            '</a>' +
            '</li>';
    return str;
}

function load_galleries_images(id) {
    console.log( 'load galleries images ' );
    var json = '{ "gallery":"' + id + '" }';
    $.ajax( {
        url:'/api/images/get/?data=' + json,
        dataType:'json',
        success:function (data) {
            var str = "";
            for (var i = 0; i < data.length; i++) {
                str += build_li_images( data[i] )
            }
            $( '#album-thumbnails' ).html( str );
        }
    } );
}

function load_galleries_videos(id, callback) {
    console.log( 'load galleries videos ' + id );
    var json = '{"gallery":"' + id + '"}';
    $.ajax( {
        url:'/api/video/get/?data=' + json,
        dataType:'json',
        success:function (data) {
            var str = "";
            for (var i = 0; i < data.length; i++) {
                str += build_li_video( data[i] )
            }
            $( '#video-list' ).html( str );
            callback();
        }
    } );
}


function load_storage_images(path) {
    console.log( 'load storage images ' );
    var json = '{ "path":"' + path + '" }';
    $.ajax( {
        url:'/api/storage/list/?data=' + json,
        dataType:'json',
        success:function (data) {
            var back = data["back"];
            var images = data["files"];
            var dirs = data["dirs"];
            var str = "";
            if (data["path"] != "") {
                str += '<li id="dir-' + back + '" class="storage-thumbnails-dir" >' +
                        '<a href="#" class="thumbnail thumbnail-admin">' +
                        '<img src="/static/core/img/gallery.png" alt=""><p class="caption-abs">Back</p>' +
                        '</a>' +
                        '</li>';
            }
            for (var i = 0; i < dirs.length; i++) {
                str += build_li_dir( dirs[i] )
            }
            for (var i = 0; i < images.length; i++) {
                str += build_li_images2( images[i] )
            }
            $( '#storage-thumbnails' ).html( str );
            $( '#storage-path' ).attr( 'value', data["path"] );
        }
    } );
}

function load_album(id) {
    console.log( 'load album ' + id );
    var json = '{ "id":"' + id + '" }';
    $.ajax( {
        url:'/api/gallery/get?data=' + json,
        dataType:'json',
        success:function (data) {
            $( '#gallery-name' ).attr( 'value', data['title'] );
            if ('thumbnail' in data) {
                var link = '/user/download/small/' + data['thumbnail'] + '.jpg'
                $( '#gallery-thumbnail' ).attr( 'src', link );
            } else {
                $( '#gallery-thumbnail' ).attr( 'src', '/static/core/img/gallery.png' );
            }
            if ('description' in data) {
                $( '#gallery-description' ).val( data['description'] );
            } else {
                $( '#gallery-description' ).val( '' );
            }
            if ('time' in data) {
                $( '#gallery-time' ).attr( 'value', data['time'] );
            }
            var li = $( '#gallery-' + id );
            if (!li.is( '.active' )) {
                li.addClass( 'active' );
            }

        }
    } );
}


function load_video(id) {
    console.log( 'load video ' + id );
    var json = '{ "id":"' + id + '" }';
    $.ajax( {
        url:'/api/video/get?data=' + json,
        dataType:'json',
        success:function (data) {
            $( '#video-uid' ).attr( 'value', data['uid'] );
            $( '#video-title' ).attr( 'value', data['title'] );

            if ('description' in data) {
                $( '#video-description' ).val( data['description'] );
            } else {
                $( '#video-description' ).val( '' );
            }
            var li = $( '#gallery-video-' + id );
            if (!li.is( '.active' )) {
                li.addClass( 'active' );
            }
        }
    } );
}

function add_album(name) {
    console.log( 'add album ' + name );
    var json = '{ "title":"' + name + '" }';
    $.ajax( {
        url:'/api/gallery/add/?data=' + json,
        dataType:'json',
        success:function (data) {
            load_galleries_tree( true );
            load_album( data['id'] );
            $( '#galleries-tree .active' ).removeClass( 'active' );
            $( '#gallery-' + data['id'] ).addClass( 'active' );
        }
    } );
}

function add_image(gallery, path) {
    console.log( 'add image ' + gallery + ' ' + path );
    var json = '{ "gallery":"' + gallery + '", "path":"' + path + '" }';
    $.ajax( {
        url:'/api/images/add/?data=' + json,
        dataType:'json',
        success:function (data) {
        }
    } );
}

function remove_album(id) {
    console.log( 'remove album ' + id );
    var json = '{ "id":"' + id + '" }';
    $.ajax( {
        url:'/api/gallery/del/?data=' + json,
        dataType:'json',
        success:function (data) {
            load_galleries_tree( true );
        }
    } );
}

function remove_image(id) {
    console.log( 'remove image ' + id );
    var json = '{ "id":"' + id + '" }';
    $.ajax( {
        url:'/api/images/del/?data=' + json,
        dataType:'json',
        success:function (data) {
        }
    } );
}

function pre_cache_album(id) {
    console.log( 'pre cache album ' + id );
    var json = '{"id":"' + id + '","each":2,"size":["small","big"]}';
    $.ajax( {
        url:'/api/gallery/cache/?data=' + json,
        dataType:'json'
    } );
}

function update_album(id) {
    console.log( 'save album ' + id );
    var name = $( '#gallery-name' ).attr( 'value' );
    var description = $( '#gallery-description' ).val().split( "\n" ).join( "\\n" );
    var time = $( '#gallery-time' ).attr( 'value' );
    var json = '{"id":"' + id + '", "title":"' + name + '", "description":"' + description + '", "time":"' + time + '" }';
    $.ajax( {
        url:'/api/gallery/update/?data=' + json,
        dataType:'json',
        success:function (data) {
            load_galleries_tree( true );
        }
    } );
}


function update_video(id, collback) {
    console.log( 'update video ' + id );
    var uid = $( '#video-uid' ).attr( 'value' );
    var title = $( '#video-title' ).attr( 'value' );
    var description = $( '#video-description' ).val().split( "\n" ).join( "\\n" );
    var json = '{ "id":"' + id + '", "uid":"' + uid + '", "title":"' + title + '", "description":"' + description + '" }';
    $.ajax( {
        url:'/api/video/update/?data=' + json,
        dataType:'json',
        success:function (data) {
            collback();
        }
    } );
}

function update_about() {
    console.log( 'update about' );
    var title = $( '#about-title' ).attr( 'value' );
    var text = $( '#about-description' ).val().split( "\n" ).join( "\\n" );
    text = text.split( "\n" ).join( "\\n" );
    var json = '{"about.title":"' + title + '","about.text":"' + text + '"}';
    $.ajax( {
        url:'/api/users/update/',
        type:'POST',
        contentType:'application/json; charset=utf-8',
        data:{ "data":json },
        dataType:'text'
    } );
}

function update_avatar(id) {
    console.log( 'update avatar' );
    var json = '{"avatar":"' + id + '"}';
    $.ajax( {
        url:'/api/users/update/?data=' + json,
        dataType:'json',
        success:function (data) {
        }
    } );
}

function add_video(gallery, id, collback) {
    console.log( 'add video ' + id );
    var json = '{ "uid":"' + id + '", "gallery":"' + gallery + '"}';
    console.log( json );
    $.ajax( {
        url:'/api/video/add/?data=' + json,
        dataType:'json',
        success:function (data) {
            collback();
        }
    } );
}

function del_video(id, collback) {
    console.log( 'del video ' + id );
    var json = '{ "id":"' + id + '" }';
    console.log( json );
    $.ajax( {
        url:'/api/video/del/?data=' + json,
        dataType:'json',
        success:function (data) {
            collback();
        }
    } );
}

function set_thumbnail(gallery, image_id) {
    var json = '{ "id":"' + gallery + '", "thumbnail":"' + image_id + '" }';
    $.ajax( {
        url:'/api/gallery/update/?data=' + json,
        dataType:'json'
    } );
}

function add_sub_album(id, sub_album_id) {
    console.log( 'add sub album ' + sub_album_id + ' to ' + id );
    var json = '{ "id":"' + id + '", "child":"' + sub_album_id + '" }';
    $.ajax( {
        url:'/api/gallery/child/add/?data=' + json,
        dataType:'json',
        success:function (data) {
            load_galleries_tree( false );
            load_album( sub_album_id );
        }
    } );
}

function del_sub_album(id, sub_album_id) {
    console.log( 'del sub album ' + sub_album_id + ' to ' + id );
    var json = '{ "id":"' + id + '", "child":"' + sub_album_id + '" }';
    $.ajax( {
        url:'/api/gallery/child/del/?data=' + json,
        dataType:'json',
        success:function (data) {
            load_galleries_tree( false );
            load_album( sub_album_id );
        }
    } );
}