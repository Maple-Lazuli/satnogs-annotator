import React, {useState} from "react";
import {getUsername, getSession} from '../credentials'
import {redirect, useNavigate} from "react-router-dom";
import axios from 'axios';
import Backend from '../api';
import Annotator from "../annotate";

export default function CreateAnnotation() {
  const [status, setStatus] = useState(-1);
  
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

    const onItemSubmit = async (annotations) => {
      getSession().then(s => setSession(s))
      getUsername().then(u => setUsername(u))
      
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
              setStatus(res['data']['status'])
            } else {
              setStatus(-2)
              }
          })}

    if (status == -1){
      fetchObservation()
    }
   

    return (
    <form onSubmit={onFormSubmit}>
      {Annotator(window.location.search.split("=")[1], 'origional', setAnnotations)}
      { status < 0 ? (
        <div className="spinner-border" style={{width: "3rem", height: "3rem"}} role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
      ) : (
      <div className="container text-center">
          <div className="row">
          <div className="col">
            Original
          </div>
          <div className="col">
            Greyscaled
          </div>
          <div className="col">
            Thresholded
          </div>
        </div>
        <br />
        <div className="row">
        <div className="col">
        <img src={`http://localhost:5001/images?satnogs_id=7808415&type=origional`} className="img-fluid"/>
          </div>
          <div className="col">
            Greyscaled
          </div>
          <div className="col">
            Thresholded
          </div>
        </div>
      </div>)}
        <div className="mb-3">
        <label htmlFor="annotations" className="form-label">Annotations:</label>
        <input type="text" className="form-control" id="annotations" value={annotations}
        onChange={() => setAnnotations(event.target.value)}/>
        {/* Add a submit button here */}
        </div>
    </form>
    );
  }