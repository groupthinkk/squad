(function(global) {

    var postIndex = 0;
    var score = {
        right: 0,
        wrong: 0
    };
    var timer;
    console.log(timer);

    function setupStopwatch() {
        timer = $("#timer").TimeCircles({
            "animation": "smooth",
            "bg_width": 1,
            "fg_width": 0.13333333333333333,
            "circle_bg_color": "#EEEEEE",
            "total_duration": 10,
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
                //timer.stop();
                //showTimesUp();
                showNextPost();
                //timer.start();
            }
        });

        //timer.stop();
        console.log(timer);
    }

    function highlightPost(post) {
        post.addClass('selected');
        setTimeout(function() {
            post.removeClass('selected');
        }, 200);
    }

    function displayDashboard() {
        //window.location.href="/end";
        var total = score.right + score.wrong;
        var accuracy = score.right / (score.right + score.wrong) * 100;
        accuracy = accuracy.toFixed(1);
        //$(body).addClass('dashboard');
        $('.main').hide();
        $('#right').text(score.right);
        $('#wrong').text(score.wrong);
        $('#accuracy').text(accuracy);
        $('#dashboard').fadeIn();
    }

    function showTimestamps() {
        var timeFormat = 'dd MMM D, h:mma';
        var timestamp1 = moment.utc(post1timestamp).toDate();
        timestamp1 = moment(post1timestamp).format(timeFormat);
        var timestamp2 = moment.utc(post2timestamp).toDate();
        timestamp2 = moment(post2timestamp).format(timeFormat);

        $('#timestamp1').text(timestamp1);
        $('#timestamp2').text(timestamp2);
    }

    function showPost() {
        var $container = $('.viewport');
        var scrollTo = $container.offset().left + $container.width() / 2;

        setTimeout(function() {
            $container.scrollLeft(scrollTo);
        }, 200);

    }

    function showNextPost() {
        if (postIndex < posts.length - 1) {
            //timer.stop();
            //timer = null;
            postIndex++;
            showPost();
            //setupStopwatch();
            //timer.restart();
            //timer.start();
        } else {
            displayDashboard();
            //showTimesUp();
        }
    }

    function updateScore(selected) {
        var selectedIndex = selected.attr('id').split('-')[1];
        var post0likes = posts[postIndex].posts[0].likes;
        var post1likes = posts[postIndex].posts[1].likes;
        var betterPostIndex = post0likes > post1likes ? 0 : 1;

        if (selectedIndex == betterPostIndex) {
            score.right++;
        } else {
            score.wrong++;
        }
    }

    function setupTouchDetect() {
        var post = $('.post').singletap(function() {
            //$("#timer").TimeCircles().destroy();
            //highlightPost($(this));
            //updateScore($(this));
            //showNextPost();
            //setupStopwatch();
        }).doubletap(function() {
            $("#timer").TimeCircles().destroy();
            highlightPost($(this));
            updateScore($(this));
            showNextPost();
            setupStopwatch();
        });

        post.tapend(function(e, touch) {
            e.preventDefault();
        });
    }

    function cacheNextImages(index) {

        var url0 = posts[index].posts[0].image;
        var url1 = posts[index].posts[1].image;

        var img1 = new Image();
        img1.src = 'images/' + url0;

        var img2 = new Image();
        img2.src = 'images/' + url1;
    }

    function parallelLoadImages(imageArray, index) {
        index = index || 0;
        debugger;

        if (imageArray && imageArray.length > index) {
            var img = new Image();
            img.onload = function () {
                parallelLoadImages(imageArray, index + 1);
            };

            img.src = imageArray[index];
        }
    }

    function init() {
        var $container = $('.viewport');
        var scrollTo = $container.offset().left + $container.width() / 2;
        var images = collectImageUrls();

        //parallelLoadImages(images);
        showPost();
        setupStopwatch();
        setupTouchDetect();
        $container.scrollLeft(scrollTo);
    }

    global.init = init;
    global.displayDashboard = displayDashboard;

})(window);

$(document).ready(function() {
   init();
    //displayDashboard();
});