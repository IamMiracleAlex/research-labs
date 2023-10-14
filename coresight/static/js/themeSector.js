$(document).ready(function () {
            $('.scrollmenu').slick({
                infinite: true,
                slidesToScroll: 1,
                arrows: true,
                variableWidth: true,
                responsive: [
                    {
                        breakpoint: 1024,
                        settings: {
                            slidesToShow: 6,
                            slidesToScroll: 1,
                            infinite: true,
                            dots: true
                        }
                    },
                    {
                        breakpoint: 600,
                        settings: {
                            slidesToShow: 2,
                            slidesToScroll: 1
                        }
                    },
                    {
                        breakpoint: 480,
                        settings: {
                            slidesToShow: 1,
                            slidesToScroll: 1
                        }
                    }
                ]
            })
            ;
        });
        window.onload = () => {
            // scroll to the selected tab
            document.querySelector(".active").scrollIntoView()
        };