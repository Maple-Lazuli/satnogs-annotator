import React, {useState} from "react";
import {getUsername, getSession} from '../credentials'

import {redirect, useNavigate} from "react-router-dom";
import axios from 'axios';
import Backend from '../api';
import Annotator from "../annotate";
import MachineObservationAnnotations from "./MachineObservationAnnotations";

export default function CreateAnnotation() {
  const [status, setStatus] = useState(-1);
  
  const [annotations, setAnnotations] = useState([]);
  const [fetched, setFetched] = useState(false);
  
  const [username, setUsername] = useState("");
  const [session, setSession] = useState("");
  const [selection, setSelection] = useState("");
  getSession().then(s => setSession(s))
  getUsername().then(u => setUsername(u))
    const navigate = useNavigate()

    const onFormSubmit = (event) => {
        event.preventDefault();        
        annotations.map(a => submitAnnotation(a))
        navigate("/Contributions")
      };


    const BackendAuthorized = axios.create({
        baseURL: 'http://localhost:5001',
        headers: {
          'Content-Type': 'application/json',
          'Accept':'application/json',
          'Authorization': `${username} ${session}`
        }
      })

    const submitAnnotation = async (annotation) => {
        if (annotation['annotation_id'] == -1) {
            const response = BackendAuthorized.post(
            '/annotation', {
              x0: annotation['upperLeft'][0],
              y0: annotation['upperLeft'][1],
              x1: annotation['lowerRight'][0],
              y1: annotation['lowerRight'][1],
              image_width: annotation['imageWidth'],
              image_height: annotation['imageHeight'],
              observation_id: window.location.search.split("=")[1]
              }).then( (res) => {console.log(res)})
        } 
        // else {
        //   const response = BackendAuthorized.put(
        //     '/annotation', {
        //       x0: annotation['upperLeft'][0],
        //       y0: annotation['upperLeft'][1],
        //       x1: annotation['lowerRight'][0],
        //       y1: annotation['lowerRight'][1],
        //       image_width: annotation['imageWidth'],
        //       image_height: annotation['imageHeight'],
        //       annotation_id: annotation['annotation_id']
        //       }).then( (res) => {console.log(res)})
        // }
    }

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

    const get_annotations = async () => {
      const response2 = await Backend.get(`/annotationsBySatnogsID?satnogs_id=${window.location.search.split("=")[1]}`, {})
      .then( (res) => {update_annotations(res['data'])})
    }

    const update_annotations = (annotations) => {
      for(let i = 0; i < annotations.length; i++){
        annotations[i] = parse_annotation(annotations[i])
        annotations[i]['key'] = i
      }

      setAnnotations(annotations)
    }

    const parse_annotation = (annotation) => {
      return {
        'upperLeft': [annotation['x0'], annotation['y0']],
        'lowerRight': [annotation['x1'], annotation['y1']],
        'image_width': annotation['image_width'],
        'image_height': annotation['image_height'],
        'annotation_id': annotation['annotation_id'],
      }
    }

    const removeAnnotation = async (annotation) => {

      if (annotation['annotation_id'] != -1){
          const code = await deleteAnnotation(annotation)
          if (code == 3){
              alert("Permission Denied. Cannot other user annotations.")
          } else {
              setAnnotations(annotations.filter(a => a['key'] != key))
          }
      } else {
          setAnnotations(annotations.filter(a => a['key'] != key))
      }        
  }
  const deleteAnnotation = async (a) => {
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
        `/annotation?annotation_id=${a['annotation_id']}`).then( (res) => code = res['data']['status'])
    
    return code
}

    const clearAnnotations = () => {
      annotations.map(a => removeAnnotation(a))
    }

    if (!fetched){
      setFetched(true)
      get_annotations()
    }
    

    return (
      <div>
    <form onSubmit={onFormSubmit}>
      {Annotator(window.location.search.split("=")[1], selection, annotations, setAnnotations, clearType)}
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
      <button type="button" className="btn btn-secondary" style={{'margin': "4px"}} onClick={() => clearAnnotations()}>Clear Annotations</button>
    </form>
        <hr />
        {MachineObservationAnnotations(window.location.search.split("=")[1])}
    </div>
    );
  }