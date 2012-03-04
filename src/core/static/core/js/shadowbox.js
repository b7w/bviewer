/*
 * Shadowbox.js, version 3.0.3
 * http://shadowbox-js.com/
 *
 * Copyright 2007-2010, Michael J. I. Jackson
 * Date: 2011-05-14 08:08:40 +0000
 */
(function (au, k) {
    var Q = {version:"3.0.3"};
    var J = navigator.userAgent.toLowerCase();
    if (J.indexOf( "windows" ) > -1 || J.indexOf( "win32" ) > -1) {
        Q.isWindows = true
    } else {
        if (J.indexOf( "macintosh" ) > -1 || J.indexOf( "mac os x" ) > -1) {
            Q.isMac = true
        } else {
            if (J.indexOf( "linux" ) > -1) {
                Q.isLinux = true
            }
        }
    }
    Q.isIE = J.indexOf( "msie" ) > -1;
    Q.isIE6 = J.indexOf( "msie 6" ) > -1;
    Q.isIE7 = J.indexOf( "msie 7" ) > -1;
    Q.isGecko = J.indexOf( "gecko" ) > -1 && J.indexOf( "safari" ) == -1;
    Q.isWebKit = J.indexOf( "applewebkit/" ) > -1;
    var ab = /#(.+)$/, af = /^(light|shadow)box\[(.*?)\]/i, az = /\s*([a-z_]*?)\s*=\s*(.+)\s*/, f = /[0-9a-z]+$/i, aD = /(.+\/)shadowbox\.js/i;
    var A = false, a = false, l = {}, z = 0, R, ap;
    Q.current = -1;
    Q.dimensions = null;
    Q.ease = function (K) {
        return 1 + Math.pow( K - 1, 3 )
    };
    Q.errorInfo = {fla:{name:"Flash", url:"http://www.adobe.com/products/flashplayer/"}, qt:{name:"QuickTime", url:"http://www.apple.com/quicktime/download/"}, wmp:{name:"Windows Media Player", url:"http://www.microsoft.com/windows/windowsmedia/"}, f4m:{name:"Flip4Mac", url:"http://www.flip4mac.com/wmv_download.htm"}};
    Q.gallery = [];
    Q.onReady = aj;
    Q.path = null;
    Q.player = null;
    Q.playerId = "sb-player";
    Q.options = {animate:true, animateFade:true, autoplayMovies:true, continuous:false, enableKeys:true, flashParams:{bgcolor:"#000000", allowfullscreen:true}, flashVars:{}, flashVersion:"9.0.115", handleOversize:"resize", handleUnsupported:"link", onChange:aj, onClose:aj, onFinish:aj, onOpen:aj, showMovieControls:true, skipSetup:false, slideshowDelay:0, viewportPadding:20};
    Q.getCurrent = function () {
        return Q.current > -1 ? Q.gallery[Q.current] : null
    };
    Q.hasNext = function () {
        return Q.gallery.length > 1 && (Q.current != Q.gallery.length - 1 || Q.options.continuous)
    };
    Q.isOpen = function () {
        return A
    };
    Q.isPaused = function () {
        return ap == "pause"
    };
    Q.applyOptions = function (K) {
        l = aC( {}, Q.options );
        aC( Q.options, K )
    };
    Q.revertOptions = function () {
        aC( Q.options, l )
    };
    Q.init = function (aG, aJ) {
        if (a) {
            return
        }
        a = true;
        if (Q.skin.options) {
            aC( Q.options, Q.skin.options )
        }
        if (aG) {
            aC( Q.options, aG )
        }
        if (!Q.path) {
            var aI, S = document.getElementsByTagName( "script" );
            for (var aH = 0, K = S.length; aH < K; ++aH) {
                aI = aD.exec( S[aH].src );
                if (aI) {
                    Q.path = aI[1];
                    break
                }
            }
        }
        if (aJ) {
            Q.onReady = aJ
        }
        P()
    };
    Q.open = function (S) {
        if (A) {
            return
        }
        var K = Q.makeGallery( S );
        Q.gallery = K[0];
        Q.current = K[1];
        S = Q.getCurrent();
        if (S == null) {
            return
        }
        Q.applyOptions( S.options || {} );
        G();
        if (Q.gallery.length) {
            S = Q.getCurrent();
            if (Q.options.onOpen( S ) === false) {
                return
            }
            A = true;
            Q.skin.onOpen( S, c )
        }
    };
    Q.close = function () {
        if (!A) {
            return
        }
        A = false;
        if (Q.player) {
            Q.player.remove();
            Q.player = null
        }
        if (typeof ap == "number") {
            clearTimeout( ap );
            ap = null
        }
        z = 0;
        aq( false );
        Q.options.onClose( Q.getCurrent() );
        Q.skin.onClose();
        Q.revertOptions()
    };
    Q.play = function () {
        if (!Q.hasNext()) {
            return
        }
        if (!z) {
            z = Q.options.slideshowDelay * 1000
        }
        if (z) {
            R = aw();
            ap = setTimeout( function () {
                z = R = 0;
                Q.next()
            }, z );
            if (Q.skin.onPlay) {
                Q.skin.onPlay()
            }
        }
    };
    Q.pause = function () {
        if (typeof ap != "number") {
            return
        }
        z = Math.max( 0, z - (aw() - R) );
        if (z) {
            clearTimeout( ap );
            ap = "pause";
            if (Q.skin.onPause) {
                Q.skin.onPause()
            }
        }
    };
    Q.change = function (K) {
        if (!(K in Q.gallery)) {
            if (Q.options.continuous) {
                K = (K < 0 ? Q.gallery.length + K : 0);
                if (!(K in Q.gallery)) {
                    return
                }
            } else {
                return
            }
        }
        Q.current = K;
        if (typeof ap == "number") {
            clearTimeout( ap );
            ap = null;
            z = R = 0
        }
        Q.options.onChange( Q.getCurrent() );
        c( true )
    };
    Q.next = function () {
        Q.change( Q.current + 1 )
    };
    Q.previous = function () {
        Q.change( Q.current - 1 )
    };
    Q.setDimensions = function (aS, aJ, aQ, aR, aI, K, aO, aL) {
        var aN = aS, aH = aJ;
        var aM = 2 * aO + aI;
        if (aS + aM > aQ) {
            aS = aQ - aM
        }
        var aG = 2 * aO + K;
        if (aJ + aG > aR) {
            aJ = aR - aG
        }
        var S = (aN - aS) / aN, aP = (aH - aJ) / aH, aK = (S > 0 || aP > 0);
        if (aL && aK) {
            if (S > aP) {
                aJ = Math.round( (aH / aN) * aS )
            } else {
                if (aP > S) {
                    aS = Math.round( (aN / aH) * aJ )
                }
            }
        }
        Q.dimensions = {height:aS + aI, width:aJ + K, innerHeight:aS, innerWidth:aJ, top:Math.floor( (aQ - (aS + aM)) / 2 + aO ), left:Math.floor( (aR - (aJ + aG)) / 2 + aO ), oversized:aK};
        return Q.dimensions
    };
    Q.makeGallery = function (aI) {
        var K = [], aH = -1;
        if (typeof aI == "string") {
            aI = [aI]
        }
        if (typeof aI.length == "number") {
            aF( aI, function (aK, aL) {
                if (aL.content) {
                    K[aK] = aL
                } else {
                    K[aK] = {content:aL}
                }
            } );
            aH = 0
        } else {
            if (aI.tagName) {
                var S = Q.getCache( aI );
                aI = S ? S : Q.makeObject( aI )
            }
            if (aI.gallery) {
                K = [];
                var aJ;
                for (var aG in Q.cache) {
                    aJ = Q.cache[aG];
                    if (aJ.gallery && aJ.gallery == aI.gallery) {
                        if (aH == -1 && aJ.content == aI.content) {
                            aH = K.length
                        }
                        K.push( aJ )
                    }
                }
                if (aH == -1) {
                    K.unshift( aI );
                    aH = 0
                }
            } else {
                K = [aI];
                aH = 0
            }
        }
        aF( K, function (aK, aL) {
            K[aK] = aC( {}, aL )
        } );
        return[K, aH]
    };
    Q.makeObject = function (aH, aG) {
        var aI = {content:aH.href, title:aH.getAttribute( "title" ) || "", link:aH};
        if (aG) {
            aG = aC( {}, aG );
            aF( ["player", "title", "height", "width", "gallery"], function (aJ, aK) {
                if (typeof aG[aK] != "undefined") {
                    aI[aK] = aG[aK];
                    delete aG[aK]
                }
            } );
            aI.options = aG
        } else {
            aI.options = {}
        }
        if (!aI.player) {
            aI.player = Q.getPlayer( aI.content )
        }
        var K = aH.getAttribute( "rel" );
        if (K) {
            var S = K.match( af );
            if (S) {
                aI.gallery = escape( S[2] )
            }
            aF( K.split( ";" ), function (aJ, aK) {
                S = aK.match( az );
                if (S) {
                    aI[S[1]] = S[2]
                }
            } )
        }
        return aI
    };
    Q.getPlayer = function (aG) {
        if (aG.indexOf( "#" ) > -1 && aG.indexOf( document.location.href ) == 0) {
            return"inline"
        }
        var aH = aG.indexOf( "?" );
        if (aH > -1) {
            aG = aG.substring( 0, aH )
        }
        var S, K = aG.match( f );
        if (K) {
            S = K[0].toLowerCase()
        }
        if (S) {
            if (Q.img && Q.img.ext.indexOf( S ) > -1) {
                return"img"
            }
            if (Q.swf && Q.swf.ext.indexOf( S ) > -1) {
                return"swf"
            }
            if (Q.flv && Q.flv.ext.indexOf( S ) > -1) {
                return"flv"
            }
            if (Q.qt && Q.qt.ext.indexOf( S ) > -1) {
                if (Q.wmp && Q.wmp.ext.indexOf( S ) > -1) {
                    return"qtwmp"
                } else {
                    return"qt"
                }
            }
            if (Q.wmp && Q.wmp.ext.indexOf( S ) > -1) {
                return"wmp"
            }
        }
        return"iframe"
    };
    function G() {
        var aH = Q.errorInfo, aI = Q.plugins, aK, aL, aO, aG, aN, S, aM, K;
        for (var aJ = 0; aJ < Q.gallery.length; ++aJ) {
            aK = Q.gallery[aJ];
            aL = false;
            aO = null;
            switch (aK.player) {
                case"flv":
                case"swf":
                    if (!aI.fla) {
                        aO = "fla"
                    }
                    break;
                case"qt":
                    if (!aI.qt) {
                        aO = "qt"
                    }
                    break;
                case"wmp":
                    if (Q.isMac) {
                        if (aI.qt && aI.f4m) {
                            aK.player = "qt"
                        } else {
                            aO = "qtf4m"
                        }
                    } else {
                        if (!aI.wmp) {
                            aO = "wmp"
                        }
                    }
                    break;
                case"qtwmp":
                    if (aI.qt) {
                        aK.player = "qt"
                    } else {
                        if (aI.wmp) {
                            aK.player = "wmp"
                        } else {
                            aO = "qtwmp"
                        }
                    }
                    break
            }
            if (aO) {
                if (Q.options.handleUnsupported == "link") {
                    switch (aO) {
                        case"qtf4m":
                            aN = "shared";
                            S = [aH.qt.url, aH.qt.name, aH.f4m.url, aH.f4m.name];
                            break;
                        case"qtwmp":
                            aN = "either";
                            S = [aH.qt.url, aH.qt.name, aH.wmp.url, aH.wmp.name];
                            break;
                        default:
                            aN = "single";
                            S = [aH[aO].url, aH[aO].name]
                    }
                    aK.player = "html";
                    aK.content = '<div class="sb-message">' + s( Q.lang.errors[aN], S ) + "</div>"
                } else {
                    aL = true
                }
            } else {
                if (aK.player == "inline") {
                    aG = ab.exec( aK.content );
                    if (aG) {
                        aM = ad( aG[1] );
                        if (aM) {
                            aK.content = aM.innerHTML
                        } else {
                            aL = true
                        }
                    } else {
                        aL = true
                    }
                } else {
                    if (aK.player == "swf" || aK.player == "flv") {
                        K = (aK.options && aK.options.flashVersion) || Q.options.flashVersion;
                        if (Q.flash && !Q.flash.hasFlashPlayerVersion( K )) {
                            aK.width = 310;
                            aK.height = 177
                        }
                    }
                }
            }
            if (aL) {
                Q.gallery.splice( aJ, 1 );
                if (aJ < Q.current) {
                    --Q.current
                } else {
                    if (aJ == Q.current) {
                        Q.current = aJ > 0 ? aJ - 1 : aJ
                    }
                }
                --aJ
            }
        }
    }

    function aq(K) {
        if (!Q.options.enableKeys) {
            return
        }
        (K ? F : M)( document, "keydown", an )
    }

    function an(aG) {
        if (aG.metaKey || aG.shiftKey || aG.altKey || aG.ctrlKey) {
            return
        }
        var S = v( aG ), K;
        switch (S) {
            case 81:
            case 88:
            case 27:
                K = Q.close;
                break;
            case 37:
                K = Q.previous;
                break;
            case 39:
                K = Q.next;
                break;
            case 32:
                K = typeof ap == "number" ? Q.pause : Q.play;
                break
        }
        if (K) {
            n( aG );
            K()
        }
    }

    function c(aK) {
        aq( false );
        var aJ = Q.getCurrent();
        var aG = (aJ.player == "inline" ? "html" : aJ.player);
        if (typeof Q[aG] != "function") {
            throw"unknown player " + aG
        }
        if (aK) {
            Q.player.remove();
            Q.revertOptions();
            Q.applyOptions( aJ.options || {} )
        }
        Q.player = new Q[aG]( aJ, Q.playerId );
        if (Q.gallery.length > 1) {
            var aH = Q.gallery[Q.current + 1] || Q.gallery[0];
            if (aH.player == "img") {
                var S = new Image();
                S.src = aH.content
            }
            var aI = Q.gallery[Q.current - 1] || Q.gallery[Q.gallery.length - 1];
            if (aI.player == "img") {
                var K = new Image();
                K.src = aI.content
            }
        }
        Q.skin.onLoad( aK, W )
    }

    function W() {
        if (!A) {
            return
        }
        if (typeof Q.player.ready != "undefined") {
            var K = setInterval( function () {
                if (A) {
                    if (Q.player.ready) {
                        clearInterval( K );
                        K = null;
                        Q.skin.onReady( e )
                    }
                } else {
                    clearInterval( K );
                    K = null
                }
            }, 10 )
        } else {
            Q.skin.onReady( e )
        }
    }

    function e() {
        if (!A) {
            return
        }
        Q.player.append( Q.skin.body, Q.dimensions );
        Q.skin.onShow( I )
    }

    function I() {
        if (!A) {
            return
        }
        if (Q.player.onLoad) {
            Q.player.onLoad()
        }
        Q.options.onFinish( Q.getCurrent() );
        if (!Q.isPaused()) {
            Q.play()
        }
        aq( true )
    }

    if (!Array.prototype.indexOf) {
        Array.prototype.indexOf = function (S, aG) {
            var K = this.length >>> 0;
            aG = aG || 0;
            if (aG < 0) {
                aG += K
            }
            for (; aG < K; ++aG) {
                if (aG in this && this[aG] === S) {
                    return aG
                }
            }
            return -1
        }
    }
    function aw() {
        return(new Date).getTime()
    }

    function aC(K, aG) {
        for (var S in aG) {
            K[S] = aG[S]
        }
        return K
    }

    function aF(aH, aI) {
        var S = 0, K = aH.length;
        for (var aG = aH[0]; S < K && aI.call( aG, S, aG ) !== false; aG = aH[++S]) {
        }
    }

    function s(S, K) {
        return S.replace( /\{(\w+?)\}/g, function (aG, aH) {
            return K[aH]
        } )
    }

    function aj() {
    }

    function ad(K) {
        return document.getElementById( K )
    }

    function C(K) {
        K.parentNode.removeChild( K )
    }

    var h = true, x = true;

    function d() {
        var K = document.body, S = document.createElement( "div" );
        h = typeof S.style.opacity === "string";
        S.style.position = "fixed";
        S.style.margin = 0;
        S.style.top = "20px";
        K.appendChild( S, K.firstChild );
        x = S.offsetTop == 20;
        K.removeChild( S )
    }

    Q.getStyle = (function () {
        var K = /opacity=([^)]*)/, S = document.defaultView && document.defaultView.getComputedStyle;
        return function (aJ, aI) {
            var aH;
            if (!h && aI == "opacity" && aJ.currentStyle) {
                aH = K.test( aJ.currentStyle.filter || "" ) ? (parseFloat( RegExp.$1 ) / 100) + "" : "";
                return aH === "" ? "1" : aH
            }
            if (S) {
                var aG = S( aJ, null );
                if (aG) {
                    aH = aG[aI]
                }
                if (aI == "opacity" && aH == "") {
                    aH = "1"
                }
            } else {
                aH = aJ.currentStyle[aI]
            }
            return aH
        }
    })();
    Q.appendHTML = function (aG, S) {
        if (aG.insertAdjacentHTML) {
            aG.insertAdjacentHTML( "BeforeEnd", S )
        } else {
            if (aG.lastChild) {
                var K = aG.ownerDocument.createRange();
                K.setStartAfter( aG.lastChild );
                var aH = K.createContextualFragment( S );
                aG.appendChild( aH )
            } else {
                aG.innerHTML = S
            }
        }
    };
    Q.getWindowSize = function (K) {
        if (document.compatMode === "CSS1Compat") {
            return document.documentElement["client" + K]
        }
        return document.body["client" + K]
    };
    Q.setOpacity = function (aG, K) {
        var S = aG.style;
        if (h) {
            S.opacity = (K == 1 ? "" : K)
        } else {
            S.zoom = 1;
            if (K == 1) {
                if (typeof S.filter == "string" && (/alpha/i).test( S.filter )) {
                    S.filter = S.filter.replace( /\s*[\w\.]*alpha\([^\)]*\);?/gi, "" )
                }
            } else {
                S.filter = (S.filter || "").replace( /\s*[\w\.]*alpha\([^\)]*\)/gi, "" ) + " alpha(opacity=" + (K * 100) + ")"
            }
        }
    };
    Q.clearOpacity = function (K) {
        Q.setOpacity( K, 1 )
    };
    function o(S) {
        var K = S.target ? S.target : S.srcElement;
        return K.nodeType == 3 ? K.parentNode : K
    }

    function V(S) {
        var K = S.pageX || (S.clientX + (document.documentElement.scrollLeft || document.body.scrollLeft)), aG = S.pageY || (S.clientY + (document.documentElement.scrollTop || document.body.scrollTop));
        return[K, aG]
    }

    function n(K) {
        K.preventDefault()
    }

    function v(K) {
        return K.which ? K.which : K.keyCode
    }

    function F(aH, aG, S) {
        if (aH.addEventListener) {
            aH.addEventListener( aG, S, false )
        } else {
            if (aH.nodeType === 3 || aH.nodeType === 8) {
                return
            }
            if (aH.setInterval && (aH !== au && !aH.frameElement)) {
                aH = au
            }
            if (!S.__guid) {
                S.__guid = F.guid++
            }
            if (!aH.events) {
                aH.events = {}
            }
            var K = aH.events[aG];
            if (!K) {
                K = aH.events[aG] = {};
                if (aH["on" + aG]) {
                    K[0] = aH["on" + aG]
                }
            }
            K[S.__guid] = S;
            aH["on" + aG] = F.handleEvent
        }
    }

    F.guid = 1;
    F.handleEvent = function (aH) {
        var K = true;
        aH = aH || F.fixEvent( ((this.ownerDocument || this.document || this).parentWindow || au).event );
        var S = this.events[aH.type];
        for (var aG in S) {
            this.__handleEvent = S[aG];
            if (this.__handleEvent( aH ) === false) {
                K = false
            }
        }
        return K
    };
    F.preventDefault = function () {
        this.returnValue = false
    };
    F.stopPropagation = function () {
        this.cancelBubble = true
    };
    F.fixEvent = function (K) {
        K.preventDefault = F.preventDefault;
        K.stopPropagation = F.stopPropagation;
        return K
    };
    function M(aG, S, K) {
        if (aG.removeEventListener) {
            aG.removeEventListener( S, K, false )
        } else {
            if (aG.events && aG.events[S]) {
                delete aG.events[S][K.__guid]
            }
        }
    }

    var y = false, al;
    if (document.addEventListener) {
        al = function () {
            document.removeEventListener( "DOMContentLoaded", al, false );
            Q.load()
        }
    } else {
        if (document.attachEvent) {
            al = function () {
                if (document.readyState === "complete") {
                    document.detachEvent( "onreadystatechange", al );
                    Q.load()
                }
            }
        }
    }
    function g() {
        if (y) {
            return
        }
        try {
            document.documentElement.doScroll( "left" )
        } catch (K) {
            setTimeout( g, 1 );
            return
        }
        Q.load()
    }

    function P() {
        if (document.readyState === "complete") {
            return Q.load()
        }
        if (document.addEventListener) {
            document.addEventListener( "DOMContentLoaded", al, false );
            au.addEventListener( "load", Q.load, false )
        } else {
            if (document.attachEvent) {
                document.attachEvent( "onreadystatechange", al );
                au.attachEvent( "onload", Q.load );
                var K = false;
                try {
                    K = au.frameElement === null
                } catch (S) {
                }
                if (document.documentElement.doScroll && K) {
                    g()
                }
            }
        }
    }

    Q.load = function () {
        if (y) {
            return
        }
        if (!document.body) {
            return setTimeout( Q.load, 13 )
        }
        y = true;
        d();
        Q.onReady();
        if (!Q.options.skipSetup) {
            Q.setup()
        }
        Q.skin.init()
    };
    Q.plugins = {};
    if (navigator.plugins && navigator.plugins.length) {
        var w = [];
        aF( navigator.plugins, function (K, S) {
            w.push( S.name )
        } );
        w = w.join( "," );
        var ai = w.indexOf( "Flip4Mac" ) > -1;
        Q.plugins = {fla:w.indexOf( "Shockwave Flash" ) > -1, qt:w.indexOf( "QuickTime" ) > -1, wmp:!ai && w.indexOf( "Windows Media" ) > -1, f4m:ai}
    } else {
        var p = function (K) {
            var S;
            try {
                S = new ActiveXObject( K )
            } catch (aG) {
            }
            return !!S
        };
        Q.plugins = {fla:p( "ShockwaveFlash.ShockwaveFlash" ), qt:p( "QuickTime.QuickTime" ), wmp:p( "wmplayer.ocx" ), f4m:false}
    }
    var X = /^(light|shadow)box/i, am = "shadowboxCacheKey", b = 1;
    Q.cache = {};
    Q.select = function (S) {
        var aG = [];
        if (!S) {
            var K;
            aF( document.getElementsByTagName( "a" ), function (aJ, aK) {
                K = aK.getAttribute( "rel" );
                if (K && X.test( K )) {
                    aG.push( aK )
                }
            } )
        } else {
            var aI = S.length;
            if (aI) {
                if (typeof S == "string") {
                    if (Q.find) {
                        aG = Q.find( S )
                    }
                } else {
                    if (aI == 2 && typeof S[0] == "string" && S[1].nodeType) {
                        if (Q.find) {
                            aG = Q.find( S[0], S[1] )
                        }
                    } else {
                        for (var aH = 0; aH < aI; ++aH) {
                            aG[aH] = S[aH]
                        }
                    }
                }
            } else {
                aG.push( S )
            }
        }
        return aG
    };
    Q.setup = function (K, S) {
        aF( Q.select( K ), function (aG, aH) {
            Q.addCache( aH, S )
        } )
    };
    Q.teardown = function (K) {
        aF( Q.select( K ), function (S, aG) {
            Q.removeCache( aG )
        } )
    };
    Q.addCache = function (aG, K) {
        var S = aG[am];
        if (S == k) {
            S = b++;
            aG[am] = S;
            F( aG, "click", u )
        }
        Q.cache[S] = Q.makeObject( aG, K )
    };
    Q.removeCache = function (K) {
        M( K, "click", u );
        delete Q.cache[K[am]];
        K[am] = null
    };
    Q.getCache = function (S) {
        var K = S[am];
        return(K in Q.cache && Q.cache[K])
    };
    Q.clearCache = function () {
        for (var K in Q.cache) {
            Q.removeCache( Q.cache[K].link )
        }
        Q.cache = {}
    };
    function u(K) {
        Q.open( this );
        if (Q.gallery.length) {
            n( K )
        }
    }

    /*
     * Sizzle CSS Selector Engine - v1.0
     *  Copyright 2009, The Dojo Foundation
     *  Released under the MIT, BSD, and GPL Licenses.
     *  More information: http://sizzlejs.com/
     *
     * Modified for inclusion in Shadowbox.js
     */
    Q.find = (function () {
        var aP = /((?:\((?:\([^()]+\)|[^()]+)+\)|\[(?:\[[^[\]]*\]|['"][^'"]*['"]|[^[\]'"]+)+\]|\\.|[^ >+~,(\[\\]+)+|[>+~])(\s*,\s*)?((?:.|\r|\n)*)/g, aQ = 0, aS = Object.prototype.toString, aK = false, aJ = true;
        [0, 0].sort( function () {
            aJ = false;
            return 0
        } );
        var aG = function (a1, aW, a4, a5) {
            a4 = a4 || [];
            var a7 = aW = aW || document;
            if (aW.nodeType !== 1 && aW.nodeType !== 9) {
                return[]
            }
            if (!a1 || typeof a1 !== "string") {
                return a4
            }
            var a2 = [], aY, a9, bc, aX, a0 = true, aZ = aH( aW ), a6 = a1;
            while ((aP.exec( "" ), aY = aP.exec( a6 )) !== null) {
                a6 = aY[3];
                a2.push( aY[1] );
                if (aY[2]) {
                    aX = aY[3];
                    break
                }
            }
            if (a2.length > 1 && aL.exec( a1 )) {
                if (a2.length === 2 && aM.relative[a2[0]]) {
                    a9 = aT( a2[0] + a2[1], aW )
                } else {
                    a9 = aM.relative[a2[0]] ? [aW] : aG( a2.shift(), aW );
                    while (a2.length) {
                        a1 = a2.shift();
                        if (aM.relative[a1]) {
                            a1 += a2.shift()
                        }
                        a9 = aT( a1, a9 )
                    }
                }
            } else {
                if (!a5 && a2.length > 1 && aW.nodeType === 9 && !aZ && aM.match.ID.test( a2[0] ) && !aM.match.ID.test( a2[a2.length - 1] )) {
                    var a8 = aG.find( a2.shift(), aW, aZ );
                    aW = a8.expr ? aG.filter( a8.expr, a8.set )[0] : a8.set[0]
                }
                if (aW) {
                    var a8 = a5 ? {expr:a2.pop(), set:aO( a5 )} : aG.find( a2.pop(), a2.length === 1 && (a2[0] === "~" || a2[0] === "+") && aW.parentNode ? aW.parentNode : aW, aZ );
                    a9 = a8.expr ? aG.filter( a8.expr, a8.set ) : a8.set;
                    if (a2.length > 0) {
                        bc = aO( a9 )
                    } else {
                        a0 = false
                    }
                    while (a2.length) {
                        var bb = a2.pop(), ba = bb;
                        if (!aM.relative[bb]) {
                            bb = ""
                        } else {
                            ba = a2.pop()
                        }
                        if (ba == null) {
                            ba = aW
                        }
                        aM.relative[bb]( bc, ba, aZ )
                    }
                } else {
                    bc = a2 = []
                }
            }
            if (!bc) {
                bc = a9
            }
            if (!bc) {
                throw"Syntax error, unrecognized expression: " + (bb || a1)
            }
            if (aS.call( bc ) === "[object Array]") {
                if (!a0) {
                    a4.push.apply( a4, bc )
                } else {
                    if (aW && aW.nodeType === 1) {
                        for (var a3 = 0; bc[a3] != null; a3++) {
                            if (bc[a3] && (bc[a3] === true || bc[a3].nodeType === 1 && aN( aW, bc[a3] ))) {
                                a4.push( a9[a3] )
                            }
                        }
                    } else {
                        for (var a3 = 0; bc[a3] != null; a3++) {
                            if (bc[a3] && bc[a3].nodeType === 1) {
                                a4.push( a9[a3] )
                            }
                        }
                    }
                }
            } else {
                aO( bc, a4 )
            }
            if (aX) {
                aG( aX, a7, a4, a5 );
                aG.uniqueSort( a4 )
            }
            return a4
        };
        aG.uniqueSort = function (aX) {
            if (aR) {
                aK = aJ;
                aX.sort( aR );
                if (aK) {
                    for (var aW = 1; aW < aX.length; aW++) {
                        if (aX[aW] === aX[aW - 1]) {
                            aX.splice( aW--, 1 )
                        }
                    }
                }
            }
            return aX
        };
        aG.matches = function (aW, aX) {
            return aG( aW, null, null, aX )
        };
        aG.find = function (a3, aW, a4) {
            var a2, a0;
            if (!a3) {
                return[]
            }
            for (var aZ = 0, aY = aM.order.length; aZ < aY; aZ++) {
                var a1 = aM.order[aZ], a0;
                if ((a0 = aM.leftMatch[a1].exec( a3 ))) {
                    var aX = a0[1];
                    a0.splice( 1, 1 );
                    if (aX.substr( aX.length - 1 ) !== "\\") {
                        a0[1] = (a0[1] || "").replace( /\\/g, "" );
                        a2 = aM.find[a1]( a0, aW, a4 );
                        if (a2 != null) {
                            a3 = a3.replace( aM.match[a1], "" );
                            break
                        }
                    }
                }
            }
            if (!a2) {
                a2 = aW.getElementsByTagName( "*" )
            }
            return{set:a2, expr:a3}
        };
        aG.filter = function (a6, a5, a9, aZ) {
            var aY = a6, bb = [], a3 = a5, a1, aW, a2 = a5 && a5[0] && aH( a5[0] );
            while (a6 && a5.length) {
                for (var a4 in aM.filter) {
                    if ((a1 = aM.match[a4].exec( a6 )) != null) {
                        var aX = aM.filter[a4], ba, a8;
                        aW = false;
                        if (a3 === bb) {
                            bb = []
                        }
                        if (aM.preFilter[a4]) {
                            a1 = aM.preFilter[a4]( a1, a3, a9, bb, aZ, a2 );
                            if (!a1) {
                                aW = ba = true
                            } else {
                                if (a1 === true) {
                                    continue
                                }
                            }
                        }
                        if (a1) {
                            for (var a0 = 0; (a8 = a3[a0]) != null; a0++) {
                                if (a8) {
                                    ba = aX( a8, a1, a0, a3 );
                                    var a7 = aZ ^ !!ba;
                                    if (a9 && ba != null) {
                                        if (a7) {
                                            aW = true
                                        } else {
                                            a3[a0] = false
                                        }
                                    } else {
                                        if (a7) {
                                            bb.push( a8 );
                                            aW = true
                                        }
                                    }
                                }
                            }
                        }
                        if (ba !== k) {
                            if (!a9) {
                                a3 = bb
                            }
                            a6 = a6.replace( aM.match[a4], "" );
                            if (!aW) {
                                return[]
                            }
                            break
                        }
                    }
                }
                if (a6 === aY) {
                    if (aW == null) {
                        throw"Syntax error, unrecognized expression: " + a6
                    } else {
                        break
                    }
                }
                aY = a6
            }
            return a3
        };
        var aM = aG.selectors = {order:["ID", "NAME", "TAG"], match:{ID:/#((?:[\w\u00c0-\uFFFF-]|\\.)+)/, CLASS:/\.((?:[\w\u00c0-\uFFFF-]|\\.)+)/, NAME:/\[name=['"]*((?:[\w\u00c0-\uFFFF-]|\\.)+)['"]*\]/, ATTR:/\[\s*((?:[\w\u00c0-\uFFFF-]|\\.)+)\s*(?:(\S?=)\s*(['"]*)(.*?)\3|)\s*\]/, TAG:/^((?:[\w\u00c0-\uFFFF\*-]|\\.)+)/, CHILD:/:(only|nth|last|first)-child(?:\((even|odd|[\dn+-]*)\))?/, POS:/:(nth|eq|gt|lt|first|last|even|odd)(?:\((\d*)\))?(?=[^-]|$)/, PSEUDO:/:((?:[\w\u00c0-\uFFFF-]|\\.)+)(?:\((['"]*)((?:\([^\)]+\)|[^\2\(\)]*)+)\2\))?/}, leftMatch:{}, attrMap:{"class":"className", "for":"htmlFor"}, attrHandle:{href:function (aW) {
            return aW.getAttribute( "href" )
        }}, relative:{"+":function (a2, aX) {
            var aZ = typeof aX === "string", a1 = aZ && !/\W/.test( aX ), a3 = aZ && !a1;
            if (a1) {
                aX = aX.toLowerCase()
            }
            for (var aY = 0, aW = a2.length, a0; aY < aW; aY++) {
                if ((a0 = a2[aY])) {
                    while ((a0 = a0.previousSibling) && a0.nodeType !== 1) {
                    }
                    a2[aY] = a3 || a0 && a0.nodeName.toLowerCase() === aX ? a0 || false : a0 === aX
                }
            }
            if (a3) {
                aG.filter( aX, a2, true )
            }
        }, ">":function (a2, aX) {
            var a0 = typeof aX === "string";
            if (a0 && !/\W/.test( aX )) {
                aX = aX.toLowerCase();
                for (var aY = 0, aW = a2.length; aY < aW; aY++) {
                    var a1 = a2[aY];
                    if (a1) {
                        var aZ = a1.parentNode;
                        a2[aY] = aZ.nodeName.toLowerCase() === aX ? aZ : false
                    }
                }
            } else {
                for (var aY = 0, aW = a2.length; aY < aW; aY++) {
                    var a1 = a2[aY];
                    if (a1) {
                        a2[aY] = a0 ? a1.parentNode : a1.parentNode === aX
                    }
                }
                if (a0) {
                    aG.filter( aX, a2, true )
                }
            }
        }, "":function (aZ, aX, a1) {
            var aY = aQ++, aW = aU;
            if (typeof aX === "string" && !/\W/.test( aX )) {
                var a0 = aX = aX.toLowerCase();
                aW = K
            }
            aW( "parentNode", aX, aY, aZ, a0, a1 )
        }, "~":function (aZ, aX, a1) {
            var aY = aQ++, aW = aU;
            if (typeof aX === "string" && !/\W/.test( aX )) {
                var a0 = aX = aX.toLowerCase();
                aW = K
            }
            aW( "previousSibling", aX, aY, aZ, a0, a1 )
        }}, find:{ID:function (aX, aY, aZ) {
            if (typeof aY.getElementById !== "undefined" && !aZ) {
                var aW = aY.getElementById( aX[1] );
                return aW ? [aW] : []
            }
        }, NAME:function (aY, a1) {
            if (typeof a1.getElementsByName !== "undefined") {
                var aX = [], a0 = a1.getElementsByName( aY[1] );
                for (var aZ = 0, aW = a0.length; aZ < aW; aZ++) {
                    if (a0[aZ].getAttribute( "name" ) === aY[1]) {
                        aX.push( a0[aZ] )
                    }
                }
                return aX.length === 0 ? null : aX
            }
        }, TAG:function (aW, aX) {
            return aX.getElementsByTagName( aW[1] )
        }}, preFilter:{CLASS:function (aZ, aX, aY, aW, a2, a3) {
            aZ = " " + aZ[1].replace( /\\/g, "" ) + " ";
            if (a3) {
                return aZ
            }
            for (var a0 = 0, a1; (a1 = aX[a0]) != null; a0++) {
                if (a1) {
                    if (a2 ^ (a1.className && (" " + a1.className + " ").replace( /[\t\n]/g, " " ).indexOf( aZ ) >= 0)) {
                        if (!aY) {
                            aW.push( a1 )
                        }
                    } else {
                        if (aY) {
                            aX[a0] = false
                        }
                    }
                }
            }
            return false
        }, ID:function (aW) {
            return aW[1].replace( /\\/g, "" )
        }, TAG:function (aX, aW) {
            return aX[1].toLowerCase()
        }, CHILD:function (aW) {
            if (aW[1] === "nth") {
                var aX = /(-?)(\d*)n((?:\+|-)?\d*)/.exec( aW[2] === "even" && "2n" || aW[2] === "odd" && "2n+1" || !/\D/.test( aW[2] ) && "0n+" + aW[2] || aW[2] );
                aW[2] = (aX[1] + (aX[2] || 1)) - 0;
                aW[3] = aX[3] - 0
            }
            aW[0] = aQ++;
            return aW
        }, ATTR:function (a0, aX, aY, aW, a1, a2) {
            var aZ = a0[1].replace( /\\/g, "" );
            if (!a2 && aM.attrMap[aZ]) {
                a0[1] = aM.attrMap[aZ]
            }
            if (a0[2] === "~=") {
                a0[4] = " " + a0[4] + " "
            }
            return a0
        }, PSEUDO:function (a0, aX, aY, aW, a1) {
            if (a0[1] === "not") {
                if ((aP.exec( a0[3] ) || "").length > 1 || /^\w/.test( a0[3] )) {
                    a0[3] = aG( a0[3], null, null, aX )
                } else {
                    var aZ = aG.filter( a0[3], aX, aY, true ^ a1 );
                    if (!aY) {
                        aW.push.apply( aW, aZ )
                    }
                    return false
                }
            } else {
                if (aM.match.POS.test( a0[0] ) || aM.match.CHILD.test( a0[0] )) {
                    return true
                }
            }
            return a0
        }, POS:function (aW) {
            aW.unshift( true );
            return aW
        }}, filters:{enabled:function (aW) {
            return aW.disabled === false && aW.type !== "hidden"
        }, disabled:function (aW) {
            return aW.disabled === true
        }, checked:function (aW) {
            return aW.checked === true
        }, selected:function (aW) {
            aW.parentNode.selectedIndex;
            return aW.selected === true
        }, parent:function (aW) {
            return !!aW.firstChild
        }, empty:function (aW) {
            return !aW.firstChild
        }, has:function (aY, aX, aW) {
            return !!aG( aW[3], aY ).length
        }, header:function (aW) {
            return/h\d/i.test( aW.nodeName )
        }, text:function (aW) {
            return"text" === aW.type
        }, radio:function (aW) {
            return"radio" === aW.type
        }, checkbox:function (aW) {
            return"checkbox" === aW.type
        }, file:function (aW) {
            return"file" === aW.type
        }, password:function (aW) {
            return"password" === aW.type
        }, submit:function (aW) {
            return"submit" === aW.type
        }, image:function (aW) {
            return"image" === aW.type
        }, reset:function (aW) {
            return"reset" === aW.type
        }, button:function (aW) {
            return"button" === aW.type || aW.nodeName.toLowerCase() === "button"
        }, input:function (aW) {
            return/input|select|textarea|button/i.test( aW.nodeName )
        }}, setFilters:{first:function (aX, aW) {
            return aW === 0
        }, last:function (aY, aX, aW, aZ) {
            return aX === aZ.length - 1
        }, even:function (aX, aW) {
            return aW % 2 === 0
        }, odd:function (aX, aW) {
            return aW % 2 === 1
        }, lt:function (aY, aX, aW) {
            return aX < aW[3] - 0
        }, gt:function (aY, aX, aW) {
            return aX > aW[3] - 0
        }, nth:function (aY, aX, aW) {
            return aW[3] - 0 === aX
        }, eq:function (aY, aX, aW) {
            return aW[3] - 0 === aX
        }}, filter:{PSEUDO:function (a2, aY, aZ, a3) {
            var aX = aY[1], a0 = aM.filters[aX];
            if (a0) {
                return a0( a2, aZ, aY, a3 )
            } else {
                if (aX === "contains") {
                    return(a2.textContent || a2.innerText || S( [a2] ) || "").indexOf( aY[3] ) >= 0
                } else {
                    if (aX === "not") {
                        var a1 = aY[3];
                        for (var aZ = 0, aW = a1.length; aZ < aW; aZ++) {
                            if (a1[aZ] === a2) {
                                return false
                            }
                        }
                        return true
                    } else {
                        throw"Syntax error, unrecognized expression: " + aX
                    }
                }
            }
        }, CHILD:function (aW, aZ) {
            var a2 = aZ[1], aX = aW;
            switch (a2) {
                case"only":
                case"first":
                    while ((aX = aX.previousSibling)) {
                        if (aX.nodeType === 1) {
                            return false
                        }
                    }
                    if (a2 === "first") {
                        return true
                    }
                    aX = aW;
                case"last":
                    while ((aX = aX.nextSibling)) {
                        if (aX.nodeType === 1) {
                            return false
                        }
                    }
                    return true;
                case"nth":
                    var aY = aZ[2], a5 = aZ[3];
                    if (aY === 1 && a5 === 0) {
                        return true
                    }
                    var a1 = aZ[0], a4 = aW.parentNode;
                    if (a4 && (a4.sizcache !== a1 || !aW.nodeIndex)) {
                        var a0 = 0;
                        for (aX = a4.firstChild; aX; aX = aX.nextSibling) {
                            if (aX.nodeType === 1) {
                                aX.nodeIndex = ++a0
                            }
                        }
                        a4.sizcache = a1
                    }
                    var a3 = aW.nodeIndex - a5;
                    if (aY === 0) {
                        return a3 === 0
                    } else {
                        return(a3 % aY === 0 && a3 / aY >= 0)
                    }
            }
        }, ID:function (aX, aW) {
            return aX.nodeType === 1 && aX.getAttribute( "id" ) === aW
        }, TAG:function (aX, aW) {
            return(aW === "*" && aX.nodeType === 1) || aX.nodeName.toLowerCase() === aW
        }, CLASS:function (aX, aW) {
            return(" " + (aX.className || aX.getAttribute( "class" )) + " ").indexOf( aW ) > -1
        }, ATTR:function (a1, aZ) {
            var aY = aZ[1], aW = aM.attrHandle[aY] ? aM.attrHandle[aY]( a1 ) : a1[aY] != null ? a1[aY] : a1.getAttribute( aY ), a2 = aW + "", a0 = aZ[2], aX = aZ[4];
            return aW == null ? a0 === "!=" : a0 === "=" ? a2 === aX : a0 === "*=" ? a2.indexOf( aX ) >= 0 : a0 === "~=" ? (" " + a2 + " ").indexOf( aX ) >= 0 : !aX ? a2 && aW !== false : a0 === "!=" ? a2 !== aX : a0 === "^=" ? a2.indexOf( aX ) === 0 : a0 === "$=" ? a2.substr( a2.length - aX.length ) === aX : a0 === "|=" ? a2 === aX || a2.substr( 0, aX.length + 1 ) === aX + "-" : false
        }, POS:function (a0, aX, aY, a1) {
            var aW = aX[2], aZ = aM.setFilters[aW];
            if (aZ) {
                return aZ( a0, aY, aX, a1 )
            }
        }}};
        var aL = aM.match.POS;
        for (var aI in aM.match) {
            aM.match[aI] = new RegExp( aM.match[aI].source + /(?![^\[]*\])(?![^\(]*\))/.source );
            aM.leftMatch[aI] = new RegExp( /(^(?:.|\r|\n)*?)/.source + aM.match[aI].source )
        }
        var aO = function (aX, aW) {
            aX = Array.prototype.slice.call( aX, 0 );
            if (aW) {
                aW.push.apply( aW, aX );
                return aW
            }
            return aX
        };
        try {
            Array.prototype.slice.call( document.documentElement.childNodes, 0 )
        } catch (aV) {
            aO = function (a0, aZ) {
                var aX = aZ || [];
                if (aS.call( a0 ) === "[object Array]") {
                    Array.prototype.push.apply( aX, a0 )
                } else {
                    if (typeof a0.length === "number") {
                        for (var aY = 0, aW = a0.length; aY < aW; aY++) {
                            aX.push( a0[aY] )
                        }
                    } else {
                        for (var aY = 0; a0[aY]; aY++) {
                            aX.push( a0[aY] )
                        }
                    }
                }
                return aX
            }
        }
        var aR;
        if (document.documentElement.compareDocumentPosition) {
            aR = function (aX, aW) {
                if (!aX.compareDocumentPosition || !aW.compareDocumentPosition) {
                    if (aX == aW) {
                        aK = true
                    }
                    return aX.compareDocumentPosition ? -1 : 1
                }
                var aY = aX.compareDocumentPosition( aW ) & 4 ? -1 : aX === aW ? 0 : 1;
                if (aY === 0) {
                    aK = true
                }
                return aY
            }
        } else {
            if ("sourceIndex" in document.documentElement) {
                aR = function (aX, aW) {
                    if (!aX.sourceIndex || !aW.sourceIndex) {
                        if (aX == aW) {
                            aK = true
                        }
                        return aX.sourceIndex ? -1 : 1
                    }
                    var aY = aX.sourceIndex - aW.sourceIndex;
                    if (aY === 0) {
                        aK = true
                    }
                    return aY
                }
            } else {
                if (document.createRange) {
                    aR = function (aZ, aX) {
                        if (!aZ.ownerDocument || !aX.ownerDocument) {
                            if (aZ == aX) {
                                aK = true
                            }
                            return aZ.ownerDocument ? -1 : 1
                        }
                        var aY = aZ.ownerDocument.createRange(), aW = aX.ownerDocument.createRange();
                        aY.setStart( aZ, 0 );
                        aY.setEnd( aZ, 0 );
                        aW.setStart( aX, 0 );
                        aW.setEnd( aX, 0 );
                        var a0 = aY.compareBoundaryPoints( Range.START_TO_END, aW );
                        if (a0 === 0) {
                            aK = true
                        }
                        return a0
                    }
                }
            }
        }
        function S(aW) {
            var aX = "", aZ;
            for (var aY = 0; aW[aY]; aY++) {
                aZ = aW[aY];
                if (aZ.nodeType === 3 || aZ.nodeType === 4) {
                    aX += aZ.nodeValue
                } else {
                    if (aZ.nodeType !== 8) {
                        aX += S( aZ.childNodes )
                    }
                }
            }
            return aX
        }

        (function () {
            var aX = document.createElement( "div" ), aY = "script" + (new Date).getTime();
            aX.innerHTML = "<a name='" + aY + "'/>";
            var aW = document.documentElement;
            aW.insertBefore( aX, aW.firstChild );
            if (document.getElementById( aY )) {
                aM.find.ID = function (a0, a1, a2) {
                    if (typeof a1.getElementById !== "undefined" && !a2) {
                        var aZ = a1.getElementById( a0[1] );
                        return aZ ? aZ.id === a0[1] || typeof aZ.getAttributeNode !== "undefined" && aZ.getAttributeNode( "id" ).nodeValue === a0[1] ? [aZ] : k : []
                    }
                };
                aM.filter.ID = function (a1, aZ) {
                    var a0 = typeof a1.getAttributeNode !== "undefined" && a1.getAttributeNode( "id" );
                    return a1.nodeType === 1 && a0 && a0.nodeValue === aZ
                }
            }
            aW.removeChild( aX );
            aW = aX = null
        })();
        (function () {
            var aW = document.createElement( "div" );
            aW.appendChild( document.createComment( "" ) );
            if (aW.getElementsByTagName( "*" ).length > 0) {
                aM.find.TAG = function (aX, a1) {
                    var a0 = a1.getElementsByTagName( aX[1] );
                    if (aX[1] === "*") {
                        var aZ = [];
                        for (var aY = 0; a0[aY]; aY++) {
                            if (a0[aY].nodeType === 1) {
                                aZ.push( a0[aY] )
                            }
                        }
                        a0 = aZ
                    }
                    return a0
                }
            }
            aW.innerHTML = "<a href='#'></a>";
            if (aW.firstChild && typeof aW.firstChild.getAttribute !== "undefined" && aW.firstChild.getAttribute( "href" ) !== "#") {
                aM.attrHandle.href = function (aX) {
                    return aX.getAttribute( "href", 2 )
                }
            }
            aW = null
        })();
        if (document.querySelectorAll) {
            (function () {
                var aW = aG, aY = document.createElement( "div" );
                aY.innerHTML = "<p class='TEST'></p>";
                if (aY.querySelectorAll && aY.querySelectorAll( ".TEST" ).length === 0) {
                    return
                }
                aG = function (a2, a1, aZ, a0) {
                    a1 = a1 || document;
                    if (!a0 && a1.nodeType === 9 && !aH( a1 )) {
                        try {
                            return aO( a1.querySelectorAll( a2 ), aZ )
                        } catch (a3) {
                        }
                    }
                    return aW( a2, a1, aZ, a0 )
                };
                for (var aX in aW) {
                    aG[aX] = aW[aX]
                }
                aY = null
            })()
        }
        (function () {
            var aW = document.createElement( "div" );
            aW.innerHTML = "<div class='test e'></div><div class='test'></div>";
            if (!aW.getElementsByClassName || aW.getElementsByClassName( "e" ).length === 0) {
                return
            }
            aW.lastChild.className = "e";
            if (aW.getElementsByClassName( "e" ).length === 1) {
                return
            }
            aM.order.splice( 1, 0, "CLASS" );
            aM.find.CLASS = function (aX, aY, aZ) {
                if (typeof aY.getElementsByClassName !== "undefined" && !aZ) {
                    return aY.getElementsByClassName( aX[1] )
                }
            };
            aW = null
        })();
        function K(aX, a2, a1, a5, a3, a4) {
            for (var aZ = 0, aY = a5.length; aZ < aY; aZ++) {
                var aW = a5[aZ];
                if (aW) {
                    aW = aW[aX];
                    var a0 = false;
                    while (aW) {
                        if (aW.sizcache === a1) {
                            a0 = a5[aW.sizset];
                            break
                        }
                        if (aW.nodeType === 1 && !a4) {
                            aW.sizcache = a1;
                            aW.sizset = aZ
                        }
                        if (aW.nodeName.toLowerCase() === a2) {
                            a0 = aW;
                            break
                        }
                        aW = aW[aX]
                    }
                    a5[aZ] = a0
                }
            }
        }

        function aU(aX, a2, a1, a5, a3, a4) {
            for (var aZ = 0, aY = a5.length; aZ < aY; aZ++) {
                var aW = a5[aZ];
                if (aW) {
                    aW = aW[aX];
                    var a0 = false;
                    while (aW) {
                        if (aW.sizcache === a1) {
                            a0 = a5[aW.sizset];
                            break
                        }
                        if (aW.nodeType === 1) {
                            if (!a4) {
                                aW.sizcache = a1;
                                aW.sizset = aZ
                            }
                            if (typeof a2 !== "string") {
                                if (aW === a2) {
                                    a0 = true;
                                    break
                                }
                            } else {
                                if (aG.filter( a2, [aW] ).length > 0) {
                                    a0 = aW;
                                    break
                                }
                            }
                        }
                        aW = aW[aX]
                    }
                    a5[aZ] = a0
                }
            }
        }

        var aN = document.compareDocumentPosition ? function (aX, aW) {
            return aX.compareDocumentPosition( aW ) & 16
        } : function (aX, aW) {
            return aX !== aW && (aX.contains ? aX.contains( aW ) : true)
        };
        var aH = function (aW) {
            var aX = (aW ? aW.ownerDocument || aW : 0).documentElement;
            return aX ? aX.nodeName !== "HTML" : false
        };
        var aT = function (aW, a3) {
            var aZ = [], a0 = "", a1, aY = a3.nodeType ? [a3] : a3;
            while ((a1 = aM.match.PSEUDO.exec( aW ))) {
                a0 += a1[0];
                aW = aW.replace( aM.match.PSEUDO, "" )
            }
            aW = aM.relative[aW] ? aW + "*" : aW;
            for (var a2 = 0, aX = aY.length; a2 < aX; a2++) {
                aG( aW, aY[a2], aZ )
            }
            return aG.filter( a0, aZ )
        };
        return aG
    })();
    Q.lang = {code:"en", of:"of", loading:"loading", cancel:"Cancel", next:"Next", previous:"Previous", play:"Play", pause:"Pause", close:"Close", errors:{single:'You must install the <a href="{0}">{1}</a> browser plugin to view this content.', shared:'You must install both the <a href="{0}">{1}</a> and <a href="{2}">{3}</a> browser plugins to view this content.', either:'You must install either the <a href="{0}">{1}</a> or the <a href="{2}">{3}</a> browser plugin to view this content.'}};
    var D, at = "sb-drag-proxy", E, j, ag;

    function ax() {
        E = {x:0, y:0, startX:null, startY:null}
    }

    function aA() {
        var K = Q.dimensions;
        aC( j.style, {height:K.innerHeight + "px", width:K.innerWidth + "px"} )
    }

    function O() {
        ax();
        var K = ["position:absolute", "cursor:" + (Q.isGecko ? "-moz-grab" : "move"), "background-color:" + (Q.isIE ? "#fff;filter:alpha(opacity=0)" : "transparent")].join( ";" );
        Q.appendHTML( Q.skin.body, '<div id="' + at + '" style="' + K + '"></div>' );
        j = ad( at );
        aA();
        F( j, "mousedown", L )
    }

    function B() {
        if (j) {
            M( j, "mousedown", L );
            C( j );
            j = null
        }
        ag = null
    }

    function L(S) {
        n( S );
        var K = V( S );
        E.startX = K[0];
        E.startY = K[1];
        ag = ad( Q.player.id );
        F( document, "mousemove", H );
        F( document, "mouseup", i );
        if (Q.isGecko) {
            j.style.cursor = "-moz-grabbing"
        }
    }

    function H(aI) {
        var K = Q.player, aJ = Q.dimensions, aH = V( aI );
        var aG = aH[0] - E.startX;
        E.startX += aG;
        E.x = Math.max( Math.min( 0, E.x + aG ), aJ.innerWidth - K.width );
        var S = aH[1] - E.startY;
        E.startY += S;
        E.y = Math.max( Math.min( 0, E.y + S ), aJ.innerHeight - K.height );
        aC( ag.style, {left:E.x + "px", top:E.y + "px"} )
    }

    function i() {
        M( document, "mousemove", H );
        M( document, "mouseup", i );
        if (Q.isGecko) {
            j.style.cursor = "-moz-grab"
        }
    }

    Q.img = function (S, aG) {
        this.obj = S;
        this.id = aG;
        this.ready = false;
        var K = this;
        D = new Image();
        D.onload = function () {
            K.height = S.height ? parseInt( S.height, 10 ) : D.height;
            K.width = S.width ? parseInt( S.width, 10 ) : D.width;
            K.ready = true;
            D.onload = null;
            D = null
        };
        D.src = S.content
    };
    Q.img.ext = ["bmp", "gif", "jpg", "jpeg", "png"];
    Q.img.prototype = {append:function (S, aI) {
        var aG = document.createElement( "img" );
        aG.id = this.id;
        aG.src = this.obj.content;
        aG.style.position = "absolute";
        var K, aH;
        if (aI.oversized && Q.options.handleOversize == "resize") {
            K = aI.innerHeight;
            aH = aI.innerWidth
        } else {
            K = this.height;
            aH = this.width
        }
        aG.setAttribute( "height", K );
        aG.setAttribute( "width", aH );
        S.appendChild( aG )
    }, remove:function () {
        var K = ad( this.id );
        if (K) {
            C( K )
        }
        B();
        if (D) {
            D.onload = null;
            D = null
        }
    }, onLoad:function () {
        var K = Q.dimensions;
        if (K.oversized && Q.options.handleOversize == "drag") {
            O()
        }
    }, onWindowResize:function () {
        var aH = Q.dimensions;
        switch (Q.options.handleOversize) {
            case"resize":
                var K = ad( this.id );
                K.height = aH.innerHeight;
                K.width = aH.innerWidth;
                break;
            case"drag":
                if (ag) {
                    var aG = parseInt( Q.getStyle( ag, "top" ) ), S = parseInt( Q.getStyle( ag, "left" ) );
                    if (aG + this.height < aH.innerHeight) {
                        ag.style.top = aH.innerHeight - this.height + "px"
                    }
                    if (S + this.width < aH.innerWidth) {
                        ag.style.left = aH.innerWidth - this.width + "px"
                    }
                    aA()
                }
                break
        }
    }};
    Q.iframe = function (S, aG) {
        this.obj = S;
        this.id = aG;
        var K = ad( "sb-overlay" );
        this.height = S.height ? parseInt( S.height, 10 ) : K.offsetHeight;
        this.width = S.width ? parseInt( S.width, 10 ) : K.offsetWidth
    };
    Q.iframe.prototype = {append:function (K, aG) {
        var S = '<iframe id="' + this.id + '" name="' + this.id + '" height="100%" width="100%" frameborder="0" marginwidth="0" marginheight="0" style="visibility:hidden" onload="this.style.visibility=\'visible\'" scrolling="auto"';
        if (Q.isIE) {
            S += ' allowtransparency="true"';
            if (Q.isIE6) {
                S += " src=\"javascript:false;document.write('');\""
            }
        }
        S += "></iframe>";
        K.innerHTML = S
    }, remove:function () {
        var K = ad( this.id );
        if (K) {
            C( K );
            if (Q.isGecko) {
                delete au.frames[this.id]
            }
        }
    }, onLoad:function () {
        var K = Q.isIE ? ad( this.id ).contentWindow : au.frames[this.id];
        K.location.href = this.obj.content
    }};
    Q.html = function (K, S) {
        this.obj = K;
        this.id = S;
        this.height = K.height ? parseInt( K.height, 10 ) : 300;
        this.width = K.width ? parseInt( K.width, 10 ) : 500
    };
    Q.html.prototype = {append:function (K, S) {
        var aG = document.createElement( "div" );
        aG.id = this.id;
        aG.className = "html";
        aG.innerHTML = this.obj.content;
        K.appendChild( aG )
    }, remove:function () {
        var K = ad( this.id );
        if (K) {
            C( K )
        }
    }};
    var ao = false, Y = [], q = ["sb-nav-close", "sb-nav-next", "sb-nav-play", "sb-nav-pause", "sb-nav-previous"], aa, ae, Z, m = true;

    function N(aG, aQ, aN, aL, aR) {
        var K = (aQ == "opacity"), aM = K ? Q.setOpacity : function (aS, aT) {
            aS.style[aQ] = "" + aT + "px"
        };
        if (aL == 0 || (!K && !Q.options.animate) || (K && !Q.options.animateFade)) {
            aM( aG, aN );
            if (aR) {
                aR()
            }
            return
        }
        var aO = parseFloat( Q.getStyle( aG, aQ ) ) || 0;
        var aP = aN - aO;
        if (aP == 0) {
            if (aR) {
                aR()
            }
            return
        }
        aL *= 1000;
        var aH = aw(), aK = Q.ease, aJ = aH + aL, aI;
        var S = setInterval( function () {
            aI = aw();
            if (aI >= aJ) {
                clearInterval( S );
                S = null;
                aM( aG, aN );
                if (aR) {
                    aR()
                }
            } else {
                aM( aG, aO + aK( (aI - aH) / aL ) * aP )
            }
        }, 10 )
    }

    function aB() {
        aa.style.height = Q.getWindowSize( "Height" ) + "px";
        aa.style.width = Q.getWindowSize( "Width" ) + "px"
    }

    function aE() {
        aa.style.top = document.documentElement.scrollTop + "px";
        aa.style.left = document.documentElement.scrollLeft + "px"
    }

    function ay(K) {
        if (K) {
            aF( Y, function (S, aG) {
                aG[0].style.visibility = aG[1] || ""
            } )
        } else {
            Y = [];
            aF( Q.options.troubleElements, function (aG, S) {
                aF( document.getElementsByTagName( S ), function (aH, aI) {
                    Y.push( [aI, aI.style.visibility] );
                    aI.style.visibility = "hidden"
                } )
            } )
        }
    }

    function r(aG, K) {
        var S = ad( "sb-nav-" + aG );
        if (S) {
            S.style.display = K ? "" : "none"
        }
    }

    function ah(K, aJ) {
        var aI = ad( "sb-loading" ), aG = Q.getCurrent().player, aH = (aG == "img" || aG == "html");
        if (K) {
            Q.setOpacity( aI, 0 );
            aI.style.display = "block";
            var S = function () {
                Q.clearOpacity( aI );
                if (aJ) {
                    aJ()
                }
            };
            if (aH) {
                N( aI, "opacity", 1, Q.options.fadeDuration, S )
            } else {
                S()
            }
        } else {
            var S = function () {
                aI.style.display = "none";
                Q.clearOpacity( aI );
                if (aJ) {
                    aJ()
                }
            };
            if (aH) {
                N( aI, "opacity", 0, Q.options.fadeDuration, S )
            } else {
                S()
            }
        }
    }

    function t(aO) {
        var aJ = Q.getCurrent();
        ad( "sb-title-inner" ).innerHTML = aJ.title || "";
        var aP, aL, S, aQ, aM;
        if (Q.options.displayNav) {
            aP = true;
            var aN = Q.gallery.length;
            if (aN > 1) {
                if (Q.options.continuous) {
                    aL = aM = true
                } else {
                    aL = (aN - 1) > Q.current;
                    aM = Q.current > 0
                }
            }
            if (Q.options.slideshowDelay > 0 && Q.hasNext()) {
                aQ = !Q.isPaused();
                S = !aQ
            }
        } else {
            aP = aL = S = aQ = aM = false
        }
        r( "close", aP );
        r( "next", aL );
        r( "play", S );
        r( "pause", aQ );
        r( "previous", aM );
        var K = "";
        if (Q.options.displayCounter && Q.gallery.length > 1) {
            var aN = Q.gallery.length;
            if (Q.options.counterType == "skip") {
                var aI = 0, aH = aN, aG = parseInt( Q.options.counterLimit ) || 0;
                if (aG < aN && aG > 2) {
                    var aK = Math.floor( aG / 2 );
                    aI = Q.current - aK;
                    if (aI < 0) {
                        aI += aN
                    }
                    aH = Q.current + (aG - aK);
                    if (aH > aN) {
                        aH -= aN
                    }
                }
                while (aI != aH) {
                    if (aI == aN) {
                        aI = 0
                    }
                    K += '<a onclick="Shadowbox.change(' + aI + ');"';
                    if (aI == Q.current) {
                        K += ' class="sb-counter-current"'
                    }
                    K += ">" + (++aI) + "</a>"
                }
            } else {
                K = [Q.current + 1, Q.lang.of, aN].join( " " )
            }
        }
        ad( "sb-counter" ).innerHTML = K;
        aO()
    }

    function U(aH) {
        var K = ad( "sb-title-inner" ), aG = ad( "sb-info-inner" ), S = 0.35;
        K.style.visibility = aG.style.visibility = "";
        if (K.innerHTML != "") {
            N( K, "marginTop", 0, S )
        }
        N( aG, "marginTop", 0, S, aH )
    }

    function av(aG, aM) {
        var aK = ad( "sb-title" ), K = ad( "sb-info" ), aH = aK.offsetHeight, aI = K.offsetHeight, aJ = ad( "sb-title-inner" ), aL = ad( "sb-info-inner" ), S = (aG ? 0.35 : 0);
        N( aJ, "marginTop", aH, S );
        N( aL, "marginTop", aI * -1, S, function () {
            aJ.style.visibility = aL.style.visibility = "hidden";
            aM()
        } )
    }

    function ac(K, aH, S, aJ) {
        var aI = ad( "sb-wrapper-inner" ), aG = (S ? Q.options.resizeDuration : 0);
        N( Z, "top", aH, aG );
        N( aI, "height", K, aG, aJ )
    }

    function ar(K, aH, S, aI) {
        var aG = (S ? Q.options.resizeDuration : 0);
        N( Z, "left", aH, aG );
        N( Z, "width", K, aG, aI )
    }

    function ak(aM, aG) {
        var aI = ad( "sb-body-inner" ), aM = parseInt( aM ), aG = parseInt( aG ), S = Z.offsetHeight - aI.offsetHeight, K = Z.offsetWidth - aI.offsetWidth, aK = ae.offsetHeight, aL = ae.offsetWidth, aJ = parseInt( Q.options.viewportPadding ) || 20, aH = (Q.player && Q.options.handleOversize != "drag");
        return Q.setDimensions( aM, aG, aK, aL, S, K, aJ, aH )
    }

    var T = {};
    T.markup = '<div id="sb-container"><div id="sb-overlay"></div><div id="sb-wrapper"><div id="sb-title"><div id="sb-title-inner"></div></div><div id="sb-wrapper-inner"><div id="sb-body"><div id="sb-body-inner"></div><div id="sb-loading"><div id="sb-loading-inner"><span>{loading}</span></div></div></div></div><div id="sb-info"><div id="sb-info-inner"><div id="sb-counter"></div><div id="sb-nav"><a id="sb-nav-close" title="{close}" onclick="Shadowbox.close()"></a><a id="sb-nav-next" title="{next}" onclick="Shadowbox.next()"></a><a id="sb-nav-play" title="{play}" onclick="Shadowbox.play()"></a><a id="sb-nav-pause" title="{pause}" onclick="Shadowbox.pause()"></a><a id="sb-nav-previous" title="{previous}" onclick="Shadowbox.previous()"></a></div></div></div></div></div>';
    T.options = {animSequence:"sync", counterLimit:10, counterType:"default", displayCounter:true, displayNav:true, fadeDuration:0.35, initialHeight:160, initialWidth:320, modal:false, overlayColor:"#000", overlayOpacity:0.5, resizeDuration:0.35, showOverlay:true, troubleElements:["select", "object", "embed", "canvas"]};
    T.init = function () {
        Q.appendHTML( document.body, s( T.markup, Q.lang ) );
        T.body = ad( "sb-body-inner" );
        aa = ad( "sb-container" );
        ae = ad( "sb-overlay" );
        Z = ad( "sb-wrapper" );
        if (!x) {
            aa.style.position = "absolute"
        }
        if (!h) {
            var aG, K, S = /url\("(.*\.png)"\)/;
            aF( q, function (aI, aJ) {
                aG = ad( aJ );
                if (aG) {
                    K = Q.getStyle( aG, "backgroundImage" ).match( S );
                    if (K) {
                        aG.style.backgroundImage = "none";
                        aG.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(enabled=true,src=" + K[1] + ",sizingMethod=scale);"
                    }
                }
            } )
        }
        var aH;
        F( au, "resize", function () {
            if (aH) {
                clearTimeout( aH );
                aH = null
            }
            if (A) {
                aH = setTimeout( T.onWindowResize, 10 )
            }
        } )
    };
    T.onOpen = function (K, aG) {
        m = false;
        aa.style.display = "block";
        aB();
        var S = ak( Q.options.initialHeight, Q.options.initialWidth );
        ac( S.innerHeight, S.top );
        ar( S.width, S.left );
        if (Q.options.showOverlay) {
            ae.style.backgroundColor = Q.options.overlayColor;
            Q.setOpacity( ae, 0 );
            if (!Q.options.modal) {
                F( ae, "click", Q.close )
            }
            ao = true
        }
        if (!x) {
            aE();
            F( au, "scroll", aE )
        }
        ay();
        aa.style.visibility = "visible";
        if (ao) {
            N( ae, "opacity", Q.options.overlayOpacity, Q.options.fadeDuration, aG )
        } else {
            aG()
        }
    };
    T.onLoad = function (S, K) {
        ah( true );
        while (T.body.firstChild) {
            C( T.body.firstChild )
        }
        av( S, function () {
            if (!A) {
                return
            }
            if (!S) {
                Z.style.visibility = "visible"
            }
            t( K )
        } )
    };
    T.onReady = function (aH) {
        if (!A) {
            return
        }
        var S = Q.player, aG = ak( S.height, S.width );
        var K = function () {
            U( aH )
        };
        switch (Q.options.animSequence) {
            case"hw":
                ac( aG.innerHeight, aG.top, true, function () {
                    ar( aG.width, aG.left, true, K )
                } );
                break;
            case"wh":
                ar( aG.width, aG.left, true, function () {
                    ac( aG.innerHeight, aG.top, true, K )
                } );
                break;
            default:
                ar( aG.width, aG.left, true );
                ac( aG.innerHeight, aG.top, true, K )
        }
    };
    T.onShow = function (K) {
        ah( false, K );
        m = true
    };
    T.onClose = function () {
        if (!x) {
            M( au, "scroll", aE )
        }
        M( ae, "click", Q.close );
        Z.style.visibility = "hidden";
        var K = function () {
            aa.style.visibility = "hidden";
            aa.style.display = "none";
            ay( true )
        };
        if (ao) {
            N( ae, "opacity", 0, Q.options.fadeDuration, K )
        } else {
            K()
        }
    };
    T.onPlay = function () {
        r( "play", false );
        r( "pause", true )
    };
    T.onPause = function () {
        r( "pause", false );
        r( "play", true )
    };
    T.onWindowResize = function () {
        if (!m) {
            return
        }
        aB();
        var K = Q.player, S = ak( K.height, K.width );
        ar( S.width, S.left );
        ac( S.innerHeight, S.top );
        if (K.onWindowResize) {
            K.onWindowResize()
        }
    };
    Q.skin = T;
    au.Shadowbox = Q
})( window );