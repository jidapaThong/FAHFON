import React from "react";
import "../css/Nav.css"
import { Link } from "react-router-dom";

const Nav = () =>{
    return(
      <div className="content" id="nav">
        <p id="nav-option"><Link to="/fahfon" style={{textDecoration:"none"}}>FahFon</Link></p>
        <p id="nav-option"><Link to="/handysense" style={{textDecoration:"none"}}>HandySense</Link></p>
      </div>
    )
}
export default Nav;