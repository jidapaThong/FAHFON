import { useEffect, useState } from "react";
import  {useLocation, useNavigate} from "react-router-dom";
import "../css/Specification.css"

const Specification = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { project } = location.state || {};
    // console.log(project);
    const  [jsonData, setJsonData] = useState(null);
    useEffect(() => {
        if(project !== undefined)
        {
            import(`../specifications/${project}.json`)
            .then(module => setJsonData(module.default))
            .catch((error)=>{
                console.error(error);
            });
        }
        else{
            navigate('/');
        }
        console.log(jsonData);
    }, []);
    return (
        jsonData !== null && (
            <div className="table-container">
                <table className="table">
            <thead>
                <tr>
                    <th id="spec">Specification</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                {
                    jsonData.map((field, index) => (
                                <tr>
                                    <td>{field["Specification"]}</td>
                                    <td>{field["Description"]}</td>
                                </tr>
                            ))
                }
            </tbody>
        </table>
            </div>
        )
    );
}
export default Specification;