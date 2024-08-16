import React, { useEffect, useRef, useState } from 'react';
import "../css/Style.css"
import Map from "../components/Map"
import MapTab  from '../components/MapTab';
import Nav from '../components/Nav';
import DataCard from '../components/DataCard';

import humidity from "../icon/humidity.png";
import temperature from "../icon/celsius.png";
import pressure from "../icon/pressure.png";
import rain from "../icon/rain.png";
import wind from "../icon/wind.png";
import windDirection from "../icon/wind-direction.png";
import redLight from "../icon/red-light.jpg";
import greenLight from "../icon/green-light.png";
import blueLight from "../icon/blue-dot.png";
import IR from "../icon/infrared.png";
import UVIndex from "../icon/uv-index.png";
import lux from "../icon/sun.png";
import polution from "../icon/co2.png"

//This component also handle the ineteraction and the transaction between the side bar and the map components
const Fahfon = () => {
  const [displayData, setDisplayData] = useState("temp");
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(20);
  const device = useRef({value: [null, null]});
  const options = [
    {
      option:"temp",
      img: temperature,
      display: "Temperature"
    },
    {
      option:"relativeHumidity",
      img: humidity,
      display: "Humidity"
    },
    {
      option:"barometricPressure",
      img: pressure,
      display: "Pressure"
    },
    {
      option:"rainfall",
      img: rain,
      display: "Rainfall"
    },
    {
      option:"windSpeed",
      img: wind,
      display: "Wind Speed"
    },
    {
      option:"windDirection",
      img: windDirection,
      display: "Wind Direction"
    },
    {
      option:"redLightIntensity",
      img: redLight,
      display: "Red Light Intensity"
    },
    {
      option:"greenLightIntensity",
      img: greenLight,
      display: "Green Light Intensity"
    },
    {
      option:"blueLightIntensity",
      img: blueLight,
      display: "Blue Light Intensity"
    },
    {
      option:"nearInfraredLightIntensity",
      img: IR,
      display: "Near Infrared"
    },
    {
      option:"lightIntensity",
      img: lux,
      display: "Light Intensity"
    },
    {
      option:"UVIndex",
      img: UVIndex,
      display: "UV Index"
    },
    {
      option:"PM1dot0",
      img: polution,
      display: "PM 1.0"
    },
    {
      option:"PM2dot5",
      img: polution,
      display: "PM 2.5"
    },
    {
      option:"PM4",
      img: polution,
      display: "PM 4"
    },
    {
      option:"PM10",
      img: polution,
      display: "PM 10"
    },
    {
      option:"CO2",
      img: polution,
      display: "Carbon dioxide"
    },
  ];

  //Fetch all the necessary data for the project
  const fetchData = async () =>{
    const URL = "http://209.15.96.129:8000/fahfon/latest";
    const response = await fetch(URL, {mode: "cors"});
    const jsonData = await response.json();
    return jsonData;
  }
  
  //For counting devices
  let active = 0;
  let all = 0;
  
  const rounding = (data) => {
    //Count active and all devices
    if (data["device_active"] > 0){
      active = active + 1;
    }
    all = all + 1;

    //Round the data to 2 decimal places
    data["temperature"] = Math.round(data["temperature"] * 100) / 100;
    data["humidity"] = Math.round(data["humidity"] * 100) / 100;
    data["lux"] = Math.round(data["lux"] * 100) / 100;
    data["soil"] = Math.round(data["soil"] * 100) / 100;
  }

  //Fetch the data and process it with rounding function
  const fetchDataAndProcess = async () => {
    try {
      const data = await fetchData();
      setDevices(data);
      console.log("Fetched");
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    document.title = 'Fahfon';
    fetchDataAndProcess();
  }, []);

  //The rendered components when the page is rendered
  return (
    <div className='full'>
        <Nav/>
        <div style={{height:"90%", width:"100%"}}>
        <MapTab options={options} displayData={displayData} setDisplayData = {setDisplayData}/>
          <div style={{height:"88%", display:"flex", boxSizing:"border-box"}}>
            <Map displayData={displayData} devices={devices} setSelectedDevice={setSelectedDevice}  selectedDevice={selectedDevice}/>
            <DataCard dataFields={options} data={devices[selectedDevice]} project={"fahfon"}/>
          </div>
        </div>
    </div>
  );
};

export default Fahfon;

