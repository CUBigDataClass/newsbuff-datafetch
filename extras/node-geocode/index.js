require('dotenv').config()
const fetch = require('node-fetch');
const fs = require('fs');
const base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
const key = process.env.google_api_key;
const batchSize = 40;

const fetchCoords = async (location) => {
    const url = `${base_url}?address=${location}&key=${key}`
    const response = await fetch(url);
    if (!response.ok) return null;
    const data = await response.json();
    try {
        const {lat, lng} = data.results[0].geometry.location;
        return [lat, lng];
    } catch {
        return null;
    }
};

const procIte = (locations, start, end) => {
    const promises = [];
    for (let i=start; i<end; i++) {
        const location = locations[i];
        const promise = fetchCoords(location).then(res => {
            let op = `${i},"${location}",`;
            if (!res) {
                op += 'null,null';
            } else {
                op += `${res[0]},${res[1]}`;
            }
            op += '\n';
            return op;
        });
        promises.push(promise);
    }
    return Promise.all(promises);
};

(async()=>{
    const locations = JSON.parse(fs.readFileSync('../locations.json', 'utf8'));
    const count = locations.length;

    const fullItn = Math.floor(count / batchSize);
    console.log(count, fullItn);
    for(let i=595; i<fullItn; i++) {
        const start = i * batchSize;
        const end = start + batchSize;
        console.log(`Current index: ${start}`);
        const res = await procIte(locations, start, end);
        const cont = res.join('');
        // console.log(cont);
        fs.appendFileSync('../locations-n.csv', cont);
    }
    if (count > fullItn * batchSize) {
        const start = fullItn * batchSize;
        const end = count;
        console.log(`Current index: ${start}`);
        const res = await procIte(locations, start, end);
        const cont = res.join('');
        // console.log(cont);
        fs.appendFileSync('../locations-n.csv', cont);
    }
})();
