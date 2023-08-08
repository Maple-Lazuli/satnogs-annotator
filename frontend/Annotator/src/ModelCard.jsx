import axios from 'axios';
export default function ModelCard(model) {
    return(
    <div class="col-3" key={model['model_id']}>
        <div className="card">
        <div className="card-body">
            <h5 className="card-title">{model['model_name']} </h5> 
            <p className="card-text">{model['description']}</p> 
            <p className="card-text"><small className="text-body-secondary"><i>Created: {model['creation_date'].split(" ")[0]}</i></small></p>
            <a className="btn btn-outline-primary" href={`http://localhost:5173/Model?model_name=${model['model_name']}`} role="button">View</a> 
        </div>
        </div>
    </div>
    )
}