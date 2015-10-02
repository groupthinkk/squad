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
    function startTimer(seconds) {
        timer&&clearTimeout(timer);
        var timerStart = new Date();
        var timerStop = new Date();
        timerStop.setSeconds(timerStop.getSeconds() + seconds); // js properly handles wrapping of time 11:55 +10s -> 12:05
        var $timer = $('#timer').show();

        timer = setInterval(function () {
            var now = new Date();
            if (now > timerStop) {
                stopTimer();
                timerExpired();
            }

            var x = timerStop - now;
            var w = x / (timerStop - timerStart);
            
            $timer.width((w * 100) + '%');
        }, 100);
    }

    function stopTimer() {
        clearTimeout(timer);
        $('#timer').hide();
    }

    function showImages() {
        var loaded = 0;
        function ready() {
                startTimer(10);
                $('.image').fadeIn('slow');
                $('#left').addClass('rotate-left');
                $('#right').addClass('rotate-right');
            }
        showBadge();
        ready();
    }

    function showBadge() {
        $('.badger').fadeIn('fast');
    }

    $(window).load(showImages());

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