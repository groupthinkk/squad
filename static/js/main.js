(function (window, $) {
    // var currentPackageId;

    // function packageAvailable(p) {
    //  currentPackageId = p.packageId;
    //  showImages(p.images.a, p.images.b);
    // }

    // function loadServerPackage(next) {
    //  // this is where you make a server call and return JSON in the format of getRandomPackage()
    //  // $.getJSON( 'my-flask-app/next-image-trial', next );
    //  setTimeout(function() {
    //      var result = getRandomPackage();
    //      next(result);
    //  }, 200);
    // }

    // function loadNext() {
    //  loadServerPackage(packageAvailable);
    // }

    // function reportClick(packageId, choice, next) {
    //  console.info("CLICK %s: %s", packageId, choice);
        
    //  // this is where you call your server, report, respond with 'correct' or 'wrong'
    //  setTimeout(function() {
    //      next(getRandomBadge());
    //  }, 500);
    // }

    function timerExpired() {
        document.getElementById("posttype1").setAttribute("value", "skipped");
        document.getElementById("post1form").submit();
    }

    var timer;

    function setupStopwatch() {
        timer = $("#timer").TimeCircles({
            "animation": "smooth",
            "bg_width": 1,
            "fg_width": 0.13333333333333333,
            "circle_bg_color": "#EEEEEE",
            "total_duration": 15,
            "time": {
                "Days": {
                    "show": false
                },
                "Hours": {
                    "show": false
                },
                "Minutes": {
                    "show": false
                },
                "Seconds": {
                    //"text": "Seconds",
                    //"color": "#CCCCCC",
                    "show": true
                }
            }
        }).addListener(function(unit, value, total) {
            if (value === 0) {
                console.log(value);
                timerExpired();
            }
        });

        //timer.stop();
        console.log(timer);
    }

    function showImages() {
        function ready() {
            
            $('.image').fadeIn('slow');
        }
        //showBadge();
        ready();
    }

    // function showBadge() {
    //     $('.badger').fadeIn('fast', function() {
    //         $(this).delay(1000).fadeOut('slow');
    //     });
    // }

    function showTimestamps() {
        var timeFormat = 'dd MMM D, h:mma';
        var timestamp1 = moment.utc(post1timestamp).toDate();
        timestamp1 = moment(post1timestamp).format(timeFormat);
        var timestamp2 = moment.utc(post2timestamp).toDate();
        timestamp2 = moment(post2timestamp).format(timeFormat);

        $('#timestamp1').text(timestamp1);
        $('#timestamp2').text(timestamp2);
    }

    function highlightPost(post) {
        post.addClass('selected');
        setTimeout(function() {
            post.removeClass('selected');
        }, 200);
    }

    function setupTouchDetect() {
        var post = $('.post').singletap(function(e) {
            //$("#timer").TimeCircles().destroy();
            //highlightPost($(this));
            //updateScore($(this));
            //showNextPost();
            //setupStopwatch();
        }).tap(function() {

        }).doubletap(function() {
            $("#timer").TimeCircles().destroy();
            highlightPost($(this));
            var id = $(this).attr('id');
            submitPost(id);
        });

        post.tapend(function(e, touch) {
            e.preventDefault();
        });
    }

    // function bindArrowKeys() {
    //     $('body').on('keyup', function(e) {
    //         if (e.which === 37) { // left
    //             submitPost('post1');
    //         } else if (e.which === 39) { // right
    //             submitPost('post2');
    //         }
    //     });
    // }

    function submitPost(post) {
        var postId = '#' + post;
        $(postId).addClass('selected');
        postId = postId + 'form';

        setTimeout(function() {
            $(postId).submit();
        }, 10);

    }

    function showPost() {
        var $container = $('.viewport');
        var scrollTo = $container.offset().left + $container.width() / 2;
        var postSet = posts[postIndex];

        $('.user-avatar').attr('src', '/images/avatars/' + postSet.profile);
        $('.user-name').text(postSet.username);

        for (var i = 0; i < 2; i++) {
            var post = postSet.posts[i];
            $('.' + 'image' + i).attr('src', '/images/' + post.image);
            $('.' + 'caption' + i).text(post.caption);
            $('#' + 'timestamp' + i).text(post.date);
        }



        setTimeout(function() {
            $container.scrollLeft(scrollTo);
        }, 200);

    }

    window.init = function() {
        var $container = $('.viewport');
        var scrollTo = $container.offset().left + $container.width() / 2;
        showTimestamps();
        //showImages();
        setupStopwatch();
        setupTouchDetect();
        //bindArrowKeys();
        $container.scrollLeft(scrollTo);
    };

    // this is all testing only
    // var badges = [
    //  'correct',
    //  'wrong'
    // ];

    // var images = [
    //  'https://scontent.cdninstagram.com/hphotos-xaf1/t51.2885-15/s640x640/sh0.08/e35/11925778_1661863810693987_2072289849_n.jpg',
    //  'https://scontent.cdninstagram.com/hphotos-xaf1/t51.2885-15/s640x640/sh0.08/e35/11849361_1019883731385489_1739249310_n.jpg',
    //  'https://scontent.cdninstagram.com/hphotos-xaf1/t51.2885-15/s640x640/sh0.08/e35/11820714_512793175550228_380584461_n.jpg',
    //  'https://scontent.cdninstagram.com/hphotos-xaf1/t51.2885-15/e15/11363769_934798456581193_778702834_n.jpg',
    //  'https://scontent.cdninstagram.com/hphotos-xfa1/t51.2885-15/s640x640/sh0.08/e35/11261249_468509123326957_2035770824_n.jpg'
    // ];

    // function getRandomImageUrl() {
    //  return images[Math.floor(Math.random() * images.length)];
    // }

    // function getRandomBadge() {
    //  return badges[Math.floor(Math.random() * badges.length)];
    // }

    // function getRandomPackage() {
    //  // this is typically something you don't use when you're server provides the information
    //  return {
    //      images: {
    //          a: getRandomImageUrl(),
    //          b: getRandomImageUrl(),
    //      },
    //      packageId: 'some-identifier-provider-for-your-correlation' // could be some encoded object of time, expirey, images shown, etc.. 
    //  }
    // }

})(window,jQuery);

$(document).ready(function() {
    init();
});
