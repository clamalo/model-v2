function add_region() {
    document.querySelector("div#region").innerHTML = "";
    Object.keys(window.data.accum).map(region => {
      region_tab = document.createElement("div");
      region_tab.setAttribute("class", "tab");
      region_tab.setAttribute("id", region);
      region_tab.textContent = region;
      document.querySelector("div#region").appendChild(region_tab);
    });
  }
  function add_area(region) {
    document.querySelector("div#area").innerHTML = "";
    Object.keys(window.data.accum[region]).map(area => {
      area_tab = document.createElement("div");
      area_tab.setAttribute("class", "tab");
      area_tab.setAttribute("id", area);
      area_tab.textContent = area;
      document.querySelector("div#area").appendChild(area_tab);
    });
  }
  function switch_region(region) {
    document.querySelectorAll("div#region .tab").forEach(tab => {
      if (tab.id == region) {
        tab.classList.add("active");
      } else {
        tab.classList.remove("active");
      }
    });
    add_area(region);
    // switch_area(document.querySelector("div#area .tab").textContent);
    update_event_listener();
  }
  function switch_area(area) {
    document.querySelectorAll("div#area .tab").forEach(tab => {
      if (tab.id == area) {
        tab.classList.add("active");
      } else {
        tab.classList.remove("active");
      }
    });
    region = document.querySelector("div#region .tab.active").textContent;
    document.querySelector("img#accum").src = window.data.accum[region][area];
    update_event_listener();
  }
  function update_event_listener() {
    document.querySelectorAll("div#region .tab").forEach(tab => {
      tab.onclick = function (event) {
        switch_region(tab.id);
      };
    });
    document.querySelectorAll("div#area .tab").forEach(tab => {
      tab.onclick = function (event) {
        switch_area(tab.id);
      };
    });
  }
  
  add_region();
  add_area(document.querySelector("div#region .tab").id);
  switch_region(document.querySelector("div#region .tab").textContent);
  switch_area(document.querySelector("div#area .tab").textContent);
