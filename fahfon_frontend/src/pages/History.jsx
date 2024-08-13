import React, {useEffect, useState} from 'react';
import { Line } from 'react-chartjs-2';
import Nav from '../components/Nav';
import MapTab from '../components/MapTab';
import DownloadButton from '../components/DownloadButton';
import { useLocation, useNavigate } from 'react-router-dom';
import "../css/Style.css";
import {
    Chart as ChartJS,
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement,
    Title,
    Tooltip
} from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';

const History = ()=>{
    const location = useLocation();
    const navigate = useNavigate();
    const { project, serial } = location.state || {};
    const [labels, setLabels] = useState([]);
    const [xscale, setXscale] = useState([]);
    const [fields, setFields] = useState([]);
    const [dataDictionary, setData] = useState([]);
    const [display, setDisplay] = useState("");
    const [data, setNewData] = useState({
      labels: labels,
      datasets: [
        {
          data: dataDictionary[display],
          fill: false,
          borderColor: 'rgb(85, 192, 192)',
          pointRadius: 0
        }
      ]
    });
    const [key, setKey] = useState(0);
    const click = (option) =>{
      setDisplay(option);
    }

    useEffect(() => {
      let newData = {...data};
      newData.datasets[0].data = dataDictionary[display];
      setNewData(newData);
      setKey(key+1);
      // console.log(key);
      // console.log(data);
    }, [display])
    
    useEffect(() => {
      if(project === undefined){
        navigate('/');
      }
      fetch(`http://209.15.96.129:8000/${project}/graph/${serial}`).then(response => response.json()).then((json) => {
        setLabels(json["labels"]);
        setXscale(json["xscale"]);
        setFields(json["fields"]);
        setData(json["data"]);
        setDisplay(json["fields"][0]["option"])
      });
    }, []);
    
    ChartJS.register(
      LineElement,
      CategoryScale,
      LinearScale,
      PointElement,
      // ChartDataLabels,
      Title,
      Tooltip
  );
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                labels: xscale
              },
            y: {
            beginAtZero: false
          }
        },
        plugins: {
            title: {
              display: true,
              text: 'Archived data of ' + serial,
            },
            tooltip: {
                callbacks:
                {
                  title: function(item){
                    const index = item[0].dataIndex;
                    return labels[index]
                  }
                }
              },
          }
      };
    console.log(options);
    return (
        <div>
            <Nav/>
            <MapTab options={fields} displayData={display} setDisplayData={click}/>
            <div id='chartContainer'>
                <div id='chart' key={key}>
                  <Line data={data} options={options}/>
                </div>    
                <div style={{paddingLeft:"80%"}}>
                  <DownloadButton url={`http://209.15.96.129:8000/${project}/download/${serial}`} filename={`${serial}.csv`}/>
                </div>
            </div>
        </div>
    );
}
export default History;