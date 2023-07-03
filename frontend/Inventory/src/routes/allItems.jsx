import React, {useState} from "react";
import {redirect, useNavigate} from "react-router-dom";
import Backend from '../api';
import ItemCard from "../itemCard"


export default function ShowAllItems() {
    const [items, setItems] = useState([]);
    const [accounts, setAccounts] = useState([]);
    const [tried, setTried] = useState(false);
    

    const getItems = async () => {
        const response = await Backend.get(
            '/itemsMapped', {}).then( (res) => {setItems(res['data'])})}

    if (items.length == 0 && !tried){
        getItems()
        setTried(true)
    }

    return (
        <div class="container">
<div class="row flex-row">
        {
        items.length == 0 ?
        (<i>No items have been added yet.</i>):
        (items.map(item => ItemCard(item)))
        }
</div>
        </div>
    );
  }