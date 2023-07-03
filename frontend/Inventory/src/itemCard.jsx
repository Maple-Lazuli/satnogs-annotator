export default function ItemCard(item, accounts) {

    return(
    <div class="col-3" key={item.name + item.item_id}>
        <div className="card">
        <div className="card-body">
            <h5 className="card-title">{item.name} ({item.quantity})</h5>
            <h6 className="card-subtitle mb-2 text-body-secondary">Owner: &nbsp;{item.account_id}</h6>
            <p className="card-text">{item.description.length <= 100 ? (item.description): (item.description.slice(0,100) + "...")}</p> 
            <p class="card-text"><small class="text-body-secondary">{item.modification_date? (<i>Updated: {item.modification_date.split(".")[0]}</i>) : (<i>Created: {item.creation_date.split(".")[0]}</i>)}</small></p>
        </div>
        </div>
    </div>
    )
}