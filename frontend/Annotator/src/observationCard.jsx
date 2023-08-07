import axios from 'axios';
import {redirect, useNavigate} from "react-router-dom";
export default function Observation(observation, username, session) {


    const deleteObservation = async (a) => {
        let code = 0
        const BackendAuthorized = axios.create({
            baseURL: 'http://localhost:5001',
            headers: {
              'Content-Type': 'application/json',
              'Accept':'application/json',
              'Authorization': `${username} ${session}`
            }
          })

        const response = await BackendAuthorized.delete(
            `/observation?observation_id=${observation.observation_id}`).then( (res) => code = res['data']['status'])
        if (code == 0){
            alert(`Deleted ${observation.satnogs_id}:${observation.satellite_name}`)
            navigate("/allObservations");
        } else {
            alert(`Could Not Delete ${observation.satnogs_id}:${observation.satellite_name}`)
        }
        
    }

    return(
    <div class="col-3" key={observation.observation_id}>
        <div className="card">
        <img class="card-img-top" src={`http://localhost:5001/images?satnogs_id=${observation.satnogs_id}&type=origional`} alt="Card image cap"/>
        <div className="card-body">
            <h5 className="card-title">{observation.satnogs_id} </h5> 
            <h6 className="card-subtitle mb-2 text-body-secondary">{observation.satellite_name} ({observation.transmitter.split(" ")[0]})</h6>
            <p className="card-text">{`Human: ${'Yes'}`}<br/>{`Machine: ${'No'}`}</p> 
            <p class="card-text"><small class="text-body-secondary"><i>Pulled: {observation.pull_date.split(".")[0]}</i></small></p>
            <a class="btn btn-primary" href={`http://localhost:5173/CreateAnnotation?observation_id=${observation.satnogs_id}`} role="button">Annotate</a> 
            <button type="button" style={{'marginLeft':'5px'}} onClick={() => deleteObservation()}class="btn btn-danger">Delete</button>
        </div>
        </div>
    </div>
    )
}