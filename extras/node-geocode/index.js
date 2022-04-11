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

const procIte = async (locations, start, end) => {
    const startAll = Date.now();
    const promises = [];
    for (let i=start; i<end; i++) {
        const location = locations[i];
        const start = Date.now();
        const promise = fetchCoords(location).then(res => {
            let op = `${i},"${location}",`;
            if (!res) {
                op += 'null,null';
            } else {
                op += `${res[0]},${res[1]}`;
            }
            op += '\n';
            const duration = Date.now() - start;
            console.log(`\t\ti: ${i}, dur: ${duration}`);
            return [op, duration];
        });
        promises.push(promise);
    }
    const zipped = await Promise.all(promises);
    const durationAll = Date.now() - startAll;
    // console.log(zipped);
    const ops = [];
    let first=zipped[0][1], min=first, max=first, sum=0;
    zipped.map((e) => { 
        ops.push(e[0]);
        min = Math.min(min, e[1]);
        max = Math.max(max, e[1]);
        sum += e[1];
    });
    const avg = sum/zipped.length;
    console.log(`\ttotal: ${durationAll}, min: ${min}, max: ${max}, avg: ${avg}`);
    return ops.join('');
};

(async()=>{
    const locations = JSON.parse(fs.readFileSync('../locations.json', 'utf8'));
    const count = locations.length;

    const fullItn = Math.floor(count / batchSize);
    console.log(`Count: ${count}, Full Iterations: ${fullItn}`);
    for(let i=722; i<fullItn; i++) {
        const start = i * batchSize;
        const end = start + batchSize;
        console.log(`Index: ${start}`);
        const res = await procIte(locations, start, end);
        // console.log(res);
        fs.appendFileSync('../locations-n.csv', res);
    }
    if (count > fullItn * batchSize) {
        const start = fullItn * batchSize;
        const end = count;
        console.log(`Current index: ${start}`);
        const res = await procIte(locations, start, end);
        // console.log(res);
        fs.appendFileSync('../locations-n.csv', res);
    }
})();
