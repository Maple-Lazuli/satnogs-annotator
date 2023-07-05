import axios from 'axios';
export default function ItemCardOwned(item, session, username) {

    const Backend = axios.create({
        baseURL: 'http://localhost:5001',
        headers: {
          'Content-Type': 'application/json',
          'Accept':'application/json',
          'Authorization': `${username} ${session}`
        }
      })


    const deleteItem = async (item_id, username, session) => {
        const response = await Backend.delete(
            `/item?item_id=${item_id}`).then( (res) => {
        console.log(res)

        navigate("/YourItems")
    
    })}

    return(
        <div class="col-3" key={item.name + item.item_id}>
            <div className="card">
            <div className="card-body">
                <h5 className="card-title">{item.name}</h5>
                <h6 className="card-subtitle mb-2 text-body-secondary">Quantity: {item.quantity}</h6>
                <p className="card-text">{item.description.length <= 100 ? (item.description): (item.description.slice(0,100) + "...")}</p> 
                <a href={`/EditItem?item_id=${item.item_id}`} class="card-link">Edit</a>
                <a href={"/YourItems"} class="card-link" onClick={() => deleteItem(item.item_id, username, session)}>Delete</a>
            </div>
            </div>
        </div>
        )
    }

