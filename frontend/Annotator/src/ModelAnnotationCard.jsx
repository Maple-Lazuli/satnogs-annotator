import axios from 'axios';
export default function ModelAnnotationCard(image) {

    return(
    <div class="col-3" key={image['image_id']}>
        <div className="card">
        <img className="card-img-top" src={`http://127.0.0.1:5001/machine_image?image_id=${image['image_id']}`} alt="Card image cap"/>
        <div className="card-body">
            <h5 className="card-title">{image['satnogs_id']} </h5> 
            <h6 className="card-subtitle mb-2 text-body-secondary">{image['satellite']} ({image['transmitter']})</h6>
            <p className="card-text"><small className="text-body-secondary"><i>Created: {image['creation_date'].split(" ")[0]}</i></small></p>
            <a className="btn btn-outline-primary" href={`http://localhost:5173/CreateAnnotation?observation_id=${image['satnogs_id']}`} role="button">View</a> 
        </div>
        </div>
    </div>
    )
}