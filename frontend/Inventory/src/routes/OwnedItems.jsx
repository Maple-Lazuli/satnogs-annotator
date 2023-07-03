import React, {useState} from "react";
import {redirect, useNavigate} from "react-router-dom";
import Backend from '../api';
import {getUsername, getSession} from '../credentials'
import ItemCardOwned from "../itemCardOwned"



export default function OwnedItems() {
    const [items, setItems] = useState([]);
   // const [accountID, setAccountID] = useState(-1);
    const [session, setSession] = useState("");
    const [username, setUserName] = useState("");
    const [tried, setTried] = useState(false);
    const navigate = useNavigate()
    getSession().then(s => setSession(s))
    getUsername().then(u => setUserName(u))


    const getItems = async () => {
        let aID = null
        let u = null 
        await getUsername().then(i => {u = i})

        const response1 = await Backend.get(`/account?username=${u}`, {}).then( (res) => {aID = res['data'].account_id})
        const response2 = await Backend.get('/items', {}).then( (res) => {setItems(res['data'].filter(item => item.account_id == aID))})
    }

    if (items.length == 0 && !tried){
        getItems()
        setTried(true)
    }
    
    return (
        <div class="container">
            <a class="btn btn-primary" href="/CreateItem" role="button">Add Item</a>
            <hr />
        <div class="row flex-row">
        {items.map(item => ItemCardOwned(item, session, username))}
        </div>
        </div>
    );
  }