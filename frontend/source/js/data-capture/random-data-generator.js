
function randomize(item){
  const max = item.length;
  // Get random index of passed array
  return item[Math.round(Math.random() * (max + 1))];
}

function generateVendorName(){
  const vendorNames = ["Bailey", "Battaglia", "Brouilette", "Seppi", "Trammell", "Varma"];
  const vendorServices = ["Button-Pressing", "Bike Shed", "Cat Herding", "Interpretive Dance", "Sausage", "Spandex", "Underwater Basket Weaving"];
  const vendorBizTypes = ["Emporium", ", LLC", ", Inc.", "Providers", "Services", "Solutions", "Suppliers"];

  const vendorName = `${randomize(vendorNames)}'s ${randomize(vendorServices)} ${randomize(vendorBizTypes)}`;

  return vendorName;
}

function generateRandomDataset() {
  /* TODO: build out a single set of dummy data */
  const data = {
    "vendor": generateVendorName()
  };
  return data;
}

/* Generate desired number of sets of vendor data */
function generateRandomData(limit){
  const data = [];
  for (let i=0; i<limit; i++) {
    data.push(generateRandomDataset());
  }
  return data;
}

let randomData = generateRandomData(3);
