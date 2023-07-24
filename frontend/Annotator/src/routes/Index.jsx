export default function Index() {

    return(
        <div className="jumbotron">
        <h1 className="display-4">SATNOGS Annotator</h1>
        <p className="lead">This is a tool for annotating SATNOGS Spectrograms</p>
        <hr className="my-4"/>
        <p>Use the button below to see the current annotations</p>
        <p className="lead">
            <a className="btn btn-outline-primary btn-lg" href="/AllItems" role="button">View Current Annotations</a>
        </p>
        </div>
    )
}