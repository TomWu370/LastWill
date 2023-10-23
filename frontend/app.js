const { MongoClient, ServerApiVersion } = require('mongodb');
const uri = "mongoDBURL";
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true, serverApi: ServerApiVersion.v1 });
client.connect(err => {
  const collection = client.db("test").collection("devices");
  console.log("success")
  // perform actions on the collection object
  client.close();
});
const simulateAsyncPause = () =>
  new Promise(resolve => {
    setTimeout(() => resolve(), 1000);
  });
let changeStream;

async function run() {
  try {
    await client.connect();
    const database = client.db("lastwill");
    const collection = database.collection("contract");
    // open a Change Stream on the "haikus" collection
    changeStream = collection.watch();
    // set up a listener when change events are emitted
    changeStream.on("change", next => {
      // process any change event
      console.log("received a change to the collection: \t", next.operationType, );
    });
    // await simulateAsyncPause();


    await changeStream.close();

    console.log("closed the change stream");
  } finally {
    await client.close();
    run().catch(console.dir);
  }
}
run().catch(console.dir);
