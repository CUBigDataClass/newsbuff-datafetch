require('dotenv').config()
const fetch = require('node-fetch');
const fs = require('fs');
const base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
const key = process.env.google_api_key;

const fetchTimeout = async (i, url, timeout = 10000) => {
    try {
        const response = await Promise.race([
            fetch(url),
            new Promise((_, reject) =>
                setTimeout(() => reject(new Error('timeout')), timeout)
            )
        ]);
        return response;
    } catch {
        console.log(`\t\ti: ${i}, timed out, retrying...`)
        await new Promise(resolve => setTimeout(resolve, timeout));
        return fetchTimeout(i, url, timeout);
    }
};

const fetchCoords = async (i, location) => {
    const url = `${base_url}?address=${location}&key=${key}`
    const response = await fetchTimeout(i, url);
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
        const promise = fetchCoords(i, location).then(res => {
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

const locationFetchCoords = async () => {
    const locations = JSON.parse(fs.readFileSync('../locations.json', 'utf8'));
    const count = locations.length;
    const batchSize = 40;
    const fullItn = Math.floor(count / batchSize);
    console.log(`Count: ${count}, Full Iterations: ${fullItn}`);
    for(let i=1316; i<fullItn; i++) {
        const start = i * batchSize;
        const end = start + batchSize;
        console.log(`Iteration: ${i}, Index: ${start}`);
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
};

const readLine = (line) => {
    const firstComma = line.indexOf(',');
    const index = +line.slice(0, firstComma);
    const lastComma = line.lastIndexOf(',');
    const data2 = line.slice(firstComma, lastComma);
    const secondLastComma = data2.lastIndexOf(',');
    const location = line.slice(firstComma + 2, firstComma + secondLastComma - 1);
    const latitude = +data2.slice(secondLastComma + 1);
    const longitude = +line.slice(lastComma + 1);
    return {index, location, latitude, longitude};
};

const locationsJson = () => {
    const locationsData = fs.readFileSync('../locations-n.csv', 'utf8');
    const records = locationsData.split('\n');
    console.log(records.length);
    const locations = records.map(e=>readLine(e));
    console.log(locations.length);
    console.log(locations[0]);
    const locationsDataJson = JSON.stringify(locations, undefined, 2);
    fs.writeFileSync('../locations-n3.json', locationsDataJson, 'utf8');
};

const locationsTrim = () => {
    const locations = JSON.parse(fs.readFileSync('../locations-n3.json', 'utf8'));
    for(let i=0; i<locations.length; i++) {
        locations[i].location = locations[i].location.trim().replace(/\s+/g, ' ');
    }
    const locationsDataJson = JSON.stringify(locations, undefined, 2);
    fs.writeFileSync('../locations-tr.json', locationsDataJson, 'utf8');
};

(async()=>{
    locationsTrim();
})();
