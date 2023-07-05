import React, {useState} from "react";
import {getUsername, getSession} from '../credentials'
import {redirect, useNavigate} from "react-router-dom";
import axios from 'axios';

export default function StartAnnotation() {
    const [satnogs_id, setSatnogs] = useState("");
    const [username, setUsername] = useState("");
    const [session, setSession] = useState("");

    const navigate = useNavigate()

    const onFormSubmit = (event) => {
        event.preventDefault();
        onSatnogsSubmit(satnogs_id)
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


    const onSatnogsSubmit = async (satnogs_id) => {
        const response = await Backend.post(
            '/pullSatnogs', {
                    satnogs_id: satnogs_id,
    }).then( (res) => {
        
      navigate(`/CreateAnnotation?observation_id=${satnogs_id}`)

    })}


    return (
    <form onSubmit={onFormSubmit}>
      <h2>Start An Annotation:</h2>
        <div className="mb-3">
        <label htmlFor="name" className="form-label">Satnogs Observation ID</label>
        <input type="text" className="form-control" id="name" placeholder=""
        onChange={() => setSatnogs(event.target.value)}/>
        </div>
            <button type="submit" className="btn btn-primary">Submit ID</button>
    </form>
    );
  }