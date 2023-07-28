import React, {useState} from "react";
import './annotator.css'
export default function annotationDisplay(annotationObject, remove, update, box) {  

    // const verifyAnnotation = (annotationObject, box) => {
    //     let a = JSON.parse(JSON.stringify(annotationObject));
    //     if (a['image_width'] != box.width) {
    //         a['upperLeft'][0] = a['upperLeft'][0] * box.width / a['image_width']
    //         a['lowerRight'][0] = a['lowerRight'][0] * box.width / a['image_width']
    //     }
    //     if (a['image_height'] != box.height) {
    //         a['upperLeft'][1] = a['upperLeft'][1] * box.height / a['image_height']
    //         a['lowerRight'][1] = a['lowerRight'][1] * box.height / a['image_height']
    //     }
    //     return a
    // }
    
    const a = annotationObject

    return (
        <div key = {a['key']} style={{'left': a['upperLeft'][0] + box['left'],
        "top":a['upperLeft'][1] + box['top'], 'width':a['lowerRight'][0] - a['upperLeft'][0],
        'height':a['lowerRight'][1] - a['upperLeft'][1]}} className="annotationSaved" onMouseDown={(event) => event.stopPropagation()} onMouseUp={(event) => event.stopPropagation()}
        onClick={() => remove(annotationObject['key'])}>
        </div>
    );
  }