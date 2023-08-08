import React, {useState} from "react";
import Backend from '../api';
import MachineAnnotationCard from "../machineAnnotationCard"

export default function MachineObservationAnnotations(satnogs_id) {

  const [fetched, setFetched] = useState(false);
  const [images, setImages] = useState([]);


    const get_image_id = async () => {

      const response = await Backend.get(
          `/machine_images?satnogs_id=${satnogs_id}`, {}).then( (res) => {
            setImages(res['data'])
          })}

    if (!fetched){
      setFetched(true)
      get_image_id()
    }
    

    return (
      <div class="row flex-row">
        {images.map(i => MachineAnnotationCard(i))}
    
    </div>
    );
  }