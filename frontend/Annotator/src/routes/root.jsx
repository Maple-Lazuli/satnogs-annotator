import { Outlet, useNavigate } from "react-router-dom";
import {getUsername, getSession, getJustAuthenticated, setJustAuthenticated, setActiveSession, getActiveSession} from "../credentials"

import React, { useRef, useEffect, useState } from 'react'

import localforage from "localforage";

export default function Root() {
  const navigate = useNavigate()
  const [active, setActive] = useState(null);
  const [username, setUsername] = useState("");
  

  getJustAuthenticated().then( (status) => {
    if (status){
      setActive(status)
      setJustAuthenticated(false)
      setActiveSession(true)
      getUsername().then( (u) => {setUsername(u)} )
    }
  })

  if (active == null){
    getActiveSession().then(status => setActive(status))
    getUsername().then( (u) => {setUsername(u)} )
  }

  const logout = () => {
    setActive(false)
    setActiveSession(false)
    navigate("/Allitems")
  }

  return (
        <>
          <nav className="navbar navbar-expand-lg bg-body-tertiary">
            <div className="container-fluid">
              <a className="navbar-brand" href="/">Annotator</a>
              <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span className="navbar-toggler-icon"></span>
              </button>
              <div className="collapse navbar-collapse" id="navbarSupportedContent">
                <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                  <li className="nav-item">
                    <a className="nav-link" aria-current="page" href="/allObservations">All Annotations</a>
                  </li>
                  <li className="nav-item">
                    <a className={active? ('nav-link') : ('nav-link disabled')} href="/YourAnnotations">Your Annotations</a>
                  </li>
                </ul>
                { active?(<>
                <i>Logged in as: &nbsp;</i><b>{username}&nbsp;</b>
                <button type="button" class="btn btn-outline-secondary" onClick={() => {logout()}}>Log Out</button>
                </>):(<>
                <button type="button" class="btn btn-outline-primary" onClick={() => {navigate("/login")}}>Log In</button>
                &nbsp;
                <button type="button" class="btn btn-outline-secondary" onClick={() => {navigate("/createAccount")}}>Create Account</button>
                </>
                )}
              </div>
            </div>
          </nav>
          <br/>
          <div className="container">
          <Outlet />
            </div>
</>
    );
  }