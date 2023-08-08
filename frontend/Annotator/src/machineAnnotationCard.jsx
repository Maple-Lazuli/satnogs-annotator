import axios from 'axios';
export default function MachineAnnotationCard(image) {
    return(
    <div class="col-3" key={image['image_id']}>
        <div className="card">
        <img className="card-img-top" src={`http://127.0.0.1:5001/machine_image?image_id=${image['image_id']}`} alt="Card image cap"/>
        <div className="card-body">
            <h5 className="card-title">{image['model_name']} </h5> 
            <p className="card-text"><small className="text-body-secondary"><i>Created: {image['creation_date'].split(" ")[0]}</i></small></p>
        </div>
        </div>
    </div>
    )
}