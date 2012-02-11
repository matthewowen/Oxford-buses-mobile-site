// to start with, offset is 10 (we've already received that many)
var offset = 10;

// create a prepatory dictionary for the info we will get
var info = {};

// create a prepatory list for all the stops we will get back
var stops = [];

function createStops(stops) 
{
  function createStop(obj, index) 
  {
   // find the list of stops
   var l = document.getElementById("item-list");
      
   // create a list item for this stop
   i = document.createElement("li");
            
   // start building the inner html
   var h="";

   // enter the basic information about the stop
    h += "          <a class =\"details\" href=\"\/stop\/" + obj.atco + "?userlat=" + userlat + "&amp;userlong=" + userlong + "\" title=\"More about {{ stop.name }}\">";
    h += "            <h2 class=\"stopname\">" + obj.name + "<\/h2>";
    h += "            <div class=\"location\">";
    h += "            <h4>" + obj.distance + " metres away<\/h4>";
    h += "            <h4 class=\"show-map\">Show on map<\/h4>";
    h += "            <\/div>";
    h += "            <div class=\"spacer\"><\/div>";
    h += "          <\/a>";
    
    // if there are some buses, start building their info
    if (obj.buses.length > 0)
    {
      // define how we build the first list item's info
      function buildFirstItem(item)
      {
        h += "          <div class=\"buses\">";
        h += "            <a class=\"show-more\" title=\"Show\/hide\" onclick=\"toggle_visibility('" + index + "');\">";
        h += "            <div class=\"nextbus\">";
        h += "              <div class=\"service\">";
        h += "                <h4>" + obj.buses[item].service + "<\/h4>";
        h += "              <\/div>";
        h += "              <div class=\"businfo\">";
        h += "                <p>To " + obj.buses[0].destination + "<\/p>";
        h += "                <p class=\"time\">" + obj.buses[item].minutes_to_departure + " minutes away<\/p>";
        h += "              <\/div>";
        h += "              <h4 class=\"show-more\">Show later buses<\/h4>";
        h += "            <\/div>";
        h += "            <\/a>";
        h += "            <div class=\"bus-list\" id=\"" + index + "\">";
        h += "            <h4>Later buses:<\/h4>";
        h += "            <ul>";
      }

      for (item in obj.buses)
      {
        // if it is the first bus, build it out as the first bus and start the list of later buses
        if (item == 0)
        {
          buildFirstItem(item)
        }
        // for the other buses, build their info
        else
        {
          h += "                  <li class=\"bus\">";
          h += "                    <div class=\"service\">";
          h += "                      <h4>" + obj.buses[item].service + "<\/h4>";
          h += "                    <\/div>";
          h += "                    <div class=\"businfo\">";
          h += "                      <p>To " + obj.buses[item].destination + "<\/p>";
          h += "                      <p class=\"time\">" + obj.buses[item].minutes_to_departure + " minutes away<\/p>";
          h += "                    <\/div>";
          h += "                  <\/li>";
        }
      }
        // close the list
        h += "                  <\/ul>";
        h += "              <div class=\"spacer\"><\/div>";
        h += "            <\/div>";
        h += "          <\/div>";    
    }   

    else {
      h += "          <div class=\"buses\">";
      h += "          <p>No more buses in the next hour<\/p>";
      h += "          <\/div>";
    }

    // put the HTML we've built inside the list item  
    i.innerHTML = h
    // put the list item on the list
    l.appendChild(i);
  }

  // for all of the stops in the list, create a stop using the create stop process designed above
  for (i in stops) 
  {
    var obj = stops[i];       
    createStop(obj, i+offset);
  }

  // hide all the buses for the loaded stops
  var collection = document.getElementsByClassName('bus-list');
  for(var i=9; i<collection.length; i++)
  {
    collection[i].style.display = 'none';
  }
  // hide the loading gif
  l.setAttribute("class", "");
}

// the function that gets called when clicked. variables live outside as they need to maintain global scope
function loadMore(offset) 
{
  // get the load-more section, show a loading gif there
  l = document.getElementById("load-more");
  l.setAttribute("class", "loading");
  // open the request, grab the relevant stops
  httpRequest=new XMLHttpRequest();
  httpRequest.open("GET", "/ajax" + location.pathname + "/" + offset, true);
  // when received, if it is a 200, create the stops
  httpRequest.onreadystatechange = function () 
  {
    if (httpRequest.readyState === 4) 
    {
      if (httpRequest.status === 200) 
      {
        info = JSON.parse(httpRequest.responseText);
        createStops(info.stops, userlat, userlong);
        // hide the load-more if there aren't any more
        if (info.more == false)
        {
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