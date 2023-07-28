import React, {useState} from "react";
import './annotator.css'
import annotationDisplay from "./annotationDisplay"
import axios from 'axios';
import {getUsername, getSession} from './credentials'
export default function Annotator(satnogs_id,type,annotations, setAnnotations, clearType) {  

    const [capture, setCapture] = useState(false);
    const [upperLeft, setUpperLeft] = useState(-1);
    const [currentPos, setCurrentPos] = useState(-1);
    // const [lowerRight, setLowerRight] = useState(-1);
    const [box, setBox] = useState(null)    
    const [username, setUsername] = useState("");
    const [session, setSession] = useState("");
    getSession().then(s => setSession(s))
    getUsername().then(u => setUsername(u))

    const onFormSubmit = (event) => {
        event.preventDefault();
      };

    const startCapture = (event) => {
        setCapture(true)
        setUpperLeft([event.clientX - event.target.getBoundingClientRect().left,
                      event.clientY - event.target.getBoundingClientRect().top])
        setBox(createDiv(event.clientX, event.clientY))
    }
    const trackMouse = (event) => {
        if (capture) {
            setCurrentPos([event.clientX - event.target.getBoundingClientRect().left,
                event.clientY - event.target.getBoundingClientRect().top])
            updateSize(event.clientX - event.target.getBoundingClientRect().left, event.clientY- event.target.getBoundingClientRect().top)
        }
    }
    const stopCapture = (event) => {
        setCapture(false)
        // setLowerRight([event.clientX - event.target.getBoundingClientRect().left,
        //     event.clientY - event.target.getBoundingClientRect().top])
        box.remove()


        if (((event.clientX - event.target.getBoundingClientRect().left - upperLeft[0]) > 5) && 
            ((event.clientY - event.target.getBoundingClientRect().top - upperLeft[1]) > 2)){
                annotations.push({
                    'parentLeft':event.target.getBoundingClientRect().left,
                    'parentTop':event.target.getBoundingClientRect().top,
                    'imageWidth':event.target.getBoundingClientRect().width,
                    'imageHeight':event.target.getBoundingClientRect().height,
                    'upperLeft':upperLeft,
                    'lowerRight':[event.clientX - event.target.getBoundingClientRect().left,
                                    event.clientY - event.target.getBoundingClientRect().top],
                    'annotation_id': -1,
                    'key': annotations.length != 0?(annotations.reduce((a,c) => Math.max(c)+1)):(0)})
                setAnnotations(annotations)
            }
    }

    const createDiv = (x, y) => {
        const d = document.createElement("div");
        d.style.position = "absolute";
        d.style.left = x+'px';
        d.style.top = y+'px';
        d.classList.add('annotationStart')
        document.getElementById("imagediv").appendChild(d)
        return d
    }
    const updateSize = (x, y) => {
        box.style.width = x - upperLeft[0] + 'px'
        box.style.height = y - upperLeft[1] + 'px'
    }
    const stopClick = (event) => {
        event.stopPropagation()
    }
    const clear = () => {
        setCapture(false)
        clearType()
    }

    const removeAnnotation = async (key) => {

        let annotation = annotations.filter(a => a['key'] == key)[0]

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


    const updateAnnotation = (a, key) => {
        const updated = annotations.filter(a => a['key'] != key)
        updated.push(a)
        setAnnotations(updated)
    }

    return (
        <div className = 'overlay' hidden ={type == ""} onClick={clear}>
            <div onMouseDown={() => startCapture(event)} id="imagediv" onMouseMove={() => trackMouse(event)} onMouseUp={()=> {stopCapture(event)}} onClick={stopClick}>
                <img src={`http://localhost:5001/images?satnogs_id=${satnogs_id}&type=${type}`} className="image" draggable={false} id="spectrogram"></img>
                {annotations.map(a => annotationDisplay(a, removeAnnotation, updateAnnotation, document.getElementById('spectrogram').getBoundingClientRect() ))}
            </div>
        </div>
    );
  }