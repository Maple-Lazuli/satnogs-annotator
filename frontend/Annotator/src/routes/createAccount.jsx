import React, {useState} from "react";
import {redirect, useNavigate} from "react-router-dom";
import Backend from '../api';

export default function CreateAccount() {
    const [firstname, setFirstname] = useState("");
    const [lastname, setLastname] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate()

    const onFormSubmit = (event) => {
        event.preventDefault();
    
        onAccountSubmit(firstname, lastname, username, password, "manager")
        
      };

    const onAccountSubmit = async (firstname, lastname, username, password, role) => {


        if (username.indexOf(' ') >= 0){
            alert("Spaces are not accepted in usernames.")
        } else {

    
                const response = await Backend.post(
                    '/account', {
                            role_name: role,
                            first_name: firstname,
                            last_name: lastname,
                            username: username,
                            password: password
            }).then( (res) => {
                
                if (res['data']['created']){
                    alert("Account Created Successfully.")
                    navigate("/login");
                } else {
                    alert("Account Could Not Be Created.")
                }
    
    })}}


    return (
    <form onSubmit={onFormSubmit}>
        <h2>Create an account:</h2>
        <div className="mb-3">
        <label htmlFor="firstname" className="form-label">First Name</label>
        <input type="text" className="form-control" id="firstname" placeholder=""
        onChange={() => setFirstname(event.target.value)}/>
        </div>
        <div className="mb-3">
        <label htmlFor="lastname" className="form-label">Last Name</label>
        <input type="text" className="form-control" id="lastname" placeholder=""
        onChange={() => setLastname(event.target.value)}/>
        </div>
        <div className="mb-3">
        <label htmlFor="username" className="form-label">User Name</label>
        <input type="text" className="form-control" id="username" placeholder=""
        onChange={() => setUsername(event.target.value)}/>
        </div>
            <div className="mb-3">
                <label htmlFor="exampleInputPassword1" className="form-label">Password</label>
                <input type="password" className="form-control" id="exampleInputPassword1"
                onChange={() => setPassword(event.target.value)}/>
            </div>
            <button type="submit" className="btn btn-primary">Create Account</button>
    </form>
    );
  }