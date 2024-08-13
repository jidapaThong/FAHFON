import React, { useEffect, useState } from "react";
import "../css/DataCard.css";
import { Link } from "react-router-dom";
import active from "../icon/active.png";
import inactive from "../icon/inactive.png";

const DataCard = ({dataFields, data, project}) =>{
    
    //Set the size of the empty space at the buttom so that there is no space between each data field
    const size = Math.max(10,64-Math.ceil(dataFields.length/2)*20)
    let emptyBoxSize = size.toString();
    emptyBoxSize = emptyBoxSize+"vh";
    const [formattedTime, setFormattedTime] = useState('');
    const serial = data && data["serial"] !== undefined ? data["serial"] :"";
    // console.log(serial);
    const stateConst = {
        project: project,
        serial: serial
    };
    // console.log(stateConst);
    useEffect(() => {
        const options = {
            day: "numeric",
            month: "numeric",
            year: "numeric",
        };
        //Format the data
        if(data !== undefined)
        {
            const date = new Date(data["localTimeOnSite"]);
            // const formattedDate = date.toLocaleDateString("th-TH", options);
            setFormattedTime(date.toLocaleTimeString("th-TH", options));
        }  
    }, [data])
    return(
        <div className="container">
            <div className="device-info-field">
                <div style={{display:"flex", alignItems:"center"}}>
                    {data !== undefined && <p>{data["serial"]}</p>}
                    {data !== undefined && <img src={data["active"] ? active : inactive} alt="connection" width={20} height={20}/>}
                </div>
            {data !== undefined && <p>Location: {data["site"]}</p>}
            <Link to={{pathname:"/specification"}} state={stateConst}><p>Specs</p></Link>
            </div>
            {dataFields.map((field, index) => (
                <div key={index} className="data-field">
                    <p>{field.display}</p>
                    {data !== undefined && <p>{data[field.option]}</p>}
                </div>
            ))}
            
            <div className = "empty-box"style={{"height":`${emptyBoxSize}`}}>
                {data !== undefined && <p style={{paddingLeft:"2px", fontSize:"14px"}}>Last-Updated: {formattedTime}</p>}
                <Link to={{pathname:"/historical-data"}} state={stateConst}>
                    <p style={{textAlign:"right", paddingRight:"2px"}}>Archived data</p>
                </Link>
            </div>
        </div>
    );
}

export default DataCard;