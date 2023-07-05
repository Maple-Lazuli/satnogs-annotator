import React, {useState} from "react";
import {getUsername, getSession} from '../credentials'
import {redirect, useNavigate} from "react-router-dom";
import axios from 'axios';
import Backend from '../api';

export default function CreateItem() {
    const [name, setName] = useState("");
    const [quantity, setQuantity] = useState("");
    const [description, setDescription] = useState("");
    const [itemId, setItemID] = useState(null);
    
    const [username, setUsername] = useState("");
    const [session, setSession] = useState("");
    const [editMode, setEditMode] = useState(false);
    

    const navigate = useNavigate()

    const onFormSubmit = (event) => {
        event.preventDefault();
      };


    const BackendAuthorized = axios.create({
        baseURL: 'http://localhost:5001',
        headers: {
          'Content-Type': 'application/json',
          'Accept':'application/json',
          'Authorization': `${username} ${session}`
        }
      })

      getSession().then(s => setSession(s))
      getUsername().then(u => setUsername(u))


    const onItemSubmit = async (itemId, name, quantity, description) => {

      
        const response = await BackendAuthorized.put(
            '/item', {
                    item_id: itemId,
                    name: name,
                    description: description,
                    quantity: quantity,
    }).then( (res) => {

      navigate("/YourItems");
    })}

    const fetchItem = async () => {

      const response = await Backend.get(
          `/item?item_id=${window.location.search.split("=")[1]}`, {}).then( (res) => {

            setItemID(window.location.search.split("=")[1])
            setName(res['data']['name'])
            setQuantity(res['data']['quantity'])
            setDescription(res['data']['description'])

          })}

    if (itemId == null){
      fetchItem()
    }


    const enableEdits = () => {
      setEditMode(true)
      document.getElementById("name").value = name
      document.getElementById("description").value = description
      document.getElementById("quantity").value = quantity
    }

    const disableEdits = () => {
      setEditMode(false)
      fetchItem()
      document.getElementById("name").value = ""
      document.getElementById("description").value = ""
      document.getElementById("quantity").value = "" 
    }

    
        
    return (
    <form onSubmit={onFormSubmit}>
        <div className="mb-3">
        <label htmlFor="name" className="form-label">Name</label>
        <input type="text" className="form-control disabled" id="name" placeholder={name}
        onChange={() => setName(event.target.value)} readOnly={!editMode}/>
        </div>
        <div className="mb-3">
        <label htmlFor="description" className="form-label">Description</label>
        <input type="text" className="form-control" id="description" placeholder={description}
        onChange={() => setDescription(event.target.value)} readOnly={!editMode}/>
        <div className="mb-3">
        <label htmlFor="quantity" className="form-label">Quantity</label>
        <input type="text" className="form-control" id="quantity" placeholder={quantity}
        onChange={() => setQuantity(event.target.value)} readOnly={!editMode}/>
        </div>
        </div>
        {editMode? (<>
          <button type="submit" className="btn btn-danger" onClick={() => onItemSubmit(itemId, name, quantity, description)}>Submit Edits</button>
          <button type="button" className="btn btn-secondary" onClick={() => disableEdits()}>Cancel Edits</button>
        </>):(<>
          <button type="button" className="btn btn-warning" onClick={() => enableEdits()}>Enable Edits</button>
        </>)
        }

            
    </form>
    );
  }