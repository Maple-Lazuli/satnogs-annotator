import React, {useState} from "react";
import {getUsername, getSession} from '../credentials'
import Backend from '../api';
import ObservationCard from "../observationCard"
import {redirect, useNavigate} from "react-router-dom";

export default function ContributedAnnotations() {
    const [username, setUsername] = useState("");
    const [session, setSession] = useState("");
    getSession().then(s => setSession(s))
    getUsername().then(u => setUsername(u))
    const [observations, setObservations] = useState([]);
    const [tried, setTried] = useState(false);
    const navigate = useNavigate()

    
    const getItems = async () => {
        const response = await Backend.get(
            `/userContributions?username=${username}`, {}).then( (res) => {setObservations(res['data'])})
        }

    if (observations.length == 0 && !tried && username != ""){
        getItems()
        setTried(true)
    }

    return (
        <div class="container">
            <a class="btn btn-primary" href="/StartAnnotation" role="button">Start Annotation</a>
            <hr />
    <div class="row flex-row">
        {
        observations.length == 0 ?
        (<i>You have not contributed yet.</i>):
        (observations.map(observation => ObservationCard(observation, username, session, navigate)))
        }
    </div>
        </div>
    );
    }