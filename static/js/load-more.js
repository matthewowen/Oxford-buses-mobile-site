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
   if (obj.buses.length > 1) 
   {
     h += "<a class=\"show-more\" title=\"Show\/hide\" onclick=\"toggle_visibility('" + index + "');\">";
     h += "            <div class=\"show-more\" id=\"arrow-" + index + "\">";
     h += "            <\/div>";
   } 
   h += "              <div class=\"details\">";
   h += "                <h2>" + obj.name + "<\/h2>";
   h += "                <h3>" + obj.distance + " metres away<\/h3>";

   // if there are some buses, start building their info
   if (obj.buses.length > 0)
    {
      // define how we build the first list item's info
      function buildFirstItem(item)
      {
        h += "<p><span class=\"label\">Next bus: <\/span>" + obj.buses[item].service + "to " + obj.buses[item].destination + " - " + obj.buses[0].minutes_to_departure + " minutes away<\/p>";
      }
              
      // if there's only one bus, just put that info in
      if (obj.buses.length == 1)
      {
        buildFirstItem(0)
      }
      // if there are multiple, build them all out
      else
      {
        for (item in obj.buses)
        {
          // if it is the first bus, build it out as the first bus and start the list of later buses
          if (item == 0)
          {
            buildFirstItem(item)
            h += "              <\/div>";
            h += "            <h4>Tap to show later buses<\/h4>";
            h += "          <ul class=\"bus-list\" id=\"" + index + "\">";
          }
          // for the other buses, build their info
          else
          {
            h += "              <li class=\"bus\">";
            h += "                <p class=\"service\">" + obj.buses[item].service + "to " + obj.buses[item].destination + "<\/p>";
            h += "                <p class=\"time\">" + obj.buses[item].minutes_to_departure + " minutes away<\/p>";
            h += "              <\/li>";
          }
          // close the list
        }
        h += "<\/ul>";
      }
    } 
    // if there were multiple buses, close the expand link
    if (obj.buses.length > 1)
    {           
      h += "<\/a>";
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
        createStops(info.stops);
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