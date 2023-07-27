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
  const [selection, setSelection] = useState("");
  
    const navigate = useNavigate()

    const onFormSubmit = (event) => {
        event.preventDefault();

        getSession().then(s => setSession(s))
        getUsername().then(u => setUsername(u))
        
        submitAnnotations(annotations[0]);
      };


    const BackendAuthorized = axios.create({
        baseURL: 'http://localhost:5001',
        headers: {
          'Content-Type': 'application/json',
          'Accept':'application/json',
          'Authorization': `${username} ${session}`
        }
      })

    const submitAnnotations = async (annotation) => {
      
        const response = await BackendAuthorized.post(
            '/annotations', {
              x0: annotation['upperLeft'][0],
              y0: annotation['upperLeft'][1],
              x1: annotation['lowerRight'][0],
              y1: annotation['lowerRight'][1],
              image_width: annotation['imageWidth'],
              image_height: annotation['imageHeight'],
              observation_id: window.location.search.split("=")[1]
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
   
    const toggleOriginal = () => {
      if (selection == "origional"){setSelection("")}
      else {setSelection("origional")}
    }

    const toggleGreyscaled = () => {
      if (selection == "greyscale"){setSelection("")}
      else {setSelection("greyscale")}
    }

    const toggleThreshold = () => {
      if (selection == "threshold"){setSelection("")}
      else {setSelection("threshold")}
    }

    const clearType = () => {setSelection("")}

    const parsed_annotations = () => {
      return annotations.map(ann => `UL:(${ann['upperLeft'].join(",")}) LR:(${ann['lowerRight'].join(",")})`).join(' , ')
    }

    return (
    <form onSubmit={onFormSubmit}>
      {Annotator(window.location.search.split("=")[1], selection,annotations, setAnnotations, clearType)}
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
        <img src={`http://localhost:5001/images?satnogs_id=${window.location.search.split("=")[1]}&type=origional`} className="img-fluid" onClick={toggleOriginal}/>
          </div>
          <div className="col">
          <img src={`http://localhost:5001/images?satnogs_id=${window.location.search.split("=")[1]}&type=greyscale`} className="img-fluid" onClick={toggleGreyscaled}/>
          </div>
          <div className="col">
          <img src={`http://localhost:5001/images?satnogs_id=${window.location.search.split("=")[1]}&type=threshold`} className="img-fluid" onClick={toggleThreshold}/>
          </div>
        </div>
      </div>)}
        <div className="mb-3">
        <label htmlFor="annotations" className="form-label">Annotations:</label>
        <textarea type="textarea" className="form-control" id="annotations"  disabled={true} value={parsed_annotations()}
        onChange={() => setAnnotations(event.target.value)} style={{'padding': "4px"}}/>
        </div>
      <button type="submit" className="btn btn-primary" style={{'margin': "4px"}}>Submit Annotations</button>
      <button type="button" className="btn btn-secondary" style={{'margin': "4px"}}onClick={() => setAnnotations([])}>Clear Annotations</button>
    </form>
    );
  }