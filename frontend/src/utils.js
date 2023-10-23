async function createContract(form) {
  alert("creating smart contract")
  const web3 = new Web3(window.ethereum)
  // const address = '0xwalletaddress'
  const accounts = await web3.eth.getAccounts();

  const abi = JSON.parse(JSON.stringify(lastWillABI));
  const data = lastWillBytes;

  var timed_willContract = new web3.eth.Contract(abi);
  recipents = await getRecipentArray(form);
  console.log(recipents[0])
  let address
  var timed_will = await timed_willContract.deploy({
  data: data,
  arguments: [
      new Date(form.exdate.value).getTime()/1000,
      form.frequency.value * form.multiplier.value,
      recipents[0],
      recipents[1]

  ]
  }).send({
  from: accounts[0],
  gas: '4700000'
  }, function (e, contract){
  console.log(e, contract);
  if (typeof contract.address !== 'undefined') {
     console.log('Contract mined! address: ' + contract.address + ' transactionHash: ' + contract.transactionHash);
  }
  }).on('receipt', function(receipt){
    console.log(receipt.contractAddress);
    address = receipt.contractAddress;
     // contains the new contract address
  })
  return address
}

async function confirmLive(address) {
  const web3 = new Web3(window.ethereum)
  await window.ethereum.enable();
  web3.eth.defaultAccount = web3.eth.accounts[0]
  const abi = JSON.parse(JSON.stringify(lastWillABI));
  const timed = new web3.eth.Contract(abi, address)
  await timed.methods.confirmLive().send()
}

async function sendJSON(json, address, form, operationType) {
  console.log("again")
  fetch(window.location.href, {
    method:"POST",
    body: JSON.stringify({
      contractAddress: address,
      contractName: json["contractName"],
      surname: json["surname"],
      firstname: json["firstname"],
      email: json["email"],
      expirationDate: json["expirationDate"],
      frequency: json["frequency"],
      recipents: await getCombinedArray(await getRecipentArray(form)),
      operationType: operationType
        })
    }).then(result => result.json())
      .then(data => {
        // do something with the result
        console.log("Completed with result:", data.response);
    }).catch(err => {
        // if any error occured, then catch it here
        console.error(err);
    });
}

async function processFile(file, remail) {
    // for processing file input and retrieval
  const node = await Ipfs.create({repo: 'ok'+ Math.random()});
  const version = await node.version();

  console.log("Version:", version.version);

  const result = await node.add(file);
  console.log(result);
  //const filen = await node.get("ipfs.io url")
  //document.getElementById("download").href = "https://ipfs.io/ipfs/" + result.path + "?filename=" + filename.type + "&download=true"; //get file anme and file type from mongodb
  url = "https://ipfs.io/ipfs/" + result.path + "?filename=" + file.name.replace(/\s/g, '') + "&download=true";
  console.log(result.path)
  // make this an json then add keypairs in it
  // add recipient email
  let processedFile = {
    remail: remail,
    url: url,
  }
  console.log(processedFile)

  return processedFile;
}

async function getRecipentArray(form) {
  let addresses = [];
  let amounts = [];
  let emails = [];
  let recipents = form.querySelectorAll("[id^=recipent]")
  for (let l = 0; l < recipents.length; l++) {
    // console.log(recipents[l].querySelector("[id^=raddress]").value)
    // console.log("here");
    // alert(stuff.value);
    await addresses.push(recipents[l].querySelector("[id^=raddress]").value);
    await amounts.push(Web3.utils.toBN(recipents[l].querySelector("[id^=bar]").value));
    await emails.push(recipents[l].querySelector("[id^=remail]").value);
  }
  let array = [addresses, amounts, emails]; // use array[0] to access addresses only
  // alert(array.toString())
  return array;
}

async function getCombinedArray(arrays) {
  let newArray = [];
  for (let m = 0; m < arrays[0].length; m++) {
    let value1 = arrays[0][m].toString(); // address
    let value2 = arrays[1][m].toString(); // amounts
    let value3 = arrays[2][m].toString(); // email
    let tempJSON = {
      raddress: value1,
      amounts: value2,
      remail: value3
    }; // json
    newArray.push(tempJSON);
    // newArray.push(["item1", "item1.2"])
    // newArray.push(["item2"])

  }
  return newArray;
}

  // scheduleTransaction();
  // var abi = await fetch("../contracts/lastwillabi.json")
  // var abi = [{"inputs":[{"internalType":"uint256","name":"value","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"uint256","name":"_funds","type":"uint256"}],"name":"addFund","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getFund","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalFunds","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]
  //
  //
  //
  // var timed_willContract = new web3.eth.Contract(abi);
  // var timed_will = timed_willContract.deploy({
  // data: '0x608060405234801561001057600080fd5b506040516102cb3803806102cb83398181016040528101906100329190610054565b80600081905550506100a7565b60008151905061004e81610090565b92915050565b60006020828403121561006a5761006961008b565b5b60006100788482850161003f565b91505092915050565b6000819050919050565b600080fd5b61009981610081565b81146100a457600080fd5b50565b610215806100b66000396000f3fe608060405234801561001057600080fd5b50600436106100415760003560e01c8063346c96e9146100465780638edd6eb614610062578063968ed60014610080575b600080fd5b610060600480360381019061005b91906100dd565b61009e565b005b61006a6100b9565b6040516100779190610119565b60405180910390f35b6100886100c2565b6040516100959190610119565b60405180910390f35b806000808282546100af9190610134565b9250508190555050565b60008054905090565b60005481565b6000813590506100d7816101c8565b92915050565b6000602082840312156100f3576100f26101c3565b5b6000610101848285016100c8565b91505092915050565b6101138161018a565b82525050565b600060208201905061012e600083018461010a565b92915050565b600061013f8261018a565b915061014a8361018a565b9250827fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0382111561017f5761017e610194565b5b828201905092915050565b6000819050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052601160045260246000fd5b600080fd5b6101d18161018a565b81146101dc57600080fd5b5056fea26469706673582212204dfacda5c0205130279a8ebe147d19dcc4d2848c43bde3ef410596ebf119261664736f6c63430008070033',
  // arguments: [
  //     param
  //     // param2,
  //     // param3
  // ]
  // }).send({
  // from: accounts[0],
  // gas: '4700000'
  // }, function (e, contract){
  // console.log(e, contract);
  // if (typeof contract.address !== 'undefined') {
  //    console.log('Contract mined! address: ' + contract.address + ' transactionHash: ' + contract.transactionHash);
  // }
  // }).on('receipt', function(receipt){
  // console.log(receipt.contractAddress) // contains the new contract address
  // })
  //    const timed = new web3.eth.Contract(abi, address)
  //    console.log(await timed.methods.getFund().call())
  // }
