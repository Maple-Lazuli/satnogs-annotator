import React, {useState} from "react";
import Backend from '../api';
import ModelAnnotationCard from "../ModelAnnotationCard"


export default function Model() {

    const [fetched, setFetched] = useState(false);
    const [images, setImages] = useState([]);
  
  
      const get_image_id = async () => {
  
        const response = await Backend.get(
            `/machine_images?model_name=${window.location.search.split("=")[1]}`, {}).then( (res) => {
              setImages(res['data'])
            })}
  
      if (!fetched){
        setFetched(true)
        get_image_id()
      }

    return (
        <div class="container">
            <div class="row flex-row">
        {
        images.length == 0 ?
        (<i>No images have been added yet.</i>):
        (images.map(image => ModelAnnotationCard(image)))
        }
    </div>
        </div>
    );
  }