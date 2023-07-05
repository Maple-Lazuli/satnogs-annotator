import React, {useState} from "react";
import {getUsername, getSession} from '../credentials'
import {redirect, useNavigate} from "react-router-dom";
import axios from 'axios';
import Backend from '../api';

export default function CreateAnnotation() {
  const [observationData, setObservationData] = useState({satnogs_id: null, status: -1});
  const [annotations, setAnnotations] = useState([]);
  const [username, setUsername] = useState("");
  const [session, setSession] = useState("");
  
    const navigate = useNavigate()

    const onFormSubmit = (event) => {
        event.preventDefault();
      };


    const BackendAuthorized = axios.create({
        baseURL: 'http://localhost:5001',
        headers: {
          'Content-Type': 'application/json',
          'Accept':'application/json',
          'Authorization': `${username} ${session}`
        }
      })

      getSession().then(s => setSession(s))
      getUsername().then(u => setUsername(u))


    const onItemSubmit = async (annotations) => {

      
        const response = await BackendAuthorized.post(
            '/annotations', {
              annotations: annotations,
                    observation_id: observation_id
              }).then( (res) => {

                navigate("/YourAnnotations");
    })}

    const fetchObservation = async () => {

      const response = await Backend.get(
          `/observation?satnogs_id=${window.location.search.split("=")[1]}`, {}).then( (res) => {

            if (res['data']['status']  == 0) {
              setObservationData({satnogs_id: res['data']['satnogs_id'], status: res['data']['status']})
            } else {
              setObservationData({status: -2})
              }
          })}

    if (observationData['status'] == -1){
      fetchObservation()
    }
   

    return (
    <form onSubmit={onFormSubmit}>
      { observationData['status'] < 0 ? (
        <div className="spinner-border" style={{width: "3rem", height: "3rem"}} role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
      ) : (<></>)}

      <div className="container text-center">
        <div className="row">
          {/* maybe add some satnogs information here? */}
          <div className="col">
            Original Image
          </div>
          </div>

          <div className="row">

            <hr />

          <div className="col">
            Greyscaled
          </div>
          <div className="col">
            Thresholded
          </div>
        </div>
      </div>

        <div className="mb-3">
        <label htmlFor="annotations" className="form-label">Annotations:</label>
        <input type="text" className="form-control" id="annotations" placeholder=""
        onChange={() => setAnnotations(event.target.value)}/>
        {/* Add a submit button here */}
        </div>
    </form>
    );
  }