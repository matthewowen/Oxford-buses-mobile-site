// to start with, offset is 10 (we've already received that many)
// variable is global to maintain value across multiple requests
var offset = 10;

function LoadMoreRequest (offset, userlat, userlong) {
	this.offset = offset;
	this.userlat = userlat;
	this.userlong = userlong;
	this.resource = "/ajax/stops/" + this.userlong + "+" + this.userlat + "/" + offset
	parentThis = this;
}

LoadMoreRequest.prototype.load = function() {
	// get the load-more section, show a loading gif there
  	l = document.getElementById("load-more");
	l.setAttribute("class", "button loading");
	// open the request, grab the relevant stops
	httpRequest=new XMLHttpRequest();
	httpRequest.open("GET", this.resource, true);
	// when received, if it is a 200, create the stops
	httpRequest.onreadystatechange = function () {
		if (httpRequest.readyState === 4) {
	  		if (httpRequest.status === 200) {
	    		parentThis.info = JSON.parse(httpRequest.responseText);
	    		parentThis.createHTML();
	    		// hide the load-more if there aren't any more
	    		if (parentThis.info.more == false) {
	      			var rem = document.getElementById('load-more');
	      			rem.style.display = 'none';
	    		}
	  		}
		}
	}

	httpRequest.send(null);
	// increment the offset
	return offset + 10;
}

LoadMoreRequest.prototype.buildFirstItem = function(item, h) {
  
  h += "<section class=\"buses\">";
  h += "<a class=\"show-more\" title=\"Show\/hide\" onclick=\"toggle_visibility('" + item + "');\">";
  h += "<div class=\"nextbus\">";
  h += "<div class=\"service\">";
  h += "<h4>" + this.obj.buses[item].service + "<\/h4>";
  h += "<\/div>";
  h += "<div class=\"businfo\">";
  h += "<p>To " + this.obj.buses[0].destination + "<\/p>";
  h += "<p class=\"time\">" + this.obj.buses[item].minutes_to_departure + " minutes away<\/p>";
  h += "<\/div>";
  h += "<h4 class=\"show-more button\">Show more<\/h4>";
  h += "<\/div>";
  h += "<\/a>";
  h += "<div class=\"bus-list\" id=\"" + item + "\">";
  h += "<h4>Later buses:<\/h4>";
  h += "<ul>";

  return h;
}

LoadMoreRequest.prototype.buildStop = function(obj, index) {
	
	// start building the inner html
	var h="";

	// enter the basic information about the stop
	h += "<a class =\"details\" href=\"\/stop\/" + this.obj.atco + "?userlat=" + this.userlat + "&amp;userlong=" + this.userlong + "\" title=\"More about this.obj.name\">";
	h += "<h2 class=\"stopname\">" + this.obj.name + "<\/h2>";
	h += "<div class=\"location\">";
	h += "<h4>" + this.obj.distance + " metres away<\/h4>";
	h += "<h4 class=\"show-map button\">Show on map<\/h4>";
	h += "<\/div>";
	h += "<div class=\"spacer\"><\/div>";
	h += "<\/a>";

	// if there are some buses, start building their info
	if (this.obj.buses.length > 0)
	{
	  for (item in this.obj.buses)
	  {
	    // if it is the first bus, build it out as the first bus and start the list of later buses
	    if (item == 0)
	    {
	      h = this.buildFirstItem(item, h)
	    }
	    // for the other buses, build their info
	    else
	    {
	      h += "<li class=\"bus\">";
	      h += "<div class=\"service\">";
	      h += "<h4>" + this.obj.buses[item].service + "<\/h4>";
	      h += "<\/div>";
	      h += "<div class=\"businfo\">";
	      h += "<p>To " + this.obj.buses[item].destination + "<\/p>";
	      h += "<p class=\"time\">" + this.obj.buses[item].minutes_to_departure + " minutes away<\/p>";
	      h += "<\/div>";
	      h += "<\/li>";
	    }
	  }
	    // close the list
	    h += "<\/ul>";
	    h += "<div class=\"spacer\"><\/div>";
	    h += "<\/div>";
	    h += "<\/section>";    
	}   

	else {
	  h += "<section class=\"buses\">";
	  h += "<p>No more buses in the next hour<\/p>";
	  h += "<\/section>";
	}

	// find the list of stops
	var l = document.getElementById("item-list");
	// create a list item for this stop
	i = document.createElement("li");
	// put the HTML we've built inside the list item  
	i.innerHTML = h
	// put the list item on the list
	l.appendChild(i);
  }

LoadMoreRequest.prototype.createHTML = function() {

  // for all of the stops in the list, create a stop using the create stop process designed above
  for (i in this.info.stops) 
  {
    this.obj = this.info.stops[i];       
    this.buildStop(this.obj, i+this.offset);
  }

  // hide all the buses for the loaded stops
  var collection = document.getElementsByClassName('bus-list');
  for(var i=9; i<collection.length; i++)
  {
    collection[i].style.display = 'none';
  }
  // hide the loading gif
  l.setAttribute("class", "button");
}

function doLoad (offset, userlong, userlat) {
	loadrequest = new LoadMoreRequest (offset, userlat, userlong);
	offset = loadrequest.load();
	return offset;
}