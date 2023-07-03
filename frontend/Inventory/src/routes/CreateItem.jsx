import React, {useState} from "react";
import {getUsername, getSession} from '../credentials'
import {redirect, useNavigate} from "react-router-dom";
import axios from 'axios';

export default function CreateItem() {
    const [name, setName] = useState("");
    const [quantity, setQuantity] = useState("");
    const [description, setDescription] = useState("");
    const [username, setUsername] = useState("");
    const [session, setSession] = useState("");

    const navigate = useNavigate()

    const onFormSubmit = (event) => {
        event.preventDefault();
        onItemSubmit(name, quantity, description)
      };


    const Backend = axios.create({
        baseURL: 'http://localhost:5001',
        headers: {
          'Content-Type': 'application/json',
          'Accept':'application/json',
          'Authorization': `${username} ${session}`
        }
      })

      getSession().then(s => setSession(s))
      getUsername().then(u => setUsername(u))


    const onItemSubmit = async (name, quantity, description) => {
        const response = await Backend.post(
            '/item', {
                    name: name,
                    description: description,
                    quantity: quantity,
    }).then( (res) => {
        
      navigate("/YourItems")

    })}


    return (
    <form onSubmit={onFormSubmit}>
      <h2>Add an item:</h2>
        <div className="mb-3">
        <label htmlFor="name" className="form-label">Name</label>
        <input type="text" className="form-control" id="name" placeholder=""
        onChange={() => setName(event.target.value)}/>
        </div>
        <div className="mb-3">
        <label htmlFor="description" className="form-label">Description</label>
        <input type="text" className="form-control" id="description" placeholder=""
        onChange={() => setDescription(event.target.value)}/>
        <div className="mb-3">
        <label htmlFor="quantity" className="form-label">Quantity</label>
        <input type="text" className="form-control" id="quantity" placeholder=""
        onChange={() => setQuantity(event.target.value)}/>
        </div>
        </div>
            <button type="submit" className="btn btn-primary">Create Item</button>
    </form>
    );
  }