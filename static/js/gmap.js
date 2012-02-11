function initialize(stoplat, stoplong, userlat, userlong) {
	theStop = new google.maps.LatLng(stoplat, stoplong);
	var stopIcon = new google.maps.MarkerImage("/static/bus.png");
	var userIcon = new google.maps.MarkerImage("/static/person.png");

	var myOptions = {
		center: theStop,
		zoom: 16,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};

	var map = new google.maps.Map(document.getElementById("map_canvas"),
	    myOptions);

	var stopMarker = new google.maps.Marker({
      position: theStop,
      map: map,
      icon: stopIcon,
      title: "Stop"
    })

    if (userlat && userlong){
		theUser = new google.maps.LatLng(userlat, userlong);

	    var userMarker = new google.maps.Marker({
	      position: theUser,
	   	  map: map,
	      icon: userIcon,
	      title: "You are here"
	    })

	    var directionsService = new google.maps.DirectionsService();
	    var directionsDisplay = new google.maps.DirectionsRenderer({
		    markerOptions: {
			    visible:false
			    }
			});

	    var request = {
	    	origin: theUser,
	    	destination: theStop,
	    	travelMode: google.maps.TravelMode.WALKING
	    };

	    directionsService.route(request, function(response, status) {
	    	if (status == google.maps.DirectionsStatus.OK) {
	    		directionsDisplay.setDirections(response);
	    		duration = response.routes[0].legs[0].duration.text;
	    		document.getElementById("duration").innerHTML = "Around " + duration + " walk";
	    	}
	    });

	    directionsDisplay.setMap(map);

	}

    var bounds = new google.maps.LatLngBounds();
    bounds.extend(theStop)
    bounds.extend(theUser)
    map.fitBounds(bounds)
} 

initialize(stoplat, stoplong, userlat, userlong);