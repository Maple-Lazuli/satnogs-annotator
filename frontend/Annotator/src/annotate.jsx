import React, {useState} from "react";
import './annotator.css'
import annotationDisplay from "./annotationDisplay"
export default function Annotator(satnogs_id,type,annotations, setAnnotations, clearType) {  

    const [capture, setCapture] = useState(false);
    const [upperLeft, setUpperLeft] = useState(-1);
    const [currentPos, setCurrentPos] = useState(-1);
    const [lowerRight, setLowerRight] = useState(-1);
    const [box, setBox] = useState(null)    

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
        setLowerRight([event.clientX - event.target.getBoundingClientRect().left,
            event.clientY - event.target.getBoundingClientRect().top])
        box.remove()
        annotations.push({
            'parentLeft':event.target.getBoundingClientRect().left,
            'parentTop':event.target.getBoundingClientRect().top,
            'upperLeft':upperLeft,
            'lowerRight':[event.clientX - event.target.getBoundingClientRect().left,
                            event.clientY - event.target.getBoundingClientRect().top],
            'key':annotations.length
        })
        setAnnotations(annotations)
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

    const removeAnnotation = (key) => {
        setAnnotations(annotations.filter(a => a['key'] != key))
    }

    return (
        <div className = 'overlay' hidden ={type == ""} onClick={clear}>
            <div onMouseDown={() => startCapture(event)} id="imagediv" onMouseMove={() => trackMouse(event)} onMouseUp={()=> {stopCapture(event)}} onClick={stopClick}>
                <img src={`http://localhost:5001/images?satnogs_id=${satnogs_id}&type=${type}`} className="image" draggable={false}></img>
                {annotations.map(a => annotationDisplay(a, removeAnnotation))}
            </div>
        </div>
    );
  }