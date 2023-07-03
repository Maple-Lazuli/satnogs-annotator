import localforage from "localforage";

  export function setAccount(account) {
    return localforage.setItem("account", account);
}

export async function getAccount() {
    return await localforage.getItem("account")
}

export async function getSession() {
    return await localforage.getItem("session_code")
}

export async function setSession(session_code) {
    return localforage.setItem("session_code", session_code);
  }

export async function getUsername() {
    return await localforage.getItem("username")
}

export async function setUsername(username) {
    return localforage.setItem("username", username);
  }

  export async function getJustAuthenticated() {
    return await localforage.getItem("just_authenticated")
}

export async function setJustAuthenticated(status) {
    return localforage.setItem("just_authenticated", status)
  }


  export async function getAccountID() {
    return await localforage.getItem("account_id")
}

export async function setAccountID(id) {
    return localforage.setItem("account_id", id)
  }

  export async function getActiveSession() {
    return await localforage.getItem("session_status")
}

export async function setActiveSession(status) {
    return localforage.setItem("session_status", status)
  }
