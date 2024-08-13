import React, { useEffect, useRef, useState } from "react";
import L from 'leaflet';
import "leaflet.heat";
import 'leaflet/dist/leaflet.css';
import 'leaflet-defaulticon-compatibility';
import "../css/Style.css";

import { activeIcon, inactiveIcon, selectedIcon } from "../icon/marker";

const Map = ({displayData, devices, setSelectedDevice, selectedDevice}) => {
  
  const mapRef = useRef(null); // Reference current map
  const [markers, setMarkers] = useState([]); //Marker icon, Marker data, index

  //Remove the data layer
  const hideMarker = () =>{
    markers.map((marker) =>{
      mapRef.current.removeLayer(marker[0])
      mapRef.current.removeLayer(marker[1])
    })
  }
  //Add the data layer
  const displayMarker = (markerData) =>{
    markers.map((marker) => {marker[0].addTo(mapRef.current)});
    markers.map((marker) => {marker[1].addTo(mapRef.current)});
  }
  //Set the selected device to be displayed on the data card
  const handleClick = (marker) => {
    setSelectedDevice(marker[2]);
  };

  //Set the markers
  const mapDevice = (device, index) =>{
    let marker_ret = null;
    let dataLayer = L.divIcon({
      className:'icon',iconSize: [22,33],html: `${device[displayData]}`
    });
    if (index === selectedDevice){
      marker_ret = L.marker([device["latitude"],device["longitude"]], {icon: selectedIcon})
      dataLayer = L.divIcon({
        className:'icon' ,iconSize: [22,33],html: `<p style="color:white;">${device[displayData]}</p>`
      })
    }
    else{
      if (device["active"]){
        marker_ret = L.marker([device["latitude"],device["longitude"]], {icon: activeIcon})
      }
      else{      
          marker_ret = L.marker([device["latitude"],device["longitude"]], {icon: inactiveIcon})
      }
    }
    const markerData = L.marker([device["latitude"],device["longitude"]],{icon:dataLayer})
    return [marker_ret, markerData, index]
  }

  //Dispay the plain map: the first time the map component is loaded
  useEffect(() => {
    //Set the center of the map
    mapRef.current = L.map('map').setView([15.5184268,103.1895305], 12);
    //Display the tile layer (Map image layer)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      crossOrigin: true,
    }).addTo(mapRef.current);

    return () => {
      // Clean up the map when the component is unmounted
      mapRef.current.remove();
    };
  }, []);

  useEffect(() => {
    // Attach onclick event to both the icon and data layer
    markers.map((marker) => {
      marker[0].on('click', () => handleClick(marker));
      marker[1].on('click', () => handleClick(marker));
    });

    return () => {
      // Remove onclick event from each marker when the component is unmounted
      markers.map((marker) => {
        marker[0].off('click');
        marker[1].off('click');
      });
    };
  }, [markers]);

  //Everytime the sidebar is clicked or the new data is loaded
  useEffect(() => {
    const newMarkers = devices.map(mapDevice);
    hideMarker();
    setMarkers(newMarkers);
  }, [devices, displayData, selectedDevice]);

  useEffect(()=>{
    hideMarker();
    displayMarker();
  }, [markers])
  
  //Return the map
  return (
      <div className="map-container">
        <div id="map" style={{ width: '100%', height: '100%'}} />
      </div>
  );
};

export default Map;
