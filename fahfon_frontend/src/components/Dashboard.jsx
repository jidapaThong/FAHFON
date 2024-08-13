import React, { useEffect } from "react";
const Dashboard = ({url}) =>{
    return(
            <iframe title="CPD_dashboardV1" width="100%" height="80%" src={url.current}></iframe>
    )
}
export default Dashboard;