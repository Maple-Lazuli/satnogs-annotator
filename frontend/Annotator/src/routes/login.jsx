import React, {useState} from "react";
import {redirect, useNavigate} from "react-router-dom";
import Backend from '../api';
import {setSession, setUsername, setJustAuthenticated, setAccountID} from "../credentials"

export default function Login() {
    const [username, setUsernameLocal] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate()

    const onFormSubmit = (event) => {
        event.preventDefault();
    
        onLogin(username, password)
        
      };

    const onLogin = async (username, password) => {
        const response = await Backend.post(
            '/login', {
                    username: username,
                    password: password
    }).then( (res) => {
        console.log(res)
        if (res['data']['status'] == 0){
            setSession(res['data']['code'])
            setUsername(username)
            setAccountID(res['data']['account_id'])
            setJustAuthenticated(true)
            navigate("/Contributions");
        } else {
            alert("Authentication Failed")
        }
    })}

    return (
    <form onSubmit={onFormSubmit}>
        <h2>Login:</h2>
        <div className="mb-3">
        <label htmlFor="username" className="form-label">User Name</label>
        <input type="text" className="form-control" id="username" placeholder=""
        onChange={() => setUsernameLocal(event.target.value)}/>
        </div>
            <div className="mb-3">
                <label htmlFor="exampleInputPassword1" className="form-label">Password</label>
                <input type="password" className="form-control" id="exampleInputPassword1"
                onChange={() => setPassword(event.target.value)}/>
            </div>
            <button type="submit" className="btn btn-primary">Login</button>
    </form>
    );
  }