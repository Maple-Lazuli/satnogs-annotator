import React, {useState} from "react";
import './annotator.css'
export default function annotationDisplay(annotationObject, remove) {  

    return (
        <div key = {annotationObject['key']} style={{'left': annotationObject['upperLeft'][0] + annotationObject['parentLeft'],
        "top":annotationObject['upperLeft'][1] + annotationObject['parentTop'], 'width':annotationObject['lowerRight'][0] - annotationObject['upperLeft'][0],
        'height':annotationObject['lowerRight'][1] - annotationObject['upperLeft'][1]}} className="annotationSaved" onMouseDown={(event) => event.stopPropagation()} onMouseUp={(event) => event.stopPropagation()}
        onClick={() => remove(annotationObject['key'])}>
        </div>
    );
  }