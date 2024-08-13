import {React, useRef} from "react";
import "../css/Style.css";
import "../css/MapTab.css";

const MapSide = ({ options, displayData ,setDisplayData }) =>{
    const clickbutton = (option) =>{
        setDisplayData(option);
    }
    return(
        <div className="side">
            {options.map((option, index) => (
            <div onClick={() => clickbutton(option.option)} className={`option-container ${option.option === displayData? 'select' : ''}`}>
                {option.img !== null && <img src={option.img} alt="icon" style={{width:"20px",height:"20px", paddingLeft:"5%"}}/>}                
                <p key={index} id="side-option">{option.display}</p>
            </div>
            ))}
        </div>
    );
}
export default MapSide;