import React, { useEffect, useRef, useState } from 'react';
import Dashboard from "../components/Dashboard";
import Nav from "../components/Nav"
import DropDown from '../components/DropDown';
import DownloadButton from '../components/DownloadButton';
import "../css/Style.css";
const HandySense = () =>{
    const url = useRef("https://app.powerbi.com/view?r=eyJrIjoiOTI5ZjYyZjgtNzNmYS00MDU2LTlmNmMtZTgxODZiMGJkOTlkIiwidCI6IjRhNGY3YjUyLTBlMDUtNDQxNS04NDU0LTc2ODliMDBhODdiMiIsImMiOjEwfQ%3D%3D")
    const downloadLink = useRef("http://209.15.96.129:8000/handysense/download/")
    const [device, setDevice] = useState(1);
    const [devices, setDevices] = useState([]);
    const fetchDevice = async () => {
        const URL = "http://209.15.96.129:8000/handysense/id";
        const response = await fetch(URL, {mode: "cors"});
        const jsonData = await response.json();
        return jsonData
    }
    useEffect(()=>{
        // Set the title
        document.title = 'HandySense';
        fetchDevice().then(deviceIDs =>setDevices(deviceIDs));
    }, [])

    return (
        <div className='full'>
            {/* Render nav bar and the PowerBI component */}
            <Nav/>
            <Dashboard url = {url}/>
            <DownloadButton url={downloadLink.current+`${device}`} filename={`device_${device}.csv`}/>
            <DropDown option={device} options={devices} setOption={setDevice} text={"Device"}/>
        </div>
    )
}
export default HandySense;