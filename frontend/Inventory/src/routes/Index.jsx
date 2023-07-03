export default function Index() {

    return(
        <div className="jumbotron">
        <h1 className="display-4">Inventory Manager</h1>
        <p className="lead">This is a simple Create Read Update Delete (CRUD) App for managing inventory.</p>
        <hr className="my-4"/>
        <p>Use the button below to see the current inventory</p>
        <p className="lead">
            <a className="btn btn-outline-primary btn-lg" href="/AllItems" role="button">View Current Inventory</a>
        </p>
        </div>
    )
}