import React, {useState} from "react";
import Backend from '../api';
import ModelCard from "../ModelCard"


export default function Models() {

    const [models, setModels] = useState([]);
    const [tried, setTried] = useState(false);
    

    const getModels = async () => {
        const response = await Backend.get(
            '/models', {}).then( (res) => {setModels(res['data'])})}

    if (models.length == 0 && !tried){
        getModels()
        setTried(true)
    }

    return (
        <div class="container">
            <div class="row flex-row">
        {
        models.length == 0 ?
        (<i>No models have been added yet.</i>):
        (models.map(model => ModelCard(model)))
        }
    </div>
        </div>
    );
  }